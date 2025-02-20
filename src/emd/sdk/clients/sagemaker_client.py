import json
import os
from typing import Optional,Dict,Any,Union
import io
from urllib.parse import urlparse
from pydantic import model_validator
import uuid
import codecs
import time
from functools import reduce
import botocore
import threading
from botocore.exceptions import WaiterError
from botocore.exceptions import ClientError

from .client_base import ClientBase
from emd.utils.aws_service_utils import check_stack_exists,get_model_stack_info
from emd.models import Model
from emd.constants import MODEL_DEFAULT_TAG
from emd.utils.logger_utils import get_logger
# from sagemaker.async_inference

logger = get_logger(__name__)


class AsyncInferenceError(Exception):
    """The base exception class for Async Inference exceptions."""

    fmt = "An unspecified error occurred"

    def __init__(self, **kwargs):
        msg = self.fmt.format(**kwargs)
        Exception.__init__(self, msg)
        self.kwargs = kwargs


class PollingTimeoutError(AsyncInferenceError):
    """Raised when wait longer than expected and no result object in Amazon S3 bucket yet"""

    fmt = "No result at {output_path} after polling for {seconds} seconds. {message}"

    def __init__(self, message, output_path, seconds):
        super().__init__(message=message, output_path=output_path, seconds=seconds)

class AsyncInferenceModelError(AsyncInferenceError):
    """Raised when model returns errors for failed requests"""

    fmt = "Model returned error: {message} "

    def __init__(self, message):
        super().__init__(message=message)

class UnexpectedClientError(AsyncInferenceError):
    """Raised when ClientError's error code is not expected"""

    fmt = "Encountered unexpected client error: {message}"

    def __init__(self, message):
        super().__init__(message=message)



class ObjectNotExistedError(AsyncInferenceError):
    """Raised when Amazon S3 object not exist in the given path"""

    fmt = "Object not exist at {output_path}. {message}"

    def __init__(self, message, output_path):
        super().__init__(message=message, output_path=output_path)



class LineIterator:
    """
    A helper class for parsing the byte stream input.

    The output of the model will be in the following format:

    b'{"outputs": [" a"]}\n'
    b'{"outputs": [" challenging"]}\n'
    b'{"outputs": [" problem"]}\n'
    ...

    While usually each PayloadPart event from the event stream will
    contain a byte array with a full json, this is not guaranteed
    and some of the json objects may be split acrossPayloadPart events.

    For example:

    {'PayloadPart': {'Bytes': b'{"outputs": '}}
    {'PayloadPart': {'Bytes': b'[" problem"]}\n'}}


    This class accounts for this by concatenating bytes written via the 'write' function
    and then exposing a method which will return lines (ending with a '\n' character)
    within the buffer via the 'scan_lines' function.
    It maintains the position of the last read position to ensure
    that previous bytes are not exposed again.

    For more details see:
    https://aws.amazon.com/blogs/machine-learning/elevating-the-generative-ai-experience-introducing-streaming-support-in-amazon-sagemaker-hosting/
    """

    def __init__(self, stream: Any) -> None:
        self.byte_iterator = iter(stream)
        self.buffer = io.BytesIO()
        self.read_pos = 0

    def __iter__(self) -> "LineIterator":
        return self

    def __next__(self) -> Any:
        while True:
            self.buffer.seek(self.read_pos)
            line = self.buffer.readline()
            if line and line[-1] == ord("\n"):
                self.read_pos += len(line)
                return line[:-1]
            try:
                chunk = next(self.byte_iterator)
            except StopIteration:
                if self.read_pos < self.buffer.getbuffer().nbytes:
                    continue
                raise
            if "PayloadPart" not in chunk:
                # Unknown Event Type
                continue
            self.buffer.seek(0, io.SEEK_END)
            self.buffer.write(chunk["PayloadPart"]["Bytes"])


class WaiterConfig(object):
    """Configuration object passed in when using async inference and wait for the result."""

    def __init__(
        self,
        max_attempts=60,
        delay=15,
    ):
        """Initialize a WaiterConfig object that provides parameters to control waiting behavior.

        Args:
            max_attempts (int): The maximum number of attempts to be made. If the max attempts is
            exceeded, Amazon SageMaker will raise ``PollingTimeoutError``. (Default: 60)
            delay (int): The amount of time in seconds to wait between attempts. (Default: 15)
        """

        self.max_attempts = max_attempts
        self.delay = delay

    def _to_request_dict(self):
        """Generates a dictionary using the parameters provided to the class."""
        waiter_dict = {
            "Delay": self.delay,
            "MaxAttempts": self.max_attempts,
        }

        return waiter_dict



