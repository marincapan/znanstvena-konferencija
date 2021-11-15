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
        Username = request.POST['Username']
        Fname = request.POST['Fname']
        Lname = request.POST['Lname']
        email = request.POST['email']
        matustName = request.POST['matustName']
        matustAdr = request.POST['matustAdr']
        matustCity = request.POST['matustCity']
        matustDrz = request.POST['matustDrz']
        uloga = request.POST['uloga']
        title = request.POST['title']
        emailCon = request.POST['emailCon']
        Section = request.POST['section']
        numOfAuthors = request.POST["numOfAuthors"]

        if uloga=='sudionik':
            uloga="Sudionik"
        else:
            uloga="Recezent"
        
        randPassword=get_random_string(length=16)
        request.session['randPassword'] = randPassword
        Ustanova = models.Ustanova(naziv=matustName,adresa=matustAdr,grad=matustCity,drzava=matustDrz)
        if models.Ustanova.objects.filter(naziv=matustName,adresa=matustAdr,grad=matustCity,drzava=matustDrz).exists():
            Ustanova = models.Ustanova.objects.get(naziv=matustName,adresa=matustAdr,grad=matustCity,drzava=matustDrz)
        else:
            Ustanova.save()
        Sekcija = models.Sekcija(naziv=Section,konferencijaSekcija=models.Sekcija.objects.get(naziv=Section).konferencijaSekcija)
        if  models.Sekcija.objects.filter(naziv=Section).exists():
            Sekcija=models.Sekcija.objects.get(naziv=Section)
        else:
            print(Sekcija)
            Sekcija.save()
        try:
            NoviKorisnik = models.Korisnik(korisnickoIme=Username,lozinka=randPassword,ime=Fname,prezime=Lname,email=email,vrstaKorisnik=models.Uloga.objects.get(naziv=uloga), korisnikUstanova=Ustanova, korisnikSekcija=Sekcija)
            NoviKorisnik.save()
        except IntegrityError:
            messages.error(request, "Korisnicko ime ili email je vec u uporabi")
            return redirect('signup')
           

        noviRad=models.Rad(
            naslov=title,
            radSekcija=Sekcija,
            radKorisnik=NoviKorisnik
        )
        if not models.Rad.objects.filter(naslov=title, radSekcija=Sekcija,radKorisnik=NoviKorisnik).exists():
            noviRad.save()
        else:
            messages.error(request, "Rad s tim naslovom na toj sekciji već postoji")
            return redirect('signup')
        noviRad=models.Rad.objects.get(naslov=title, radSekcija=Sekcija,radKorisnik=NoviKorisnik)


        authorName= request.POST["authorName"]
        authorLName= request.POST["authorLname"]
        authoremail= request.POST["emailautora"]
        
        noviAutori=[]
        
        print(authorName,authorLName,authoremail)
        if not models.Autor.objects.filter(ime=authorName,prezime=authorLName,email=authoremail).exists():
            newAutor = models.Autor(
                ime = authorName,
                prezime = authorLName,
                email = authoremail
            )
            noviAutori.append(newAutor)
            newAutor.save()
            noviRad.autori.add(newAutor)
            noviRad.save()
            noviRad=models.Rad.objects.get(naslov=title, radSekcija=Sekcija,radKorisnik=NoviKorisnik)



        for i in range(1,int(numOfAuthors)):
            name="authorName{}".format(i+1)
            Lname="authorLname{}".format(i+1)
            email="emailautora{}".format(i+1)
            authorName= request.POST[name]
            authorLName= request.POST[Lname]
            authoremail= request.POST[email]
            print(authorName,authorLName,authoremail)
            if not models.Autor.objects.filter(ime=authorName,prezime=authorLName,email=authoremail).exists():
                newAutor = models.Autor(
                    ime = authorName,
                    prezime = authorLName,
                    email = authoremail
                )
                noviAutori.append(newAutor)
                newAutor.save()
                noviRad.autori.add(newAutor)
                noviRad.save()
                noviRad=models.Rad.objects.get(naslov=title, radSekcija=Sekcija,radKorisnik=NoviKorisnik)


        for autor in noviAutori:
            if autor.email==emailCon:
                saveAutor=models.Autor.objects.get(sifAutor=autor.sifAutor)
                saveAutor.OZK=True
                saveAutor.save()
        
        noviAutori.clear()
        noviRad.save()

        messages.success(request, "Success")

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