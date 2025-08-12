from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from web.forms import SendCommentForm
from web.class_comment import CommentControl
from django.core.paginator import Paginator
from web.models import *



def index(request):

    all = CommentControl().get_all()

    paginator = Paginator(all, 25)
    page = request.GET.get('page')
    comments = paginator.get_page(page)


    data = {
        "comments": comments,
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
                return JsonResponse({"message": "Выполняется обработка комментария", "status": "allow"})
            
        return JsonResponse({"message": "Форма невалидна...", "status": "deny"})

    return JsonResponse({"message": "Hello", "status": "allow"})




def get_img(request, filename):
    return CommentControl().get_image(filename)