class AsyncInferenceResponse(object):
    """Response from Async Inference endpoint

    This response object provides a method to check for an async inference result in the
    Amazon S3 output path specified. If result object exists in that path, get and return
    the result
    """

    def __init__(
        self,
        predictor_async,
        output_path,
        failure_path,
    ):
        """Initialize an AsyncInferenceResponse object.

        AsyncInferenceResponse can help users to get async inference result
        from the Amazon S3 output path

        Args:
            predictor_async (sagemaker.predictor.AsyncPredictor): The ``AsyncPredictor``
                that return this response.
            output_path (str): The Amazon S3 location that endpoints upload inference responses
                to.
            failure_path (str): The Amazon S3 location that endpoints upload model errors
                for failed requests.
        """
        self.predictor_async = predictor_async
        self.output_path = output_path
        self._result = None
        self.failure_path = failure_path

    def get_result(
        self,
        waiter_config=None,
    ):
        """Get async inference result in the Amazon S3 output path specified

        Args:
            waiter_config (sagemaker.async_inference.waiter_config.WaiterConfig): Configuration
                for the waiter. The pre-defined value for the delay between poll is 15 seconds
                and the default max attempts is 60
        Raises:
            ValueError: If a wrong type of object is provided as ``waiter_config``
        Returns:
            object: Inference result in the given Amazon S3 output path. If a deserializer was
                specified when creating the AsyncPredictor, the result of the deserializer is
                returned. Otherwise the response returns the sequence of bytes
                as is.
        """
        if waiter_config is not None and not isinstance(waiter_config, WaiterConfig):
            raise ValueError("waiter_config should be a WaiterConfig object")

        if self._result is None:
            if waiter_config is None:
                self._result = self._get_result_from_s3(self.output_path, self.failure_path)
            else:
                self._result = self.predictor_async._wait_for_output(
                    self.output_path, self.failure_path, waiter_config
                )
        return self._result

    def _get_result_from_s3(self, output_path, failure_path):
        """Retrieve output based on the presense of failure_path"""
        if failure_path is not None:
            return self._get_result_from_s3_output_failure_paths(output_path, failure_path)

        return self._get_result_from_s3_output_path(output_path)

    def _get_result_from_s3_output_path(self, output_path):
        """Get inference result from the output Amazon S3 path"""
        bucket, key = parse_s3_url(output_path)
        try:
            response = self.predictor_async.s3_client.get_object(Bucket=bucket, Key=key)
            return self.predictor_async.predictor._handle_response(response)
        except ClientError as ex:
            if ex.response["Error"]["Code"] == "NoSuchKey":
                raise ObjectNotExistedError(
                    message="Inference could still be running",
                    output_path=output_path,
                )
            raise UnexpectedClientError(
                message=ex.response["Error"]["Message"],
            )

    def _get_result_from_s3_output_failure_paths(self, output_path, failure_path):
        """Get inference result from the output & failure Amazon S3 path"""
        bucket, key = parse_s3_url(output_path)
        try:
            response = self.predictor_async.s3_client.get_object(Bucket=bucket, Key=key)
            return self.predictor_async._handle_response(response)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                try:
                    failure_bucket, failure_key = parse_s3_url(failure_path)
                    failure_response = self.predictor_async.s3_client.get_object(
                        Bucket=failure_bucket, Key=failure_key
                    )
                    failure_response = self.predictor_async._handle_response(
                        failure_response
                    )
                    raise AsyncInferenceModelError(message=failure_response)
                except ClientError as ex:
                    if ex.response["Error"]["Code"] == "NoSuchKey":
                        raise ObjectNotExistedError(
                            message="Inference could still be running", output_path=output_path
                        )
                    raise UnexpectedClientError(message=ex.response["Error"]["Message"])
            raise UnexpectedClientError(message=e.response["Error"]["Message"])



def parse_s3_url(url):
    """Returns an (s3 bucket, key name/prefix) tuple from a url with an s3 scheme.

    Args:
        url (str):

    Returns:
        tuple: A tuple containing:

            - str: S3 bucket name
            - str: S3 key
    """
    parsed_url = urlparse(url)
    if parsed_url.scheme != "s3":
        raise ValueError("Expecting 's3' scheme, got: {} in {}.".format(parsed_url.scheme, url))
    return parsed_url.netloc, parsed_url.path.lstrip("/")

