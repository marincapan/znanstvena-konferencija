from collections import defaultdict
from datetime import date, datetime, tzinfo
from enum import auto
from io import StringIO, BytesIO
from typing import DefaultDict
from django.core.checks.messages import Error
from django.db.models.fields import DateField, DateTimeCheckMixin, NullBooleanField
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
from IzvorniKod.MK2ZK_App.tokens import account_activation_token
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from IzvorniKod.MK2ZK_App.tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth.password_validation import *
import hashlib
import zipfile
import os
import requests
import time
import csv
from datetime import datetime, timezone

def increment_KorisnikID():
  last_korisnik = models.Korisnik.objects.filter(vrstaKorisnik=4).order_by('id').last()
  if not last_korisnik:
    return '0001'
  korisnik_id = last_korisnik.idSudionik
  korisnik_int = int(korisnik_id)
  new_korisnik_int = korisnik_int + 1
  new_korisnik_id =str(new_korisnik_int).zfill(4)
  return new_korisnik_id

def sloziobrazac(request):
    context={}
    if "LoggedInUserId" in request.session:
        korisnik=models.Korisnik.objects.get(id=request.session['LoggedInUserId'])
        korisnik.lastActive=datetime.now()
        korisnik.save()
        context["LoggedInUser"]=korisnik.id
    else: #nismo ulogirani
        return redirect('signin')
    
    if "LoggedInUserRole" in request.session:
        if request.session['LoggedInUserRole'] == "Admin":
            context["LoggedInUserRole"]=request.session['LoggedInUserRole']
        else: #nije admin
            messages.error(request,"Nemate ovlasti za pristup ovoj stranici!")
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
    dobriradovi = 0

    #Shvatio sam da je puno lakse napravit ovo nego stavljat naziv unutar templatea
    for rad in radovi:
        rad.radSekcija_naziv = sekcije.get(sifSekcija=rad.radSekcija_id).naziv
        rad.radKorisnik_prezime = korisnici.get(id=rad.radKorisnik_id).prezime
        if(rad.pdf != ""):
            brojPredanihRadova += 1
        if( rad.recenziranBool == 1 and rad.revizijaBool == 0):
            dobriradovi +=1 
    context={}
    context["javniBool"] = models.Konferencija.objects.get(sifKonferencija=1).javniRadoviBool
    context["brojPredanihRadova"] = brojPredanihRadova
    context["brojDobrihRadova"] = dobriradovi

    fetchedPolja=models.DodatnaPoljaObrasca.objects.filter().all()
    fetchedClanci = models.Clanak.objects.filter().all()

    info = models.Konferencija.objects.get(sifKonferencija = 1).opisKonferencije
    context['info'] = info

    for polje in fetchedPolja:
        print(polje.imePolja)

    
    
    if request.method == "POST":
        if 'nazivKonferencije' in request.POST: #podaci o konferenciji
            konferencija=models.Konferencija.objects.get(sifKonferencija=1)

            konferencija.nazivKonferencije = request.POST["nazivKonferencije"]
            konferencija.opisKonferencije = request.POST["opisKonferencije"]
            konferencija.datumKonferencije = datetime.strptime(request.POST["datumKonferencije"], "%Y-%m-%d").date()
            konferencija.rokPocPrijava = datetime.strptime(request.POST["pocetakPrijavaKonferencije"], "%Y-%m-%d").date()
            konferencija.rokPrijave = datetime.strptime(request.POST["rokPrijava"], "%Y-%m-%d").date()
            konferencija.rokPocRecenzija = datetime.strptime(request.POST["pocetakRecenzija"], "%Y-%m-%d").date()
            konferencija.rokRecenzenti = datetime.strptime(request.POST["rokRecenzija"], "%Y-%m-%d").date()
            konferencija.rokAdmin = datetime.strptime(request.POST["rokIzmjena"], "%Y-%m-%d").date()
            konferencija.save()

            messages.success(request, "Podaci o konferenciji su uspješno ažurirani!")
            return redirect('/adminsucelje#podatciOKonferenciji')
      
        if 'username' in request.POST: #podaci o predsjedavajucem
            predsjedavajuci = models.Korisnik.objects.get(id = 4) #HARDKODIRAN PREDSJEDAVAJUCI ID
            username = request.POST["username"]
            ime = request.POST["ime"]
            prezime = request.POST["prezime"]
            email = request.POST["email"]

            #Provjeri jesu li sva polja u redu prije spremanja u bazu
            #username - pogledaj postoji li netko s istim usernameom, a da nije trenutni predsjedavajuci
            if models.Korisnik.objects.filter(korisnickoIme = username).exclude(id = 4).exists(): #HARDKODIRAN PREDSJEDAVAJUCI ID
                messages.error(request, "Korisničko ime je zauzeto")
                return redirect('adminsucelje')
            
            #email - pogledaj postoji li netko s istim emailom, a da nije trenutni predsjedavajuci
            if models.Korisnik.objects.filter(email = email).exclude(id = 4).exists(): #HARDKODIRAN PREDSJEDAVAJUCI ID
                messages.error(request, "E-mail adresa je zauzeta")
                return redirect('adminsucelje')

            #ako smo prosli gornje provjere onda je sve ok, idemo dalje (VALIDACIJA UNOSA?)
            predsjedavajuci.korisnickoIme = username
            predsjedavajuci.ime = ime
            predsjedavajuci.prezime = prezime
            trenutniemail = predsjedavajuci.email
            if (trenutniemail != email): #promjena maila, šalji nove podatke na mail, inače samo mijenja ime/prezime/korisnickoime sadašnjeg predsjedavajuceg

                predsjedavajuci.email = email

                #Generiraj password za korisnika
                randPassword=get_random_string(length=16)
                salt=os.urandom(32)
                key=hashlib.pbkdf2_hmac(
                'sha256',
                randPassword.encode('utf-8'),
                salt,
                100000
                )
                predsjedavajuci.salt = salt
                predsjedavajuci.lozinka = key

                try:
                    predsjedavajuci.potvrdenBool = False #novi predsjedavajuci
                    predsjedavajuci.save()
                 #email
                    poruka = render_to_string('PredsjedavajuciEmail.html', {
                'user': predsjedavajuci,
                'lozinka': randPassword,
                'domain': '127.0.0.1:8000',
                'uid':urlsafe_base64_encode(force_bytes(predsjedavajuci.id)),
                'token':account_activation_token.make_token(predsjedavajuci),
                'protocol':'http'
                    })
                    to_email = email
                    email = EmailMessage(
                '[ZK] Podatci za prijavu u sustav', poruka, 'Pametna ekipa', to=[to_email]
                )
                    email.send()
                
                    messages.success(request, "Podaci o predsjedavajućem uspješno promijenjeni. Predsjedavajućem su na adresu e-pošte poslani podaci za prijavu.")
                    return redirect('/adminsucelje')
                except:
                    messages.error(request,"Dogodila se pogreška. Pokušajte ponovno.")
                    return redirect('/adminsucelje')
                    



            predsjedavajuci.save()
            messages.success(request, "Podaci o predsjedavajućem uspješno promijenjeni")
            return redirect('/adminsucelje#upravljanjePredsjedavajućem')
            
        if "makePublic" in request.POST:
            konferencija=models.Konferencija.objects.get(sifKonferencija=1)
            if konferencija.javniRadoviBool==True:
                konferencija.javniRadoviBool=False
                konferencija.save()
            else:
                konferencija.javniRadoviBool=True
                konferencija.save()
            print(konferencija.javniRadoviBool)

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
            return redirect('/adminsucelje#upravljanjeObrascem')
        if 'ActiveFields' in request.POST:

            for polje in fetchedPolja:
                try:
                    checked = request.POST[polje.imePolja]
                    try:
                        checked = True 
                        obavezan = request.POST[polje.imePolja+"1"]
                        obavezan = True
                    except:
                        obavezan = False
                except:
                    #ako polje nije u obrascu ne može biti obavezno, mozda neki error message ako tako označi korisnik
                    checked = False
                    obavezan = False
                polje.active = checked
                polje.obavezan = obavezan
                polje.save()
            return redirect('/adminsucelje#aktivnaPolja')

        if 'AddNewSection' in request.POST:
           
            SectionName = request.POST["SectionName"]
           
            konferencija=models.Konferencija.objects.filter().first() 
            if (not konferencija):
                konferencija = models.Konferencija() #ako još nemamo podataka za konferenciju

            if not models.Sekcija.objects.filter(naziv = SectionName).exists():
                newSection=models.Sekcija(naziv = SectionName, konferencijaSekcija=konferencija)
                newSection.save()
            return redirect("/adminsucelje#upravljanjeSekcijama")

        if 'AddNewAdmin' in request.POST:

            AdminName = request.POST['adminime']
            AdminSurname = request.POST['adminprezime']
            AdminUsername = request.POST['adminusername']
            AdminEmail = request.POST['adminemail']
            #idKorisnika = increment_KorisnikID()
            #AdminPassword = request.POST['adminpassword']
            
            
            #Provjeri jesu li sva polja u redu prije spremanja u bazu
            #username - pogledaj postoji li netko s istim usernameom
            if models.Korisnik.objects.filter(korisnickoIme = AdminUsername).exists():
                messages.error(request, "Korisničko ime je zauzeto")
                return redirect('adminsucelje')
            
            #email - pogledaj postoji li netko s istim emailom
            if models.Korisnik.objects.filter(email = AdminEmail).exists():
                messages.error(request, "E-mail adresa je zauzeta")
                return redirect('adminsucelje')

            #Generiraj password za korisnika
            randPassword=get_random_string(length=16)
            salt=os.urandom(32)
            key=hashlib.pbkdf2_hmac(
                'sha256',
                randPassword.encode('utf-8'),
                salt,
                100000
            )

            #Probaj spremiti novog korisnika
            try:
                NoviKorisnik = models.Korisnik(korisnickoIme=AdminUsername,lozinka=key, salt = salt, ime=AdminName,prezime=AdminSurname,email=AdminEmail,vrstaKorisnik=models.Uloga.objects.get(id=1))
                NoviKorisnik.save()
            except IntegrityError:
                messages.error(request, "Korisničko ime ili email je vec u uporabi.")
                return redirect('/adminsucelje#upravljanjeAdministratorima')

            
            #email
            poruka = render_to_string('AdministratorEmail.html', {
                'user': NoviKorisnik,
                'lozinka': randPassword,
                'domain': '127.0.0.1:8000',
                'uid':urlsafe_base64_encode(force_bytes(NoviKorisnik.id)),
                'token':account_activation_token.make_token(NoviKorisnik),
                'protocol':'http'
                    })
            to_email = AdminEmail
            email = EmailMessage(
            '[ZK] Tvoj administratorski račun je stvoren!', poruka, 'Pametna ekipa', to=[to_email]
            )
            email.send()
            
            messages.success(request, "Novi administrator je uspješno dodan.\n Na adresu pošte poslan je aktivacijski link i podaci za prijavu.")
            return redirect('/adminsucelje')

            

        ### Dodavanje novog članka
        if "AddArticle" in request.POST:
            ArticleTitle = request.POST['clanakTitle']
            ArticleText = request.POST['clanakText']

            if models.Clanak.objects.filter(naslov = ArticleTitle).exists():
                messages.error(request, "Već postoji članak s ovim naslovom")
                return redirect('adminsucelje')

            newArticle = models.Clanak(naslov=ArticleTitle, tekst=ArticleText, autor=models.Korisnik.objects.get(id = request.session['LoggedInUserId']))
            newArticle.save()
            context['Clanci'] = fetchedClanci
            messages.success(request, "Uspješno dodan novi članak")
            return redirect('/adminsucelje#uređivanjeNaslovne')

        ## Odabir aktivnih članaka
        if "ActiveArticles" in request.POST:
            for clanak in fetchedClanci:
                try:
                    checked = request.POST[clanak.naslov]
                    checked = True
                except:
                    checked = False
                clanak.active = checked
                clanak.save()
            return redirect('/adminsucelje#prikazaniČlanci')
                
        context['DodatnaPolja']=fetchedPolja
        context['Clanci'] = fetchedClanci
             
        return redirect('adminsucelje')


    context['DodatnaPolja']=fetchedPolja
    context['Clanci'] = fetchedClanci
    
    if "LoggedInUserId" in request.session:
        korisnik=models.Korisnik.objects.get(id=request.session['LoggedInUserId'])
        korisnik.lastActive=datetime.now()
        korisnik.save()
        context["LoggedInUser"]=korisnik.id
    else: #nismo ulogirani
        return redirect('signin')

    fetchedSekcije=models.Sekcija.objects.filter().all()
    if (fetchedSekcije.first()):
        context['sekcije'] = fetchedSekcije
    
    if "LoggedInUserRole" in request.session:
        if request.session['LoggedInUserRole'] == "Admin":
            context["LoggedInUserRole"]=request.session['LoggedInUserRole']
            Predsjedavajuci=models.Korisnik.objects.filter(id=4).first()
            Administratori = models.Korisnik.objects.filter(vrstaKorisnik_id = 1, potvrdenBool = True) #znamo da je bar 1
            context["AdministratoriPopis"] = Administratori
            
            print(context)
            if (Predsjedavajuci):
                context['korisnickoIme']=Predsjedavajuci.korisnickoIme
                context['ime']=Predsjedavajuci.ime
                context['prezime']=Predsjedavajuci.prezime
                context['email']=Predsjedavajuci.email
                context['uloga']=Predsjedavajuci.vrstaKorisnik.naziv
                context['sekcija']=Predsjedavajuci.korisnikSekcija.naziv
        else: #nije admin
            messages.error(request,"Nemate ovlasti za pristup ovoj stranici!")
            return redirect('/') #redirect na homepage

    recenzenti = models.Korisnik.objects.filter(vrstaKorisnik_id=3)
    sudionici = models.Korisnik.objects.filter(vrstaKorisnik_id=4)
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

    #konferencija je u bazi
    konferencija=models.Konferencija.objects.first()
    if konferencija:
        context['konferencijaNaziv']=konferencija.nazivKonferencije
        context['opis']=konferencija.opisKonferencije
        context['datum'] = dateformat.format(konferencija.datumKonferencije, formats.get_format('Y-m-d'))
        context['rokPrijave']= dateformat.format(konferencija.rokPrijave, formats.get_format('Y-m-d'))
        context['rokRecenzenti']=dateformat.format(konferencija.rokRecenzenti, formats.get_format('Y-m-d'))
        context['rokAdmin']=dateformat.format(konferencija.rokAdmin, formats.get_format('Y-m-d'))
        context['rokPocRecenzija']=dateformat.format(konferencija.rokPocRecenzija, formats.get_format('Y-m-d'))
        context['rokPocPrijava']=dateformat.format(konferencija.rokPocPrijava, formats.get_format('Y-m-d'))

    context["Radovi"] = radovi
    context["brojPredanihRadova"] = brojPredanihRadova
    if "jumpto" in request.session:
        context["jumpto"]=request.session["jumpto"]

    return render(request, 'AdminSucelje.html', context)

