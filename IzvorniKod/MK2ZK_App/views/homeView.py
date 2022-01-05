from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from io import StringIO, BytesIO
from typing import DefaultDict
from django.core.checks.messages import Error
from django.core.exceptions import ValidationError
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
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from IzvorniKod.MK2ZK_App.tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth.password_validation import *
import hashlib

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
        korisnik=models.Korisnik.objects.get(id=request.session['LoggedInUserId'])
        korisnik.lastActive=datetime.now()
        korisnik.save()
        context["LoggedInUser"]=korisnik.id
    
    if "LoggedInUserRole" in request.session:
        context["LoggedInUserRole"]=request.session['LoggedInUserRole']
        if request.session['LoggedInUserRole'] == 'Sudionik':
            context["LoggedInUserCode"]=models.Korisnik.objects.get(id=request.session['LoggedInUserId']).idSudionik
    
    konferencija=models.Konferencija.objects.filter().first()
    
    if (konferencija):
        #da bismo imali naš format imam ovaj rokPrijave1, a JS ne radi dobro s tim formatom pa tamo koristim drugi
        konferencija.rokPrijave1 = dateformat.format(konferencija.rokPrijave, formats.get_format('d.m.Y.')) #dodati ovisno što će nam trebati na naslovnici
        konferencija.rokRecenzenti1 = dateformat.format(konferencija.rokRecenzenti, formats.get_format('d.m.Y.'))
        context["infoKonferencija"] = konferencija #trebat ce mozda za countdown ili neke druge podatke stavit na naslovnicu
        
    sviKorisnici=models.Korisnik.objects.all()
    for korisnik in sviKorisnici:
        print(korisnik.korisnickoIme, korisnik.id in request.session)




    ##clanci
    fetchedClanci = models.Clanak.objects.filter(active=True)
    context['Clanci'] = fetchedClanci
    
    print(context)
    return render(request, 'Index.html',context)