def sagemaker_timestamp():
    """Return a timestamp with millisecond precision."""
    moment = time.time()
    moment_ms = repr(moment).split(".")[1][:3]
    return time.strftime("%Y-%m-%d-%H-%M-%S-{}".format(moment_ms), time.gmtime(moment))

def sagemaker_short_timestamp():
    """Return a timestamp that is relatively short in length"""
    return time.strftime("%y%m%d-%H%M")


def s3_path_join(*args, with_end_slash: bool = False):
    """Returns the arguments joined by a slash ("/"), similar to ``os.path.join()`` (on Unix).

    Behavior of this function:
    - If the first argument is "s3://", then that is preserved.
    - The output by default will have no slashes at the beginning or end. There is one exception
        (see `with_end_slash`). For example, `s3_path_join("/foo", "bar/")` will yield
        `"foo/bar"` and `s3_path_join("foo", "bar", with_end_slash=True)` will yield `"foo/bar/"`
    - Any repeat slashes will be removed in the output (except for "s3://" if provided at the
        beginning). For example, `s3_path_join("s3://", "//foo/", "/bar///baz")` will yield
        `"s3://foo/bar/baz"`.
    - Empty or None arguments will be skipped. For example
        `s3_path_join("foo", "", None, "bar")` will yield `"foo/bar"`

    Alternatives to this function that are NOT recommended for S3 paths:
    - `os.path.join(...)` will have different behavior on Unix machines vs non-Unix machines
    - `pathlib.PurePosixPath(...)` will apply potentially unintended simplification of single
        dots (".") and root directories. (for example
        `pathlib.PurePosixPath("foo", "/bar/./", "baz")` would yield `"/bar/baz"`)
    - `"{}/{}/{}".format(...)` and similar may result in unintended repeat slashes

    Args:
        *args: The strings to join with a slash.
        with_end_slash (bool): (default: False) If true and if the path is not empty, appends a "/"
            to the end of the path

    Returns:
        str: The joined string, without a slash at the end unless with_end_slash is True.
    """
    delimiter = "/"

    non_empty_args = list(filter(lambda item: item is not None and item != "", args))

    merged_path = ""
    for index, path in enumerate(non_empty_args):
        if (
            index == 0
            or (merged_path and merged_path[-1] == delimiter)
            or (path and path[0] == delimiter)
        ):
            # dont need to add an extra slash because either this is the beginning of the string,
            # or one (or more) slash already exists
            merged_path += path
        else:
            merged_path += delimiter + path

    if with_end_slash and merged_path and merged_path[-1] != delimiter:
        merged_path += delimiter

    # At this point, merged_path may include slashes at the beginning and/or end. And some of the
    # provided args may have had duplicate slashes inside or at the ends.
    # For backwards compatibility reasons, these need to be filtered out (done below). In the
    # future, if there is a desire to support multiple slashes for S3 paths throughout the SDK,
    # one option is to create a new optional argument (or a new function) that only executes the
    # logic above.
    filtered_path = merged_path
    # remove duplicate slashes
    if filtered_path:
        def duplicate_delimiter_remover(sequence, next_char):
            if sequence[-1] == delimiter and next_char == delimiter:
                return sequence
            return sequence + next_char

        if filtered_path.startswith("s3://"):
            filtered_path = reduce(
                duplicate_delimiter_remover, filtered_path[5:], filtered_path[:5]
            )
        else:
            filtered_path = reduce(duplicate_delimiter_remover, filtered_path)

    # remove beginning slashes
    filtered_path = filtered_path.lstrip(delimiter)

    # remove end slashes
    if not with_end_slash and filtered_path != "s3://":
        filtered_path = filtered_path.rstrip(delimiter)

    return filtered_path


def name_from_base(base, max_length=63, short=False):
    """Append a timestamp to the provided string.

    This function assures that the total length of the resulting string is
    not longer than the specified max length, trimming the input parameter if
    necessary.

    Args:
        base (str): String used as prefix to generate the unique name.
        max_length (int): Maximum length for the resulting string (default: 63).
        short (bool): Whether or not to use a truncated timestamp (default: False).

    Returns:
        str: Input parameter with appended timestamp.
    """
    timestamp = sagemaker_short_timestamp() if short else sagemaker_timestamp()
    trimmed_base = base[: max_length - len(timestamp) - 1]
    return "{}-{}".format(trimmed_base, timestamp)


