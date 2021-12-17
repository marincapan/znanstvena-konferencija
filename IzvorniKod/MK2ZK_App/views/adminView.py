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


def sloziobrazac(request):
    context={}
    if "LoggedInUserId" in request.session: #ulogirani smo
        context["LoggedInUser"]=request.session['LoggedInUserId']
    else: #nismo ulogirani
        return redirect('signin')
    
    if "LoggedInUserRole" in request.session:
        if request.session['LoggedInUserRole'] == "Admin":
            context["LoggedInUserRole"]=request.session['LoggedInUserRole']
        else: #nije admin
            return redirect('/') #redirect na homepage

    fetchedPolja=models.DodatnaPoljaObrasca.objects.filter().all()

    for polje in fetchedPolja:
        print(polje.imePolja)        

    if request.method == "POST":            
        if 'AddNewField' in request.POST:
            print(request.POST)
            fieldName = request.POST["fieldName"]
            fieldType = request.POST["fieldType"]
            newfield=models.TipPoljaObrasca.objects.get(naziv=fieldType)
            if not models.DodatnaPoljaObrasca.objects.filter(imePolja=fieldName,tipPolja=newfield).exists():
                newField=models.DodatnaPoljaObrasca(
                    imePolja=fieldName,
                    tipPolja=newfield
                )
                newField.save()
            context['DodatnaPolja']=fetchedPolja
            return redirect('sloziobrazac')
        if 'ActiveFields' in request.POST:
            for polje in fetchedPolja:
                try:
                    checked = request.POST[polje.imePolja]
                    checked = True 
                except:
                    checked = False
                polje.active = checked
                polje.save()
                
        context['DodatnaPolja']=fetchedPolja
        return redirect('sloziobrazac')
    context['DodatnaPolja']=fetchedPolja
    return render(request, 'SloziObrazac.html', context)
def adminsucelje(request):
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
    context={}
    context["javniBool"] = models.Konferencija.objects.get(sifKonferencija=1).javniRadoviBool
    context["brojPredanihRadova"] = brojPredanihRadova
    if request.method == "POST":
      
        if 'NewUserName' in request.POST:
            Username = request.POST['Username']
            Predsjedavajuci=models.Korisnik.objects.get(id=4)
            Predsjedavajuci.korisnickoIme = Username
            try:
                Predsjedavajuci.save()
            except IntegrityError:
                messages.error(request, "To korisnicko ime je vec u uporabi")
                return redirect('adminsucelje')

        if 'NewFName' in request.POST:
            Fname = request.POST['Fname']
            Predsjedavajuci=models.Korisnik.objects.get(id=4)
            Predsjedavajuci.ime = Fname
            Predsjedavajuci.save()

        if 'NewLName' in request.POST:
            Lname = request.POST['Lname']
            Predsjedavajuci=models.Korisnik.objects.get(id=4)
            Predsjedavajuci.prezime = Lname
            Predsjedavajuci.save()

        if 'NewEmail' in request.POST:
            email = request.POST['email']
            Predsjedavajuci=models.Korisnik.objects.get(id=4)
            Predsjedavajuci.email = email
            try:
                Predsjedavajuci.save()
            except IntegrityError:
                messages.error(request, "Ta email adresa je vec u uporabi")
                return redirect('adminsucelje')
        if "makePublic" in request.POST:
            konferencija=models.Konferencija.objects.get(sifKonferencija=1)
            if konferencija.javniRadoviBool==True:
                konferencija.javniRadoviBool=False
                konferencija.save()
            else:
                konferencija.javniRadoviBool=True
                konferencija.save()
            print(konferencija.javniRadoviBool)
             
        return redirect('adminsucelje')
        

    if "LoggedInUserId" in request.session: #ulogirani smo
        context["LoggedInUser"]=request.session['LoggedInUserId']
    else: #nismo ulogirani
        return redirect('signin')
    
    if "LoggedInUserRole" in request.session:
        if request.session['LoggedInUserRole'] == "Admin":
            context["LoggedInUserRole"]=request.session['LoggedInUserRole']
            Predsjedavajuci=models.Korisnik.objects.get(id=4)
            context['korisnickoIme']=Predsjedavajuci.korisnickoIme
            context['ime']=Predsjedavajuci.ime
            context['prezime']=Predsjedavajuci.prezime
            context['email']=Predsjedavajuci.email
            context['uloga']=Predsjedavajuci.vrstaKorisnik.naziv
            context['MaticnaUstanova']=Predsjedavajuci.korisnikUstanova.naziv
            context['sekcija']=Predsjedavajuci.korisnikSekcija.naziv
        else: #nije admin
            return redirect('/') #redirect na homepage

    recenzenti = models.Korisnik.objects.filter(vrstaKorisnik_id=3)
    sudionici = models.Korisnik.objects.filter(vrstaKorisnik_id=1)
    radovi = models.Rad.objects.all()
    sekcije = models.Sekcija.objects.all()
    korisnici = models.Korisnik.objects.all()

    #brojac predanih radova
    brojPredanihRadova = 0

    for rad in radovi:
        rad.radSekcija_naziv = sekcije.get(sifSekcija=rad.radSekcija_id).naziv
        rad.radKorisnik_prezime = korisnici.get(id=rad.radKorisnik_id).prezime
        if(rad.pdf != ""):
            brojPredanihRadova += 1

    context["Radovi"] = radovi
    context["brojPredanihRadova"] = brojPredanihRadova

    return render(request, 'AdminSucelje.html', context)
