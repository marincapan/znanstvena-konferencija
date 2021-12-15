from collections import defaultdict
from typing import DefaultDict
from django.core.checks.messages import Error
from django.db.models.fields import DateTimeCheckMixin, NullBooleanField
from django.db.models.query import EmptyQuerySet
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.utils.crypto import get_random_string
from . import models
from django.db import IntegrityError 
from django.core import serializers



def increment_KorisnikID():
  last_korisnik = models.Korisnik.objects.all().order_by('id').last()
  if not last_korisnik:
    return '0001'
  korisnik_id = last_korisnik.idSudionik
  korisnik_int = int(korisnik_id)
  new_korisnik_int = korisnik_int + 1
  new_korisnik_id =str(new_korisnik_int).zfill(4)
  return new_korisnik_id
# Create your views here.
def home(request):
    if 'randPassword' in request.session:
        del request.session['randPassword']
    #Password se pokazuje jedanput i vise nikad.

    context={}
    if "LoggedInUserId" in request.session:
        context["LoggedInUser"]=models.Korisnik.objects.get(id=request.session['LoggedInUserId']).idSudionik
    
    if "LoggedInUserRole" in request.session:
        context["LoggedInUserRole"]=request.session['LoggedInUserRole']
    print(context)
    return render(request, 'Index.html',context)

def signup(request):
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
        
        return redirect('signin')

    if "LoggedInUserId" in request.session: #otprije smo registrirani
        return redirect('/')
    context={}
    fetchedPolja=models.DodatnaPoljaObrasca.objects.filter().all()
    fetchedSekcije=models.Sekcija.objects.filter().all()
    context['DodatnaPolja']=fetchedPolja
    #!!
    context['sekcije']=fetchedSekcije.exclude(naziv="Admin Sekcija") #dodao sam ovo kako bih mogao implementirati select za sekcije
    ##
    print(context)
    return render(request, 'Signup.html',context)
    
def signin(request):
    if request.method == "POST":
        Username = request.POST['Username']
        pass1 = request.POST['pass1']
        try:
            if models.Korisnik.objects.filter(korisnickoIme=Username,lozinka=pass1).exists():
                LoggedInUser=models.Korisnik.objects.get(korisnickoIme=Username,lozinka=pass1)
                print(LoggedInUser.vrstaKorisnik.naziv)
                request.session['LoggedInUserId']=LoggedInUser.id
                request.session['LoggedInUserRole']=LoggedInUser.vrstaKorisnik.naziv
                if LoggedInUser.odobrenBool==False:
                    messages.warning(request,"Vaš account još nije potvređen, molimo pogledajte vaš email")
                return redirect('home')

        except:
            messages.error(request, "Korisnicko ime ili lozinka su krivi")
            return redirect('signin')
    
    context = {}
    if "randPassword" in request.session: #tek smo se registrirali
        context["randPassword"]=request.session["randPassword"]
    elif "LoggedInUserId" in request.session: #otprije smo registrirani
        return redirect('/')
        
    return render(request, 'Signin.html',context)

def signout(request):
    if 'LoggedInUserId' in request.session:
        del request.session['LoggedInUserId']
    return redirect('home')

def osobnipodaci(request):
    if request.method == "POST":
        if 'NewUserName' in request.POST:
            Username = request.POST['Username']
            LoggedInUser=models.Korisnik.objects.get(idSudionik=request.session['LoggedInUserId'])
            LoggedInUser.korisnickoIme = Username
            try:
                LoggedInUser.save()
            except IntegrityError:
                messages.error(request, "To korisnicko ime je vec u uporabi")
                return redirect('osobnipodaci')

        if 'NewFName' in request.POST:
            Fname = request.POST['Fname']
            LoggedInUser=models.Korisnik.objects.get(idSudionik=request.session['LoggedInUserId'])
            LoggedInUser.ime = Fname
            LoggedInUser.save()

        if 'NewLName' in request.POST:
            Lname = request.POST['Lname']
            LoggedInUser=models.Korisnik.objects.get(idSudionik=request.session['LoggedInUserId'])
            LoggedInUser.prezime = Lname
            LoggedInUser.save()

        if 'NewEmail' in request.POST:
            email = request.POST['email']
            LoggedInUser=models.Korisnik.objects.get(idSudionik=request.session['LoggedInUserId'])
            LoggedInUser.email = email
            try:
                LoggedInUser.save()
            except IntegrityError:
                messages.error(request, "Ta email adresa je vec u uporabi")
                return redirect('osobnipodaci')  
        return redirect('osobnipodaci')

    if "LoggedInUserId" in request.session: #ulogirani smo
        LoggedInUser=models.Korisnik.objects.get(idSudionik=request.session['LoggedInUserId'])
        context={}
        context['LoggedInUser']=request.session['LoggedInUserId']
        context['LoggedInUserRole']=request.session['LoggedInUserRole']
        context['korisnickoIme']=LoggedInUser.korisnickoIme
        context['ime']=LoggedInUser.ime
        context['prezime']=LoggedInUser.prezime
        context['email']=LoggedInUser.email
        context['uloga']=LoggedInUser.vrstaKorisnik.naziv
        context['MaticnaUstanova']=LoggedInUser.korisnikUstanova.naziv
        context['sekcija']=LoggedInUser.korisnikSekcija.naziv
    else:
        return redirect('signin')
    
    return render(request, 'OsobniPodaci.html',context)

