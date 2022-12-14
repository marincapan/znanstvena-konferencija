from collections import defaultdict
from datetime import date, datetime
from io import StringIO, BytesIO
from typing import DefaultDict
from django.core.checks.messages import Error
from django.core.mail.message import EmailMessage
from django.db.models.fields import DateTimeCheckMixin, NullBooleanField
from django.db.models.query import EmptyQuerySet
from django.db.models.expressions import RawSQL
from django.http.response import FileResponse, HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from IzvorniKod.MK2ZK_App import models
from django.db import IntegrityError 
from django.core import serializers
from django.utils import (dateformat, formats)
import zipfile
import os

def mojerecenzije(request):
    context={}
    if "LoggedInUserId" in request.session:
        korisnik=models.Korisnik.objects.get(id=request.session['LoggedInUserId'])
        korisnik.lastActive=datetime.now()
        korisnik.save()
        context["LoggedInUser"]=korisnik.id
        context['LoggedInUserRole']=request.session['LoggedInUserRole']

    else: #nismo ulogirani
        return redirect('signin')
    
    LoggedInUser=models.Korisnik.objects.get(id=request.session['LoggedInUserId'])
    if LoggedInUser.vrstaKorisnik_id==3 and LoggedInUser.odobrenBool==None:
        messages.error(request,"Još nisi odobren kao recenzent!")
        return redirect('home')
    elif LoggedInUser.vrstaKorisnik_id==3 and LoggedInUser.odobrenBool==False:
        messages.error(request,"Vaš zahtjev recenzenstvom je odbijen. Ne možete recenzirati radove.")
        return redirect('home')
    elif LoggedInUser.vrstaKorisnik_id > 3: #1-admin 2-predsjedavajuci 3-recenzent 4-sudionik
        messages.error(request,"Nemate ovlasti za pristup ovoj stranici!")
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
        if (ocjena == 3): #id ocjene
            rad.revizijaBool = True
        else:
            rad.revizijaBool = False

        rad.save()
        novaRecenzija.save()
        poruka = render_to_string('RecenziranEmail.html', {
            'user': rad.radKorisnik,
            'rad': rad,
            'domain': os.getenv("DOMAIN"),
            'protocol':os.getenv("PROTOCOL"),
            'recenzija':novaRecenzija
            })
        to_email = rad.radKorisnik.email
        email = EmailMessage(
           '[ZK] Vaš rad je ocjenjen!', poruka, 'Pametna ekipa', to=[to_email]
        )
        email.send()

        findOzk=models.AutorRad.objects.filter(Rad=rad)
        for autor in findOzk:
            if autor.OZK==True:
                if not autor.Autor.email==rad.radKorisnik.email:
                    poruka = render_to_string('RecenziranEmail.html', {
                        'user': autor,
                        'rad': rad,
                        'domain': os.getenv("DOMAIN"),
                        'protocol': os.getenv("PROTOCOL"),
                        'recenzija':novaRecenzija
                        })
                    to_email = autor.Autor.email
                    email = EmailMessage(
                    '[ZK] Vaš rad je ocjenjen!', poruka, 'Pametna ekipa', to=[to_email]
                    )
                    email.send()

        return redirect('mojerecenzije')
    #radovi koji nemaju predan pdf se ne recenziraju, a također nas ne zanimaju radovi koji su recenzirani no ne trebaju reviziju (oni su tako i tako u recenzijama)
    fetchRadovi = models.Rad.objects.filter(radSekcija=LoggedInUser.korisnikSekcija).exclude(pdf="").exclude(recenziranBool = True, revizijaBool = False)
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
    context["prosoDatum"]=date.today()>=models.Konferencija.objects.get(sifKonferencija=1).rokRecenzenti
    context["poceoDatum"]=date.today()>=models.Konferencija.objects.get(sifKonferencija=1).rokPocRecenzija
    
    return render(request, 'MojeRecenzije.html', context)
