from web.models import *
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)



class CommentControl:
    def __init__(self):
        self._logger = logging.getLogger(__name__)



    def _log(self, text):
        self._logger.error(f"{self.__class__.__name__}: {text}")


    def _if_exists_user(self, request):
        pass


    def get_all(self):
        try:

            return Comment.objects.all()
        
        except Exception as e:
            self._log(f"get_all -> {e}")
            return []
        



    def add_comment(self, request):
        try:

            username = request.POST.get("username")
            comment = request.POST.get("comment")

            if not username or not comment:
                self._log(f"add_comment -> данные не пришли")
                return False

            Comment.objects.create(user=username, text=comment)
            return True
        
        except Exception as e:
            self._log(f"add_comment -> {e}")
            return False