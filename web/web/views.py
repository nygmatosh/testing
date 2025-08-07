from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from web.forms import SendCommentForm



def index(request):

    data = {
        "form": SendCommentForm()
    }

    return render(request, 'web/index.html', data)




def send(request):
    if request.method == 'POST':
        
        form = SendCommentForm(request.POST)

        if form.is_valid():
            return JsonResponse({"message": "OK", "status": "allow"})
        return JsonResponse({"message": "Форма невалидна...", "status": "deny"})

    return JsonResponse({"message": "Hello", "status": "allow"})