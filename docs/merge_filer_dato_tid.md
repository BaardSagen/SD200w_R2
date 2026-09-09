# Sammenslåing av to datafiler basert på dato og tid

Dette dokumentet beskriver en funksjon som skal kunne implementeres i et annet program. Reglene for sammenkobling er basert på eksisterende merge-funksjon. Beskrivelsen av de to filvalgsvinduene og grønn markering er krav til brukergrensesnittet i det nye programmet.

## Formål

Koble sammen målerader fra to filer når dato og klokkeslett passer sammen innenfor en valgt tidstoleranse. Brukeren velger en hovedfil (master) og en sekundærfil. Resultatet skrives til en ny fil, og originalfilene beholdes.

## Filvalg og visning

To filvalgsvinduer eller paneler skal kunne vises samtidig:

1. **Hovedfil (master):** Viser den valgte hovedfilen med filnavn, dato, tidsperiode og antall målerader. Brukeren skal kunne velge eller bytte hovedfil. Hovedfilen bestemmer rekkefølgen og hvilke klokkeslett som beholdes i resultatet.
2. **Sekundærfil:** Lar brukeren bla i mapper og hente frem andre filer med en Windows-filvelger eller en innebygd filbrowser. Den valgte filen vises med filnavn, dato, tidsperiode og antall målerader.

Brukeren skal kunne prøve forskjellige sekundærfiler mens hovedfilen beholdes. Samme kildefil skal ikke kunne velges som begge filer.

En vanlig Windows-filvelger brukes til å finne og åpne filen. Grønn treffmarkering vises i programmets egne paneler, ikke som et krav til fargemerking inne i Windows-filvelgeren. Ved en innebygd filbrowser kan programmet også markere kontrollerte filer i fillisten.

## Automatisk kontroll og grønn markering

Når begge filer er valgt, leser programmet dem og kontrollerer dato og tidspunkt for måleradene. Kontrollen kjøres på nytt ved bytte av fil eller endring av toleranse.

Standard toleranse er **2 sekunder**, justerbar fra **0,1 til 30 sekunder**. Grensen er inklusiv: en forskjell på nøyaktig 2 sekunder godtas når toleransen er 2 sekunder.

Filene markeres **grønt**, og knappen **«Merge / Slå sammen»** aktiveres når:

- Begge filer inneholder rader med gyldige tidspunkter.
- Den tidligste gyldige måleraden i hver fil har samme kalenderdato.
- Minst ett par målerader kan kobles sammen innenfor toleransen.

Vis også en tekststatus, slik at resultatet er forståelig uten fargene. Grønn markering betyr at sammenslåing er mulig; det betyr ikke at alle rader har treff.

Før sammenslåing skal programmet vise:

- Antall sammenkoblede radpar.
- Antall rader uten treff i hver fil.
- Antall rader utelatt på grunn av manglende eller ugyldig tidspunkt, separat fra gyldige rader uten treff.
- Gjennomsnittlig og største absolutte tidsforskjell mellom treffene.

Hvis filene ikke kan kobles sammen, deaktiveres knappen, og årsaken vises. Eksempler er «Ulik startdato», «Ingen målinger innenfor toleransen», «Mangler gyldig dato og tid» eller «Filen kunne ikke leses».

## Beregning av tidspunkt for hver rad

Sammenligningen bruker målingenes dato og tid, ikke filenes opprettelsesdato eller sist endret-dato i Windows.

1. Hent startdato og starttid fra filens innleste metadata.
2. Hvis disse mangler eller er ugyldige, forsøk å hente dato og tid fra filnavnet, for eksempel `2026-09-08_12-30-00.txt`.
3. Hvis raden har et gyldig klokkeslett, kombineres dette med filens startdato.
4. Ellers beregnes tidspunktet som starttidspunkt pluss radens relative tid i minutter, omregnet og avrundet til hele sekunder.
5. Rader som ikke kan gis et gyldig tidspunkt, utelates fra sammenkoblingen.

Begge filenes gyldige rader sorteres kronologisk. Behold en referanse til hver originalrad, slik at de riktige måleverdiene kan skrives ut senere.

## Regler for sammenkobling

### 1. Kontroller dato

Den tidligste gyldige raden i begge filer må ha samme kalenderdato. Hvis datoene er forskjellige, returneres ingen treff. Dette er en regel fra den eksisterende implementasjonen.

### 2. Finn alle kandidatpar

For hver rad i hovedfilen finnes alle rader i sekundærfilen som oppfyller:

```text
absolutt(tidspunkt_hovedfil − tidspunkt_sekundærfil) <= toleranse
```

Med toleranse 2 sekunder kan `12:00:00` kobles til tidspunkt fra og med `11:59:58` til og med `12:00:02`, forutsatt at de fullstendige dato- og tidspunktene ligger innenfor toleransen.

For store filer kan et glidende tidsvindu over de sorterte radene brukes for å unngå å sammenligne alle rader med alle andre rader.

### 3. Prioriter nærmeste par

Alle kandidatpar fra hele datasettet sorteres etter:

1. Minst absolutt tidsforskjell.
2. Tidligste tidspunkt i hovedfilen ved lik tidsforskjell.
3. Tidligste tidspunkt i sekundærfilen dersom det fortsatt er likt.

Gå gjennom kandidatene i denne rekkefølgen. Godta et par bare hvis ingen av de to radene allerede er brukt. **Hver rad kan brukes maksimalt én gang.**

