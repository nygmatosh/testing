from web.models import Users, Comment
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




    def _if_exists_user(self, data):
        try:

            username = data.get("username")
            home_page = data.get("home_page")
            email = data.get("email")

            if not all([data.get("username"), data.get("home_page"), data.get("email")]):
                self._log(f"_if_exists_user -> не все нужные данные пришли")
                return False

            return Users.objects.filter(
                user=username, 
                site=home_page, 
                email=email
            ).exists()
        
        except Exception as e:
            self._log(f"_if_exists_user -> {e}")
            return False
        


    def _save_user_in_model(self, data):
        try:

            username = data.get("username")
            home_page = data.get("home_page")
            email = data.get("email")

            Users.objects.create(user=username, site=home_page, email=email)
            return True
        
        except Exception as e:
            self._log(f"_save_user_in_model -> {e}")
            return False




    def _post_data(self, request):
        try:

            return {
                "username": request.POST.get("username"),
                "home_page": request.POST.get("home_page"),
                "email": request.POST.get("email"),
                "comment": request.POST.get("comment")
            }
        
        except Exception as e:
            self._log(f"_post_data -> {e}")
            return {}
        

    

    def _find_comment_with_id(self, id):
        try:

            return Comment.objects.get(id=id)
        
        except Exception as e:
            self._log(f"_find_comment_with_id -> {e}")
            return None



    def get_all(self):
        try:

            return Comment.objects.all()
        
        except Exception as e:
            self._log(f"get_all -> {e}")
            return []
        



    def add_comment(self, request):
        try:

            data = self._post_data(request)

            username = data.get("username")
            comment = data.get("comment")

            if not self._if_exists_user(data):
                self._save_user_in_model(data)

            if not username or not comment:
                self._log(f"add_comment -> данные не пришли")
                return False

            Comment.objects.create(user=username, text=comment)
            return True
        
        except Exception as e:
            self._log(f"add_comment -> {e}")
            return False
        


    

    def answer_comment(self, request):
        pass