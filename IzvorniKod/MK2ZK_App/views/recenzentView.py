from collections import defaultdict
from io import StringIO, BytesIO
from typing import DefaultDict
from django.core.checks.messages import Error
from django.db.models.fields import DateTimeCheckMixin, NullBooleanField
from django.db.models.query import EmptyQuerySet
from django.http.response import FileResponse, HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.utils.crypto import get_random_string
from IzvorniKod.MK2ZK_App import models
from django.db import IntegrityError 
from django.core import serializers
from django.utils import (dateformat, formats)
import zipfile
import os

def mojerecenzije(request):
    
    context={}
    if "LoggedInUserId" in request.session: #ulogirani smo
        context["LoggedInUser"]=request.session['LoggedInUserId']
        context["LoggedInUserRole"]=request.session['LoggedInUserRole']
    else: #nismo ulogirani
        return redirect('signin')
    
    LoggedInUser=models.Korisnik.objects.get(id=request.session['LoggedInUserId'])
    recenzentSekcija = LoggedInUser.korisnikSekcija
    fetchRadovi = models.Rad.objects.filter(radSekcija=recenzentSekcija)
    fetchOcjene = models.Ocjena.objects.all()
    fetchMyRecenzije = models.Recenzija.objects.filter(recenzent=LoggedInUser)
    fetchRecenzije = models.Recenzija.objects.all()
    
    if request.method == "POST":
        print(request.POST)
        
        for rad in fetchRadovi:
            print(rad.sifRad)
            print(str(rad.sifRad) in request.POST)
            if str(rad.sifRad) in request.POST:
                ocjena=request.POST[str(rad.sifRad) + "ocjena"]
                obrazlozenje=request.POST[str(rad.sifRad) + "obrazlozenje"]
                newRecenzija=models.Recenzija(
                    ocjena = models.Ocjena.objects.get(znacenje=ocjena),
                    obrazlozenje = obrazlozenje,
                    recenzent = LoggedInUser,
                    rad = rad
                )
                rad.recenziranBool=True
                if models.Ocjena.objects.get(znacenje=ocjena).id==3:
                    rad.revizijaBool=True
                else:
                    rad.revizijaBool=False
                rad.save()
                newRecenzija.save()
        return redirect('mojerecenzije')

    for rad in fetchRadovi:
        print(rad in fetchRecenzije)

    context['fetchedOcjene']=fetchOcjene
    context['fetchedRadovi']=fetchRadovi
    context['fetchedMyRecenzije']=fetchMyRecenzije
    context['fetchedRecenzije']=fetchRecenzije
    
    return render(request, 'MojeRecenzije.html', context)
