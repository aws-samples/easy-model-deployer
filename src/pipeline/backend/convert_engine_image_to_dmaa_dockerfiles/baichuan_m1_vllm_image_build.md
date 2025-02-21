
To build the current image, please first download the following repo:
```shell
git clone https://github.com/baichuan-inc/vllm.git
cd vllm
```
Then run the following command to build the image:
```shell
#optionally specifies: --build-arg max_jobs=8 --build-arg nvcc_threads=2
DOCKER_BUILDKIT=1 docker build . --target vllm-openai --tag vllm/vllm-openai
```
