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

def pregled(request):
    context={}
    if "LoggedInUserId" in request.session:
        context["LoggedInUser"]=request.session['LoggedInUserId']
    
    if "LoggedInUserRole" in request.session:
        context["LoggedInUserRole"]=request.session['LoggedInUserRole']

    recenzenti = models.Korisnik.objects.filter(vrstaKorisnik_id=3)
    sudionici = models.Korisnik.objects.filter(vrstaKorisnik_id=1)
    radovi = models.Rad.objects.all()

    context["recenzenti_broj_odobrenih"] = recenzenti.filter(odobrenBool=True).count()
    context["recenzenti_broj_neodobrenih"] = recenzenti.filter(odobrenBool=False).count()
    context["sudionici_broj_odobrenih"] = sudionici.filter(odobrenBool=True).count()
    context["sudionici_broj_neodobrenih"] = sudionici.filter(odobrenBool=False).count()
    context["radovi_broj_recenziranih"] = radovi.filter(recenziranBool=True).count()
    context["radovi_broj_nerecenziranih"] = radovi.filter(recenziranBool=False).count()

    return render(request, 'Pregled.html', context)

def recenzenti(request):
    context={}
    if "LoggedInUserId" in request.session:
        context["LoggedInUser"]=request.session['LoggedInUserId']
    
    if "LoggedInUserRole" in request.session:
        context["LoggedInUserRole"]=request.session['LoggedInUserRole']

    recenzenti = models.Korisnik.objects.filter(vrstaKorisnik_id=3)
    sekcije = models.Sekcija.objects.all()
    ustanove = models.Ustanova.objects.all()

    #Shvatio sam da je puno lakse napravit ovo nego stavljat naziv unutar templatea
    for recenzent in recenzenti:
        recenzent.korisnikSekcija_naziv = sekcije.get(sifSekcija=recenzent.korisnikSekcija_id).naziv
        recenzent.korisnikUstanova_naziv = ustanove.get(sifUstanova=recenzent.korisnikUstanova_id).naziv


    context["Recenzenti"] = recenzenti

    return render(request, 'Recenzenti.html', context)

def sudionici(request):
    context={}
    if "LoggedInUserId" in request.session:
        context["LoggedInUser"]=request.session['LoggedInUserId']
    
    if "LoggedInUserRole" in request.session:
        context["LoggedInUserRole"]=request.session['LoggedInUserRole']

    sudionici = models.Korisnik.objects.filter(vrstaKorisnik_id=4)
    sekcije = models.Sekcija.objects.all()
    ustanove = models.Ustanova.objects.all()

    #Shvatio sam da je puno lakse napravit ovo nego stavljat naziv unutar templatea
    for sudionik in sudionici:
        sudionik.korisnikSekcija_naziv = sekcije.get(sifSekcija=sudionik.korisnikSekcija_id).naziv
        sudionik.korisnikUstanova_naziv = ustanove.get(sifUstanova=sudionik.korisnikUstanova_id).naziv

    context["Sudionici"] = sudionici

    return render(request, 'Sudionici.html', context)

def radovi(request):
    print(models.Konferencija.objects.get(sifKonferencija=1).javniRadoviBool)
    if request.method == "POST":
        if "downloadAll" in request.POST:
            #Dohvacanje svih potrebnih podataka
            korisnici = models.Korisnik.objects.all()
            radovi = models.Rad.objects.all()

            #Postavljanje zipa
            zip_name = "radovi.zip"
            s = BytesIO()
            zip = zipfile.ZipFile(s, "w")

            #Iteriranje kroz sve radove kako bi se mogla napraviti odgovarajuca struktura .zip datoteke
            for rad in radovi:
                if(rad.pdf.name == ''):
                    continue
                korisnik = korisnici.get(id=rad.radKorisnik_id)
                pdf_dir, pdf_name = os.path.split(rad.pdf.name)
                path = os.path.join(korisnik.prezime + korisnik.ime, rad.naslov, pdf_name)

                zip.write("IzvorniKod/Radovi/" + rad.pdf.name, path)

            zip.close()

            resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
            resp["Content-Disposition"] = 'attachment; filename=%s' % zip_name
            return resp
        if "makePublic" in request.POST:
            konferencija=models.Konferencija.objects.get(sifKonferencija=1)
            print("IM HERE")
            print(konferencija.javniRadoviBool)
            if konferencija.javniRadoviBool==True:
                print("flag1")
                konferencija.javniRadoviBool=False
                konferencija.save()
            else:
                print("flag2")
                konferencija.javniRadoviBool=True
                konferencija.save()
            print(konferencija.javniRadoviBool)
            

    context={}
    if "LoggedInUserId" in request.session: #ulogirani smo
        context["LoggedInUser"]=request.session['LoggedInUserId']
    else: #nismo ulogirani
        return redirect('signin')
    
    if "LoggedInUserRole" in request.session:
        if request.session['LoggedInUserRole'] == "Admin" or models.Konferencija.objects.get(sifKonferencija=1).javniRadoviBool==True:
            context["LoggedInUserRole"]=request.session['LoggedInUserRole']
        else: #nije admin ili radovi nisu javni
            return redirect('/')


    radovi = models.Rad.objects.all()
    sekcije = models.Sekcija.objects.all()
    korisnici = models.Korisnik.objects.all()

    #brojac predanih radova
    brojPredanihRadova = 0

    #Shvatio sam da je puno lakse napravit ovo nego stavljat naziv unutar templatea
    for rad in radovi:
        rad.radSekcija_naziv = sekcije.get(sifSekcija=rad.radSekcija_id).naziv
        rad.radKorisnik_prezime = korisnici.get(id=rad.radKorisnik_id).prezime
        if(rad.pdf != ""):
            brojPredanihRadova += 1

    context["javniBool"] = models.Konferencija.objects.get(sifKonferencija=1).javniRadoviBool
    context["Radovi"] = radovi
    context["brojPredanihRadova"] = brojPredanihRadova

    return render(request, 'Radovi.html', context)
    