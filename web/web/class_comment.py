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
        try:

            username = request.POST.get("username")
            home_page = request.POST.get("home_page")
            email = request.POST.get("email")

            if not all([username, home_page, email]):
                self._log(f"_if_exists_user -> не все нужные данные пришли")
                return False

            return Users.objects.filter(
                username=username, 
                site=home_page, 
                email=email
            ).exists()
        
        except Exception as e:
            self._log(f"_if_exists_user -> {e}")
            return False
        


    def _save_user_in_model(self, request):
        pass



    def _parse_post_data(self, request):
        return {
            "username": request.POST.get("username"),
            "home_page": request.POST.get("home_page"),
            "email": request.POST.get("email"),
            "comment": request.POST.get("comment")
        }



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

            data = self._parse_post_data(request)

            if not self._if_exists_user(request):
                self._save_user_in_model(request)

            if not username or not comment:
                self._log(f"add_comment -> данные не пришли")
                return False

            Comment.objects.create(user=username, text=comment)
            return True
        
        except Exception as e:
            self._log(f"add_comment -> {e}")
            return False