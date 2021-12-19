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

def increment_KorisnikID():
  last_korisnik = models.Korisnik.objects.filter(vrstaKorisnik=4).order_by('id').last()
  if not last_korisnik:
    return '0001'
  korisnik_id = last_korisnik.idSudionik
  korisnik_int = int(korisnik_id)
  new_korisnik_int = korisnik_int + 1
  new_korisnik_id =str(new_korisnik_int).zfill(4)
  return new_korisnik_id

def home(request):
    if 'randPassword' in request.session:
        del request.session['randPassword']
    #Password se pokazuje jedanput i vise nikad.

    context={}
    if "LoggedInUserId" in request.session:
        context["LoggedInUser"]=models.Korisnik.objects.get(id=request.session['LoggedInUserId']).id
    
    if "LoggedInUserRole" in request.session:
        context["LoggedInUserRole"]=request.session['LoggedInUserRole']
        if request.session['LoggedInUserRole'] == 'Sudionik':
            context["LoggedInUserCode"]=models.Korisnik.objects.get(id=request.session['LoggedInUserId']).idSudionik
    
    konferencija=models.Konferencija.objects.filter().first()
    
    if (konferencija):
        #da bismo imali naš format imam ovaj rokPrijave1, a JS ne radi dobro s tim formatom pa tamo koristim drugi
        konferencija.rokPrijave1 = dateformat.format(konferencija.rokPrijave, formats.get_format('d.m.Y')) #dodati ovisno što će nam trebati na naslovnici
        konferencija.rokRecenzenti1 = dateformat.format(konferencija.rokRecenzenti, formats.get_format('d.m.Y'))
        context["infoKonferencija"] = konferencija #trebat ce mozda za countdown ili neke druge podatke stavit na naslovnicu
    print(context)
    return render(request, 'Index.html',context)


