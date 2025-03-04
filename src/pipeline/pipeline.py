import sys
import os
import time
import argparse
import importlib
import json
import logging
from concurrent.futures import as_completed,ProcessPoolExecutor

from emd.models import Model
from emd.constants import MODEL_DEFAULT_TAG,LOCAL_REGION
from emd.models.utils.constants import FrameworkType,ServiceType,InstanceType

from utils.common import str2bool
from emd.utils.aws_service_utils import check_cn_region
from emd.models import Model, ExecutableConfig
from emd.models.utils.serialize_utils import load_extra_params,dump_extra_params
import threading
from multiprocessing import Event
from emd.models import Instance
from emd.models import ValueWithDefault
from emd.utils.logger_utils import get_logger

logger = get_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_s3_bucket', type=str)
    parser.add_argument('--model_id', type=str)
    # TODO: Check the default value of model_tag
    parser.add_argument('--model_tag', type=str, default=MODEL_DEFAULT_TAG)
    parser.add_argument('--backend_type', type=str)
    parser.add_argument('--service_type', type=str)
    # parser.add_argument('--gpu_num', type=int, default=1)
    parser.add_argument('--instance_type', type=str)
    parser.add_argument('--region', type=str)
    parser.add_argument("--image_uri", type=str,default=None)
    parser.add_argument("--image_name", type=str, default=None)
    parser.add_argument("--image_tag", type=str, default="latest")

    parser.add_argument("--s3_output_path", type=str, default="")
    parser.add_argument("--framework_type", type=str, default=FrameworkType.FASTAPI)
    parser.add_argument("--role_name", type=str, default=os.environ.get('role_name','SageMakerExecutionRoleTest'))
    parser.add_argument("--skip_prepare_model", action='store_true')
    parser.add_argument("--skip_image_build", action='store_true')
    parser.add_argument("--skip_deploy", action='store_true')
    parser.add_argument("--disable_parallel_prepare_and_build_image", action='store_true')
    parser.add_argument(
            "--extra_params",
            type=load_extra_params,
            default=os.environ.get("extra_params","{}")
        )
    return parser.parse_args()

def set_envs(args):
    for k,v in vars(args).items():
        if k == "extra_params":
            v = dump_extra_params(v)
        os.environ[k] = str(v)

def run_prepare_model(args):
    model = get_executable_model(args)
    # model = Model.get_model(args.model_id)
    t1 = time.time()
    from deploy import prepare_model
    prepare_model.run(
        model,
        # args.model_s3_bucket,
        # args.backend_type,
        # args.service_type,
        # args.region,
        # args=vars(args)
    )
    # else:
    #     print("skip prepare model...")
    print(f"prepare_model elapsed time: ",time.time() - t1)


def run_build_image(args):
    t2 = time.time()
    if not args.image_uri and not args.skip_image_build:
        logger.info("build image...")
        from deploy import build_and_push_image
        build_and_push_output_params = build_and_push_image.run(
            region=args.region,
            model_id=args.model_id,
            model_tag=args.model_tag,
            backend_type=args.backend_type,
            service_type=args.service_type,
            framework_type=args.framework_type,
            image_name=args.image_name,
            image_tag="latest" if args.model_tag == MODEL_DEFAULT_TAG else args.model_tag,
            model_s3_bucket=args.model_s3_bucket,
            instance_type=args.instance_type,
            extra_params=args.extra_params
        )
    else:
        print("skip build image...")
    print(f"image build elapsed time: ", time.time() - t2)
    print(f'build_and_push_output_params: ',build_and_push_output_params)
    return build_and_push_output_params


def init_worker(event):
    global shared_event
    shared_event = event


class MyThread(threading.Thread):
    def run(self):
        self.ret = None
        self.err = None
        try:
            ret = self._target(*self._args, **self._kwargs)
            print("thread ret: ",ret)
            self.ret = ret
        except Exception as err:
            self.err = err
            raise
            # import traceback
            # traceback_info = traceback.format_exc()
            # logger.error(f"thread {self.name} got error: {err}\n{traceback_info}")
            # pass # or raise err

def worker(fn,*args,**kwargs):
    thread = MyThread(target=fn, args=args, kwargs=kwargs)
    thread.start()
    while True:
        if shared_event.is_set():
            # print("There exists any process got wrong...",flush=True)
            raise RuntimeError("There exists any process got wrong...")
        if not thread.is_alive():
            if thread.err is not None:
                shared_event.set()
                print("Current process got wrong...",flush=True)
                raise RuntimeError("Current process got wrong...")
                # os.system("kill -9 %d" % os.getpid())
            break
        time.sleep(0.1)
    return thread.ret

def run_prepare_model_and_build_image(args):
    if args.disable_parallel_prepare_and_build_image:
        logger.info("disable parallel prepare and build image")
        run_prepare_model(args)
        build_and_push_output_params = run_build_image(args)
        return build_and_push_output_params
    else:
        # TODO: get build_and_push_output_params
        logger.info("enable parallel prepare and build image")
        ret = None
        with ProcessPoolExecutor(2,initializer=init_worker,initargs=(Event(),)) as pool:
            feature1 = pool.submit(worker,run_prepare_model, args)
            feature1.name = "run_prepare_model"
            feature2 = pool.submit(worker,run_build_image, args)
            feature2.name = "run_build_image"

            for future in as_completed([feature1,feature2]):
                try:
                    r = future.result()
                    print(f"{future.name}: {r}")
                    if future.name == "run_build_image":
                        ret = r
                except:
                    import traceback
                    print(traceback.format_exc(),flush=True)
                    sys.exit(1)

                    # os.system("kill -9 %d" % os.getpid())
        return ret


