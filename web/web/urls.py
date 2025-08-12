from django.contrib import admin
from django.urls import path, include
from django.urls import re_path as url
from . import views


urlpatterns = [
    #path('admin/', admin.site.urls),
    url('^$', views.index, name='index'),
    url('^send/', views.send, name='send'),
    path("media/<str:filename>/", views.get_img, name='get_img'),
    path('captcha/', include('captcha.urls'))
]