def covidstats(request):
    context = {}

    if "LoggedInUserId" in request.session:
        korisnik=models.Korisnik.objects.get(id=request.session['LoggedInUserId'])
        korisnik.lastActive=datetime.now()
        korisnik.save()
        context["LoggedInUser"]=korisnik.id
    else: #nismo ulogirani
        return redirect('signin')
    
    if "LoggedInUserRole" in request.session:
        if request.session['LoggedInUserRole'] == "Admin" or request.session['LoggedInUserRole'] == "Predsjedavajuci" :
            context["LoggedInUserRole"]=request.session['LoggedInUserRole']
        else: #nije admin
            messages.error(request,"Nemate ovlasti za pristup ovoj stranici!")
            return redirect('/') #redirect na homepage

            
    url = "https://covid19.who.int/WHO-COVID-19-global-data.csv"
    response = requests.get(url)
    bytes=response.content
    data=bytes.decode('UTF-8')
    data=data.split("\n")
    fetchUstanove = models.Ustanova.objects.all()

    module_dir = os.path.dirname(__file__)  # get current directory
    path1 = os.path.join(module_dir, '../static/txt/SveDrzave.txt')
    path2 = os.path.join(module_dir, '../static/txt/SveDrzaveHR.txt')

    file1 = open(path1, "r", encoding='utf-8')
    file2 = open(path2, "r", encoding='utf-8')

    drzaveEng = file1.read().replace("\"","\'")
    drzaveHrv = file2.read().replace("\"","\'")

    drzaveEngList = drzaveEng[1:len(drzaveEng)-2].split("',\n '")
    drzaveHrvList = drzaveHrv[1:len(drzaveHrv)-2].split("',\n '")

    konfDrzave={}
    for row in data:
        date=row.split(",") #0 - Date_reported,1 - Country_code,2 - Country,3 - WHO_region,4 - New_cases,5 - Cumulative_cases,6 - New_deaths, 7- Cumulative_deaths
        for ustanova in fetchUstanove:
            if ustanova.drzava in drzaveHrvList:
                indexHRV=drzaveHrvList.index(ustanova.drzava)
                drzavaENG=drzaveEngList[indexHRV]
                if drzavaENG in date:
                    if date[0]!="": #Kraj
                        datum =  datetime.strptime(date[0], '%Y-%m-%d').date()
                        konfDrzave[str(ustanova.drzava)]=[dateformat.format(datum, formats.get_format('d.m.Y.')),date[4]]
                        print(date) # Rijecnik s drzavom (Na engleskom zasad) i vrijednostima koje zelim prenijeti (zasad datum dohavacanja podataka i novih slucajeva)
    context["konfDrzave"]=konfDrzave
    print(context)    
    return render(request, 'CovidStats.html', context)

