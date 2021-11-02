from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def home(request):
    return render(request, 'Index.html')

def signup(request):
    return render(request, 'Signup.html')
    
def signin(request):
    return render(request, 'Signin.html')

def signout(request):
    pass