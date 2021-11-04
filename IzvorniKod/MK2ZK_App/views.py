from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.utils.crypto import get_random_string


# Create your views here.
def home(request):
    if 'randPassword' in request.session:
        del request.session['randPassword']
    #Password se pokazuje jedanput i vise nikad.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_visits': num_visits,
    }
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

        #Ubaci u bazu podataka

        #messages.success(request, "Success")
        randPassword=get_random_string(length=16)
        request.session['randPassword'] = randPassword

        return redirect('signin')

    return render(request, 'Signup.html')
    
def signin(request):
    if request.method == "POST":
        Username = request.POST['Username']
        pass1 = request.POST['pass1']

        #Authentikacija usera

        return redirect('home')
    randPassword=0
    if 'randPassword' in request.session:
        randPassword=request.session['randPassword']
    context = {
            "randPassword" : randPassword,
        }
    return render(request, 'Signin.html',context)

def signout(request):
    pass