# Generated by Django 3.2.9 on 2021-11-12 12:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MK2ZK_App', '0007_delete_poljaobrasca'),
    ]

    operations = [
        migrations.CreateModel(
            name='DodatnaPoljaObrasca',
            fields=[
                ('sifPolja', models.AutoField(primary_key=True, serialize=False)),
                ('imePolja', models.CharField(max_length=50)),
                ('tipPolja', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ActiveDodatnaPolja',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('obavezan', models.BooleanField(default=False)),
                ('dodatnoPolje', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MK2ZK_App.dodatnapoljaobrasca')),
            ],
        ),
    ]