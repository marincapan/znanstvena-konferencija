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



# Create your views here.
def home(request):
    fetchedPolja=models.DodatnaPoljaObrasca.objects.filter().all()
    if 'randPassword' in request.session:
        del request.session['randPassword']
    #Password se pokazuje jedanput i vise nikad.

    context={}
    if "LoggedInUserId" in request.session:
        context["LoggedInUser"]=request.session['LoggedInUserId']
    
    if "LoggedInUserRole" in request.session:
        context["LoggedInUserRole"]=request.session['LoggedInUserRole']
    context['DodatnaPolja']=fetchedPolja
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
                NoviKorisnik = models.Korisnik(korisnickoIme=username,lozinka=randPassword,ime=fName,prezime=lName,email=email,vrstaKorisnik=models.Uloga.objects.get(naziv=uloga), korisnikUstanova=Ustanova, korisnikSekcija=Sekcija)
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
    context['sekcije']=fetchedSekcije #dodao sam ovo kako bih mogao implementirati select za sekcije
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
                request.session['LoggedInUserId']=LoggedInUser.idSudionik
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

def osobnipodatci(request):
    if request.method == "POST":

        if 'NewUserName' in request.POST:
            Username = request.POST['Username']
            LoggedInUser=models.Korisnik.objects.get(idSudionik=request.session['LoggedInUserId'])
            LoggedInUser.korisnickoIme = Username
            try:
                LoggedInUser.save()
            except IntegrityError:
                messages.error(request, "To korisnicko ime je vec u uporabi")
                return redirect('osobnipodatci')

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
                return redirect('osobnipodatci')  
        return redirect('osobnipodatci')

    if "LoggedInUserId" in request.session: #ulogirani smo
        LoggedInUser=models.Korisnik.objects.get(idSudionik=request.session['LoggedInUserId'])
        context={}
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
    
    return render(request, 'OsobniPodatci.html',context)

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
    fetchedPolja=models.DodatnaPoljaObrasca.objects.filter().all()

    fetchedRadovi=models.Rad.objects.filter(radKorisnik=LoggedInUser)
    for rad in fetchedRadovi:
        print(rad.pdf)
        context['pdf']=rad.pdf
    context['fetchedRadovi']=fetchedRadovi

    if request.method == "POST":
        if 'UploadFile' in request.POST:
            if len(fetchedRadovi) >= 1 and fetchedRadovi[0].pdf: #jedan rad i ima pdf
                
                fileTitle = request.POST["fileTitle"]
                uploadedFile = request.FILES["uploadedFile"]

                rad = models.Rad(
                    naslov = fileTitle,
                    pdf = uploadedFile,
                    radSekcija = LoggedInUser.korisnikSekcija,
                    radKorisnik = LoggedInUser
                )
                if not models.Rad.objects.filter(naslov = fileTitle,pdf = uploadedFile,radSekcija = LoggedInUser.korisnikSekcija,radKorisnik = LoggedInUser).exists():
                    print("Flag2")
                    rad.save()
                return redirect('mojiradovi')
            else: #jedan rad, ali nema pdf
                uploadedFile = request.FILES["uploadedFile"]
                for rad in fetchedRadovi:
                    rad.pdf = uploadedFile
                    rad.save()
                
                return redirect('mojiradovi')
            
        if 'AddNewField' in request.POST:
            fieldName = request.POST["fieldName"]
            fieldType = request.POST["fieldType"]
            if not models.DodatnaPoljaObrasca.objects.filter(imePolja=fieldName,tipPolja=fieldType).exists():
                newField=models.DodatnaPoljaObrasca(
                    imePolja=fieldName,
                    tipPolja=fieldType
                )
                newField.save()
        if 'ActiveFields' in request.POST:
            for polje in fetchedPolja:
                try:
                    checked = request.POST[polje.imePolja]
                    checked = True 
                except:
                    checked = False
                polje.active = checked
                polje.save()
    
    for polje in fetchedPolja:
        print(polje.imePolja)        
    context['DodatnaPolja']=fetchedPolja
    
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
    context['DodatnaPolja']=fetchedPolja

    if request.method == "POST":            
        if 'AddNewField' in request.POST:
            fieldName = request.POST["fieldName"]
            fieldType = request.POST["fieldType"]
            if not models.DodatnaPoljaObrasca.objects.filter(imePolja=fieldName,tipPolja=fieldType).exists():
                newField=models.DodatnaPoljaObrasca(
                    imePolja=fieldName,
                    tipPolja=fieldType
                )
                newField.save()
        if 'ActiveFields' in request.POST:
            for polje in fetchedPolja:
                try:
                    checked = request.POST[polje.imePolja]
                    checked = True 
                except:
                    checked = False
                polje.active = checked
                polje.save()
    
    return render(request, 'SloziObrazac.html', context)

def info(request):
    context={}
    if "LoggedInUserId" in request.session:
        context["LoggedInUser"]=request.session['LoggedInUserId']
    
    if "LoggedInUserRole" in request.session:
        context["LoggedInUserRole"]=request.session['LoggedInUserRole']
    print(context)
    return render(request, 'Info.html', context)
