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
    path('info', homeView.info, name='info'),
    path('mojerecenzije', recenzentView.mojerecenzije, name='mojerecenzije'),
    path('pregled', predsjedavajuciView.pregled, name='pregled'),
    path('pregled/recenzenti', predsjedavajuciView.recenzenti, name='recenzenti'),
    path('pregled/sudionici', predsjedavajuciView.sudionici, name='sudionici'),
    path('pregled/radovi', predsjedavajuciView.radovi, name='radovi'),
    path('adminsucelje', adminView.adminsucelje, name='adminsucelje'),
    path('javniradovi', homeView.javniradovi, name='javniradovi'),
    path('posaljiobavijest', predsjedavajuciView.obavijest, name='obavijest'),
    path('predsjedavajuci', predsjedavajuciView.uprsucelje, name='predsjedavajuci'),
    path('covidstats', adminView.covidstats, name='covidstats'),
    path('pregled/recenzenti/<korisnickoime>', adminView.uredipodatke, name='uredipodatke1'),
    path('pregled/sudionici/<korisnickoime>', adminView.uredipodatke, name='uredipodatke2'),
    path('pregled/radovi/<sifrada>', adminView.uredirad, name='uredirad'),
    path('activate/<uidb64>/<token>',  homeView.activate, name='activate'), 
    path('reset/<uidb64>/<token>/', homeView.new_password, name='password_reset_confirm'), 
    path('reset_password', homeView.reset_password, name='password_reset_save'),
    path('statistika', predsjedavajuciView.statistika, name='statistika')
]