def _botocore_resolver():
    """Get the DNS suffix for the given region.

    Args:
        region (str): AWS region name

    Returns:
        str: the DNS suffix
    """
    loader = botocore.loaders.create_loader()
    return botocore.regions.EndpointResolver(loader.load_data("endpoints"))


def sts_regional_endpoint(region):
    """Get the AWS STS endpoint specific for the given region.

    We need this function because the AWS SDK does not yet honor
    the ``region_name`` parameter when creating an AWS STS client.

    For the list of regional endpoints, see
    https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_enable-regions.html#id_credentials_region-endpoints.

    Args:
        region (str): AWS region name

    Returns:
        str: AWS STS regional endpoint
    """
    endpoint_data = _botocore_resolver().construct_endpoint("sts", region)
    if region == "il-central-1" and not endpoint_data:
        endpoint_data = {"hostname": "sts.{}.amazonaws.com".format(region)}
    return "https://{}".format(endpoint_data["hostname"])

def generate_default_sagemaker_bucket_name(boto_session):
    """Generates a name for the default sagemaker S3 bucket.

    Args:
        boto_session (boto3.session.Session): The underlying Boto3 session which AWS service
    """
    region = boto_session.region_name
    account = boto_session.client(
        "sts", region_name=region, endpoint_url=sts_regional_endpoint(region)
    ).get_caller_identity()["Account"]
    return "sagemaker-{}-{}".format(region, account)


