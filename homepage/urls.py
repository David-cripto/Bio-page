from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("publications/", views.publications, name="publications"),
    path("blog/", views.blog_index, name="blog"),
    path("blog/idlm/", views.idlm_blog, name="idlm_blog"),
]
