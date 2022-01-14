# UPUTE

U nastavku možete pronaći upute kako pokrenuti aplikaciju u razvojnom ili produkcijskom okruženju.

## Lokalno pokretanje

### Docker alat

1. [Preuzmite Docker](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe) (za Windows i Mac sustave) i instalirajte ga. Za Linux sustave možete to odraditi pomoću naredbe: 
`sudo apt-get install docker-ce docker-ce-cli containerd.io`
2. [Preuzmite](https://git-scm.com/downloads) i instalirajte git.
3. Pozicionirajte se u mapu u koju želite klonirati repozitorij aplikacije naredbom: 
`git clone https://gitlab.com/fotoModeli/znanstvenakonferencija.git`
4. Unutar mape *IzvorniKod* preimenovati *.env.example* u *.env* datoteku te popuniti varijable u datoteci
7. Unutar mape *IzvorniKod* povjeriti je li način čitanja datoteke *docker-entrypoint.sh* postavljen na Unix način (LF) te ako nije, tako ga treba postaviti.
5. Pozicionirati se u mapu *znanstvenakonferencija* i pokrenite naredbu: `docker-compose up -d --build`


## Produkcijsko pokretanje

Koraci za produkcijsko pokretanje su jednaki koracima za lokalno pokretnaje s Docker alatom s time da se u varijablima okruženjatrebaju promijeniti podaci koji su odgovarajući produkcijskom okruženju.