def signup(request):
    if "LoggedInUserId" in request.session: #otprije smo registrirani
        return redirect('/')
    context={}
    fetchedPolja=models.DodatnaPoljaObrasca.objects.filter().all()
    fetchedSekcije=models.Sekcija.objects.filter().all()
    if (fetchedSekcije.first()): #ako je admin unio sekcije
        context['sekcije'] = fetchedSekcije
    context['DodatnaPolja']=fetchedPolja
    # #!!
    # context['sekcije']=fetchedSekcije.exclude(naziv="Admin Sekcija") #dodao sam ovo kako bih mogao implementirati select za sekcije
    # ##
    print(context)
    if request.method == "POST":        
        username = request.POST['Username']
        fName = request.POST['Fname']
        lName = request.POST['Lname']
        email = request.POST['email']
        matustName = request.POST['matustName']
        matustAdr = request.POST['matustAdr']
        matustCity = request.POST['matustCity']
        matustDrz = request.POST['matustDrz']
        uloga = request.POST['uloga']
        section = request.POST['section']

        #Ove ifove treba optimizirati!
        #Ako obradjujemo sudionika, imamo dodatne podatke i treba napraviti odredjene provjere
        if(uloga == "Sudionik"):
            title = request.POST['title']
            brojAutora = int(request.POST['brojAutora'])
            idSudionik=increment_KorisnikID()

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
                        return redirect('signup')

            #Nije pretjerano optimalno, but it gets the job done
            for autor in autori:
                if models.Autor.objects.filter(email=autor.email).exists():
                    postojeciAutor = models.Autor.objects.get(email=autor.email)
                    if postojeciAutor.ime != autor.ime or postojeciAutor.prezime != autor.prezime:
                        messages.error(request, "E-mail adresa autora je zauzeta")
                        return redirect('signup')

            #Ako ustanova ne postoji spremi ju, inace dohvati postojecu
            Ustanova = Ustanova = models.Ustanova(naziv=matustName,adresa=matustAdr,grad=matustCity,drzava=matustDrz)
            if models.Ustanova.objects.filter(naziv=matustName,adresa=matustAdr,grad=matustCity,drzava=matustDrz).exists():
                Ustanova = models.Ustanova.objects.get(naziv=matustName,adresa=matustAdr,grad=matustCity,drzava=matustDrz)
            else:
                Ustanova.save()

            #Ako sekcija ne postoji spremi ju, inace dohvati postojecu (nepotrebno jer se za sad ne mogu dodavati nove sekcije)
            Sekcija = models.Sekcija(naziv=section,konferencijaSekcija=models.Sekcija.objects.get(naziv=section).konferencijaSekcija)
            if  models.Sekcija.objects.filter(naziv=section).exists():
                Sekcija=models.Sekcija.objects.get(naziv=section)
            else:
                Sekcija.save()

            #Generiraj password za korisnika
            randPassword=get_random_string(length=16)
            request.session['randPassword'] = randPassword

            #Probaj spremiti novog korisnika
            try:
                NoviKorisnik = models.Korisnik(korisnickoIme=username,lozinka=randPassword,idSudionik=idSudionik,ime=fName,prezime=lName,email=email,vrstaKorisnik=models.Uloga.objects.get(naziv=uloga), korisnikUstanova=Ustanova, korisnikSekcija=Sekcija)
                NoviKorisnik.save()
            except IntegrityError:
                messages.error(request, "Korisnicko ime ili email je vec u uporabi")
                return redirect('signup')

            #Provjeri je li rad ranije prijavljen
            noviRad=models.Rad(
                naslov=title,
                radSekcija=Sekcija,
                radKorisnik=NoviKorisnik
            )
            if not models.Rad.objects.filter(naslov=title, radSekcija=Sekcija, radKorisnik=NoviKorisnik).exists():
                noviRad.save()
            else:
                messages.error(request, "Rad s tim naslovom na toj sekciji već postoji")
                return redirect('signup')

            noviRad=models.Rad.objects.get(naslov=title, radSekcija=Sekcija,radKorisnik=NoviKorisnik)
            
            #
            #Autor moze biti povezan na vise radova i zato ne moze imati atribut OZK jer se ne zna na koji rad se to odnosi
            #

            #Autori se povezuju s radom
            for autor in autori:
                noviAutor = models.Autor(ime=autor.ime,prezime=autor.prezime,email=autor.email)
                #Ako autor vec postoji u bazi, samo ga dodaj na ovaj rad
                if models.Autor.objects.filter(ime=autor.ime,prezime=autor.prezime,email=autor.email).exists():
                    noviAutor = models.Autor.objects.get(ime=autor.ime,prezime=autor.prezime,email=autor.email)
                #Ako autor ne postoji, napravi novog
                else:
                    noviAutor.save()
                noviRad.autori.add(noviAutor)

            noviRad.save()

            for dodatnoPolje in fetchedPolja:
                noviPodatak = request.POST[dodatnoPolje.imePolja]
                noviDodatniPodatak = models.DodatniPodatci(
                    podatak=noviPodatak,
                    korisnik=NoviKorisnik,
                    poljeObrasca=dodatnoPolje
                )
                noviDodatniPodatak.save()
                
        
        #Ako obradjujemo recenzenta, radimo drugacije provjere
        elif(uloga == "Recenzent"):
            #Ako ustanova ne postoji spremi ju, inace dohvati postojecu
            Ustanova = Ustanova = models.Ustanova(naziv=matustName,adresa=matustAdr,grad=matustCity,drzava=matustDrz)
            if models.Ustanova.objects.filter(naziv=matustName,adresa=matustAdr,grad=matustCity,drzava=matustDrz).exists():
                Ustanova = models.Ustanova.objects.get(naziv=matustName,adresa=matustAdr,grad=matustCity,drzava=matustDrz)
            else:
                Ustanova.save()

            #Ako sekcija ne postoji spremi ju, inace dohvati postojecu (nepotrebno jer se za sad ne mogu dodavati nove sekcije)
            Sekcija = models.Sekcija(naziv=section,konferencijaSekcija=models.Sekcija.objects.get(naziv=section).konferencijaSekcija)
            if  models.Sekcija.objects.filter(naziv=section).exists():
                Sekcija=models.Sekcija.objects.get(naziv=section)
            else:
                Sekcija.save()

            #Generiraj password za korisnika
            randPassword=get_random_string(length=16)
            request.session['randPassword'] = randPassword

            #Probaj spremiti novog korisnika
            try:
                NoviKorisnik = models.Korisnik(korisnickoIme=username,lozinka=randPassword,ime=fName,prezime=lName,email=email,vrstaKorisnik=models.Uloga.objects.get(naziv=uloga), korisnikUstanova=Ustanova, korisnikSekcija=Sekcija)
                NoviKorisnik.save()
            except IntegrityError:
                messages.error(request, "Korisnicko ime ili email je vec u uporabi")
                return redirect('signup')
                
            for dodatnoPolje in fetchedPolja:
                noviPodatak = request.POST[dodatnoPolje.imePolja]
                noviDodatniPodatak = models.DodatniPodatci(
                    podatak=noviPodatak,
                    korisnik=NoviKorisnik,
                    poljeObrasca=dodatnoPolje
                )
                noviDodatniPodatak.save()
        
        return redirect('signin')

    
    return render(request, 'Signup.html',context)
    
