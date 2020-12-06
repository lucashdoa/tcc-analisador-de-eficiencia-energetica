import json
from datetime import timedelta

from django.db.models import Avg
from django.db.models.functions import datetime
from django.utils import timezone
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.datetime_safe import date
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from django_datatables_view.base_datatable_view import BaseDatatableView
from app.models import Address, HouseholdAppliance, Measure, Refrigerator

def get_consumed_energy(household_appliance):
    measures_queryset = Measure.objects.filter(household_appliance=household_appliance.pk,created_at__month=(datetime.datetime.now().month - 1))
    power_sum = 0
    for measure in measures_queryset:
        power_sum += measure.active_power
    try:
        mean_power = power_sum/measures_queryset.count()
    except:
        mean_power = 0
    return (mean_power*24*30)/1000

def calculate_IEE_refrigarator(household_appliance):

    # 1 - Calcular volume ajustado: AV = Vr + Somatoria(f*Vc)

    f = 0.0
    if household_appliance.freezer_stars == 1:
        f = 1.41
    if household_appliance.freezer_stars == 2:
        f = 1.63
    if household_appliance.freezer_stars == 3:
        f = 1.85
    Vr = household_appliance.refrigerator_volume
    Vc = household_appliance.freezer_volume

    # Se for Frost-Free, Vr e Vc são multiplicados por 1,2
    if household_appliance.is_frost_free is True:
        Vr = Vr * 1.2;
        Vc = Vc * 1.2;

    AV = Vr + (f*Vc)

    # 2 - Calcular consumo padrão: Cp = a*AV + b
    if household_appliance.category == "Refrigerador":
        a = 0.0346
        b = 19.117
    if household_appliance.category == "Combinado" and household_appliance.is_frost_free is False:
        a = 0.0916
        b = 17.083
    if household_appliance.category == "Combinado" and household_appliance.is_frost_free is True:
        a = 0.1059
        b = 7.4862
    if household_appliance.category == "Congelador Vertical" and household_appliance.is_frost_free is False:
        a = 0.0211
        b = 39.228
    if household_appliance.category == "Congelador Vertical" and household_appliance.is_frost_free is True:
        a = 0.0178
        b = 58.712
    if household_appliance.category == "Congelador Horizontal":
        a = 0.0758
        b = 13.095

    Cp = (a*AV) + b

    # 3 - Calcular o consumo declarado (C)
    measures_queryset = Measure.objects.filter(household_appliance=household_appliance.pk)
    power_sum = 0
    for measure in measures_queryset:
        power_sum += measure.active_power
    mean_power = power_sum/measures_queryset.count()
    C = (mean_power*24*30)/1000
    print("C :", C)

    # 4 - Calcular índicepytho de eficiência energética: IEE = C/Cp

    IEE = float(C)/float(Cp)
    print(IEE)

    # 5 - Definir classificação

    if IEE < 0.869:
        return 'A'
    if IEE < 0.949:
        return 'B'
    if IEE < 1.020:
        return 'C'
    if IEE < 1.097:
        return 'D'
    if IEE < 1.179:
        return 'E'
    if IEE < 1.267:
        return 'F'
    else:
        return 'G'


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


@csrf_protect
def login_view(request):
    typed_email = json.loads(request.body)['email']
    typed_password = json.loads(request.body)['password']
    try:
        user = User.objects.get(email=typed_email)
        # user = authenticate(username=username, password=typed_password)
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


def register_view(request):
    typed_first_name = json.loads(request.body)['firstName']
    typed_last_name = json.loads(request.body)['lastName']
    typed_email = json.loads(request.body)['email']
    typed_password = json.loads(request.body)['password']
    try:
        username = typed_email
        user = User(
            first_name=typed_first_name,
            last_name=typed_last_name,
            email=typed_email,
            password=typed_password,
            username=username
        )
        user.save()
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
    try:
        user_addresses = Address.objects.get(user=user)
    except:
        user_addresses = None
    user_househould_appliances = HouseholdAppliance.objects.filter(user=user)
    return render(request, 'home.html', {
        'user': user,
        'address': user_addresses,
        'household_appliances': user_househould_appliances
    })


def panel(request, user_id):
    user = User.objects.get(username=request.user)
    user_household_appliances = HouseholdAppliance.objects.filter(user=user)
    user_addresses = Address.objects.filter(user=user)
    try:
        selectedHouseholdID = request.POST.get('selected-household')
        selected_household_appliance = HouseholdAppliance.objects.get(id=selectedHouseholdID)
    except:
        selected_household_appliance = HouseholdAppliance.objects.filter(user=user).first()
    address = Address.objects.get(user=user)
    try:
        classification = calculate_IEE_refrigarator(selected_household_appliance.refrigerator)
        consumed_energy = get_consumed_energy(selected_household_appliance.refrigerator)
    except:
        classification = 0
        consumed_energy = 0
    print(classification)
    return render(request, 'panel.html', {
        'user': user,
        'household_appliances': user_household_appliances,
        'address': address,
        'addresses': user_addresses,
        'selected_household_appliance': selected_household_appliance,
        'classification': classification,
        'consumed_energy': consumed_energy
    })



