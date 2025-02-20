
from emd.constants import EMD_DEFAULT_PROFILE_PARH
import os
from emd.utils.logger_utils import get_logger

logger = get_logger(
    __name__,
    format='%(message)s',
)


class ProfileManager:
    def __init__(self,profile_path = EMD_DEFAULT_PROFILE_PARH):
        self.profile_path = os.path.expanduser(profile_path)

    def write_default_profile_name_to_local(self,aws_profile_name: str):
        with open(self.profile_path,'w') as f:
            f.write(aws_profile_name)

    def load_profile_name_from_local(self):
        try:
            with open(self.profile_path,'r') as f:
                return f.read()
        except FileNotFoundError:
            return None


    def set_default_aws_profile_from_local(self):
        try:
            profile_name = self.load_profile_name_from_local()
        except Exception as e:
            logger.warning(f"Error loading AWS profile: {str(e)}")

        if profile_name:
            os.environ["AWS_PROFILE"] = profile_name
            logger.info(f"Set AWS_PROFILE to {profile_name}")

    def remove_profile_name_from_local(self):
        if os.path.exists(self.profile_path):
            default_name = self.load_profile_name_from_local()
            os.remove(self.profile_path)
            return default_name

profile_manager = ProfileManager()
