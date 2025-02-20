import unittest
from unittest.mock import MagicMock
from typing import List, Iterable
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from backend.vllm.vllm_backend import (
    VLLMBackend,
)  # Adjust the import based on your actual module structure
from models import Model, ExecutableConfig

class TestVLLMBackend(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        region = "us-west-2"
        backend_type = "vllm"
        instance_type = "g5.4xlarge"
        service_type = "sagemaker"
        framework_type = "fastapi"
        model_s3_bucket = "emd-us-east-1-bucket-75c6f785084f4fd998da560a0a6190fc"
        vllm_cli_args = "--max_model_len 4096"
        # model_id = "Qwen2.5-0.5B-Instruct"
        model_id = "bge-m3"
        model = Model.get_model(model_id)
        executable_config = ExecutableConfig(
            region=region,
            current_engine=model.find_current_engine(backend_type),
            current_instance=model.find_current_instance(instance_type),
            current_service=model.find_current_service(service_type),
            current_framework=model.find_current_framework(framework_type),
            model_s3_bucket=model_s3_bucket,
            vllm_cli_args=vllm_cli_args,

        )
        self.execute_model = model.convert_to_execute_model(executable_config)
        self.backend = self.execute_model.get_engine()

    def test_start(self):
        self.backend.start()

    def test_invoke(self):
        # Mock payload
        model_id = self.execute_model.model_id
        mock_payload = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Who won the world series in 2020?"},
                {
                    "role": "assistant",
                    "content": "The Los Angeles Dodgers won the World Series in 2020.",
                },
                {
                    "role": "user",
                    "content": "Where was it played? The answer should be as long as possible.",
                },
            ],
            "model": model_id
        }

        # Call the method
        logger.info("invoke")
        result = self.backend.invoke(mock_payload)
        logger.info(result)

        # Check the result
        logger.info("result")
        self.assertIsInstance(result, Iterable)

    @classmethod
    def tearDownClass(self):
        self.backend.stop()


if __name__ == "__main__":
    # Create a test suite with the desired order of test functions
    suite = unittest.TestSuite()
    suite.addTest(TestVLLMBackend('test_start'))
    suite.addTest(TestVLLMBackend('test_invoke'))

    # Run the test suite
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
