from os import truncate
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.enums import Choices
from django.db.models.fields import BooleanField
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.utils.crypto import get_random_string

# Create your models here.
class Sekcija(models.Model):
    sifSekcija = models.AutoField(primary_key=True)
    naziv = models.CharField(max_length=50)
    konferencijaSekcija = models.ForeignKey('Konferencija',on_delete=models.CASCADE)

class Ustanova(models.Model):
    sifUstanova = models.AutoField(primary_key=True)
    naziv = models.CharField(max_length=50)
    grad = models.CharField(max_length=50)
    drzava = models.CharField(max_length=50)
    adresa = models.CharField(max_length=50)

class Autor(models.Model):
    sifAutor = models.AutoField(primary_key=True)
    ime = models.CharField(max_length=50)
    prezime = models.CharField(max_length=50)
    email = models.CharField(max_length=50,unique=True)


class Korisnik(models.Model):
    id = models.AutoField(primary_key=True)
    korisnickoIme = models.CharField(max_length=50, unique=True) 
    lozinka = models.CharField(max_length=50)
    ime = models.CharField(max_length=50)
    prezime = models.CharField(max_length=50)
    email = models.CharField(max_length=50, unique=True)
    idSudionik = models.CharField(max_length=10)
    odobrenBool = models.BooleanField(default=False)
    potvrdenBool = models.BooleanField(default=False)
    vrstaKorisnik = models.ForeignKey('Uloga',on_delete=models.CASCADE)
    korisnikUstanova = models.ForeignKey('Ustanova',on_delete=models.CASCADE)
    korisnikSekcija = models.ForeignKey('Sekcija',on_delete=models.CASCADE)
    token=models.CharField(max_length=50)
    dodatniPodatak = ManyToManyField("DodatnaPoljaObrasca",through='DodatniPodatci')

class Uloga(models.Model):
    id = models.AutoField(primary_key=True)
    naziv = models.CharField(max_length=50)

def custom_directory(instance, filename):
    return 'user_{0}/{1}/{2}'.format(instance.radKorisnik.id,get_random_string(length=8), filename)

class Rad(models.Model):
    sifRad = models.AutoField(primary_key=True)
    naslov = models.CharField(max_length=500)
    recenziranBool = models.BooleanField(default=False)
    pdf = models.FileField(upload_to=custom_directory)
    radSekcija = models.ForeignKey("Sekcija", on_delete=models.CASCADE)
    radKorisnik = models.ForeignKey("Korisnik", on_delete=models.CASCADE)
    autori = models.ManyToManyField(Autor,through="AutorRad")
    revizijaBool = models.BooleanField(default=False)

class AutorRad(models.Model):
    Autor = models.ForeignKey("Autor", on_delete=models.CASCADE)
    Rad = models.ForeignKey("Rad",on_delete=models.CASCADE)
    OZK = models.BooleanField(default=False)

class Konferencija(models.Model):
    sifKonferencija = models.AutoField(primary_key=True)
    nazivKonferencije = models.CharField(max_length=50)
    opisKonferencije = models.CharField(max_length=1000)
    datumKonferencije = models.DateField()
    rokPrijave = models.DateField()
    rokRecenzenti = models.DateField()
    rokAdmin = models.DateField()
    rokPocRecenzija = models.DateField()
    rokPocPrijava = models.DateField()

class TipPoljaObrasca(models.Model):
    id = models.AutoField(primary_key=True)
    naziv = models.CharField(max_length=50)

class DodatnaPoljaObrasca(models.Model):
    sifPolja = models.AutoField(primary_key=True)
    imePolja = models.CharField(max_length=50)
    tipPolja = models.ForeignKey("TipPoljaObrasca", on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    obavezan = models.BooleanField(default=False)

class Recenzija(models.Model):
    sifRecenzija = models.AutoField(primary_key=True)
    ocjena = models.ForeignKey("Ocjena",on_delete=models.CASCADE)
    obrazlozenje = models.CharField(max_length=500)
    recenzent = models.ForeignKey("Korisnik",on_delete=models.CASCADE)
    rad = models.ForeignKey("Rad",on_delete=models.CASCADE)

class DodatniPodatci(models.Model):
    korisnik = models.ForeignKey("Korisnik",on_delete=models.CASCADE)
    poljeObrasca = models.ForeignKey("DodatnaPoljaObrasca", on_delete=models.CASCADE)
    podatak = models.CharField(max_length=50)

class Ocjena(models.Model):
    id = models.AutoField(primary_key=True)
    znacenje = models.CharField(max_length=500)