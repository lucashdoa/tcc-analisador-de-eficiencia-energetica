from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('sobre', views.about, name="about"),
    path('pbe', views.pbe, name="pbe"),
    path('ajuda', views.help, name="help"),
    path('contato', views.contact, name="contact"),
    path('check_email', views.check_email, name="check_email"),
    path('login', views.login_view, name="login"),
    path('register', views.register_view, name="register"),
    path('logout', views.logout_view, name="logout"),
    path('home', views.home, name="home_page"),
    path('add_household_appliance', views.add_household_appliance, name="add_household_appliance"),
    path('add_address', views.add_address, name="add_address"),
    path('update_address', views.update_address, name="update_address"),
    path('update_user_data', views.update_user_data, name="update_user_data"),
    path('painel/<int:user_id>', views.panel, name="panel"),
    path('measure_datatable/<str:household_appliance>', views.MeasureDatatable.as_view(), name="measure_datatable"),
    path('test_chart', views.test_chart, name="test_chart"),
    path('measures_api/', views.measures_save_api),
]
