from django.shortcuts import render

from .profile_data import PROFILE


def home(request):
    return render(request, "homepage/concept.html", {"profile": PROFILE})


def publications(request):
    return render(request, "homepage/publications.html", {"profile": PROFILE})


def blog_index(request):
    return render(request, "homepage/blog_index.html", {"profile": PROFILE})


def idlm_blog(request):
    return render(request, "homepage/idlm_blog.html", {"profile": PROFILE})
