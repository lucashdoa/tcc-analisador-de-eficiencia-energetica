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
    path('logout', views.logout_view, name="logout"),
    path('home', views.home, name="home_page"),
    path('painel', views.panel, name="panel"),
]