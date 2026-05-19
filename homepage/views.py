from django.shortcuts import render

from .profile_data import PROFILE


def home(request):
    return render(request, "homepage/home.html", {"profile": PROFILE})


def concept(request):
    return render(request, "homepage/concept.html", {"profile": PROFILE})