def uredipodatke(request, korisnickoime):
    korisnik = models.Korisnik.objects.filter(korisnickoIme = korisnickoime).first()
    
    if korisnik:
        uloga = korisnik.vrstaKorisnik.naziv

        if request.method == "POST":
            username = request.POST["username"]
            ime = request.POST["ime"]
            prezime = request.POST["prezime"]
            email = request.POST["email"]
            maticnaUstanova = request.POST["ustanova"]

            #Provjeri jesu li sva polja u redu prije spremanja u bazu
            #username - pogledaj postoji li netko s istim usernameom, a da nije trenutni korisnik
            if models.Korisnik.objects.filter(korisnickoIme = username).exclude(id = korisnik.id).exists():
                messages.error(request, "Korisničko ime je zauzeto")
                
                if (uloga == "Sudionik"):
                    return redirect('pregled/sudionici/'+username)
                if (uloga == "Recenzent"):
                    return redirect('pregled/recenzneti/'+username)
        
            #email - pogledaj postoji li netko s istim emailom, a da nije trenutni korisnik
            if models.Korisnik.objects.filter(email = email).exclude(id = korisnik.id).exists():
                messages.error(request, "E-mail adresa je zauzeta")
                
                if (uloga == "Sudionik"):
                    return redirect('pregled/sudionici/'+username)
                if (uloga == "Recenzent"):
                    return redirect('pregled/recenzneti/'+username)
            
            i = 1

            provjera = models.DodatnaPoljaObrasca.objects.first()
            if (provjera): #ima dodatnih polja u obrascu
                dodatno = models.DodatnaPoljaObrasca.objects.all()
                print(len(dodatno))
            
                for polje in dodatno:
                        dodatno = models.DodatniPodatci.objects.filter(korisnik = korisnik, poljeObrasca = polje).first()
                        
                        if dodatno:
                            print(dodatno.podatak)
                            novo = request.POST["dodatni"+str(i)]
                            #validacija unosa?

                            i = i + 1
                            print(novo)
                            dodatno.podatak = novo
                            dodatno.save()

            #ako smo prosli gornje provjere onda je sve ok, idemo dalje (VALIDACIJA UNOSA?)
            korisnik.korisnickoIme = username
            korisnik.ime = ime
            korisnik.prezime = prezime
            korisnik.email = email
        
            #ustanova (ako je isti naziv kao i do sad, nema smisla updateati)
            if maticnaUstanova != korisnik.korisnikUstanova.naziv:
                if models.Ustanova.objects.filter(naziv = maticnaUstanova, grad = korisnik.korisnikUstanova.grad, drzava = korisnik.korisnikUstanova.drzava, adresa = korisnik.korisnikUstanova.adresa).exists():
                    novaUstanova = models.Ustanova.objects.get(naziv = maticnaUstanova, grad = korisnik.korisnikUstanova.grad, drzava = korisnik.korisnikUstanova.drzava, adresa = korisnik.korisnikUstanova.adresa)
                else:
                    #print("Tu sam 1")
                    novaUstanova = models.Ustanova(
                    naziv = maticnaUstanova,
                    grad = korisnik.korisnikUstanova.grad,
                    drzava = korisnik.korisnikUstanova.drzava,
                    adresa = korisnik.korisnikUstanova.adresa
                )
                    novaUstanova.save()
                
                korisnik.korisnikUstanova = novaUstanova

            korisnik.save()
            messages.success(request, "Podaci uspješno promijenjeni.")
            uloga = korisnik.vrstaKorisnik.naziv
            if (uloga == "Sudionik"):
                url = "/pregled/sudionici/"+username
              
                return redirect(url)
            if (uloga == "Recenzent"):
                url = "/pregled/recenzenti/"+username
                print(url)
                return redirect(url)
            else:
        
                messages.info(request, "Ne radi se o sudioniku/recenzentu.") #do ovoga ne bi smjelo ni doći
                return redirect('pregled')



        if "LoggedInUserId" in request.session:
            User=models.Korisnik.objects.get(id=request.session['LoggedInUserId'])
            User.lastActive=datetime.now()
            User.save()
            context={}
            context["LoggedInUser"]=korisnik.id
            korisnik2=models.Korisnik.objects.get(id=request.session["LoggedInUserId"]) #mora biti ili admin ili predsjedavajuci
            uloga = korisnik2.vrstaKorisnik.naziv
            
            if (uloga == 'Admin' or uloga == 'Predsjedavajuci'):

                
                context['LoggedInUser']=request.session['LoggedInUserId']
                context['LoggedInUserRole']=request.session['LoggedInUserRole']

                context['korisnickoIme']=korisnik.korisnickoIme
                context['ime']=korisnik.ime
                context['prezime']=korisnik.prezime
                context['email']=korisnik.email
                context['uloga']=korisnik.vrstaKorisnik.naziv
                if not korisnik.korisnikUstanova==None:
                    context['MaticnaUstanova']=korisnik.korisnikUstanova.naziv
                if not korisnik.korisnikSekcija==None:
                    context['sekcija']=korisnik.korisnikSekcija.naziv
       
                if (context['uloga']=='Sudionik' or context['uloga']=='Recenzent'):
                    dodatnipodatci = {}
                    provjera = models.DodatnaPoljaObrasca.objects.first()
                    if (provjera): #ima dodatnih polja u obrascu
                        dodatno = models.DodatnaPoljaObrasca.objects.all()
                        for polje in dodatno:
                            dodatno = models.DodatniPodatci.objects.filter(korisnik = korisnik, poljeObrasca = polje).first()
                    
                            if dodatno:
                                podatak = dodatno.podatak
                            #print(dodatno.podatak)
                                if (dodatno.poljeObrasca.tipPolja.naziv == "date"):
                                #želimo naš format datuma
                                #print("tu")

                                    try:
                                        date_object = datetime.strptime(dodatno.podatak, '%Y-%m-%d').date() #validacija datuma?
                                        podatak = dateformat.format(date_object, formats.get_format('d.m.Y.'))
                                    except:
                                        podatak = dodatno.podatak
                                ime = dodatno.poljeObrasca.imePolja
                                dodatnipodatci[ime] = podatak
                  

                    context['dodatnipodatci'] = dodatnipodatci
                #print(dodatnipodatci)


                if context['uloga']=='Sudionik':
                    context['SudionikID']=korisnik.idSudionik
                    radovi = models.Rad.objects.filter(radKorisnik = korisnik)
                    sekcije = [i.radSekcija for i in radovi]
                    sekcije = list(dict.fromkeys(sekcije)) #po 1 pojavljivanje svake sekcije
                    context['sekcije'] = sekcije
            
            else:
                messages.info(request, "Nemate ovlasti za pristup ovoj stranici!")
                return redirect('home')

            
        
        else:
            messages.info(request, "Trebate biti prijavljeni kako biste pristupili toj stranici.")
            return redirect('signin')

    else:
        messages.info(request, "Taj korisnik ne postoji u sustavu.") #do ovoga ne bi smjelo ni doći
        return redirect('pregled')
    
    return render(request, 'UrediPodatke.html',context)

