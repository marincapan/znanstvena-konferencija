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
from datetime import datetime
import zipfile
import os
from datetime import date

def osobnipodaci(request):
    if request.method == "POST":
        LoggedInUser=models.Korisnik.objects.get(id=request.session['LoggedInUserId'])
        username = request.POST["username"]
        ime = request.POST["ime"]
        prezime = request.POST["prezime"]
        email = request.POST["email"]
        maticnaUstanova = request.POST["ustanova"]
        


        #Provjeri jesu li sva polja u redu prije spremanja u bazu
        #username - pogledaj postoji li netko s istim usernameom, a da nije trenutni korisnik
        if models.Korisnik.objects.filter(korisnickoIme = username).exclude(id = LoggedInUser.id).exists():
            messages.error(request, "Korisničko ime je zauzeto")
            return redirect('osobnipodaci')
        
        #email - pogledaj postoji li netko s istim emailom, a da nije trenutni korisnik
        if models.Korisnik.objects.filter(email = email).exclude(id = LoggedInUser.id).exists():
            messages.error(request, "E-mail adresa je zauzeta")
            return redirect('osobnipodaci')
        i = 1

        provjera = models.DodatnaPoljaObrasca.objects.first()
        if (provjera): #ima dodatnih polja u obrascu
            dodatno = models.DodatnaPoljaObrasca.objects.all()
            print(len(dodatno))
            
            for polje in dodatno:
                    dodatno = models.DodatniPodatci.objects.filter(korisnik = LoggedInUser, poljeObrasca = polje).first()
                    
                    if dodatno:
                        print(dodatno.podatak)
                        novo = request.POST["dodatni"+str(i)]
                        #validacija unosa?

                        i = i + 1
                        print(novo)
                        dodatno.podatak = novo
                        dodatno.save()

        #ako smo prosli gornje provjere onda je sve ok, idemo dalje (VALIDACIJA UNOSA?)
        LoggedInUser.korisnickoIme = username
        LoggedInUser.ime = ime
        LoggedInUser.prezime = prezime
        LoggedInUser.email = email
        
        #ustanova (ako je isti naziv kao i do sad, nema smisla updateati)
        if maticnaUstanova != LoggedInUser.korisnikUstanova.naziv:
            if models.Ustanova.objects.filter(naziv = maticnaUstanova, grad = LoggedInUser.korisnikUstanova.grad, drzava = LoggedInUser.korisnikUstanova.drzava, adresa = LoggedInUser.korisnikUstanova.adresa).exists():
                novaUstanova = models.Ustanova.objects.get(naziv = maticnaUstanova, grad = LoggedInUser.korisnikUstanova.grad, drzava = LoggedInUser.korisnikUstanova.drzava, adresa = LoggedInUser.korisnikUstanova.adresa)
            else:
                print("Tu sam 1")
                novaUstanova = models.Ustanova(
                    naziv = maticnaUstanova,
                    grad = LoggedInUser.korisnikUstanova.grad,
                    drzava = LoggedInUser.korisnikUstanova.drzava,
                    adresa = LoggedInUser.korisnikUstanova.adresa
                )
                novaUstanova.save()
                
            LoggedInUser.korisnikUstanova = novaUstanova

        LoggedInUser.save()
        messages.success(request, "Podaci uspješno promijenjeni")
        return redirect('osobnipodaci')

    if "LoggedInUserId" in request.session:
        korisnik=models.Korisnik.objects.get(id=request.session['LoggedInUserId'])
        korisnik.lastActive=datetime.now()
        korisnik.save()
        context={}
        context["LoggedInUser"]=korisnik.id #ulogirani smo
        LoggedInUser=models.Korisnik.objects.get(id=request.session['LoggedInUserId'])
        context['LoggedInUser']=request.session['LoggedInUserId']
        context['LoggedInUserRole']=request.session['LoggedInUserRole']
        context['korisnickoIme']=LoggedInUser.korisnickoIme
        context['ime']=LoggedInUser.ime
        context['prezime']=LoggedInUser.prezime
        context['email']=LoggedInUser.email
        context['uloga']=LoggedInUser.vrstaKorisnik.naziv
        if LoggedInUser.korisnikUstanova:
            context['MaticnaUstanova']=LoggedInUser.korisnikUstanova.naziv
        if LoggedInUser.korisnikSekcija:
            context['sekcija']=LoggedInUser.korisnikSekcija.naziv
       
        if (context['LoggedInUserRole']=='Sudionik' or context['LoggedInUserRole']=='Recenzent'):
            dodatnipodatci = {}
            provjera = models.DodatnaPoljaObrasca.objects.first()
            if (provjera): #ima dodatnih polja u obrascu
                dodatno = models.DodatnaPoljaObrasca.objects.all()
                for polje in dodatno:
                    dodatno = models.DodatniPodatci.objects.filter(korisnik = LoggedInUser, poljeObrasca = polje).first()
                    
                    if dodatno:
                        podatak = dodatno.podatak
                        print(dodatno.podatak)
                        if (dodatno.poljeObrasca.tipPolja.naziv == "date"):
                            #želimo naš format datuma
                            #print("tu")
                            try:
                                date_object = datetime.strptime(dodatno.podatak, '%Y-%m-%d').date() #tako su spremljeni pri registraciji kasnije je vjerojatno drugi format pa nek ispisuje taj
                                podatak = dateformat.format(date_object, formats.get_format('d.m.Y.'))
                            except:
                                podatak = dodatno.podatak
                        ime = dodatno.poljeObrasca.imePolja
                        dodatnipodatci[ime] = podatak
                  

            context['dodatnipodatci'] = dodatnipodatci
            print(dodatnipodatci)


        if context['LoggedInUserRole']=='Sudionik':
            context['SudionikID']=LoggedInUser.idSudionik
            radovi = models.Rad.objects.filter(radKorisnik = LoggedInUser)
            sekcije = [i.radSekcija for i in radovi]
            sekcije = list(dict.fromkeys(sekcije)) #po 1 pojavljivanje svake sekcije
            context['sekcije'] = sekcije
            
        
    else:
        messages.info(request, "Trebate biti prijavljeni kako biste pristupili toj stranici.")
        return redirect('signin')
    
    return render(request, 'OsobniPodaci.html',context)