def signup(request):
    context={}
    if "LoggedInUserId" in request.session:
        korisnik=models.Korisnik.objects.get(id=request.session['LoggedInUserId'])
        korisnik.lastActive=datetime.now()
        korisnik.save()
        context["LoggedInUser"]=korisnik.id #otprije smo registrirani
        return redirect('/')
    fetchedPolja=models.DodatnaPoljaObrasca.objects.filter().all()
    fetchedSekcije=models.Sekcija.objects.filter().all()
    if (fetchedSekcije.first()): #ako je admin unio sekcije
        context['sekcije'] = fetchedSekcije
    context['DodatnaPolja']=fetchedPolja
    # #!!
    # context['sekcije']=fetchedSekcije.exclude(naziv="Admin Sekcija") #dodao sam ovo kako bih mogao implementirati select za sekcije
    # ##

    #za obradu drzave
    ######
    module_dir = os.path.dirname(__file__)  # get current directory
    path1 = os.path.join(module_dir, '../static/txt/SveDrzave.txt')
    path2 = os.path.join(module_dir, '../static/txt/SveDrzaveHR.txt')

    file1 = open(path1, "r", encoding='utf-8')
    file2 = open(path2, "r", encoding='utf-8')

    drzaveEng = file1.read().replace("\"","\'")
    drzaveHrv = file2.read().replace("\"","\'")

    drzaveEngList = drzaveEng[1:len(drzaveEng)-2].split("',\n '")
    drzaveHrvList = drzaveHrv[1:len(drzaveHrv)-2].split("',\n '")
    dropDownDrzave = drzaveHrvList[1:]
    dropDownDrzave.sort()
    dropDownDrzave.remove("Hrvatska")
    dropDownDrzave.remove("Ostalo")
    dropDownDrzave[0]="Hrvatska"
    context["Drzave"] = dropDownDrzave
    ######

    #print(context)

    if request.method == "POST":        
        print(request.POST)
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
        #za obradu drzave
        ######
        #matustDrz = ""
        #matustDrzHrv = request.POST['matustDrz']
        #for i in range(len(drzaveHrvList)):
            #if drzaveHrvList[i] == matustDrzHrv:
                #matustDrz = drzaveEngList[i]
        ######

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
                if "autorKontakt"+i in request.POST:
                    OZKIndex=int(i)
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
                        messages.error(request, "Autori ne smiju imati istu adresu e-pošte!")
                        return redirect('signup')

            #Nije pretjerano optimalno, but it gets the job done
            for autor in autori:
                if models.Autor.objects.filter(email=autor.email).exists():
                    postojeciAutor = models.Autor.objects.get(email=autor.email)
                    if postojeciAutor.ime != autor.ime or postojeciAutor.prezime != autor.prezime:
                        messages.error(request, "Adresa e-pošte autora je zauzeta!")
                        return redirect('signup')

            #Ako ustanova ne postoji spremi ju, inace dohvati postojecu
            Ustanova = models.Ustanova(naziv=matustName,adresa=matustAdr,grad=matustCity,drzava=matustDrz)
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
            salt=os.urandom(32)
            key=hashlib.pbkdf2_hmac(
                'sha256',
                randPassword.encode('utf-8'),
                salt,
                100000
            )



            #Probaj spremiti novog korisnika
            try:
                NoviKorisnik = models.Korisnik(korisnickoIme=username,lozinka=key,idSudionik=idSudionik,ime=fName,prezime=lName,email=email,vrstaKorisnik=models.Uloga.objects.get(naziv=uloga), korisnikUstanova=Ustanova, korisnikSekcija=Sekcija,salt=salt)
                NoviKorisnik.save()
            except IntegrityError:
                messages.error(request, "Korisničko ime ili adresa e-pošte već se koristi!")
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
                    messages.error(request, "Rad s tim naslovom u toj sekciji već postoji!")
                    NoviKorisnik.delete()
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

            print(OZKIndex)
            for index,autor in enumerate(autori):
                if index==OZKIndex:
                    autorrad=models.AutorRad.objects.get(Rad=noviRad,Autor=models.Autor.objects.get(ime=autor.ime,prezime=autor.prezime,email=autor.email))
                    print(autorrad.id)
                    autorrad.OZK=True
                    autorrad.save()

            fetchedPolja=models.DodatnaPoljaObrasca.objects.filter(active = "True").all()
            for dodatnoPolje in fetchedPolja:
                try:
                    noviPodatak = request.POST[dodatnoPolje.imePolja]
                    
                   
                    noviDodatniPodatak = models.DodatniPodatci(
                    podatak=noviPodatak,
                    korisnik=NoviKorisnik,
                    poljeObrasca=dodatnoPolje
                )
                    noviDodatniPodatak.save()
                except:
                    continue
            poruka = render_to_string('AktivirajEmail.html', {
                'user': NoviKorisnik,
                'lozinka': randPassword,
                'domain': '127.0.0.1:8000',
                'uid':urlsafe_base64_encode(force_bytes(NoviKorisnik.id)),
                'token':account_activation_token.make_token(NoviKorisnik),
                'protocol':'http'
                    })
            to_email = email
            email = EmailMessage(
            '[ZK] Tvoj račun je stvoren!', poruka, 'Pametna ekipa', to=[to_email]
            )
            email.send()
            messages.info(request, "Na adresu e-pošte pošte poslan je aktivacijski link i podaci za prijavu.")
            return redirect('signin')
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
            
            #Probaj spremiti novog korisnika
            try:
                NoviKorisnik = models.Korisnik(korisnickoIme=username,ime=fName,prezime=lName,email=email,vrstaKorisnik=models.Uloga.objects.get(naziv=uloga), korisnikUstanova=Ustanova, korisnikSekcija=Sekcija)
                NoviKorisnik.save()
            except IntegrityError:
                messages.error(request, "Korisničko ime ili adresa e-pošte već se koristi!")
                return redirect('signup')
                
            for dodatnoPolje in fetchedPolja:
                noviPodatak = request.POST[dodatnoPolje.imePolja]
                noviDodatniPodatak = models.DodatniPodatci(
                    podatak=noviPodatak,
                    korisnik=NoviKorisnik,
                    poljeObrasca=dodatnoPolje
                )
                noviDodatniPodatak.save()
            messages.info(request, "Hvala na prijavi! Predsjedavajući će pregledati vašu prijavu te Vas obavijestiti o potvrdi recenziranja e-mailom. Hvala na strpljenju!")
            return redirect('home')
        

    
    return render(request, 'Signup.html',context)

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        print(token)
        print(uid)
        postojeciKorisnik = models.Korisnik.objects.get(id=uid)
        print(postojeciKorisnik.korisnickoIme)
        print(account_activation_token.check_token(postojeciKorisnik, token))
    except(TypeError, ValueError, OverflowError, models.Korisnik.DoesNotExist):
        postojeciKorisnik = None
    if postojeciKorisnik is not None and account_activation_token.check_token(postojeciKorisnik, token):
        postojeciKorisnik.potvrdenBool = True
        postojeciKorisnik
        #print(postojeciKorisnik)
        postojeciKorisnik.save()
        signin(request)
        messages.info(request,'Hvala na potvrdi! Sada se možete prijaviti!')
        return redirect('signin')
    else:
        messages.info(request,'Aktivacijska poveznica nije valjana!')
        return redirect('signin')

