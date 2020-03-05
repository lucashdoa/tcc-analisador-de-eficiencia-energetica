from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('sobre', views.about, name="about"),
    path('pbe', views.pbe, name="pbe"),
    path('ajuda', views.help, name="help"),
    path('contato', views.contact, name="contact"),
    path('check_email', views.check_email, name="check_email"),
]