def mojiradovi(request):
    context={}
    if "LoggedInUserId" in request.session: #ulogirani smo
        context["LoggedInUser"]=request.session['LoggedInUserId']
    else: #nismo ulogirani
        return redirect('signin')
    
    if "LoggedInUserRole" in request.session:
        if request.session['LoggedInUserRole'] != "Admin":
            context["LoggedInUserRole"]=request.session['LoggedInUserRole']
        else: #admin je
            return redirect('/') #redirect na homepage
        context["LoggedInUserRole"]=request.session['LoggedInUserRole']

    LoggedInUser=models.Korisnik.objects.get(idSudionik=request.session['LoggedInUserId'])

    fetchedRadovi=models.Rad.objects.filter(radKorisnik=LoggedInUser)
    context['fetchedRadovi']=fetchedRadovi
    fetchRecenzije=[]
    for rad in fetchedRadovi:
        if rad.recenziranBool==True:
            fetchRecenzije.append(models.Recenzija.objects.get(rad=rad))
    context['fetchedRecenzije']=fetchRecenzije
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
            updateRad.revizijaBool=True
            updateRad.save()
            
            return redirect('mojiradovi')
        if 'UploadFile' in request.POST:
            print(request.POST)
            fileTitle = request.POST["fileTitle"]
            uploadedFile = request.FILES["uploadedFile"]

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
            noviRad=models.Rad(
                naslov=fileTitle,
                pdf = uploadedFile,
                radSekcija=LoggedInUser.korisnikSekcija,
                radKorisnik=LoggedInUser
            )
            if not models.Rad.objects.filter(naslov = fileTitle,radSekcija = LoggedInUser.korisnikSekcija,radKorisnik = LoggedInUser).exists():
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
            noviRad=models.Rad.objects.get(naslov = fileTitle,radSekcija = LoggedInUser.korisnikSekcija,radKorisnik = LoggedInUser)
            
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
                    noviAutor = models.Autor.objects.get(ime=autor.ime,prezime=autor.prezime,email=autor.email)
                noviRad.autori.add(noviAutor)

            noviRad.save()
            return redirect('mojiradovi')

    
    return render(request, 'MojiRadovi.html',context)

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

def info(request):
    context={}
    if "LoggedInUserId" in request.session:
        context["LoggedInUser"]=request.session['LoggedInUserId']
    
    if "LoggedInUserRole" in request.session:
        context["LoggedInUserRole"]=request.session['LoggedInUserRole']
    print(context)
    return render(request, 'Info.html', context)

def mojerecenzije(request):
    
    context={}
    if "LoggedInUserId" in request.session: #ulogirani smo
        context["LoggedInUser"]=request.session['LoggedInUserId']
        context["LoggedInUserRole"]=request.session['LoggedInUserRole']
    else: #nismo ulogirani
        return redirect('signin')
    
    LoggedInUser=models.Korisnik.objects.get(idSudionik=request.session['LoggedInUserId'])
    recenzentSekcija = LoggedInUser.korisnikSekcija
    fetchRadovi = models.Rad.objects.filter(radSekcija=recenzentSekcija)
    fetchOcjene = models.Ocjena.objects.all()
    fetchMyRecenzije = models.Recenzija.objects.filter(recenzent=LoggedInUser)
    fetchRecenzije = models.Recenzija.objects.all()
    
    if request.method == "POST":
        print(request.POST)
        
        for rad in fetchRadovi:
            print(rad.sifRad)
            print(str(rad.sifRad) in request.POST)
            if str(rad.sifRad) in request.POST:        
                ocjena=request.POST[str(rad.sifRad) + "ocjena"]
                obrazlozenje=request.POST[str(rad.sifRad) + "obrazlozenje"]
                newRecenzija=models.Recenzija(
                    ocjena = models.Ocjena.objects.get(znacenje=ocjena),
                    obrazlozenje = obrazlozenje,
                    recenzent = LoggedInUser,
                    rad = rad
                )
                rad.recenziranBool=True
                rad.revizijaBool=False
                rad.save()
                newRecenzija.save()
        return redirect('mojerecenzije')

    for rad in fetchRadovi:
        print(rad in fetchRecenzije)

    context['fetchedOcjene']=fetchOcjene
    context['fetchedRadovi']=fetchRadovi
    context['fetchedMyRecenzije']=fetchMyRecenzije
    context['fetchedRecenzije']=fetchRecenzije
    
    return render(request, 'MojeRecenzije.html', context)

def pregled(request):
    context={}
    if "LoggedInUserId" in request.session:
        context["LoggedInUser"]=request.session['LoggedInUserId']
    
    if "LoggedInUserRole" in request.session:
        context["LoggedInUserRole"]=request.session['LoggedInUserRole']
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

    """Shvatio sam da je puno lakse napravit ovo nego stavljat naziv unutar templatea"""
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
    return render(request, 'Sudionici.html', context)

def radovi(request):
    context={}
    if "LoggedInUserId" in request.session:
        context["LoggedInUser"]=request.session['LoggedInUserId']
    
    if "LoggedInUserRole" in request.session:
        context["LoggedInUserRole"]=request.session['LoggedInUserRole']
    return render(request, 'Radovi.html', context)