def signin(request):
    context = {}
    print(type(os.urandom(32)))
    if request.method == "POST":
        #zaboravljena lozinka
        if "email" in request.POST:
            email = request.POST['email']
            #zahtjev za novom lozinkom
            if (models.Korisnik.objects.filter(email = email).exists()):
                korisnik = models.Korisnik.objects.get(email = email)
                
                #dodati enkripciju i slanje lozinke na mail
                """
                randPassword=get_random_string(length=16)
                print(randPassword)
                korisnik.lozinka = randPassword
                korisnik.save()
                messages.error(request, "Nova lozinka poslana je na adresu e-pošte.")
                """

                subject = "[ZK] Promjena lozinke"
                email_template_name = "PromijeniLozinkuEmail.html"
                c = {
                "email":korisnik.email,
                'domain':'127.0.0.1:8000',
                'site_name': 'Znanstvena konferencija',
                "uid": urlsafe_base64_encode(force_bytes(korisnik.id)),
                "user": korisnik,
                'token': account_activation_token.make_token(korisnik),
                'protocol': 'http',
                }
                email_message = render_to_string(email_template_name, c)
                EmailMessage(subject, email_message, 'Pametna ekipa', [korisnik.email]).send()
                messages.error(request, "Poveznica za promjenu lozinke poslana je na adresu e-pošte.")
            else:
                messages.error(request, "Adresa e-pošte koji ste unijeli ne postoji u bazi!")
                return redirect('signin')

        #normalan login
        else:
            Username = request.POST['Username']
            pass1 = request.POST['pass1']
            #HARDKODIRAN PROLAZ ZA HARDKODIRANE KORISNIKE
            if (Username=="admin" and pass1=="admin") or (Username=="recenzent" and pass1=="recenzent") or (Username=="sudionik" and pass1=="sudionik") or (Username=="predsjedavajuci" and pass1=="predsjedavajuci"):
                LoggedInUser=models.Korisnik.objects.get(korisnickoIme=Username)
                request.session['LoggedInUserId']=LoggedInUser.id
                request.session['LoggedInUserRole']=LoggedInUser.vrstaKorisnik.naziv
                #odobren se odnosi na recenzente a dok nisu odobreni ni ne mogu dobiti pass
                return redirect('home')
            else:
                try: #Privremeni TRY da ne izbaci gresku ako netko slucajno krivo napise predsjedavajuci
                    if (models.Korisnik.objects.filter(korisnickoIme=Username).exists()):
                        LoggedInUser=models.Korisnik.objects.get(korisnickoIme=Username)
                        if not LoggedInUser.lozinka==None:
                            salt=LoggedInUser.salt
                            correctHash=LoggedInUser.lozinka

                            givenHash=hashlib.pbkdf2_hmac(
                                'sha256',
                                pass1.encode('utf-8'),
                                salt,
                                100000
                            )
                            print("CORRECT HASH: ",correctHash,type(correctHash),"\n\n GIVEN HASH: ",givenHash,type(givenHash))
                            if correctHash==str(givenHash):

                                if LoggedInUser.vrstaKorisnik.naziv=="Recenzent":
                                    if LoggedInUser.odobrenBool==None:
                                        messages.warning(request,"Vaš zahtjev za recenziranjem još nije odobren. Hvala Vam na strpljenju.")
                                        return redirect('home')
                                    if LoggedInUser.odobrenBool==False:
                                        messages.warning(request,"Vaš zahtjev za recenziranjem je odbijen!")
                                        return redirect('home')
                                if LoggedInUser.potvrdenBool==False:
                                    messages.warning(request,"Vaš račun još nije potvrđen, molimo pogledajte adresu e-pošte!")
                                    print("flag")
                                    return redirect('signin')
                                else:
                                    print(LoggedInUser.vrstaKorisnik.naziv)
                                    request.session['LoggedInUserId']=LoggedInUser.id
                                    request.session['LoggedInUserRole']=LoggedInUser.vrstaKorisnik.naziv
                                    #odobren se odnosi na recenzente a dok nisu odobreni ni ne mogu dobiti pass
                                    return redirect('home')
                            else:
                                messages.error(request, "Unesena lozinka nije ispravna!")
                                return redirect('signin')
                    else:
                        messages.error(request, "Korisničko ime ne postoji!")
                        return redirect('signin')
                except: #Privremeni EXCEPT da ne izbaci gresku ako netko slucajno krivo napise predsjedavajuci
                    messages.error(request, "Uneseni podaci su neispravni!")
                    return redirect('signin')
    elif "LoggedInUserId" in request.session:
        korisnik=models.Korisnik.objects.get(id=request.session['LoggedInUserId'])
        korisnik.lastActive=datetime.now()
        korisnik.save()
        context["LoggedInUser"]=korisnik.id #otprije smo registrirani
        return redirect('/')
        
    return render(request, 'Signin.html',context)