def uredirad(request, sifrada):
    context = {}
    rad = models.Rad.objects.filter(sifRad = sifrada).first()

    if rad:

        if request.method == "POST":
            pass

        if "LoggedInUserId" in request.session:
            User = models.Korisnik.objects.get(id = request.session['LoggedInUserId'])
            User.lastActive = datetime.now()
            User.save()

            context={}
            context["LoggedInUser"] = User.id
            uloga = User.vrstaKorisnik.naziv

            if (uloga == 'Admin' or uloga == 'Predsjedavajuci'): #samo admin i preds imaju pristup uredjivanju
                context['LoggedInUser']=request.session['LoggedInUserId']
                context['LoggedInUserRole']=request.session['LoggedInUserRole']
                context["rad"] = rad

                context["recenzije"] = models.Recenzija.objects.filter(rad = rad.sifRad)

                autori = []
                autorRadQuery = models.AutorRad.objects.filter(Rad = rad.sifRad)
                for autorRad in autorRadQuery:
                    autori.append(autorRad.Autor)
                context["autori"] = autori


            else: #samo admin i preds imaju pristup uredjivanju
                messages.info(request, "Nemate ovlasti za pristup ovoj stranici!")
                return redirect('home')

        else: #potreban login za pristup
            messages.info(request, "Trebate biti prijavljeni kako biste pristupili ovoj stranici.")
            return redirect("signin")
            
    else:
        messages.info(request, "Taj rad ne postoji u sustavu.")
        return redirect("pregled")

    return render(request, "UrediRad.html", context)