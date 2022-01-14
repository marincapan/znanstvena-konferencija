# UPUTE

U nastavku možete pronaći upute kako pokrenuti aplikaciju u razvojnom ili produkcijskom okruženju.

## Lokalno pokretanje

### Docker

1. [Preuzmite Docker](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe) (za Windows i Mac sustave) i instalirajte ga. Za Linux sustave možete to odraditi pomoću naredbe: 
`sudo apt-get install docker-ce docker-ce-cli containerd.io`
2. [Preuzmite](https://git-scm.com/downloads) i instalirajte git.
3. Pozicionirajte se u mapu u koju želite klonirati repozitorij aplikacije naredbom: 
`git clone https://gitlab.com/fotoModeli/znanstvenakonferencija.git`
4. Preimenovati *.env.example* u *.env* datoteku te popuniti navedene varijable 
5. Pozicionirati se u mapu *znanstvenakonferencija* i pokrenite naredbu: `docker-compose up -d --build`

### Django

1. [Preuzmite](https://www.python.org/downloads/) i instalirajte Python.
2. [Preuzmite](https://git-scm.com/downloads) i instalirajte git.
3. Pozicionirajte se u mapu u koju želite klonirati repozitorij aplikacije naredbom: 
`git clone https://gitlab.com/fotoModeli/znanstvenakonferencija.git`
4. Pozicionirati se u radni direktorij repozitorija i pokrenuti naredbu `python -m venv venv` 

## Produkcijsko pokretanje
