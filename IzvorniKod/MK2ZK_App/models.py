from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.enums import Choices
from django.db.models.fields.related import ForeignKey

# Create your models here.
class Sekcija(models.Model):
    sifSekcija = models.AutoField(primary_key=True)
    nazivSekcija = models.CharField(max_length=50)

class Ustanova(models.Model):
    sifUstanova = models.AutoField(primary_key=True)
    nazivUstanova = models.CharField(max_length=50)
    gradUstanova = models.CharField(max_length=50)
    drzavaUstanova = models.CharField(max_length=50)
    adresaUstanova = models.CharField(max_length=50)

class Autor(models.Model):
    sifAutor = models.AutoField(primary_key=True)
    ime = models.CharField(max_length=50)
    prezime = models.CharField(max_length=50)
    email = models.CharField(max_length=50,unique=True)

class PoljaObrasca(models.Model):
    IDPolja = models.AutoField(primary_key=True)
    ime = models.CharField(max_length=50)
    prezime = models.CharField(max_length=50)
    obaveznoBool = models.BooleanField(default=False)

def increment_KorisnikID():
  last_korisnik = Korisnik.objects.all().order_by('id').last()
  if not last_korisnik:
    return '0000'
  korisnik_id = last_korisnik.idSudionik
  korisnik_int = int(korisnik_id)
  new_korisnik_int = korisnik_int + 1
  new_korisnik_id =str(new_korisnik_int).zfill(4)
  return new_korisnik_id

class Korisnik(models.Model):
    id = models.AutoField(primary_key=True)
    korisnickoIme = models.CharField(max_length=50, unique=True)
    lozinka = models.CharField(max_length=50)
    ime = models.CharField(max_length=50)
    prezime = models.CharField(max_length=50)
    email = models.CharField(max_length=50, unique=True)
    idSudionik = models.CharField(max_length=10, default=increment_KorisnikID)
    odobrenBool = models.BooleanField(default=False)
    class VrstaKorisnika(models.IntegerChoices):
        ADMIN = 1
        PRESJEDAVAJUĆI = 2
        RECENZENT = 3
        SUDIONIK = 4
    vrstaKorisnik = models.IntegerField(choices=VrstaKorisnika.choices)
    korisnikUstanova = models.ForeignKey('Ustanova',on_delete=models.CASCADE)
    korisnikSekcija = models.ForeignKey('Sekcija',on_delete=models.CASCADE)

class Rad(models.Model):
    sifRad = models.AutoField(primary_key=True)
    naslov = models.CharField(max_length=50)
    recinziranBool = models.BooleanField(default=False)
    pdf = models.FileField(upload_to="Radovi/")
    radSekcija=models.ForeignKey("Sekcija", on_delete=models.CASCADE)
    radKorisnik=models.ForeignKey("Korisnik", on_delete=models.CASCADE)
class Konferencija(models.Model):
    sifKonferencija = models.AutoField(primary_key=True)
    nazivKonferencije = models.CharField(max_length=50)
    opisKonferencije = models.CharField(max_length=1000)
    datumKonferencije = models.DateField()
    rokPrijave = models.DateField()



