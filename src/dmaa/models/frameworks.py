from . import Framework
from .utils.constants import FrameworkType


fastapi_framework = Framework(
    description="FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.",
    framework_type=FrameworkType.FASTAPI,
)

custom_framework = Framework(
    description="Custom framework",
    framework_type=FrameworkType.CUSTOM,
)