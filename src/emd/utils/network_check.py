import urllib.request
from emd.utils.logger_utils import get_logger

logger = get_logger(__name__)

def check_website_urllib(url,timeout=5):
    try:
        response = urllib.request.urlopen(url, timeout=timeout)
        return True
    except Exception as e:
        logger.error(f"Error checking website: {e}")
        return False
