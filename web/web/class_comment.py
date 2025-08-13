import os
from web.models import Users, Comment
from time import time
import logging
from datetime import datetime
from pathlib import Path

from django.utils.text import get_valid_filename
from django.http import FileResponse, Http404
from django.http import JsonResponse

from web.class_rabbit_mq_sender import RMQ


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)



class CommentControl:
    def __init__(self):
        self._save_path = "/usr/src/app/web/web/static/web/files/"
        self._MAX_FILE_SIZE = 1 * 1024 * 1024
        self._MAX_FILE_SIZE_TXT = 100 * 1024
        self._extensions = ["txt", "png", "jpg", "jpeg", "gif"]
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




    def _post_data(self, form, request):

        answer_id = request.POST.get("answer_id", 0)
        answer_id = int(answer_id) if answer_id.isdigit() else 0

        ws_user = request.POST.get("ws_user", "")
        ws_user = ws_user if ws_user.startswith("user_ws_") else ""

        return {
            "username": form.cleaned_data["username"],
            "home_page": form.cleaned_data["home_page"],
            "email": form.cleaned_data["email"],
            "comment": form.cleaned_data["comment"],
            "answer_id": answer_id,
            "ws_user": ws_user,
            "file": request.FILES.get("file")
        }
        



    def _save_file_on_server(self, file):
        try:

            timestamp = int(time())
            filename = f"{timestamp}_{get_valid_filename(file.name)}"

            os.makedirs(self._save_path, exist_ok=True)            
            path = os.path.join(self._save_path, filename)

            filetype = Path(path).suffix.lstrip('.').lower()
            limit = self._MAX_FILE_SIZE_TXT if filetype == "txt" else self._MAX_FILE_SIZE
            
            if not filetype in self._extensions:
                self._log(f"_save_file_on_server -> {filename} недопустимый файл")
                return JsonResponse({"message": "Это не текстовый документ и не изображение нужного типа", "status": "deny"})

            if file.size > limit:
                self._log(f"_save_file_on_server -> размер файла {filename} превышает лимит {self._MAX_FILE_SIZE_TXT}")
                return JsonResponse({"message": "Файл превышает допустимый размер", "status": "deny"})

            with open(path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        
            return {
                "filename": filename,
                "filetype": filetype
            }

        except Exception as e:
            self._log(f"_save_file_on_server -> {e}")
            return {}
        




    def _return_image_response(self, path, ext):
        try:
            
            return FileResponse(
                open(path, 'rb'), 
                content_type=f"image/{ext}"
            )
        
        except Exception as e:
            self._log(f"_return_image_response -> {e}")
            return JsonResponse({"message": "Изображение не найдено...", "status": "deny"})





    def get_all(self):
        try:

            return Comment.objects.filter(parent=None).prefetch_related('replies').order_by('-id')
        
        except Exception as e:
            self._log(f"get_all -> {e}")
            return []
        



    def add_comment(self, form, request) -> bool:
        try:

            data = self._post_data(form, request)
            path = {}

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
                return JsonResponse({"message": "Недостаточно данных для обработки запроса", "status": "deny"})
        
            self._rabbit.send({
                "user": username,
                "comment": comment,
                "file": path.get("filename", ""),
                "filetype": path.get("filetype", ""),
                "answer_id": answer_id,
                "ws_user": data.get("ws_user")
            })

            return JsonResponse({"message": "Выполняется обработка комментария", "status": "allow"})

        
        except Exception as e:
            self._log(f"add_comment -> {e}")
            return JsonResponse({"message": "Внутренняя ошибка при добавлении комментария", "status": "deny"})
        





    def get_file(self, filename):

        path_image_not_found = os.path.join(self._save_path, "image-not-found_.png")

        try:

            path = os.path.abspath(os.path.join(self._save_path, filename))
            ext = Path(path).suffix.lstrip('.')

            if not path.startswith(os.path.abspath(self._save_path)):
                return JsonResponse({"message": "Ошибка при поиске файла", "status": "deny"})

            if not os.path.exists(path):
                if ext == "txt":
                    return JsonResponse({"message": "File not found", "status": "deny"})
                return self._return_image_response(path_image_not_found, "png")

            return self._return_image_response(path, ext)
        
        except Exception as e:
            self._log(f"get_image -> {e}")
            return self._return_image_response(path_image_not_found, "png")