def new_password(request, uidb64, token):
    context={}
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        print(token)
        print(uid)
        postojeciKorisnik = models.Korisnik.objects.get(id=uid)
        print(postojeciKorisnik.korisnickoIme)
        print(account_activation_token.check_token(postojeciKorisnik, token))
    except(TypeError, ValueError, OverflowError, models.Korisnik.DoesNotExist):
        postojeciKorisnik = None
    if postojeciKorisnik is not None and account_activation_token.check_token(postojeciKorisnik, token):
        context["usedEmail"]=postojeciKorisnik.email
        context["usedUid"]=uidb64
        context["usedToken"]=token
    return render(request, 'PromijeniLozinku.html',context)

def reset_password(request):
    if request.method == "POST":
        email=request.POST["usedEmail"]
        uid=request.POST["uid"]
        token=request.POST["token"]
        redirectString="reset/"+str(uid)+"/"+str(token)
        print(redirectString)
        pass1=request.POST["pass1"]
        pass2=request.POST["pass2"]
        user=models.Korisnik.objects.get(email=email)
        validators = [MinimumLengthValidator,CommonPasswordValidator,NumericPasswordValidator]
        print(user.ime + user.prezime)
        userAttributes = [user.korisnickoIme,user.ime,user.prezime,user.ime + user.prezime,user.ime + user.korisnickoIme,user.korisnickoIme + user.prezime]
        if not pass1==pass2: #Lozinke nisu iste
            messages.error(request,"Unesene se lozinke ne preklapaju!")
            return redirect(redirectString)
        if user.lozinka==pass1: #Lozinka je ista staroj
            messages.error(request,"Nova lozinka ne smije biti stara lozinka.")
            return redirect(redirectString)
        for atr in userAttributes:
            if SequenceMatcher(a=pass1.lower(), b=atr.lower()).quick_ratio() >= 0.7:
                messages.error(request, "Lozinka je nesigurna jer je preslična Vašim osobnim podacima.")
                return redirect(redirectString)
        try:
            for validator in validators:
                validator().validate(pass1)
        except ValidationError as e:
            if str(e) == "['This password is too short. It must contain at least 8 characters.']":
                messages.error(request, "Lozinka mora sadržavati minimalno 8 znakova.")
                return redirect(redirectString)
            if str(e) == "['This password is too common.']":
                messages.error(request, "Lozinka je prejednostavna.")
                return redirect(redirectString)
            if str(e) == "['This password is entirely numeric.']":
                messages.error(request, "Lozinka ne smije imati samo brojeve.")
                return redirect(redirectString)
            messages.error(request,str(e))
            return redirect(redirectString)
            
        
        salt=os.urandom(32)
        key=hashlib.pbkdf2_hmac(
            'sha256',
            pass1.encode('utf-8'),
            salt,
            100000
        )
        user.lozinka=key
        user.salt=salt
        user.save()
        return redirect('signin')
    #Ako nije POST
    messages.error(request, "Nemate pristup ovoj stranici!")
    return redirect('home')
    #treba promijeniti tako da se provjeri poklapaju li se lozinke te ju spremiti u bazu ili javiti grešku

