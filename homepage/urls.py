from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("blog/", views.idlm_blog, name="idlm_blog"),
]
