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
        if request.session['LoggedInUserRole'] == "Admin" or request.session['LoggedInUserRole'] == "Predsjedavajuci":
            context["LoggedInUserRole"]=request.session['LoggedInUserRole']
        else: #nije admin/predsjedavajuci
            messages.error(request,"Nemaš prava za ovu stranicu!")
            return redirect('/')

    recenzenti = models.Korisnik.objects.filter(vrstaKorisnik_id=3)
    sudionici = models.Korisnik.objects.filter(vrstaKorisnik_id=4)
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
        if request.session['LoggedInUserRole'] == "Admin" or request.session['LoggedInUserRole'] == "Predsjedavajuci":
            context["LoggedInUserRole"]=request.session['LoggedInUserRole']
        else: #nije admin/predsjedavajuci
            messages.error(request,"Nemaš prava za ovu stranicu!")
            return redirect('/')

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
        if request.session['LoggedInUserRole'] == "Admin" or request.session['LoggedInUserRole'] == "Predsjedavajuci":
            context["LoggedInUserRole"]=request.session['LoggedInUserRole']
        else: #nije admin/predsjedavajuci
            messages.error(request,"Nemaš prava za ovu stranicu!")
            return redirect('/')

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
        

    context={}
    if "LoggedInUserId" in request.session: #ulogirani smo
        context["LoggedInUser"]=request.session['LoggedInUserId']
    else: #nismo ulogirani
        return redirect('signin')
    
    if "LoggedInUserRole" in request.session:
        if request.session['LoggedInUserRole'] == "Admin" or request.session['LoggedInUserRole'] == "Predsjedavajuci" or models.Konferencija.objects.get(sifKonferencija=1).javniRadoviBool==True:
            context["LoggedInUserRole"]=request.session['LoggedInUserRole']
        else: #nije admin ili radovi nisu javni
            messages.error(request,"Nemaš prava za ovu stranicu!")
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

def obavijest(request):
    context={}
    if "LoggedInUserId" in request.session:
        context["LoggedInUser"]=request.session['LoggedInUserId']
    
    if "LoggedInUserRole" in request.session:
        if request.session['LoggedInUserRole'] == "Admin" or request.session['LoggedInUserRole'] == "Predsjedavajuci":
            context["LoggedInUserRole"]=request.session['LoggedInUserRole']
        else: #nije admin/predsjedavajuci
            messages.error(request,"Nemaš prava za ovu stranicu!")
            return redirect('/')
    
    sekcije = models.Sekcija.objects.all()
    ustanove = models.Ustanova.objects.all()

    korisnici = models.Korisnik.objects.filter(vrstaKorisnik_id__in=[3,4]).filter(odobrenBool=True)

    #Shvatio sam da je puno lakse napravit ovo nego stavljat naziv unutar templatea
    for korisnik in korisnici:
        korisnik.korisnikSekcija_naziv = sekcije.get(sifSekcija=korisnik.korisnikSekcija_id).naziv
        korisnik.korisnikUstanova_naziv = ustanove.get(sifUstanova=korisnik.korisnikUstanova_id).naziv
    
    context["Korisnici"] = korisnici

    return render(request, 'PosaljiObavijest.html', context)
    
def uprsucelje(request):
    context={}
    if "LoggedInUserId" in request.session:
        context["LoggedInUser"]=request.session['LoggedInUserId']
    
    if "LoggedInUserRole" in request.session:
        if request.session['LoggedInUserRole'] == "Predsjedavajuci":
            context["LoggedInUserRole"]=request.session['LoggedInUserRole']
        else: #nije predsjedavajuci
            messages.error(request,"Nemaš prava za ovu stranicu!")
            return redirect('/')

    recenzenti = models.Korisnik.objects.filter(vrstaKorisnik_id=3)
    sudionici = models.Korisnik.objects.filter(vrstaKorisnik_id=1)
    radovi = models.Rad.objects.all()

    neodobreni = models.Korisnik.objects.filter(vrstaKorisnik_id=3, odobrenBool__isnull=True)
    sekcije = models.Sekcija.objects.all()
    ustanove = models.Ustanova.objects.all()
    if request.method == "POST":
        for recenzent in recenzenti:
            if ("Prihvati" + str(recenzent.id)) in request.POST:
                updateRecenzent=models.Korisnik.objects.get(id=recenzent.id)
                updateRecenzent.odobrenBool=True
                updateRecenzent.save()
                return redirect("predsjedavajuci")
            if ("Odbij" + str(recenzent.id)) in request.POST:
                updateRecenzent=models.Korisnik.objects.get(id=recenzent.id)
                updateRecenzent.odobrenBool=False
                updateRecenzent.save()
                return redirect("predsjedavajuci")

    #Shvatio sam da je puno lakse napravit ovo nego stavljat naziv unutar templatea
    for recenzent in neodobreni:
        recenzent.korisnikSekcija_naziv = sekcije.get(sifSekcija=recenzent.korisnikSekcija_id).naziv
        recenzent.korisnikUstanova_naziv = ustanove.get(sifUstanova=recenzent.korisnikUstanova_id).naziv


    context["Neodobreni"] = neodobreni
    context["recenzenti_broj_odobrenih"] = recenzenti.filter(odobrenBool=True).count()
    context["recenzenti_broj_neodobrenih"] = recenzenti.filter(odobrenBool=None).count()
    context["sudionici_broj_odobrenih"] = sudionici.filter(odobrenBool=True).count()
    context["sudionici_broj_neodobrenih"] = sudionici.filter(odobrenBool=False).count()
    context["radovi_broj_recenziranih"] = radovi.filter(recenziranBool=True).count()
    context["radovi_broj_nerecenziranih"] = radovi.filter(recenziranBool=False).count()

    return render(request, 'Predsjedavajuci.html', context)

