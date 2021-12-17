from collections import defaultdict
from io import StringIO, BytesIO
from typing import DefaultDict
from django.core.checks.messages import Error
from django.db.models.fields import DateTimeCheckMixin, NullBooleanField
from django.db.models.query import EmptyQuerySet
from django.db.models.expressions import RawSQL
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

    if LoggedInUser.vrstaKorisnik_id > 3: #1-admin 2-predsjedavajuci 3-recenzent 4-sudionik
        return redirect('home') #nema ovlasti, trebalo bi dati poruku

    if request.method == "POST":
        sifRad = request.POST["sifRad"]
        rad = models.Rad.objects.get(sifRad=sifRad)
        ocjena = request.POST["ocjena"] #id ocjene
        obrazlozenje = request.POST["obrazlozenje"]

        novaRecenzija = models.Recenzija(
            ocjena = models.Ocjena.objects.get(id=ocjena),
            obrazlozenje = obrazlozenje,
            recenzent = LoggedInUser,
            rad = rad
        )

        rad.recenziranBool = True
        if ocjena == 3: #id ocjene
            rad.revizijaBool = True
        else:
            rad.revizijaBool = False

        rad.save()
        novaRecenzija.save()

        return redirect('mojerecenzije')
    #radovi koji nemaju predan pdf se ne recenziraju, a također nas ne zanimaju radovi koji su recenzirani no ne trebaju reviziju (oni su tako i tako u recenzijama)
    fetchRadovi = models.Rad.objects.exclude(pdf="").exclude(recenziranBool = True, revizijaBool = False)
    fetchOcjene = models.Ocjena.objects.all()
    #ne zanimaju nas radovi koji zahtijevaju reviziju, oni se nalaze u fetchRadovi i ne prikazuju se kao "Recenzirani radovi"
    fetchMyRecenzije = models.Recenzija.objects.filter(recenzent=LoggedInUser).exclude(rad__revizijaBool = True)

    #Trazimo najnoviju recenziju za svaki pojedini rad. Upit odvoji sve recenzije s istim rad_id te svaku posebno sortira
    #po sifRecenzija, od najvece do najmanje. Kada to napravi, za svaki skup recenzija s istim rad_id pobroji redove (prvi je 1, drugi 2, ...)
    #te to koristimo kao rank. Na kraju uzimamo samo redove kojima je rank = 1.
    """
    WITH ranked AS (
    SELECT r.*, ROW_NUMBER() OVER (PARTITION BY rad_id ORDER BY "sifRecenzija" DESC) AS rank
    FROM "MK2ZK_App_recenzija" AS r
    )
    SELECT * FROM ranked WHERE rank = 1;
    """
    #SQL upit preuzet sa https://stackoverflow.com/a/1313293/4363932
    najnovijeRecenzije = models.Recenzija.objects.raw('WITH ranked AS (SELECT r.*, ROW_NUMBER() OVER (PARTITION BY rad_id ORDER BY "sifRecenzija" DESC) AS rank FROM "MK2ZK_App_recenzija" AS r) SELECT "sifRecenzija" FROM ranked WHERE rank = 1')
    fetchMyRecenzije = fetchMyRecenzije.filter(sifRecenzija__in = (x.sifRecenzija for x in najnovijeRecenzije))

    context['fetchedOcjene']=fetchOcjene
    context['fetchedRadovi']=fetchRadovi
    context['fetchedMyRecenzije']=fetchMyRecenzije
    
    return render(request, 'MojeRecenzije.html', context)