def add_household_appliance(request):
    type = json.loads(request.body)['type']
    model = json.loads(request.body)['model']
    brand = json.loads(request.body)['brand']
    energy_consumption = json.loads(request.body)['energyConsumption']
    classification = json.loads(request.body)['classification']
    refrigerator_volume = json.loads(request.body)['refrigeratorVolume']
    freezer_volume = json.loads(request.body)['freezerVolume']
    freezer_stars = json.loads(request.body)['freezerStars']
    frost_free = json.loads(request.body)['frostFree']
    category = json.loads(request.body)['category']
    try:
        household_appliance = HouseholdAppliance(
            user=request.user,
            type=type,
            model=model,
            brand=brand,
            energy_consumption=energy_consumption,
            classification=classification,
            purchased_at=datetime.datetime.now()
        )
        household_appliance.save()

        refrigerator = Refrigerator(
            household_appliance=household_appliance,
            category=category,
            refrigerator_volume=refrigerator_volume,
            freezer_volume=freezer_volume,
            freezer_stars=freezer_stars,
            is_frost_free=frost_free
        )

        refrigerator.save()
        if refrigerator:
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

def update_user_data(request):
    new_first_name = json.loads(request.body)['newFirstName']
    new_last_name = json.loads(request.body)['newLastName']
    new_email = json.loads(request.body)['newEmail']
    print(new_first_name)
    print(new_last_name)
    print(new_email)
    try:
        user = User.objects.get(username=request.user)
        user.first_name = new_first_name
        user.last_name = new_last_name
        user.email = new_email
        user.save()
        return JsonResponse({
            'success': True,
        })
    except:
        return JsonResponse({
            'success': False,
        })

def add_address(request):
    street = json.loads(request.body)['street']
    number = json.loads(request.body)['number']
    complement = json.loads(request.body)['complement']
    neighborhood = json.loads(request.body)['neighborhood']
    city = json.loads(request.body)['city']
    state = json.loads(request.body)['state']
    energy_company = json.loads(request.body)['energyCompany']
    try:
        address = Address(
            user=request.user,
            street=street,
            number=number,
            complement=complement,
            neighborhood=neighborhood,
            city=city,
            state=state,
            energy_company=energy_company
        )
        address.save()

        if address:
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

def update_address(request):
    street = json.loads(request.body)['newStreet']
    number = json.loads(request.body)['newNumber']
    complement = json.loads(request.body)['newComplement']
    neighborhood = json.loads(request.body)['newNeighborhood']
    city = json.loads(request.body)['newCity']
    state = json.loads(request.body)['newState']
    energy_company = json.loads(request.body)['newEnergyCompany']
    user_address = Address.objects.get(user=request.user)
    try:
        user_address.street = street
        user_address.number = number
        user_address.complement = complement
        user_address.neighborhood = neighborhood
        user_address.city = city
        user_address.state = state
        user_address.energy_company  = energy_company
        user_address.save()
        return JsonResponse({
            'success': True,
        })
    except:
        return JsonResponse({
            'success': False,
        })



class MeasureDatatable(BaseDatatableView):
    def get_initial_queryset(self, *args, **kwargs):
        household_appliance = self.kwargs['household_appliance']
        print(household_appliance)
        try:
            aux = Measure.objects.filter(household_appliance=household_appliance)
        except:
            aux = None
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
            energy = 0
            past_date = date.today()-timedelta(days=idx)
            try:
                daily_measures_queryset = Measure.objects.filter(created_at__day=past_date.day, created_at__month=past_date.month, created_at__year=past_date.year)
                for measure in daily_measures_queryset:
                    energy += measure.active_power
                energy = (energy/daily_measures_queryset.count())*24/1000
            except:
                energy = 0
            measures.append(energy)
            measures_label.append(past_date)

        return JsonResponse({'valid': True, 'chart_values': measures, 'chart_labels': measures_label})
    except:
        return JsonResponse({'valid': False, 'error_message': "Deu pau."})

@csrf_exempt
def measures_save_api(request):
    print(request.body)
    user_id = json.loads(request.body)['user']
    household_id = json.loads(request.body)['household']
    voltage = json.loads(request.body)['voltage']
    current = json.loads(request.body)['current']
    power = json.loads(request.body)['power']
    frequency = json.loads(request.body)['frequency']
    energy = json.loads(request.body)['energy']
    pf = json.loads(request.body)['pf']
    try:
        measure = Measure(
            household_appliance=HouseholdAppliance.objects.get(id=household_id),
            voltage=voltage,
            current=current,
            active_power=power,
            frequency=frequency,
            energy=energy,
            power_factor=pf
        )
        measure.save()
        if measure:
            return JsonResponse({
                'success': True,
            })
    except:
        return JsonResponse({
            'success': False
        })