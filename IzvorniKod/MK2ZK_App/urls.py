from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('osobnipodatci', views.osobnipodatci, name='osobnipodatci'),
    path('mojiradovi', views.mojiradovi, name='mojiradovi'),
    path('sloziobrazac', views.sloziobrazac, name='sloziobrazac'),
    path('info', views.info, name='info')
]