def signin(request):
    context = {}
    if request.method == "POST":
        Username = request.POST['Username']
        pass1 = request.POST['pass1']
        email = request.POST['email']
        try:
            if (email != ""):
                #zahtjev za novom lozinkom
                if (models.Korisnik.objects.filter(email = email).exists()):
                    korisnik = models.Korisnik.objects.get(email = email)
                    
                    #dodati enkripciju i slanje lozinke na mail
                    randPassword=get_random_string(length=16)
                    print(randPassword)
                    korisnik.lozinka = randPassword
                    korisnik.save()
                    messages.error(request, "Nova lozinka je poslana na e-mail.")

                else:
                    
                    messages.error(request, "E-mail koji ste unijeli ne postoji u bazi.")
                    return redirect('signin')


            elif (models.Korisnik.objects.filter(korisnickoIme=Username,lozinka=pass1).exists()):
                LoggedInUser=models.Korisnik.objects.get(korisnickoIme=Username,lozinka=pass1)
                print(LoggedInUser.vrstaKorisnik.naziv)
                request.session['LoggedInUserId']=LoggedInUser.id
                request.session
                request.session['LoggedInUserRole']=LoggedInUser.vrstaKorisnik.naziv
                #odobren se odnosi na recenzente a dok nisu odobreni ni ne mogu dobiti pass
                if LoggedInUser.odobrenBool==False:
                    messages.warning(request,"Vaš account još nije potvređen, molimo pogledajte vaš email")
                return redirect('home')
            else:
               
                messages.error(request, "Korisničko ime ili lozinka su krivi.")
                return redirect('signin')


        except:
            return redirect('signin')
 
    if "randPassword" in request.session: #tek smo se registrirali
        context["randPassword"]=request.session["randPassword"]
    elif "LoggedInUserId" in request.session: #otprije smo registrirani
        return redirect('/')
        
    return render(request, 'Signin.html',context)

def signout(request):
    if 'LoggedInUserId' in request.session:
        del request.session['LoggedInUserId']
        del request.session['LoggedInUserRole']
    return redirect('home')

