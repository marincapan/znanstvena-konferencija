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
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        #Ubaci u bazu podataka

        #messages.success(request, "Success")

        return redirect('signin')

    return render(request, 'Signup.html')
    
def signin(request):
    return render(request, 'Signin.html')

def signout(request):
    pass