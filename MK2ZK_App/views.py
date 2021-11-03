from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages


# Create your views here.
def home(request):
    return render(request, 'Index.html')

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

        return redirect('signin')

    return render(request, 'Signup.html')
    
def signin(request):
    if request.method == "POST":
        Username = request.POST['Username']
        pass1 = request.POST['pass1']

        #Authentikacija usera

        return redirect('home')
    return render(request, 'Signin.html')

def signout(request):
    pass