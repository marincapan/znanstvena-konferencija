from datetime import date, datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.crypto import get_random_string
from IzvorniKod.MK2ZK_App import models
from django.db import IntegrityError
from django.utils import (dateformat, formats)
from IzvorniKod.MK2ZK_App.tokens import account_activation_token
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from IzvorniKod.MK2ZK_App.tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth.password_validation import *
import hashlib
import os
import requests
from datetime import datetime

def adminsucelje(request):
    #Incijalizacija kontexta
    #------------------------------------------------------------------------------------------------------------------------------
    
    context={}
    
    #------------------------------------------------------------------------------------------------------------------------------

    
    #Provjera dali postoji ulogirani korisnik
    #------------------------------------------------------------------------------------------------------------------------------
    
    if "LoggedInUserId" in request.session: #Ako postoji
        korisnik=models.Korisnik.objects.get(id=request.session['LoggedInUserId']) #Dohvati ga
        korisnik.lastActive=datetime.now() #Ažuriraj zadnju aktivnost
        korisnik.save() #Spremi
        context["LoggedInUser"]=korisnik.id #U kontekst spremi njegov ID
    else: #Ako ne - nismo ulogirani
        return redirect('signin') #Pošalji na stranicu za prijavu
    
    #------------------------------------------------------------------------------------------------------------------------------
    
    
    #Provjera ovlasti
    #------------------------------------------------------------------------------------------------------------------------------
    if "LoggedInUserRole" in request.session: #Ako postoji korisnik:
        if request.session['LoggedInUserRole'] == "Admin": #Ako taj korisnik ima ulogu Admina:
            context["LoggedInUserRole"]=request.session['LoggedInUserRole'] #Spremi njegovu ulogu u context
        else: #Ako nije admin:
            messages.error(request,"Nemate ovlasti za pristup ovoj stranici!") #Pošalji poruku korisniku
            return redirect('/') #redirect na homepage
    #------------------------------------------------------------------------------------------------------------------------------
    
    
    #Dohvat varijabli iz baze podataka
    #------------------------------------------------------------------------------------------------------------------------------
    predsjedavajuci=models.Korisnik.objects.filter(vrstaKorisnik=2).first() #Dohvati Predsjedavajuceg
    
    Administratori = models.Korisnik.objects.filter(vrstaKorisnik_id = 1, potvrdenBool = True) #Dohvati sve Administratore s aktivnim računom
    
    radovi = models.Rad.objects.all() #Dohvati sve radove
    
    sekcije = models.Sekcija.objects.all() #Dohvati sve sekcije
    
    korisnici = models.Korisnik.objects.all() #Dohvati sve korisnike
    
    fetchedPolja=models.DodatnaPoljaObrasca.objects.all() #Dohvati sva dodatna polja
    
    fetchedClanci = models.Clanak.objects.all() #Dohvati sve članke
    
    fetchedSekcije=models.Sekcija.objects.all() #Dohvati sve sekcije
    
    konferencija=models.Konferencija.objects.first() #Dohvati konferenciju
    #------------------------------------------------------------------------------------------------------------------------------
     
    
    #Punjenje contexta
    #------------------------------------------------------------------------------------------------------------------------------
    context["AdministratoriPopis"] = Administratori #Spremi sve Administratore
    
    if (predsjedavajuci): #Ako postoji predsjedavajuci
        context["predsjedavajuci"]=predsjedavajuci #Spremi Predsjedavajuceg
    
    if konferencija:
        context['konferencijaNaziv']=konferencija.nazivKonferencije #Spremi naziv konferencije

        context['opis']=konferencija.opisKonferencije #Spremi opis konferencije

        #Spremi sve važne datume
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        context['datum'] = dateformat.format(konferencija.datumKonferencije, formats.get_format('Y-m-d'))
        
        context['rokPrijave']= dateformat.format(konferencija.rokPrijave, formats.get_format('Y-m-d'))
        
        context['rokRecenzenti']=dateformat.format(konferencija.rokRecenzenti, formats.get_format('Y-m-d'))
        
        context['rokPocRecenzija']=dateformat.format(konferencija.rokPocRecenzija, formats.get_format('Y-m-d'))
        
        context['rokPocPrijava']=dateformat.format(konferencija.rokPocPrijava, formats.get_format('Y-m-d'))
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        context["prosoDatum"]=date.today()>=models.Konferencija.objects.get(sifKonferencija=1).rokPocPrijava #Provjeri jesu li prijave počele
        
        context["javniBool"] = konferencija.javniRadoviBool #Spremi status javnih radova
    
    dobriradovi = 0 #brojac prihvaćenih radova
    for rad in radovi: #Za svaki rad:
        if( rad.recenziranBool == 1 and rad.revizijaBool == 0): #Ako je prihvaćen
            dobriradovi +=1 #Povećaj brojac prihvaćenih radova
    context["brojDobrihRadova"] = dobriradovi #Spremi broj prihvaćenih radova
    
    context['DodatnaPolja']=fetchedPolja #Spremi sva dodatna polja

    context['Clanci'] = fetchedClanci #Spremi sve članke

    if (fetchedSekcije): #Ako postoje sekcije
        context['sekcije'] = fetchedSekcije #Spremi sve sekcije
    #------------------------------------------------------------------------------------------------------------------------------
    
    
    #POST metode
    #------------------------------------------------------------------------------------------------------------------------------
    if request.method == "POST":

        # Mijenjaje podataka o konferenciji
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if 'nazivKonferencije' in request.POST: 
            
            #Dohvati unesene podatke
            #______________________________________________________________________________________________________________________
            
            nazivKonferencije = request.POST["nazivKonferencije"]

            opisKonferencije = request.POST["opisKonferencije"]

            datumKonferencije = datetime.strptime(request.POST["datumKonferencije"], "%Y-%m-%d").date()
            
            pocetakPrijavaKonferencije = datetime.strptime(request.POST["pocetakPrijavaKonferencije"], "%Y-%m-%d").date()
            
            rokPrijava = datetime.strptime(request.POST["rokPrijava"], "%Y-%m-%d").date()
            
            pocetakRecenzija = datetime.strptime(request.POST["pocetakRecenzija"], "%Y-%m-%d").date()
            
            rokRecenzija = datetime.strptime(request.POST["rokRecenzija"], "%Y-%m-%d").date()

            #______________________________________________________________________________________________________________________

            #Validatori za datume
            #______________________________________________________________________________________________________________________
            
            if pocetakPrijavaKonferencije>rokPrijava:
                messages.error(request,"Početak prijava/Rok za promjenu obrasca ne smije biti poslije roka za prijavu i predaju radova")
                return redirect('/adminsucelje#podatciOKonferenciji')

            if pocetakRecenzija>rokRecenzija:
                messages.error(request,"Početak recenziranja ne smije biti poslije roka za recenziranje")
                return redirect('/adminsucelje#podatciOKonferenciji')

            if pocetakPrijavaKonferencije>pocetakRecenzija:
                messages.error(request,"Početak prijava/Rok za promjenu obrasca ne smije biti poslije početaka recenziranja")
                return redirect('/adminsucelje#podatciOKonferenciji')

            if rokRecenzija>datumKonferencije:
                messages.error(request,"Datum konferencije ne smije biti prije kraja recenziranja")
                return redirect('/adminsucelje#podatciOKonferenciji')  

            #______________________________________________________________________________________________________________________

            #Spremi promjene
            #______________________________________________________________________________________________________________________
            
            konferencija.nazivKonferencije = nazivKonferencije

            konferencija.opisKonferencije = opisKonferencije

            konferencija.datumKonferencije = datumKonferencije

            konferencija.rokPocPrijava = pocetakPrijavaKonferencije

            konferencija.rokPrijave = rokPrijava

            konferencija.rokPocRecenzija = pocetakRecenzija

            konferencija.rokRecenzenti = rokRecenzija

            konferencija.save()

            #______________________________________________________________________________________________________________________

            messages.success(request, "Podaci o konferenciji su uspješno ažurirani!")
            return redirect('/adminsucelje#podatciOKonferenciji') #Uspješno! Vrati na stranicu
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        
      
        # Mijenjaje podataka o predsjedavajucem
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        
        if 'username' in request.POST: 

            #Dohvati unesene podatke
            #______________________________________________________________________________________________________________________
            
            username = request.POST["username"]

            ime = request.POST["ime"]

            prezime = request.POST["prezime"]

            email = request.POST["email"]

            #______________________________________________________________________________________________________________________
            
            #Validatori za korisničko ime i email
            #______________________________________________________________________________________________________________________
            
            if models.Korisnik.objects.filter(korisnickoIme = username).exists():
                messages.error(request, "Korisničko ime je zauzeto")
                return redirect('/adminsucelje#upravljanjePredsjedavajućem')
            
            if models.Korisnik.objects.filter(email = email).exists():
                messages.error(request, "E-mail adresa je zauzeta")
                return redirect('/adminsucelje#upravljanjePredsjedavajućem')
            
            #______________________________________________________________________________________________________________________
            
            #Spremanje podataka
            #______________________________________________________________________________________________________________________
            
            predsjedavajuci.korisnickoIme = username
            predsjedavajuci.ime = ime
            predsjedavajuci.prezime = prezime

            #Provjera i rad za novog predsjedavajuceg
            #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            
            trenutniemail = predsjedavajuci.email
            if (trenutniemail != email): #Ako je novi predsjedavajuci

                predsjedavajuci.email = email

                #Generiraj i hashiraj password za novog predsjedavajuceg
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
                
                #Pošalji podatke i aktivacijski link na mail
                try:
                    predsjedavajuci.potvrdenBool = False #novi predsjedavajuci
                    predsjedavajuci.save()
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
                
                    messages.success(request, "Podaci o predsjedavajućem su uspješno promijenjeni. Predsjedavajućem su na adresu e-pošte poslani podaci za prijavu.")
                    return redirect('/adminsucelje#upravljanjePredsjedavajućem')
                except:
                    messages.error(request,"Dogodila se pogreška. Pokušajte ponovno.")
                    return redirect('/adminsucelje#upravljanjePredsjedavajućem')
            
            #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            
            predsjedavajuci.save()
            
            #______________________________________________________________________________________________________________________
            
            messages.success(request, "Podaci o predsjedavajućem su uspješno promijenjeni.")
            return redirect('/adminsucelje#upravljanjePredsjedavajućem') #Uspjesno! Vrati na stranicu

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

        
        #Promjena statusa javnih radova
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
            
        if "makePublic" in request.POST:
            konferencija=models.Konferencija.objects.get(sifKonferencija=1)
            if konferencija.javniRadoviBool==True:
                konferencija.javniRadoviBool=False
                konferencija.save()
            else:
                konferencija.javniRadoviBool=True
                konferencija.save()
            messages.success(request, "Status javnih radova je uspješno promijenjen.")
            return redirect('adminsucelje')

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        
        
        #Dodavanje novih dodatnih polja
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        
        if 'AddNewField' in request.POST:
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

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        
        
        #Aktiviranje dodatnih polja
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        
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
                    checked = False
                    obavezan = False
                polje.active = checked
                polje.obavezan = obavezan
                polje.save()
            return redirect('/adminsucelje#aktivnaPolja')

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        
        
        #Dodavanje Sekcija
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        
        if 'AddNewSection' in request.POST:
           
            SectionName = request.POST["SectionName"]
           
            konferencija=models.Konferencija.objects.filter().first() 
            if (not konferencija):
                konferencija = models.Konferencija() #ako još nemamo podataka za konferenciju

            if not models.Sekcija.objects.filter(naziv = SectionName).exists():
                newSection=models.Sekcija(naziv = SectionName, konferencijaSekcija=konferencija)
                newSection.save()
            return redirect("/adminsucelje#upravljanjeSekcijama")
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        
        
        #Dodavanje novog admina
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        
        if 'AddNewAdmin' in request.POST:

            #Dohvati unesene podatke
            #______________________________________________________________________________________________________________________
            
            AdminName = request.POST['adminime']

            AdminSurname = request.POST['adminprezime']

            AdminUsername = request.POST['adminusername']

            AdminEmail = request.POST['adminemail']

            #______________________________________________________________________________________________________________________
            
            #Validatori za korisničko ime i email
            #______________________________________________________________________________________________________________________
            
            if models.Korisnik.objects.filter(korisnickoIme = AdminUsername).exists():
                messages.error(request, "Korisničko ime je zauzeto")
                return redirect('adminsucelje')
            
            if models.Korisnik.objects.filter(email = AdminEmail).exists():
                messages.error(request, "E-mail adresa je zauzeta")
                return redirect('adminsucelje')

            #______________________________________________________________________________________________________________________
            

            #Generiranje i hasiranje lozinke, slanje aktivacijskog maila te spremanje korisnika
            #______________________________________________________________________________________________________________________
            
            randPassword=get_random_string(length=16)
            salt=os.urandom(32)
            key=hashlib.pbkdf2_hmac(
                'sha256',
                randPassword.encode('utf-8'),
                salt,
                100000
            )

            try:
                NoviKorisnik = models.Korisnik(korisnickoIme=AdminUsername,lozinka=key, salt = salt, ime=AdminName,prezime=AdminSurname,email=AdminEmail,vrstaKorisnik=models.Uloga.objects.get(id=1))
                NoviKorisnik.save()
            except IntegrityError:
                messages.error(request, "Korisničko ime ili email je vec u uporabi.")
                return redirect('/adminsucelje#upravljanjeAdministratorima')

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

            #______________________________________________________________________________________________________________________
            
            
            messages.success(request, "Novi administrator je uspješno dodan.\n Na adresu pošte poslan je aktivacijski link i podaci za prijavu.")
            return redirect('/adminsucelje') #Uspjeh! Vrati na stranicu

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        
            
        # Dodavanje novog članka
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        
        if "AddArticle" in request.POST:
            ArticleTitle = request.POST['clanakTitle']
            ArticleText = request.POST['clanakText']

            if models.Clanak.objects.filter(naslov = ArticleTitle).exists():
                messages.error(request, "Već postoji članak s ovim naslovom")
                return redirect('adminsucelje')

            newArticle = models.Clanak(naslov=ArticleTitle, tekst=ArticleText, autor=models.Korisnik.objects.get(id = request.session['LoggedInUserId']))
            newArticle.save()
            context['Clanci'] = fetchedClanci
            messages.success(request, "Uspješno je dodan novi članak.")
            return redirect('/adminsucelje#uređivanjeNaslovne')

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        

        # Odabir aktivnih članaka
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        
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

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
             
        return redirect('adminsucelje') #Glavni redirect ako se slucajno pokreno POST bez unosa

    return render(request, 'AdminSucelje.html', context) #Učitaj HTML s contextom

