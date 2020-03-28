import json
from datetime import timedelta

from django.db.models import Avg
from django.db.models.functions import datetime
from django.utils import timezone
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.datetime_safe import date
from django.views.decorators.csrf import csrf_exempt
from django_datatables_view.base_datatable_view import BaseDatatableView
from app.models import Address, HouseholdAppliance, Measure


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


def panel(request, user_id):
    user = User.objects.get(username=request.user)
    user_household_appliances = HouseholdAppliance.objects.filter(user=user)
    selected_household_appliance = HouseholdAppliance.objects.first()
    return render(request, 'panel.html', {
        'user': user,
        'household_appliances': user_household_appliances,
        'selected_household_appliance': selected_household_appliance
    })


class MeasureDatatable(BaseDatatableView):
    def get_initial_queryset(self):
        aux = Measure.objects.all()
        return aux

    # define the columns that will be returned
    columns = ['voltage', 'current', 'active_power', 'power_factor', 'frequency', 'energy', 'created_at']

    # define column names that will be used in sorting
    order_columns = ['voltage', 'current', 'active_power', 'power_factor', 'frequency', 'energy', 'created_at']

    max_display_length = 500

    def filter_queryset(self, qs):
        # simple filter:
        search = self.request.GET.get(u'search[value]', None)
        if search:
            try:
                int_search = int(search)
            except:
                int_search = None
            qs = qs.filter(Q(id=int_search) | Q(username__icontains=search) | Q(email__icontains=search) |
                           Q(full_name__icontains=search))
        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            created_at = timezone.localtime(item.created_at)
            json_data.append([
                item.voltage,
                item.current,
                item.active_power,
                item.power_factor,
                item.frequency,
                item.energy,
                created_at.strftime("%Y/%m/%d %H:%M:%S")
            ])
        return json_data


@csrf_exempt
def test_chart(request):
    try:
        measures = []
        measures_label = []
        for idx in reversed(range(7)):
            voltage = 0
            past_date = date.today()-timedelta(days=idx)
            try:
                daily_measures_queryset = Measure.objects.filter(created_at__day=past_date.day)
                for measure in daily_measures_queryset:
                    voltage += measure.voltage
                voltage = voltage/daily_measures_queryset.count()
            except:
                voltage = 0
            measures.append(voltage)
            measures_label.append(past_date)

        return JsonResponse({'valid': True, 'chart_values': measures, 'chart_labels': measures_label})
    except:
        return JsonResponse({'valid': False, 'error_message': "Deu pau."})