def signout(request):
    if 'LoggedInUserId' in request.session:
        del request.session['LoggedInUserId']
        del request.session['LoggedInUserRole']
    return redirect('home')

def info(request):
    context={}
    if "LoggedInUserId" in request.session:
        korisnik=models.Korisnik.objects.get(id=request.session['LoggedInUserId'])
        korisnik.lastActive=datetime.now()
        korisnik.save()
        context["LoggedInUser"]=korisnik.id
  
    if "LoggedInUserRole" in request.session:
        context["LoggedInUserRole"]=request.session['LoggedInUserRole']

    #konferencija je u bazi
    konferencija=models.Konferencija.objects.first()
    if konferencija:

        context['konferencijaNaziv']=konferencija.nazivKonferencije
        context['opis']=konferencija.opisKonferencije
        datum = dateformat.format(konferencija.datumKonferencije, formats.get_format('d.m.Y.'))
        context['datum']=datum
        context['rokPrijave']= dateformat.format(konferencija.rokPrijave, formats.get_format('d.m.Y.'))
        context['rokRecenzenti']=dateformat.format(konferencija.rokRecenzenti, formats.get_format('d.m.Y.'))
        context['rokPocRecenzija']=dateformat.format(konferencija.rokPocRecenzija, formats.get_format('d.m.Y.'))
        context['rokPocPrijava']=dateformat.format(konferencija.rokPocPrijava, formats.get_format('d.m.Y.'))
        context['info'] = models.Konferencija.objects.get(sifKonferencija = 1).opisKonferencije
    
    fetchedSekcije=models.Sekcija.objects.all()
    if (fetchedSekcije.first()):
        context['sekcije'] = fetchedSekcije
    if models.Korisnik.objects.filter(vrstaKorisnik = 2).exists():
        predsjedavajuci = models.Korisnik.objects.get(vrstaKorisnik = 2)
        context[predsjedavajuci] = predsjedavajuci
    
    
    print(context)
    return render(request, 'Info.html', context)

def javniradovi(request):
  context={}
  if "LoggedInUserId" in request.session:
        korisnik=models.Korisnik.objects.get(id=request.session['LoggedInUserId'])
        korisnik.lastActive=datetime.now()
        korisnik.save()
        context["LoggedInUser"]=korisnik.id
  else: #nismo ulogirani
    return redirect('signin')

  if "LoggedInUserRole" in request.session:
        context["LoggedInUserRole"]=request.session['LoggedInUserRole']

  radovi = models.Rad.objects.all()
  sekcije = models.Sekcija.objects.all()
  korisnici = models.Korisnik.objects.all()

  #brojac predanih radova
  brojPredanihRadova = 0
  
  #Shvatio sam da je puno lakse napravit ovo nego stavljat naziv unutar templatea
  for rad in radovi:
      rad.radSekcija_naziv = sekcije.get(sifSekcija=rad.radSekcija_id).naziv
      if(rad.pdf != ""):
        brojPredanihRadova += 1

  context['javniBool'] = models.Konferencija.objects.get(sifKonferencija=1).javniRadoviBool
  context['Radovi'] = radovi
  context['brojPredanihRadova'] = brojPredanihRadova

  return render(request, 'JavniRadovi.html', context)

