# Generated by Django 3.2.9 on 2021-11-07 19:05

import IzvorniKod.MK2ZK_App.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Autor',
            fields=[
                ('sifAutor', models.AutoField(primary_key=True, serialize=False)),
                ('ime', models.CharField(max_length=50)),
                ('prezime', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Konferencija',
            fields=[
                ('sifKonferencija', models.AutoField(primary_key=True, serialize=False)),
                ('nazivKonferencije', models.CharField(max_length=50)),
                ('opisKonferencije', models.CharField(max_length=1000)),
                ('datumKonferencije', models.DateField()),
                ('rokPrijave', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='PoljaObrasca',
            fields=[
                ('IDPolja', models.AutoField(primary_key=True, serialize=False)),
                ('ime', models.CharField(max_length=50)),
                ('prezime', models.CharField(max_length=50)),
                ('obaveznoBool', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Rad',
            fields=[
                ('sifRad', models.AutoField(primary_key=True, serialize=False)),
                ('naslov', models.CharField(max_length=50)),
                ('recinziranBool', models.BooleanField(default=False)),
                ('ocjena', models.IntegerField()),
                ('obrazlozenje', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Sekcija',
            fields=[
                ('sifSekcija', models.AutoField(primary_key=True, serialize=False)),
                ('nazivSekcija', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Ustanova',
            fields=[
                ('sifUstanova', models.AutoField(primary_key=True, serialize=False)),
                ('nazivUstanova', models.CharField(max_length=50)),
                ('grad', models.CharField(max_length=50)),
                ('drzava', models.CharField(max_length=50)),
                ('adresa', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Korisnik',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('korisnickoIme', models.CharField(max_length=50, unique=True)),
                ('lozinka', models.CharField(max_length=50)),
                ('ime', models.CharField(max_length=50)),
                ('prezime', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=50, unique=True)),
                ('idSudionik', models.CharField(max_length=10)),
                ('odobrenBool', models.BooleanField(default=False)),
                ('vrstaKorisnik', models.IntegerField(choices=[(1, 'Admin'), (2, 'Presjedavajući'), (3, 'Recenzent'), (4, 'Sudionik')])),
                ('korisnikSekcija', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MK2ZK_App.sekcija')),
                ('korisnikUstanova', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MK2ZK_App.ustanova')),
            ],
        ),
    ]
