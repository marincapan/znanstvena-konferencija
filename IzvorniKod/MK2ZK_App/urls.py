from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('osobnipodaci', views.osobnipodaci, name='osobnipodaci'),
    path('mojiradovi', views.mojiradovi, name='mojiradovi'),
    path('sloziobrazac', views.sloziobrazac, name='sloziobrazac'),
    path('info', views.info, name='info'),
    path('mojerecenzije', views.mojerecenzije, name='mojerecenzije')
]