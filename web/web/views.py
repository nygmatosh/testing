from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from web.forms import SendCommentForm
from web.class_comment import CommentControl
from web.models import *



def index(request):

    comments = CommentControl()

    data = {
        "comments": comments.get_all(),
        "level": 0,
        "is_root": False,
        "form": SendCommentForm(),
    }

    return render(request, 'web/index.html', data)




def send(request):
    if request.method == 'POST':

        form = SendCommentForm(request.POST)

        if form.is_valid():

            add = CommentControl().add_comment(request)
            
            if add:
                return JsonResponse({"message": "Комментарий сохранен", "data": add, "status": "allow"})
            
        return JsonResponse({"message": "Форма невалидна...", "status": "deny"})

    return JsonResponse({"message": "Hello", "status": "allow"})