def info(request):
    context={}
    if "LoggedInUserId" in request.session:
        context["LoggedInUser"]=request.session['LoggedInUserId']
  
    if "LoggedInUserRole" in request.session:
        context["LoggedInUserRole"]=request.session['LoggedInUserRole']

    if request.method == "POST":
        ##treba raditi validaciju jesu li datumi u dobrom formatu
        if 'NewNaziv' in request.POST:
            
            Naziv = request.POST['Naziv']
            konferencija=models.Konferencija.objects.filter().first() #Imamo li već neke podatke o konferenciji
            if konferencija:
                print(Naziv)
                konferencija.nazivKonferencije = Naziv
                konferencija.save()
            else:
                novakonferencija = models.Konferencija(nazivKonferencije=Naziv)
                novakonferencija.save()
        if 'NewOpis' in request.POST:
            
            Opis = request.POST['Opis']
            konferencija=models.Konferencija.objects.filter().first() 
            if konferencija:
                
                konferencija.opisKonferencije= Opis
                konferencija.save()
            else:
                novakonferencija = models.Konferencija(opisKonferencije = Opis)
                novakonferencija.save()
        if 'NewDatum' in request.POST:
            
            Datum = request.POST['Datum']
            konferencija=models.Konferencija.objects.filter().first() 
            if konferencija:
                
                konferencija.datumKonferencije=Datum
                konferencija.save()
            else:
                novakonferencija = models.Konferencija(datumKonferencije = Datum)
                novakonferencija.save()
        if 'NewRokPocPrijava' in request.POST:
            
            RokPocPrijava = request.POST['RokPocPrijava']
            konferencija=models.Konferencija.objects.filter().first() 
            if konferencija:
                
                konferencija.rokPocPrijava= RokPocPrijava
                konferencija.save()
            else:
                novakonferencija = models.Konferencija(RokPocPrijava= RokPocPrijava)
                novakonferencija.save()
        if 'NewRokPrijava' in request.POST:
            
            RokPrijava = request.POST['RokPrijava']
            konferencija=models.Konferencija.objects.filter().first() 
            if konferencija:
    
                konferencija.rokPrijave= RokPrijava
                konferencija.save()
            else:
                novakonferencija = models.Konferencija(rokPrijave= RokPrijava)
                novakonferencija.save()
        if 'NewRokPocRecenzija' in request.POST:
            
            RokPocRecenzija= request.POST['RokPocRecenzija']
            konferencija=models.Konferencija.objects.filter().first() 
            if konferencija:
    
                konferencija.rokRecenzenti= RokPocRecenzija
                konferencija.save()
            else:
                novakonferencija = models.Konferencija(rokRecenzenti= RokPocRecenzija)
                novakonferencija.save()
        if 'NewRokRecenzenti' in request.POST:
            
            RokRecenzenti= request.POST['RokRecenzenti']
            konferencija=models.Konferencija.objects.filter().first() 
            if konferencija:
    
                konferencija.rokRecenzenti= RokRecenzenti
                konferencija.save()
            else:
                novakonferencija = models.Konferencija(rokRecenzenti= RokRecenzenti)
                novakonferencija.save()
        
        if 'NewRokAdmin' in request.POST:
                    
            RokAdmin= request.POST['RokAdmin']
            konferencija=models.Konferencija.objects.filter().first() 
            if konferencija:
            
                konferencija.rokAdmin= RokAdmin
                konferencija.save()
            else:
                novakonferencija = models.Konferencija(rokAdmin= RokAdmin)
                novakonferencija.save()
        if 'AddNewSection' in request.POST:
           
            SectionName = request.POST["SectionName"]
           
            konferencija=models.Konferencija.objects.filter().first() 
            if (not konferencija):
                konferencija = models.Konferencija() #ako još nemamo podataka za konferenciju

            if not models.Sekcija.objects.filter(naziv = SectionName).exists():
                newSection=models.Sekcija(naziv = SectionName, konferencijaSekcija=konferencija)
                newSection.save()
            # context['sekcije']=models.Sekcija.objects.filter().all() #za prikaz sekcija
            # return redirect('info')
        if 'AddNewPreds' in request.POST:
             username = request.POST['Username']
             fName = request.POST['Fname']
             lName = request.POST['Lname']
             email = request.POST['email']

             predsjedavajuci=models.Korisnik.objects.filter(vrstaKorisnik = models.Uloga.objects.get(naziv = "Predsjedavajuci")).first() 
             if (not predsjedavajuci):
                #lozinku mu treba napraviti
                #poslati podatke na mail
                predsjedavajuci = models.Korisnik(korisnickoIme = username, ime = fName, prezime = lName, email = email,vrstaKorisnik = models.Uloga.objects.get(naziv = "Predsjedavajuci")) #ako još nemamo podataka za predsjedavajuceg
                predsjedavajuci.save()

            
       

    #konferencija je u bazi
    konferencija=models.Konferencija.objects.filter().first()
    if konferencija:

        context['konferencijaNaziv']=konferencija.nazivKonferencije
        context['opis']=konferencija.opisKonferencije
        datum = dateformat.format(konferencija.datumKonferencije, formats.get_format('d.m.Y.'))
        context['datum']=datum
        context['rokPrijave']= dateformat.format(konferencija.rokPrijave, formats.get_format('d.m.Y.'))
        context['rokRecenzenti']=dateformat.format(konferencija.rokRecenzenti, formats.get_format('d.m.Y.'))
        context['rokAdmin']=dateformat.format(konferencija.rokAdmin, formats.get_format('d.m.Y.'))
        context['rokPocRecenzija']=dateformat.format(konferencija.rokPocRecenzija, formats.get_format('d.m.Y.'))
        context['rokPocPrijava']=dateformat.format(konferencija.rokPocPrijava, formats.get_format('d.m.Y.'))
    
    fetchedSekcije=models.Sekcija.objects.filter().all()
    if (fetchedSekcije.first()):
        context['sekcije'] = fetchedSekcije
    if models.Korisnik.objects.filter(vrstaKorisnik = 2).exists():
        predsjedavajuci = models.Korisnik.objects.get(vrstaKorisnik = 2)
        context[predsjedavajuci] = predsjedavajuci


    

    
    print(context)
    return render(request, 'Info.html', context)

