CREATE TABLE Ustanova
(
  ID INT,
  naziv VARCHAR,
  grad VARCHAR,
  drzava VARCHAR,
  adresa VARCHAR,
  PRIMARY KEY (ID)
);

CREATE TABLE Konferencija
(
  ID INT,
  naziv VARCHAR,
  opis VARCHAR,
  datum DATE,
  rokPrijava TIMESTAMP,
  pocetakPrijava TIMESTAMP,
  rokAdmin TIMESTAMP,
  pocetakRecenzent TIMESTAMP,
  rokRecenzent TIMESTAMP,
  
  PRIMARY KEY (ID)
  
);

CREATE TABLE Sekcija
(
  ID INT,
  naziv VARCHAR,
  sifKonferencija INT,
  PRIMARY KEY (ID),
  FOREIGN KEY (sifKonferencija) REFERENCES Konferencija(ID)
);
CREATE TABLE Autor
(
  ID INT,
  ime VARCHAR,
  prezime VARCHAR,
  email VARCHAR,
  PRIMARY KEY (ID),
  UNIQUE (email)
);
CREATE TABLE TipPoljeObrasca
(
  ID INT,
  naziv VARCHAR,
  PRIMARY KEY (ID)
);
CREATE TABLE DodatnoPoljeObrasca
(
  ID INT,
  ime VARCHAR,
  tipPolja INT,
  obavezno BOOLEAN,
  prisutno BOOLEAN,
  PRIMARY KEY (ID),
  FOREIGN KEY (tipPolja) REFERENCES TipPoljeObrasca(ID)
);



CREATE TABLE Uloga
(
  ID INT,
  naziv VARCHAR,
  PRIMARY KEY (ID)
);
CREATE TABLE Korisnik
(
  ID INT,
  korisnickoIme VARCHAR,
  lozinka VARCHAR,
  ime VARCHAR,
  prezime VARCHAR,
  email VARCHAR,
  idSudionik INT,
  odobren BOOLEAN,
  token VARCHAR,
  potvrdioPrijava BOOLEAN,
  sifUstanova INT,
  sifSekcija INT,
  ulogaKorisnik INT,
  PRIMARY KEY (ID),
  FOREIGN KEY (sifUstanova) REFERENCES Ustanova(ID),
  FOREIGN KEY (sifSekcija) REFERENCES Sekcija(ID),
  FOREIGN KEY (ulogaKorisnik) REFERENCES Uloga(ID),
  UNIQUE (email),
  UNIQUE (idSudionik),
  UNIQUE (korisnickoIme)
);
CREATE TABLE Ocjena
(
  ID INT,
  znacenje VARCHAR,
  PRIMARY KEY (ID)
);


CREATE TABLE Rad
(
  ID INT,
  naslovRad VARCHAR,
  pdf VARCHAR UNIQUE,
  sifSekcija INT,
  prijavioID INT,
  recenziran BOOLEAN,
  PRIMARY KEY (ID),
  FOREIGN KEY (sifSekcija) REFERENCES Sekcija(ID),
  FOREIGN KEY (prijavioID) REFERENCES Korisnik(ID)
);




CREATE TABLE AutorRad
(
  sifRad INT,
  sifAutor INT,
  naznakaOZK BOOLEAN,
  PRIMARY KEY (sifRad, sifAutor),
  FOREIGN KEY (sifRad) REFERENCES Rad(ID),
  FOREIGN KEY (sifAutor) REFERENCES Autor(ID)
  
);
CREATE TABLE DodatniPodatak
(
  korisnikID INT,
  poljeObrascaID INT,
  PRIMARY KEY (korisnikID, poljeObrascaID),
  FOREIGN KEY (korisnikID) REFERENCES Korisnik(ID),
  FOREIGN KEY (poljeObrascaID) REFERENCES DodatnoPoljeObrasca(ID)
  
);

CREATE TABLE Recenzija
(
  ID INT,
  ocjena INT,
  obrazlozenje VARCHAR,
  sifRad INT,
  recenzentID INT,
  PRIMARY KEY (ID),
  FOREIGN KEY (recenzentID) REFERENCES Korisnik(ID),
  FOREIGN KEY (sifRad) REFERENCES Rad(ID)
);

CREATE TABLE Clanak
(
	ID INT,
	naslov VARCHAR,
	tekst VARCHAR,
	autor INT,
	prisutan BOOLEAN,
	FOREIGN KEY (autor) REFERENCES Korisnik(ID)
);
