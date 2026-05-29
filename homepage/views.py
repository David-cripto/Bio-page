from django.shortcuts import render

from .profile_data import PROFILE


def home(request):
    return render(request, "homepage/concept.html", {"profile": PROFILE})


def idlm_blog(request):
    return render(request, "homepage/idlm_blog.html", {"profile": PROFILE})
