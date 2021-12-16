from django.contrib import admin
from django.urls import path, include
from . import views
from .views import homeView, sudionikView, recenzentView, predsjedavajuciView, adminView

urlpatterns = [
    path('', homeView.home, name='home'),
    path('signup', homeView.signup, name='signup'),
    path('signin', homeView.signin, name='signin'),
    path('signout', homeView.signout, name='signout'),
    path('osobnipodaci', sudionikView.osobnipodaci, name='osobnipodaci'),
    path('mojiradovi', sudionikView.mojiradovi, name='mojiradovi'),
    path('sloziobrazac', adminView.sloziobrazac, name='sloziobrazac'),
    path('info', homeView.info, name='info'),
    path('mojerecenzije', recenzentView.mojerecenzije, name='mojerecenzije'),
    path('pregled', predsjedavajuciView.pregled, name='pregled'),
    path('pregled/recenzenti', predsjedavajuciView.recenzenti, name='recenzenti'),
    path('pregled/sudionici', predsjedavajuciView.sudionici, name='sudionici'),
    path('pregled/radovi', predsjedavajuciView.radovi, name='radovi')
]