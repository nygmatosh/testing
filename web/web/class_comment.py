import os
from web.models import Users, Comment
from time import time
import logging
from datetime import datetime
from pathlib import Path

from django.utils.text import get_valid_filename
from django.http import FileResponse, Http404

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

            #return path
            return filename

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
            answer_id = int(data.get("answer_id"))
            file = data.get("file")

            if not self._if_exists_user(data):
                self._save_user_in_model(data)

            if file:
                path = self._save_file_on_server(file)

            if not username or not comment:
                self._log(f"add_comment -> данные не пришли")
                return False
        
            self._rabbit.send({
                "user": username,
                "comment": comment,
                "file": path,
                "answer_id": answer_id,
                "ws_user": data.get("ws_user")
            })

            return True

        
        except Exception as e:
            self._log(f"add_comment -> {e}")
            return False
        



    def _return_image_response(self, path, ext):
        try:
            
            return FileResponse(
                open(path, 'rb'), 
                content_type=f"image/{ext}"
            )
        
        except Exception as e:
            self._log(f"_return_image_response -> {e}")
            return Http404("Image not found")



    def get_image(self, filename):
        try:

            path = os.path.abspath(os.path.join(self._save_path, filename))

            if not path.startswith(os.path.abspath(self._save_path)):
                return Http404("Image not found")

            if not os.path.exists(path):
                return self._return_image_response(
                    os.path.join(self._save_path, "image-not-found_.png"),
                    "png"
                )

            return self._return_image_response(
                path,
                Path(path).suffix.lstrip('.')
            )
        
        except Exception as e:
            self._log(f"get_image -> {e}")

            return self._return_image_response(
                os.path.join(self._save_path, "image-not-found_.png"),
                "png"
            )