def mojiradovi(request):
    context={}
    if "LoggedInUserId" in request.session:
        korisnik=models.Korisnik.objects.get(id=request.session['LoggedInUserId'])
        korisnik.lastActive=datetime.now()
        korisnik.save()
        context["LoggedInUser"]=korisnik.id
    else: #nismo ulogirani
        return redirect('signin')
    
    if "LoggedInUserRole" in request.session:
        if request.session['LoggedInUserRole'] != "Admin":
            context["LoggedInUserRole"]=request.session['LoggedInUserRole']
        else: #admin je
            return redirect('/') #redirect na homepage
        context["LoggedInUserRole"]=request.session['LoggedInUserRole']

    LoggedInUser=models.Korisnik.objects.get(id=request.session['LoggedInUserId'])

    fetchedRadovi=models.Rad.objects.filter(radKorisnik=LoggedInUser)
    sekcije = models.Sekcija.objects.all()
    
    context['fetchedRadovi']=fetchedRadovi
    context['sekcije']=sekcije

    #Recenzije svih radova koje je uploadao trenutni korisnik
    recenzije = models.Recenzija.objects.filter(rad__radKorisnik=LoggedInUser)

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
    recenzije = recenzije.filter(sifRecenzija__in = (x.sifRecenzija for x in najnovijeRecenzije))

    context['fetchedRecenzije']=recenzije
    print(context)
    for rad in fetchedRadovi:
        context['pdf']=rad.pdf

    """
    Mislim da bi bilo sigurnije da se uz predaju provjerava i naziv rada.
    Mozda cak i da se ovdje (u UploadFile djelu ove obrade?) pazi na mogucnost da je 
    predan NOVI rad dok PRVI rad nema pdf. U toj varijanti se baci error s odgovarajucom porukom.
    Sve potrebne informacije za to postoje, konkretno naziv rada u POST-u (fileTitle) i
    lista radova za trenutnog korisnika (fetchedRadovi).
    -luka
    """
    if request.method == "POST":
        if 'DodajPDFPostojecem' in request.POST:
            uploadedFile = request.FILES["uploadedFile"]
            for rad in fetchedRadovi:
                rad.pdf = uploadedFile
                rad.save()
            return redirect('mojiradovi')
        if 'PonovniUnosPdf' in request.POST:
            fileTitle = request.POST["fileTitle"]
            uploadedFile = request.FILES["uploadedFile"]
            updateRad=models.Rad.objects.get(naslov=fileTitle)
            updateRad.pdf=uploadedFile
            #najnovija recenzija nam treba
            recenzija = models.Recenzija.objects.filter(rad = updateRad).order_by("-sifRecenzija").first()
            print(recenzija.obrazlozenje)
            
            if (recenzija.ocjena.id == 3): #samo tada treba recenzent ponovno recenzirati
                updateRad.revizijaBool=True
            updateRad.save()
            
            return redirect('mojiradovi')
        if 'UploadFile' in request.POST:
            print(request.POST)
            fileTitle = request.POST["fileTitle"]
            uploadedFile = request.FILES["uploadedFile"]
            section = request.POST['section']

            #Kopirano iz signupa
            brojAutora = int(request.POST['brojAutora'])

            #Parsiramo autore
            autori=[]
            for i in range(brojAutora):
                i = str(i) #lol
                autorIme = request.POST['autorFName' + i]
                autorPrezime = request.POST['autorLName' + i]
                autorEmail = request.POST['autorEmail' + i]
                """ #Autori za sad nemaju oznaku OZK because its bwoken
                if "autorKontakt"+i in request.POST:
                    autor["Kontakt"] = True
                """
                autori.append(models.Autor(ime=autorIme,prezime=autorPrezime,email=autorEmail))
                i = int(i)

            #Provjera validnosti autora, provjerava svaki sa svakim i trazi je li email jednak, ako je baca error
            for i in range(brojAutora-1):
                for j in range(i+1, brojAutora):
                    if autori[i].email == autori[j].email: #dva autora imaju isti email
                        messages.error(request, "Autori ne smiju imati istu adresu e-maila")
                        return redirect('mojiradovi')

            #Kopirano iz signupa
            Sekcija=models.Sekcija.objects.get(naziv=section)
            noviRad=models.Rad(
                naslov=fileTitle,
                pdf = uploadedFile,
                radSekcija= Sekcija,
                radKorisnik=LoggedInUser
            )
            if not models.Rad.objects.filter(naslov = fileTitle,radSekcija = Sekcija,radKorisnik = LoggedInUser).exists():
                noviRad.save()
            else:
                messages.error(request, "Rad je ranije predan! Nisu učinjene nikakve promjene.")
                return redirect('mojiradovi')
            print("----------")
            print(fileTitle)
            print(uploadedFile)
            print(LoggedInUser.korisnikSekcija)
            print(LoggedInUser)
            print("----------")
            noviRad=models.Rad.objects.get(naslov = fileTitle,radSekcija = Sekcija,radKorisnik = LoggedInUser)
            
            #
            #Autor moze biti povezan na vise radova i zato ne moze imati atribut OZK jer se ne zna na koji rad se to odnosi
            #

            #Autori se povezuju s radom
            for autor in autori:

                noviAutor = models.Autor(ime=autor.ime,prezime=autor.prezime,email=autor.email)
                if models.Autor.objects.filter(email=autor.email).exists():
                    postojeciAutor = models.Autor.objects.get(email=autor.email)
                    if postojeciAutor.ime != autor.ime or postojeciAutor.prezime != autor.prezime:
                        messages.error(request, "E-mail adresa autora je zauzeta")
                        noviRad.delete()
                        return redirect('mojiradovi')
                #Ako autor vec postoji u bazi, samo ga dodaj na ovaj rad
                if models.Autor.objects.filter(ime=autor.ime,prezime=autor.prezime,email=autor.email).exists():
                    noviAutor = models.Autor.objects.get(ime=autor.ime,prezime=autor.prezime,email=autor.email)
                #Ako autor ne postoji, napravi novog
                else:
                    noviAutor.save()
                    noviAutor = models.Autor.objects.get(ime=autor.ime,prezime=autor.prezime,email=autor.email)
                noviRad.autori.add(noviAutor)

            noviRad.save()
            return redirect('mojiradovi')

    context["prosoDatum"]=date.today()>=models.Konferencija.objects.get(sifKonferencija=1).rokPrijave
    context["poceoDatum"]=date.today()>=models.Konferencija.objects.get(sifKonferencija=1).rokPocPrijava
    return render(request, 'MojiRadovi.html',context)
