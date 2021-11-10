CREATE TABLE Sekcija
(
  sifSekcija INT,
  nazivSekcija VARCHAR(50),
  PRIMARY KEY (sifSekcija)
);

CREATE TABLE Ustanova
(
  sifUstanova INT,
  nazivUstanova VARCHAR(50),
  grad VARCHAR(50),
  drzava VARCHAR(50),
  adresa VARCHAR(50),
  PRIMARY KEY (sifUstanova)
);

CREATE TABLE Autor
(
  sifAutor INT,
  ime VARCHAR(50),
  prezime VARCHAR(50),
  email VARCHAR(50),
  naznakaOZK INT,
  PRIMARY KEY (sifAutor),
  UNIQUE (email)
);

CREATE TABLE PoljaObrasca
(
  ID INT,
  naziv VARCHAR(50),
  tipolja VARCHAR(50),
  obavezno boolean,
  PRIMARY KEY (ID)
);

CREATE TABLE Korisnik
(
  korisnickoIme VARCHAR(50),
  lozinka VARCHAR(50),
  ime VARCHAR(50),
  prezime VARCHAR(50),
  email VARCHAR(50),
  idSudionik INT ,
  odobren boolean,
  vrstaKorisnik INT,
  sifUstanova INT,
  sifSekcija INT,
  PRIMARY KEY (korisnickoIme),
  FOREIGN KEY (sifUstanova) REFERENCES Ustanova(sifUstanova),
  FOREIGN KEY (sifSekcija) REFERENCES Sekcija(sifSekcija),
  UNIQUE (email),
  UNIQUE (idSudionik)
);

CREATE TABLE Rad
(
  sifRad INT,
  naslov VARCHAR(50),
  ocjena INT,
  recenziran boolean,
  obrazlozenje VARCHAR(500),
  recenzent VARCHAR(50),
  PRIMARY KEY (sifRad),
  FOREIGN KEY (recenzent) REFERENCES Korisnik(korisnickoIme)
);

CREATE TABLE PrijavaRada
(
  
  sifSekcija INT,
  sifRad INT,
  korisnickoIme VARCHAR(50),
  PRIMARY KEY (korisnickoIme, sifRad),
  FOREIGN KEY (korisnickoIme) REFERENCES Korisnik(korisnickoIme),
  FOREIGN KEY (sifRad) REFERENCES Rad(sifRad),
  FOREIGN KEY (sifSekcija) REFERENCES Sekcija(sifSekcija),
  UNIQUE (sifRad, sifSekcija)
);

CREATE TABLE Konferencija
(
  sifKonferencija INT,
  nazivKonferencija VARCHAR(50) ,
  opisKonferencija VARCHAR(1000),
  datumKonferencija DATE ,
  rokPrijava DATE ,
  predsjedavajuci VARCHAR(50) ,
  PRIMARY KEY (sifKonferencija),
  FOREIGN KEY (predsjedavajuci) REFERENCES Korisnik(korisnickoIme)
);

CREATE TABLE AutorRad
(
  sifRad INT ,
  sifAutor INT,
  PRIMARY KEY (sifRad, sifAutor),
  FOREIGN KEY (sifRad) REFERENCES Rad(sifRad),
  FOREIGN KEY (sifAutor) REFERENCES Autor(sifAutor)
);