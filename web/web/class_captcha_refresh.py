from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.http import JsonResponse
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


class Refresh:

    def __init__(self):
        self._logger = logging.getLogger(__name__)


    def _log(self, text):
        self._logger.error(f"{self.__class__.__name__}: {text}")


    def run(self):
        try:

            new_key = CaptchaStore.generate_key()
            image_url = captcha_image_url(new_key)

            return JsonResponse({"key": new_key, "url": image_url})
        
        except Exception as e:
            self._log(f"run -> {e}")
            return JsonResponse({"key": "", "url": ""})