def covidstats(request):
    #Incijalizacija kontexta
    #------------------------------------------------------------------------------------------------------------------------------
    
    context={}
    
    #------------------------------------------------------------------------------------------------------------------------------

    
    #Provjera dali postoji ulogirani korisnik
    #------------------------------------------------------------------------------------------------------------------------------
    
    if "LoggedInUserId" in request.session:
        korisnik=models.Korisnik.objects.get(id=request.session['LoggedInUserId'])
        korisnik.lastActive=datetime.now()
        korisnik.save()
        context["LoggedInUser"]=korisnik.id
    else: #nismo ulogirani
        return redirect('signin')
    
    #------------------------------------------------------------------------------------------------------------------------------
    
    
    #Provjera ovlasti
    #------------------------------------------------------------------------------------------------------------------------------
    
    if "LoggedInUserRole" in request.session:
        if request.session['LoggedInUserRole'] == "Admin" or request.session['LoggedInUserRole'] == "Predsjedavajuci" :
            context["LoggedInUserRole"]=request.session['LoggedInUserRole']
        else: #nije admin
            messages.error(request,"Nemate ovlasti za pristup ovoj stranici!")
            return redirect('/') #redirect na homepage

    #------------------------------------------------------------------------------------------------------------------------------
    

    #Dohvat i obrada podataka o COVID-19       
    #------------------------------------------------------------------------------------------------------------------------------
    
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
    context["konfDrzave"]=konfDrzave
    #------------------------------------------------------------------------------------------------------------------------------
    
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
            
                for polje in dodatno:
                        dodatno = models.DodatniPodatci.objects.filter(korisnik = korisnik, poljeObrasca = polje).first()
                        
                        if dodatno:
                            novo = request.POST["dodatni"+str(i)]
                            #validacija unosa?

                            i = i + 1
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
                    novaUstanova = models.Ustanova(
                    naziv = maticnaUstanova,
                    grad = korisnik.korisnikUstanova.grad,
                    drzava = korisnik.korisnikUstanova.drzava,
                    adresa = korisnik.korisnikUstanova.adresa
                )
                    novaUstanova.save()
                
                korisnik.korisnikUstanova = novaUstanova

            korisnik.save()
            messages.success(request, "Podaci su uspješno promijenjeni.")
            uloga = korisnik.vrstaKorisnik.naziv
            if (uloga == "Sudionik"):
                url = "/pregled/sudionici/"+username
              
                return redirect(url)
            if (uloga == "Recenzent"):
                url = "/pregled/recenzenti/"+username
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
                                if (dodatno.poljeObrasca.tipPolja.naziv == "date"):
                                #želimo naš format datuma

                                    try:
                                        date_object = datetime.strptime(dodatno.podatak, '%Y-%m-%d').date() #validacija datuma?
                                        podatak = dateformat.format(date_object, formats.get_format('d.m.Y.'))
                                    except:
                                        podatak = dodatno.podatak
                                ime = dodatno.poljeObrasca.imePolja
                                dodatnipodatci[ime] = podatak
                  

                    context['dodatnipodatci'] = dodatnipodatci


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
    rad = models.Rad.objects.get(sifRad = sifrada)

    if rad:

        if request.method == "POST":
            title=request.POST["title"]
            rad.naslov=title
            try:
                pdf=request.FILES["newPdf"]
                rad.pdf=pdf
            except:
                pass
            rad.save()
            autorRadQuery = models.AutorRad.objects.filter(Rad = rad.sifRad)
            for autorRad in autorRadQuery:
                promjenaAutora=models.Autor.objects.get(sifAutor=autorRad.Autor.sifAutor)
                promjenaAutora.ime = request.POST["newname"+str(autorRad.Autor.sifAutor)]
                promjenaAutora.prezime = request.POST["newsur"+str(autorRad.Autor.sifAutor)]
                promjenaAutora.save()

            messages.success(request, "Podaci o radu su uspješno promijenjeni.")
            return redirect('/pregled/radovi/'+sifrada)

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