def run_deploy(execute_model, service_deploy_parameters, region, role_name):
    retry_times = 60
    while retry_times > 0:
        try:
            # if "deploy.deploy" in sys.modules:
            #     importlib.reload(deploy)
            # else:
            #     from deploy import deploy
            from deploy import deploy
            deploy.run(execute_model, service_deploy_parameters, region, role_name)
            return
        except Exception as e:
            logger.error(str(e))
            if "botocore.exceptions.ClientError" in str(e.__class__) and \
            'sts:AssumeRole' in str(e):
                logger.info(f"waiting to assume role...")
                retry_times -= 1
                time.sleep(1)
                continue
            else:
                raise

def get_executable_model(args):
    model = Model.get_model(args.model_id)
    # executable_config = ExecutableConfig(
    #     region=args.region,
    #     current_engine=model.find_current_engine(args.backend_type),
    #     current_instance=model.find_current_instance(args.instance_type),
    #     current_service=model.find_current_service(args.service_type),
    #     current_framework=model.find_current_framework(args.framework_type),
    #     model_s3_bucket=args.model_s3_bucket,
    #     extra_params=args.extra_params,
    #     model_tag=args.model_tag
    # )
    execute_model = model.convert_to_execute_model(
        engine_type=args.backend_type,
        instance_type=args.instance_type,
        service_type=args.service_type,
        framework_type=args.framework_type,
        model_s3_bucket=args.model_s3_bucket,
        model_tag=args.model_tag,
        extra_params=args.extra_params,
        region=args.region
    )
    return execute_model

def download_s5cmd():
    assert os.system('curl https://github.com/peak/s5cmd/releases/download/v2.0.0/s5cmd_2.0.0_Linux-64bit.tar.gz -L -o /tmp/s5cmd.tar.gz') == 0
    assert os.system("mkdir -p /tmp/s5cmd && tar -xvf /tmp/s5cmd.tar.gz -C /tmp/s5cmd") == 0
    assert os.system(f"cp /tmp/s5cmd/s5cmd .") == 0

if __name__ == "__main__":
    t0 = time.time()
    start_time = time.time()
    args = parse_args()
    if not (check_cn_region(args.region) or args.region == LOCAL_REGION):
        download_s5cmd()

    s5_cmd_path = "./s5cmd"
    os.chmod(s5_cmd_path, os.stat(s5_cmd_path).st_mode | 0o100)
    extra_params = args.extra_params
    for k,v in extra_params.items():
        setattr(args,k,v)

    execute_model = get_executable_model(args)
    if not args.image_name:
        args.image_name = execute_model.get_normalized_model_id()
    set_envs(args)
    print(vars(args))
    output_params = run_prepare_model_and_build_image(args)
    # get ecr repo image_uri
    # image_uri = execute_model.get_image_uri(
    #     account_id=execute_model.get_image_push_account_id(),
    #     region=args.region,
    #     image_name=args.image_name,
    #     image_tag=args.image_tag
    # )
    # args.image_uri = image_uri
    # set_envs(args)
    all_params = {
        **vars(args),
        ** (output_params or {}),
        "container_cpu": Instance.get_ecs_container_cpu(args.instance_type),
        "container_memory": Instance.get_ecs_container_memory(args.instance_type),
        "instance_gpu_num": str(Instance.get_instance_from_instance_type(args.instance_type).gpu_num)
    }
    print('all params: ',all_params)
    print('output_params: ',output_params)
    instance_type = InstanceType.convert_instance_type(
                all_params['instance_type'],
                all_params['service_type']
            )

    s3_output_path = args.s3_output_path
    if not s3_output_path:
        s3_output_path = f"s3://{all_params['model_s3_bucket']}/{all_params['model_id']}/output"

    all_params_normalized = {
        **all_params,
        "instance_type":instance_type,
        "s3_output_path":s3_output_path
    }
    all_params_normalized['engine_type'] = all_params_normalized['backend_type']

    print('all_params_normalized: ',all_params_normalized)
    current_service = execute_model.executable_config.current_service
    cfn_parameters = current_service.cfn_parameters


    service_extra_params = args.extra_params.get('service_params',{})
    print(f"service_extra_params: {service_extra_params}")
    print(f"cfn_parameters: {cfn_parameters}")
    service_deploy_parameters = {}
    for k,v in cfn_parameters.items():
        if isinstance(v,dict):
            v = ValueWithDefault(**v)
        key_in_all_params_normalized = v
        default_value = None
        if isinstance(v,ValueWithDefault):
            key_in_all_params_normalized = v.name
            default_value = v.default

        value = service_extra_params.get(
            key_in_all_params_normalized,
            all_params_normalized.get(
                key_in_all_params_normalized
            )
        )
        value = value or default_value

        assert value is not None,(k,v)
        # if isinstance(v,ValueWithDefault):
        #     new_v = all_params_normalized.get(v.name,v.default)
        service_deploy_parameters[k] = str(value)

    print("service_deploy_parameters: ",service_deploy_parameters)
    with open(f"parameters.json", "w") as f:
        json.dump({"Parameters": service_deploy_parameters},f)

    if not args.skip_deploy:
        t3 = time.time()
        run_deploy(execute_model, service_deploy_parameters, args.region, args.role_name)
        print(f"deploy elapsed time: ", time.time() - t3)

    print('total elapsed time: ', time.time() - t0)
