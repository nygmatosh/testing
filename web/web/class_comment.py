import os
from web.models import Users, Comment
from time import time
import logging
from datetime import datetime

from django.utils.text import get_valid_filename
from web.class_rabbit_mq_sender import RMQ


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)



class CommentControl:
    def __init__(self):
        self._save_path = "/usr/src/app/web/web/static/web/files/"
        self._MAX_FILE_SIZE = 1 * 1024 * 1024
        self._rabbit = RMQ()
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
        return {
            "username": request.POST.get("username"),
            "home_page": request.POST.get("home_page"),
            "email": request.POST.get("email"),
            "comment": request.POST.get("comment"),
            "answer_id": request.POST.get("answer_id"),
            "ws_user": request.POST.get("ws_user"),
            "file": request.FILES.get("file")
        }
        

    

    def _find_comment_with_id(self, id):
        try:

            return Comment.objects.get(id=id)
        
        except Exception as e:
            self._log(f"_find_comment_with_id -> {e}")
            return None
        



    def _date_to_human(self, dt):
        try:

            return dt.strftime("%d.%m.%Y %H:%M:%S")
        
        except Exception as e:
            self._log(f"_date_to_human -> {e}")
            return dt




    def _answer_comment(self, data):
        try:

            id = data.get("answer_id")
            comment = self._find_comment_with_id(id)

            if not comment:
                self._log(f"_answer_comment -> [комментарий не найден]")
                return False

            username = data.get("username")
            text = data.get("comment")

            com = Comment.objects.create(user=username, text=text, parent=comment)

            return {
                "id": com.id,
                "answer_id": id,
                "created_at": self._date_to_human(com.created_at),
                "user": username,
                "comment": text,
                "ws_user": data.get("ws_user"),
                "file": ""
            }
        
            #self._rabbit.send({
            #    "user": username,
            #    "comment": text,
            #    "file": "",
            #    "answer_id": id,
            #    "ws_user": data.get("ws_user")
            #})

            #return True

        except Exception as e:
            self._log(f"_answer_comment -> {e}")
            return False
        



    def _save_file_on_server(self, file):
        try:

            timestamp = int(time())
            filename = f"{timestamp}_{get_valid_filename(file.name)}"
            os.makedirs(self._save_path, exist_ok=True)

            if file.size > self._MAX_FILE_SIZE:
                self._log(f"_save_file_on_server -> размер файла {filename} превышает лимит {self._MAX_FILE_SIZE}")
                return False
            
            path = os.path.join(self._save_path, filename)

            with open(path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            return path

        except Exception as e:
            self._log(f"_save_file_on_server -> {e}")
            return ""




    def get_all(self):
        try:

            return Comment.objects.filter(parent=None).prefetch_related('replies').order_by('-id')
        
        except Exception as e:
            self._log(f"get_all -> {e}")
            return []
        



    def add_comment(self, request) -> bool:
        try:

            data = self._post_data(request)
            path = ""

            username = data.get("username")
            comment = data.get("comment")
            answer_id = int(data.get("answer_id", 0))
            file = data.get("file")

            if not self._if_exists_user(data):
                self._save_user_in_model(data)

            if file:
                path = self._save_file_on_server(file)

            if answer_id > 0:
                return self._answer_comment(data)

            if not username or not comment:
                self._log(f"add_comment -> данные не пришли")
                return False


            #com = Comment.objects.create(user=username, text=comment, file_path=path)
        
            #return {
            #    "id": com.id,
            #    "created_at": self._date_to_human(com.created_at),
            #    "user": username,
            #    "comment": comment,
            #    "file": path,
            #    "answer_id": 0,
            #    "ws_user": data.get("ws_user")
            #}
        
            self._rabbit.send({
                "user": username,
                "comment": comment,
                "file": path,
                "answer_id": 0,
                "ws_user": data.get("ws_user")
            })

            return True

        
        except Exception as e:
            self._log(f"add_comment -> {e}")
            return False