class SageMakerClient(ClientBase):
    boto_session: Any = None

    name: str = None
    """The name of the Sagemaker client, used for logging purposes."""

    client: Any = None
    """Boto3 client for sagemaker runtime"""

    endpoint_name: Union[str,None] = None
    """The name of the endpoint from the deployed Sagemaker model.
    Must be unique within an AWS Region."""

    region_name: Union[str,None] = None
    """The aws region where the Sagemaker model is deployed, eg. `us-west-2`."""

    credentials_profile_name: Union[str,None] = None
    """The name of the profile in the ~/.aws/credentials or ~/.aws/config files, which
    has either access keys or role information specified.
    If not specified, the default credential profile or, if on an EC2 instance,
    credentials from IMDS will be used.
    See: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
    """

    model_kwargs: Optional[Dict] = None
    """Keyword arguments to pass to the model."""

    endpoint_kwargs: Optional[Dict] = None
    """Optional attributes passed to the invoke_endpoint
    function. See `boto3`_. docs for more info.
    .. _boto3: <https://boto3.amazonaws.com/v1/documentation/api/latest/index.html>
    """

    default_bucket: Union[str,None] = None
    """Default bucket to use for async inference if not specified in the request"""

    default_bucket_prefix: Union[str,None] = None
    """Default bucket prefix to use for async inference if not specified in the request"""

    s3_client: Any = None
    """Boto3 client for s3"""

    @model_validator(mode='before')
    def validate_environment(cls, values: Dict) -> Dict:
        """Dont do anything if client provided externally"""
        if not values.get("client"):
            """Validate that AWS credentials to and python package exists in environment."""
            try:
                import boto3
                try:
                    if not values.get('boto_session'):
                        if values.get("credentials_profile_name") is not None:
                            boto_session = boto3.Session(
                                profile_name=values["credentials_profile_name"]
                            )
                        else:
                            # use default credentials
                            boto_session = boto3.Session()
                        values['boto_session'] = boto_session

                    values["client"] = values['boto_session'].client(
                        "sagemaker-runtime", region_name=values.get("region_name")
                    )
                    if values.get("s3_client") is None:
                        values["s3_client"] = values['boto_session'].client(
                            "s3", region_name=values.get("region_name")
                        )

                except Exception as e:
                    import traceback
                    logger.error(traceback.format_exc())
                    raise ValueError(
                        "Could not load credentials to authenticate with AWS client. "
                        "Please check that credentials in the specified "
                        "profile name are valid."
                    ) from e

            except ImportError:
                raise ImportError(
                    "Could not import boto3 python package. "
                    "Please install it with `pip install boto3`."
                )

        if values.get("endpoint_name"):
            return values

        model_stack_name = values.get("model_stack_name")
        if model_stack_name is None:
            # check if stack is ready
            model_id = values.get("model_id")
            if model_id is None:
                raise ValueError("model_id or model_stack_name must be provided")
            model_stack_name = Model.get_model_stack_name_prefix(
                model_id,
                model_tag=values.get("model_tag") or MODEL_DEFAULT_TAG
            )

        # get endpoint name from stack
        if not check_stack_exists(model_stack_name):
            raise ValueError(f"Model stack {model_stack_name} does not exist")

        stack_info = get_model_stack_info(model_stack_name)

        Outputs = stack_info.get('Outputs')
        if not Outputs:
            raise RuntimeError(f"Model stack {model_stack_name} does not have any outputs, the model may be not deployed in success")
        for output in Outputs:
            if output['OutputKey'] == 'SageMakerEndpointName':
                values["endpoint_name"] = output['OutputValue']
                break

        assert values.get("endpoint_name") is not None, "Endpoint name not found in stack outputs"

        if not values.get("name"):
            values['name'] = model_stack_name
        return values

    def _prepare_input_body(self,pyload:dict):
        _model_kwargs = self.model_kwargs or {}
        body = json.dumps({**_model_kwargs,**pyload},ensure_ascii=False,indent=2)
        accept = "application/json"
        contentType = "application/json"
        _endpoint_kwargs = self.endpoint_kwargs or {}
        request_options = {
            "Body": body,
            "EndpointName":self.endpoint_name,
            "Accept": accept,
            "ContentType": contentType,
            **_endpoint_kwargs
        }
        enable_print_messages = os.getenv("ENABLE_PRINT_MESSAGES", 'False').lower() in ('true', '1', 't')
        if enable_print_messages:
            logger.info(f"request body: {json.loads(request_options['Body'])}")
        return request_options

    def invoke(self,pyload:dict):
        request_options = self._prepare_input_body(pyload)
        stream = pyload.get('stream', False)
        if stream:
            resp = self.client.invoke_endpoint_with_response_stream(
                **request_options
            )
            def _ret_iterator_helper():
                iterator = LineIterator(resp["Body"])
                for line in iterator:
                    chunk_dict = json.loads(line)
                    if not chunk_dict:
                        continue
                    yield chunk_dict
            return _ret_iterator_helper()
        else:
            output = self.client.invoke_endpoint(**request_options)['Body']
            response_dict = json.loads(output.read().decode("utf-8"))
            return response_dict


    def account_id(self) -> str:
        """Get the AWS account id of the caller.

        Returns:
            AWS account ID.
        """
        region = self.boto_session.region_name
        sts_client = self.boto_session.client(
            "sts", region_name=region, endpoint_url=sts_regional_endpoint(region)
        )
        return sts_client.get_caller_identity()["Account"]


    def general_bucket_check_if_user_has_permission(
        self, bucket_name, s3, bucket, region, bucket_creation_date_none
    ):
        """Checks if the person running has the permissions to the bucket

        If there is any other error that comes up with calling head bucket, it is raised up here
        If there is no bucket , it will create one

        Args:
            bucket_name (str): Name of the S3 bucket
            s3 (str): S3 object from boto session
            region (str): The region in which to create the bucket.
            bucket_creation_date_none (bool):Indicating whether S3 bucket already exists or not
        """
        try:
            s3.meta.client.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            message = e.response["Error"]["Message"]
            # bucket does not exist or forbidden to access
            if bucket_creation_date_none:
                if error_code == "404" and message == "Not Found":
                    self.create_bucket_for_not_exist_error(bucket_name, region, s3)
                elif error_code == "403" and message == "Forbidden":
                    logger.error(
                        "Bucket %s exists, but access is forbidden. Please try again after "
                        "adding appropriate access.",
                        bucket.name,
                    )
                    raise
                else:
                    raise

    def expected_bucket_owner_id_bucket_check(self, bucket_name, s3, expected_bucket_owner_id):
        """Checks if the bucket belongs to a particular owner and throws a Client Error if it is not

        Args:
            bucket_name (str): Name of the S3 bucket
            s3 (str): S3 object from boto session
            expected_bucket_owner_id (str): Owner ID string

        """
        try:
            s3.meta.client.head_bucket(
                Bucket=bucket_name, ExpectedBucketOwner=expected_bucket_owner_id
            )
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            message = e.response["Error"]["Message"]
            if error_code == "403" and message == "Forbidden":
                logger.error(
                    "Since default_bucket param was not set, SageMaker Python SDK tried to use "
                    "%s bucket. "
                    "This bucket cannot be configured to use as it is not owned by Account %s. "
                    "To unblock it's recommended to use custom default_bucket "
                    "parameter in sagemaker.Session",
                    bucket_name,
                    expected_bucket_owner_id,
                )
                raise

    def _create_s3_bucket_if_it_does_not_exist(self, bucket_name, region):
        """Creates an S3 Bucket if it does not exist.

        Also swallows a few common exceptions that indicate that the bucket already exists or
        that it is being created.

        Args:
            bucket_name (str): Name of the S3 bucket to be created.
            region (str): The region in which to create the bucket.

        Raises:
            botocore.exceptions.ClientError: If S3 throws an unexpected exception during bucket
                creation.
                If the exception is due to the bucket already existing or
                already being created, no exception is raised.
        """

        s3 = self.boto_session.resource("s3", region_name=region)

        bucket = s3.Bucket(name=bucket_name)
        if bucket.creation_date is None:
            self.general_bucket_check_if_user_has_permission(bucket_name, s3, bucket, region, True)
        else:
            self.general_bucket_check_if_user_has_permission(bucket_name, s3, bucket, region, False)

            expected_bucket_owner_id = self.account_id()
            self.expected_bucket_owner_id_bucket_check(bucket_name, s3, expected_bucket_owner_id)

        # self.general_bucket_check_if_user_has_permission(bucket_name, s3, bucket, region, False)

        # expected_bucket_owner_id = self.account_id()
        # self.expected_bucket_owner_id_bucket_check(bucket_name, s3, expected_bucket_owner_id)


    def create_bucket_for_not_exist_error(self, bucket_name, region, s3):
        """Creates the S3 bucket in the given region

        Args:
            bucket_name (str): Name of the S3 bucket
            s3 (str): S3 object from boto session
            region (str): The region in which to create the bucket.
        """
        # bucket does not exist, create one
        try:
            if region == "us-east-1":
                # 'us-east-1' cannot be specified because it is the default region:
                # https://github.com/boto/boto3/issues/125
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": region},
                )

            logger.info("Created S3 bucket: %s", bucket_name)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            message = e.response["Error"]["Message"]

            if error_code == "OperationAborted" and "conflicting conditional operation" in message:
                # If this bucket is already being concurrently created,
                # we don't need to create it again.
                pass
            else:
                raise
    def get_default_bucket(self):
        """Return the name of the default bucket to use in relevant Amazon SageMaker interactions.

        This function will create the s3 bucket if it does not exist.

        Returns:
            str: The name of the default bucket. If the name was not explicitly specified through
                the Session or sagemaker_config, the bucket will take the form:
                ``sagemaker-{region}-{AWS account ID}``.
        """

        if self.default_bucket:
            return self.default_bucket

        region = self.boto_session.region_name

        default_bucket = generate_default_sagemaker_bucket_name(self.boto_session)

        self._create_s3_bucket_if_it_does_not_exist(
            bucket_name=default_bucket,
            region=region,
        )

        self.default_bucket = default_bucket

        return self.default_bucket


    def _upload_data_to_s3(
        self,
        data,
        input_path=None,
    ):
        """Upload request data to Amazon S3 for users"""
        if input_path:
            bucket, key = parse_s3_url(input_path)
        else:
            my_uuid = str(uuid.uuid4())
            timestamp = sagemaker_timestamp()
            bucket = self.get_default_bucket()
            key = s3_path_join(
                self.default_bucket_prefix,
                "async-endpoint-inputs",
                name_from_base(self.name, short=True),
                "{}-{}".format(timestamp, my_uuid),
            )

        _model_kwargs = self.model_kwargs or {}
        data = json.dumps({**_model_kwargs,**data},ensure_ascii=False,indent=2)
        self.s3_client.put_object(
            Body=data, Bucket=bucket, Key=key, ContentType="application/json"
        )
        input_path = input_path or "s3://{}/{}".format(bucket, key)

        return input_path

    def _handle_response(self,response):
        response_body = response["Body"]
        content_type = response.get("ContentType", "application/octet-stream")
        try:
            return json.load(codecs.getreader("utf-8")(response_body))
        finally:
            response_body.close()

    def _check_output_and_failure_paths(self, output_path, failure_path, waiter_config):
        """Check the Amazon S3 output path for the output.

        This method waits for either the output file or the failure file to be found on the
        specified S3 output path. Whichever file is found first, its corresponding event is
        triggered, and the method executes the appropriate action based on the event.

        Args:
            output_path (str): The S3 path where the output file is expected to be found.
            failure_path (str): The S3 path where the failure file is expected to be found.
            waiter_config (boto3.waiter.WaiterConfig): The configuration for the S3 waiter.

        Returns:
            Any: The deserialized result from the output file, if the output file is found first.
            Otherwise, raises an exception.

        Raises:
            AsyncInferenceModelError: If the failure file is found before the output file.
            PollingTimeoutError: If both files are not found and the S3 waiter
             has thrown a WaiterError.
        """
        output_bucket, output_key = parse_s3_url(output_path)
        failure_bucket, failure_key = parse_s3_url(failure_path)

        output_file_found = threading.Event()
        failure_file_found = threading.Event()

        def check_output_file():
            try:
                output_file_waiter = self.s3_client.get_waiter("object_exists")
                output_file_waiter.wait(
                    Bucket=output_bucket,
                    Key=output_key,
                    WaiterConfig=waiter_config._to_request_dict(),
                )
                output_file_found.set()
            except WaiterError:
                pass

        def check_failure_file():
            try:
                failure_file_waiter = self.s3_client.get_waiter("object_exists")
                failure_file_waiter.wait(
                    Bucket=failure_bucket,
                    Key=failure_key,
                    WaiterConfig=waiter_config._to_request_dict(),
                )
                failure_file_found.set()
            except WaiterError:
                pass


        output_thread = threading.Thread(target=check_output_file)
        failure_thread = threading.Thread(target=check_failure_file)

        output_thread.start()
        failure_thread.start()

        while not output_file_found.is_set() and not failure_file_found.is_set():
            time.sleep(1)

        if output_file_found.is_set():
            s3_object = self.s3_client.get_object(Bucket=output_bucket, Key=output_key)
            result = self._handle_response(response=s3_object)
            return result

        failure_object = self.s3_client.get_object(Bucket=failure_bucket, Key=failure_key)
        failure_response = self._handle_response(response=failure_object)

        raise (
            AsyncInferenceModelError(message=failure_response)
            if failure_file_found.is_set()
            else PollingTimeoutError(
                message="Inference could still be running",
                output_path=output_path,
                seconds=waiter_config.delay * waiter_config.max_attempts,
            )
        )

    def _check_output_path(self, output_path, waiter_config):
        """Check the Amazon S3 output path for the output.

        Periodically check Amazon S3 output path for async inference result.
        Timeout automatically after max attempts reached
        """
        bucket, key = parse_s3_url(output_path)
        s3_waiter = self.s3_client.get_waiter("object_exists")
        try:
            s3_waiter.wait(Bucket=bucket, Key=key, WaiterConfig=waiter_config._to_request_dict())
        except WaiterError:
            raise PollingTimeoutError(
                message="Inference could still be running",
                output_path=output_path,
                seconds=waiter_config.delay * waiter_config.max_attempts,
            )
        s3_object = self.s3_client.get_object(Bucket=bucket, Key=key)
        result = self._handle_response(response=s3_object)
        return result

    def _wait_for_output(self, output_path, failure_path, waiter_config):
        """Retrieve output based on the presense of failure_path."""
        if failure_path is not None:
            return self._check_output_and_failure_paths(output_path, failure_path, waiter_config)

        return self._check_output_path(output_path, waiter_config)

    def invoke_async(
            self,
            data:dict=None,
            input_path=None,
            inference_id=None,
            waiter_config=WaiterConfig(delay=0.1,max_attempts=15*60/0.1),
            async_invoke=False
        ):
        if data is None and input_path is None:
            raise ValueError(
                "Please provide data or input_path Amazon S3 location to use async prediction"
            )
        if data is not None:
            input_path = self._upload_data_to_s3(data, input_path)

        request_options = {
            "InputLocation":input_path,
            "EndpointName":self.endpoint_name,
            "Accept":"*/*"
        }
        if inference_id:
            request_options['InferenceId']

        response = self.client.invoke_endpoint_async(
            **request_options
        )
        output_location = response["OutputLocation"]
        failure_location = response.get("FailureLocation")
        if async_invoke:
            response_async = AsyncInferenceResponse(
                predictor_async=self,
                output_path=output_location,
                failure_path=failure_location
            )
            return response_async
        else:
            result = self._wait_for_output(
                output_path=output_location, failure_path=failure_location, waiter_config=waiter_config
            )
        return result
