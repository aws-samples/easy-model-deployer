from . import Framework
from .utils.constants import FrameworkType


class FastAPIFramework(Framework):
    limit_concurrency: int = 1000
    timeout_keep_alive: int = 60
    uvicorn_log_level: str = "info"




fastapi_framework = FastAPIFramework(
    description="FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.",
    framework_type=FrameworkType.FASTAPI,
    limit_concurrency = 1000,
    timeout_keep_alive = 60,
    uvicorn_log_level = "info"
)

custom_framework = Framework(
    description="Custom framework",
    framework_type=FrameworkType.CUSTOM,
)
