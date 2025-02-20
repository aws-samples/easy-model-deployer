from .revision import VERSION

__version__ = VERSION


# try to load local profile
from .utils.profile_manager import profile_manager
profile_manager.set_default_aws_profile_from_local()


def _load_deploy():
    from .sdk.deploy import deploy
    return deploy


def _load_destroy():
    from .sdk.destroy import destroy
    return destroy

def _load_destroy_status():
    from .sdk.status import get_destroy_status
    return get_destroy_status



functions_map = {
    "deploy": _load_deploy,
    "destroy": _load_destroy,
    "destroy_status": _load_destroy_status
}


def __getattr__(attr:str):
    if attr not in functions_map:
        raise AttributeError(f"module emd has no attribute '{attr}'")
    return functions_map[attr]()
