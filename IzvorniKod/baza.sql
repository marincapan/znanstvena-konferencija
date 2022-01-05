CREATE TABLE "Ustanova" (
  "ID" INT PRIMARY KEY,
  "naziv" VARCHAR,
  "grad" VARCHAR,
  "drzava" VARCHAR,
  "adresa" VARCHAR
);

CREATE TABLE "Autor" (
  "ID" INT PRIMARY KEY,
  "ime" VARCHAR,
  "prezime" VARCHAR,
  "email" VARCHAR UNIQUE
);

CREATE TABLE "TipPoljeObrasca" (
  "ID" INT PRIMARY KEY,
  "nazivTipa" VARCHAR
);

CREATE TABLE "DodatnoPoljeObrasca" (
  "ID" INT PRIMARY KEY,
  "ime" VARCHAR,
  "tipPolja" INT,
  "obavezno" BOOLEAN,
  "prisutno" BOOLEAN
);

CREATE TABLE "Uloga" (
  "ID" INT PRIMARY KEY,
  "naziv" VARCHAR
);

CREATE TABLE "Korisnik" (
  "ID" INT PRIMARY KEY,
  "korisnickoIme" VARCHAR UNIQUE,
  "lozinka" VARCHAR,
  "ime" VARCHAR,
  "prezime" VARCHAR,
  "email" VARCHAR UNIQUE,
  "sudionikID" INT UNIQUE,
  "odobren" BOOLEAN,
  "token" VARCHAR,
  "potvrdioPrijava" BOOLEAN,
  "salt" BYTEA,
  "zadnjaaktivnost" TIMESTAMP,
  "sifUstanova" INT,
  "sifSekcija" INT,
  "ulogaKorisnik" INT
);

CREATE TABLE "Rad" (
  "ID" INT PRIMARY KEY,
  "naslov" VARCHAR,
  "pdf" VARCHAR UNIQUE,
  "recenziran" BOOLEAN,
  "revizija" BOOLEAN,
  "sifSekcija" INT,
  "prijavioID" INT
);

CREATE TABLE "Sekcija" (
  "ID" INT PRIMARY KEY,
  "naziv" VARCHAR,
  "sifKonferencija" INT
);

CREATE TABLE "Konferencija" (
  "ID" INT PRIMARY KEY,
  "naziv" VARCHAR,
  "opis" VARCHAR,
  "javniradovi" BOOLEAN,
  "datum" DATE,
  "pocetakRecenzent" TIMESTAMP,
  "pocetakPrijava" TIMESTAMP,
  "rokPrijava" TIMESTAMP,
  "rokAdmin" TIMESTAMP,
  "rokRecenzent" TIMESTAMP
);

CREATE TABLE "AutorRad" (
  "sifRad" INT,
  "sifAutor" INT,
  "naznakaOZK" BOOLEAN,
  PRIMARY KEY ("sifRad", "sifAutor")
);

CREATE TABLE "Recenzija" (
  "ID" INT PRIMARY KEY,
  "ocjena" INT,
  "obrazlozenje" VARCHAR,
  "recenzentID" INT,
  "sifRad" INT
);

CREATE TABLE "Ocjena" (
  "ID" INT PRIMARY KEY,
  "znacenje" VARCHAR
);

CREATE TABLE "DodatniPodatak" (
  "korisnikID" INT,
  "poljeObrascaID" INT,
  "podatak" VARCHAR,
  PRIMARY KEY ("korisnikID", "poljeObrascaID")
);

CREATE TABLE "Clanak" (
  "ID" INT PRIMARY KEY,
  "naslov" VARCHAR,
  "tekst" VARCHAR,
  "autorID" INT,
  "sifKonferencija" INT
);

ALTER TABLE "Korisnik" ADD FOREIGN KEY ("sifUstanova") REFERENCES "Ustanova" ("ID");

ALTER TABLE "Clanak" ADD FOREIGN KEY ("autorID") REFERENCES "Korisnik" ("ID");

ALTER TABLE "Korisnik" ADD FOREIGN KEY ("sifSekcija") REFERENCES "Sekcija" ("ID");

ALTER TABLE "Korisnik" ADD FOREIGN KEY ("ulogaKorisnik") REFERENCES "Uloga" ("ID");

ALTER TABLE "Recenzija" ADD FOREIGN KEY ("sifRad") REFERENCES "Rad" ("ID");

ALTER TABLE "Rad" ADD FOREIGN KEY ("sifSekcija") REFERENCES "Sekcija" ("ID");

ALTER TABLE "Rad" ADD FOREIGN KEY ("prijavioID") REFERENCES "Korisnik" ("ID");

ALTER TABLE "Sekcija" ADD FOREIGN KEY ("sifKonferencija") REFERENCES "Konferencija" ("ID");

ALTER TABLE "Clanak" ADD FOREIGN KEY ("sifKonferencija") REFERENCES "Konferencija" ("ID");

ALTER TABLE "AutorRad" ADD FOREIGN KEY ("sifRad") REFERENCES "Rad" ("ID");

ALTER TABLE "AutorRad" ADD FOREIGN KEY ("sifAutor") REFERENCES "Autor" ("ID");

ALTER TABLE "Recenzija" ADD FOREIGN KEY ("recenzentID") REFERENCES "Korisnik" ("ID");

ALTER TABLE "Recenzija" ADD FOREIGN KEY ("ocjena") REFERENCES "Ocjena" ("ID");

ALTER TABLE "DodatniPodatak" ADD FOREIGN KEY ("korisnikID") REFERENCES "Korisnik" ("ID");

ALTER TABLE "DodatnoPoljeObrasca" ADD FOREIGN KEY ("tipPolja") REFERENCES "TipPoljeObrasca" ("ID");

ALTER TABLE "DodatniPodatak" ADD FOREIGN KEY ("poljeObrascaID") REFERENCES "DodatnoPoljeObrasca" ("ID");

