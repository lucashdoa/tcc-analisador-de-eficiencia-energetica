import json

from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect

from app.models import Address, HouseholdAppliance


def index(request):
    if request.user.is_authenticated:
        return redirect('/home')
    else:
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
    typed_email = json.loads(request.body)['email']
    try:
        email = User.objects.get(email=typed_email)
        if email:
            return JsonResponse({
                'used': True,
                'email': typed_email
            })
        else:
            return JsonResponse({
                'used': False,
                'email': typed_email
            })
    except:
        return JsonResponse({
            'used': False,
            'email': typed_email
        })


def login_view(request):
    typed_email = json.loads(request.body)['email']
    typed_password = json.loads(request.body)['password']
    try:
        username = User.objects.get(email=typed_email)
        user = authenticate(username=username, password=typed_password)
        if user:
            login(request, user)
            return JsonResponse({
                'success': True,
            })
    except:
        return JsonResponse({
            'success': False,
        })
    return JsonResponse({
        'success': False,
    })


def logout_view(request):
    logout(request)
    return redirect('index')


def home(request):
    user = User.objects.get(username=request.user)
    user_addresses = Address.objects.filter(user=user)
    user_househould_appliances = HouseholdAppliance.objects.filter(user=user)
    return render(request, 'home.html', {
        'user': user,
        'addresses': user_addresses,
        'household_appliances': user_househould_appliances
    })


def panel(request):
    user = User.objects.get(username=request.user)
    user_househould_appliances = HouseholdAppliance.objects.filter(user=user)
    return render(request, 'panel.html', {
        'user': user,
        'household_appliances': user_househould_appliances
    })