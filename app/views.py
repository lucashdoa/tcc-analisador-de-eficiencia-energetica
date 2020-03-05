import json
from django.http import JsonResponse
from django.shortcuts import render


def home(request):
    return render(request, "index.html", {})

def about(request):
    return render(request, "about.html", {})

def pbe(request):
    return render(request, "pbe.html", {})

def help(request):
    return render(request, "help.html", {})

def contact(request):
    return render(request, "contact.html", {})

def check_email(request):
    email = json.loads(request.body)['email']
    print(email)
    return JsonResponse({
        'valid': True,
        'email': email
    })