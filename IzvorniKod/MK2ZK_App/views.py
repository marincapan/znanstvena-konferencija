from collections import defaultdict
from typing import DefaultDict
from django.core.checks.messages import Error
from django.db.models.fields import NullBooleanField
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
    if 'randPassword' in request.session:
        del request.session['randPassword']
    #Password se pokazuje jedanput i vise nikad.

    context={}
    if "LoggedInUserId" in request.session:
        context["LoggedInUser"]=request.session['LoggedInUserId']
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
        authors = request.POST['authors']
        emailCon = request.POST['emailCon']
        Section = request.POST['section']

        if uloga=='sudionik':
            uloga=4
        else:
            uloga=3
        
        randPassword=get_random_string(length=16)
        request.session['randPassword'] = randPassword
        Ustanova = models.Ustanova(nazivUstanova=matustName,adresaUstanova=matustAdr,gradUstanova=matustCity,drzavaUstanova=matustDrz)
        if models.Ustanova.objects.filter(nazivUstanova=matustName,adresaUstanova=matustAdr,gradUstanova=matustCity,drzavaUstanova=matustDrz).exists:
            Ustanova = models.Ustanova.objects.get(nazivUstanova=matustName,adresaUstanova=matustAdr,gradUstanova=matustCity,drzavaUstanova=matustDrz)
        Sekcija = models.Sekcija(nazivSekcija=Section)
        if  models.Sekcija.objects.filter(nazivSekcija=Section).exists:
            Sekcija=models.Sekcija.objects.get(nazivSekcija=Section)
        try:
            NoviKorisnik = models.Korisnik(korisnickoIme=Username,lozinka=randPassword,ime=Fname,prezime=Lname,email=email,vrstaKorisnik=uloga, korisnikUstanova=Ustanova, korisnikSekcija=Sekcija)
            NoviKorisnik.save()
        except IntegrityError:
            messages.error(request, "Korisnicko ime ili email je vec u uporabi")
            return redirect('signup')
           

        messages.success(request, "Success")

        return redirect('signin')

    return render(request, 'Signup.html')
    
def signin(request):
    if request.method == "POST":
        Username = request.POST['Username']
        pass1 = request.POST['pass1']

        if models.Korisnik.objects.filter(korisnickoIme=Username,lozinka=pass1).exists:
            LoggedInUser=models.Korisnik.objects.get(korisnickoIme=Username,lozinka=pass1)
            request.session['LoggedInUserId']=LoggedInUser.idSudionik
            if LoggedInUser.odobrenBool==False:
                messages.warning(request,"Vaš account još nije potvređen, molimo pogledajte vaš email")
                return redirect('home')

        else:
            messages.error(request, "Korisnicko ime ili lozinka su krivi")
            return redirect('signin')
    
    context = {}
    if "randPassword" in request.session:
        context["randPassword"]=request.session["randPassword"]
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

    LoggedInUser=models.Korisnik.objects.get(idSudionik=request.session['LoggedInUserId'])
    context={}
    context['korisnickoIme']=LoggedInUser.korisnickoIme
    context['ime']=LoggedInUser.ime
    context['prezime']=LoggedInUser.prezime
    context['email']=LoggedInUser.email
    if LoggedInUser.vrstaKorisnik==4:
        uloga="Sudionik"
    elif LoggedInUser.vrstaKorisnik==3:
        uloga="Recenzent"
    elif LoggedInUser.vrstaKorisnik==2:
        uloga="Presjedavajući"
    else:
        uloga="Admin"
    context['uloga']=uloga
    context['MaticnaUstanova']=LoggedInUser.korisnikUstanova.nazivUstanova
    
    return render(request, 'OsobniPodatci.html',context)

def mojiradovi(request):
    LoggedInUser=models.Korisnik.objects.get(idSudionik=request.session['LoggedInUserId'])
    if request.method == "POST":
        fileTitle = request.POST["fileTitle"]
        uploadedFile = request.FILES["uploadedFile"]

        rad = models.Rad(
            naslov = fileTitle,
            pdf = uploadedFile,
            radSekcija = LoggedInUser.korisnikSekcija,
            radKorisnik = LoggedInUser
        )
        rad.save()
        redirect('mojiradovi')
    context={}
    fetchedRad=models.Rad.objects.get(radKorisnik=LoggedInUser)
    print(fetchedRad.naslov)
    context['filelocation']=fetchedRad.pdf
    context['filetitle']=fetchedRad.naslov
    return render(request, 'MojiRadovi.html',context)