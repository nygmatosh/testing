from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from web.forms import SendCommentForm
from web.class_comment import CommentControl
from web.class_captcha_refresh import Refresh
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
        add = CommentControl()

        if form.is_valid():

            return add.add_comment(form, request)
            
        return JsonResponse({"message": "Форма невалидна...", "status": "deny"})




def get_file(request, filename):
    return CommentControl().get_file(filename)



def new_captcha(request):
    return Refresh().run()