def statistika(request):
    context={}
    if "LoggedInUserId" in request.session:
        context["LoggedInUser"]=request.session['LoggedInUserId']
    
    if "LoggedInUserRole" in request.session:
        if request.session['LoggedInUserRole'] == "Admin" or request.session['LoggedInUserRole'] == "Predsjedavajuci":
            context["LoggedInUserRole"]=request.session['LoggedInUserRole']
        else: #nije admin/predsjedavajuci
            messages.error(request,"Nemaš prava za ovu stranicu!")
            return redirect('/')
    
    sudionici_svi = models.Korisnik.objects.filter(vrstaKorisnik_id=4).count()
    sudionici_aktivni = models.Korisnik.objects.filter(vrstaKorisnik_id=4).filter(activeBool=True).count()
    sudionici_neaktivni = models.Korisnik.objects.filter(vrstaKorisnik_id=4).filter(activeBool=False).count()

    recenzenti_svi = models.Korisnik.objects.filter(vrstaKorisnik_id=3).filter(potvrdenBool=True).count()
    recenzenti_aktivni = models.Korisnik.objects.filter(vrstaKorisnik_id=3).filter(potvrdenBool=True).filter(activeBool=True).count()
    recenzenti_neaktivni = models.Korisnik.objects.filter(vrstaKorisnik_id=3).filter(potvrdenBool=True).filter(activeBool=False).count()

    radovi = models.Rad.objects.all().count()
    prijavljeni_radovi =  models.Rad.objects.filter(pdf__isnull=True).count()
    predani_radovi =  models.Rad.objects.filter(pdf__isnull=False).count()
    recenzirani_radovi = models.Recenzija.objects.order_by().values_list('rad').distinct().count()

    autori = models.Autor.objects.order_by().values_list('email').distinct().count()
    recenzije = models.Recenzija.objects.all().count()

    ustanove = models.Ustanova.objects.order_by().values_list('naziv').distinct().count()
    sve_ustanove = models.Ustanova.objects.all().count()

    sekcije = models.Sekcija.objects.all()
    sve_sekcije = models.Sekcija.objects.all().count()
    radovi_po_sekcijama={}
    for sekcija in sekcije:
        radovi_po_sekcijama[sekcija.naziv] = models.Rad.objects.filter(radSekcija=sekcija).count()

    korisnici = models.Korisnik.objects.filter(vrstaKorisnik_id__in=[1,2,3,4]).count()
    uloge = models.Uloga.objects.all()
    korisnici_po_ulogama={}
    for uloga in uloge:
        korisnici_po_ulogama[uloga.naziv] = models.Korisnik.objects.filter(vrstaKorisnik=uloga).count()

    module_dir = os.path.dirname(__file__)  # get current directory
    path1 = os.path.join(module_dir, '../static/txt/SveDrzave.txt')
    path2 = os.path.join(module_dir, '../static/txt/SveDrzaveHR.txt')

    file1 = open(path1, "r", encoding='utf-8')
    file2 = open(path2, "r", encoding='utf-8')

    drzaveEng = file1.read().replace("\"","\'")
    drzaveHrv = file2.read().replace("\"","\'")

    drzaveEngList = drzaveEng[1:len(drzaveEng)-2].split("',\n '")
    drzaveHrvList = drzaveHrv[1:len(drzaveHrv)-2].split("',\n '")
    
    context["Drzave"] = drzaveHrvList[1:]

    broj_drzava = len(drzaveHrvList[1:])

    sudionici_po_drzavama = {}
    for jedna_drzava in drzaveHrvList[1:]:
        if models.Korisnik.objects.filter(korisnikUstanova__in=models.Ustanova.objects.filter(drzava=jedna_drzava).values_list("sifUstanova")).count() > 0:
            sudionici_po_drzavama[jedna_drzava] = models.Korisnik.objects.filter(korisnikUstanova__in=models.Ustanova.objects.filter(drzava=jedna_drzava).values_list("sifUstanova")).count()    


    context["sudionici_svi"] = sudionici_svi
    context["sudionici_aktivni"] = sudionici_aktivni
    context["sudionici_neaktivni"] = sudionici_neaktivni
    context["recenzenti_svi"] = recenzenti_svi
    context["recenzenti_aktivni"] = recenzenti_aktivni
    context["recenzenti_neaktivni"] = recenzenti_neaktivni
    context["ustanove"] = ustanove
    context["sve_ustanove"] = sve_ustanove
    context["sekcije"] = sekcije
    context["sve_sekcije"] = sve_sekcije
    context["korisnici"] = korisnici
    context["broj_drzava"] = broj_drzava
    context["radovi"] = radovi
    context["autori"] = autori
    context["recenzije"] = recenzije
    context["prijavljeni_radovi"] = prijavljeni_radovi
    context["predani_radovi"] = predani_radovi
    context["recenzirani_radovi"] = recenzirani_radovi
    context["radovi_po_sekcijama"] = radovi_po_sekcijama
    context["korisnici_po_ulogama"] = korisnici_po_ulogama
    context["sudionici_po_drzavama"] = sudionici_po_drzavama

    return render(request, 'Statistika.html', context)