Dette er en grådig algoritme: den prioriterer de nærmeste parene først, men garanterer ikke størst mulig antall par. Den velger ikke bare nærmeste sekundærrad for hver hovedrad i opprinnelig filrekkefølge.

### 4. Sorter resultatet

Godkjente par sorteres etter hovedfilens tidspunkt, deretter sekundærfilens tidspunkt.

Rader uten treff tas ikke med i resultatfilen. Det utføres ingen interpolering eller beregning av gjennomsnittsverdier mellom målingene.

## Eksport

Når brukeren trykker «Slå sammen», kontrolleres de valgte dataene på nytt, og resultatet skrives til en ny fil.

For hvert godkjent par:

- Behold hele dataraden fra hovedfilen.
- Legg til måleverdiene fra sekundærfilen.
- Fjern sekundærfilens innledende radnummer og klokkeslett når disse gjenkjennes av filformatets parser.
- Bruk mellomrom eller ` - ` som valgt skilletegn mellom hovedraden og sekundærdataene.

Eksporten skal også inneholde kildefilnavn, antall sammenkoblede rader, toleranse, gjennomsnittlig og største tidsforskjell samt headerinformasjon fra begge filer. Velg et unikt filnavn slik at tidligere resultater ikke overskrives utilsiktet. Ved skrivefeil skal programmet vise en feilmelding fremfor å melde at eksporten er fullført.

Eksisterende program lagrer resultatet i `mergeProcessedFiles`. Det nye programmet kan tilpasse målmappe og filnavn til sine behov.

## Eksempel

Alle radene nedenfor gjelder samme dato. Toleransen er 2 sekunder.

| Hovedfil | Sekundærfil | Resultat |
| --- | --- | --- |
| 12:00:00 | 12:00:01 | Kobles, forskjell 1 sekund |
| 12:00:10 | 12:00:12 | Kobles, forskjell 2 sekunder |
| 12:00:20 | 12:00:25 | Ingen kobling |

Filene markeres grønt fordi to par kan kobles sammen. Visningen oppgir to treff og én gyldig rad uten treff i hver fil. Gjennomsnittlig tidsforskjell er 1,5 sekunder, og største forskjell er 2 sekunder.

Eksempel på én eksportert rad:

```text
Hovedfil:     N1 12:00:00 8.4 35.1
Sekundærfil:  S7 12:00:01 1013.2 4.8

Sammenslått:  N1 12:00:00 8.4 35.1 1013.2 4.8
```

## Pseudokode

```text
ved bytte av fil eller endring av toleranse:
    fjern tidligere treffmarkering og deaktiver Slå sammen
    kontroller at to forskjellige filer er valgt og kan leses

    A = les og sorter gyldige tidsstemplede rader fra hovedfil
    B = les og sorter gyldige tidsstemplede rader fra sekundærfil

    hvis A eller B er tom:
        vis årsak og avslutt kontrollen

    hvis dato(A.første) != dato(B.første):
        vis Ulik startdato og avslutt kontrollen

    kandidater = alle par (a, b) med absolutt(a.tid - b.tid) <= toleranse
    sorter kandidater etter (tidsforskjell, a.tid, b.tid)

    godkjente_par = tom liste
    for hvert kandidatpar:
        hvis verken a eller b er brukt:
            legg paret til godkjente_par
            marker begge radene som brukt

    sorter godkjente_par etter (a.tid, b.tid)
    vis antall treff, rader uten treff, ugyldige rader og tidsforskjeller

    hvis godkjente_par ikke er tom:
        marker begge filene grønt og aktiver Slå sammen
    ellers:
        vis Ingen målinger innenfor toleransen

ved klikk på Slå sammen:
    kontroller sammenkoblingen på nytt
    hvis det finnes godkjente par:
        skriv metadata og hovedrad + skilletegn + sekundære måleverdier
        vis resultatfilens plassering når skrivingen er fullført
```

## Avgrensninger og tilpasninger

- Tidspunktene i eksisterende sammenkobling har oppløsning på hele sekunder, selv om toleransen kan angis med desimaler.
- Klokkeslett uten egen dato knyttes til filens startdato. Eksisterende tidsberegning oppdager ikke automatisk overgang over midnatt for slike klokkeslett. Filer som går over flere døgn krever en utvidet datohåndtering hvis dette skal støttes.
- Eksisterende tidsberegning utfører ingen tidssonekonvertering. Filene må bruke samme tidsgrunnlag, eller normaliseres før sammenligning i det nye programmet.
- Ved helt identiske tidspunkter og tidsforskjeller angir eksisterende sortering ingen ytterligere prioritet mellom duplikatrader. Det nye programmet kan bruke original radposisjon som siste sorteringsnøkkel for et entydig resultat.
- Eksisterende brukerflyt søker sekundærfiler fra kategorien `schedule`. Det nye programmet kan tillate andre støttede filtyper; dette endrer ikke selve tidskoblingen.

## Referanse i eksisterende kode

Se `shared/app/instrument_app.cpp`:

- `seriesBaseTimestamp` og `sampleTimestamp`: beregning av dato og tidspunkt.
- `buildMergeSamplePairs`: kandidatpar, toleranse, prioritering og engangsbruk av rader.
- `refreshMergeFileMatches`: kontroll av aktuelle sekundærfiler og treffstatistikk.
- `exportSelectedMergeFile`: sammensetning og skriving av resultatfil.
