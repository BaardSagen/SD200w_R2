# Konvertering av måledata og eksport

Dette dokumentet beskriver hvordan dagens program beregner oksygen, salinitet, dybde og lydhastighet, og hvilke valg som finnes i «Convert and export». Formler og prioriteringsregler er hentet fra kildekoden slik at funksjonen kan gjenskapes i et annet program.

Dokumentet gjelder konvertering av innleste måledata. Instrumentspesifikk kalibrering, ADC-kanalkalibrering og kommandoer til sensorer er egne funksjoner og inngår ikke i denne filkonverteringen. Formlene nedenfor beskriver implementasjonen; de er ikke en uavhengig validering av de fysiske modellene.

## 1. Oversikt over valgene

| Funksjon | Inndata | Resultat eller valg |
| --- | --- | --- |
| Oksygenmetning til konsentrasjon | Metning i %, temperatur og salinitet | ml/L |
| Oksygenenhet | Oksygen i ml/L, eventuelt beregnet fra metning | mg/L, ml/L, µmol/L eller µmol/kg |
| Salinitet | Konduktivitet i mS/cm og temperatur i °C | Salinitet i PSU |
| Trykk uten beregning | Trykk i dbar | Behold trykk i dbar |
| Dybde, UNESCO 1983 | Trykk og breddegrad | Dybde i meter |
| Dybde, fast temperatur/salinitet | Trykk, breddegrad og faste verdier for temperatur/salinitet | Dybde i meter |
| Dybde, profilering | Trykk, breddegrad og temperatur/salinitet for hver rad | Dybde i meter |
| Lydhastighet | Temperatur, salinitet og dybde | m/s |
| Eksport | Innleste og beregnede felt | Full text, CSV, XML eller JSON |

«ml» betyr her **ml oksygen per liter vann (ml/L)**, ikke et totalvolum oksygen i hele prøven.

## 2. Brukerflyt og standardverdier

1. Brukeren åpner en målefil.
2. Programmet viser tilgjengelige målefelt og antall rader.
3. Brukeren velger beregninger, oksygenenhet, dybdemodus og posisjon.
4. Brukeren velger eksportformat og eventuelt CSV-variant og skilletegn.
5. Programmet beregner eksportverdier rad for rad og skriver en ny fil.

Startinnstillingene er:

- Beregn salinitet fra C + T: på.
- Beregn lydhastighet: på.
- Dybde: UNESCO 1983.
- Oksygen: ml/L.
- Eksport: Full text.
- CSV: vanlige kolonner og semikolon som skilletegn.
- Fast salinitet: 35 PSU; fast temperatur: 10 °C.

Ved åpning av en fil settes fast salinitet og fast temperatur til gjennomsnittet av de respektive endelige, numeriske verdiene i den innleste serien, dersom slike finnes. Uten slike verdier beholdes innstillingen. Posisjonen hentes fra programmets gjeldende posisjon. Tilstandsobjektets opprinnelige posisjon er 63,43° nord og 10,40° øst.

Breddegrad kan angis fra −90 til 90 grader og lengdegrad fra −180 til 180 grader. Brukeren kan også lime inn koordinater eller en støttet kartadresse. Breddegrad brukes i tyngdeberegningen. Lengdegrad lagres som posisjonsinformasjon, men påvirker ikke formlene nedenfor.

## 3. Felles regler for temperatur og salinitet

En gyldig numerisk verdi betyr her en endelig verdi: verken NaN eller uendelig.

### Temperatur til beregninger

Bruk radens temperatur hvis den er gyldig. Ellers brukes innstillingen «Fixed temp C».

### Salinitet til beregninger

Prioriteten er:

1. Hvis «Calculate salinity from C + T» er på og raden har gyldig konduktivitet og temperatur, beregnes saliniteten fra disse.
2. Ellers brukes radens eksisterende salinitet hvis den er gyldig.
3. Ellers brukes «Fixed salinity».

Fast temperatur brukes ikke som erstatning for manglende radtemperatur i selve C + T-beregningen. Begge kildefeltene må være gyldige for at den beregningen velges.

### Salinitet og temperatur i eksportkolonnene

Den eksporterte salinitetskolonnen bruker beregnet eller eksisterende salinitet, men fylles ikke med fast salinitet når begge mangler. Temperaturkolonnen inneholder radens temperatur, ikke den faste reserveverdien.

Dermed kan en avledet verdi være beregnet med faste reserveverdier selv om temperatur- eller salinitetskolonnen er tom. Et nytt program bør gjerne vise hvilke verdier beregningen har brukt.

## 4. Oksygenmetning (%) til ml/L

Oksygenets løselighet beregnes først fra temperatur og salinitet. Deretter skaleres løseligheten med metningsprosenten.

Definisjoner:

```text
T = temperatur i °C
S = salinitet i PSU
OX = oksygenmetning i prosent, for eksempel 100 for 100 %
K = T + 273.15
q = K / 100
ln = naturlig logaritme
exp = eksponentialfunksjonen med grunntall e
```

Eksakt formel i programmet:

```text
lnL = -173.4292
      + 249.6339 * (100 / K)
      + 143.3483 * ln(q)
      - 21.8492 * q
      + S * (-0.033096 + 0.014259*q - 0.0017000*q²)

løselighet_ml_L = exp(lnL)
oksygen_ml_L = løselighet_ml_L * max(0, OX) / 100
```

Negativ metning begrenses til 0. Metning over 100 % er tillatt og begrenses ikke til 100 %. Denne formelen bruker ikke dybde, trykk eller lufttrykk som inndata.

### Prioritet ved eksport

1. Hvis raden allerede har en gyldig verdi i `oxygenMlL`, brukes denne direkte.
2. Hvis denne mangler, men metningsprosent finnes, beregnes ml/L med temperaturen og saliniteten fra reglene i kapittel 3.
3. Hvis både ml/L og metningsprosent mangler, blir oksygenresultatet tomt.

**Viktig implementasjonsdetalj:** ml/L kan allerede være beregnet under innlesing av filen. Eksporten bruker også en slik forhåndsberegnet verdi direkte. Endring av fast temperatur, fast salinitet eller salinitetsberegning før eksport fører derfor ikke nødvendigvis til at oksygen i ml/L beregnes på nytt.

### Eksempel

Ved T = 10 °C, S = 35 PSU og OX = 100 % gir den implementerte formelen omtrent:

```text
Oksygen = 6.318517911 ml/L
        = 9.029351651 mg/L
        = 282.182482518 µmol/L
```

Ved 80 % metning, med samme temperatur og salinitet, er ml/L-verdien 0,8 ganger verdien ved 100 %.

## 5. De fire oksygenenhetene

Alle enhetsvalg tar utgangspunkt i oksygen i ml/L:

| Valgt enhet | Beregning | Eksportfelt |
| --- | --- | --- |
| ml/L | `mlL` | `oxygen_ml_l` |
| mg/L | `mlL * 1.42903` | `oxygen_mg_l` |
| µmol/L | `mlL * 44.6596` | `oxygen_umol_l` |
| µmol/kg | `(mlL * 44.6596) / max(0.001, tetthet_kg_L)` | `oxygen_umol_kg` |

For µmol/kg beregnes tettheten med temperatur og salinitet fra kapittel 3 og formelen i kapittel 8. Tetthet i kg/L er tetthet i kg/m³ delt på 1000.

Metningsprosenten beholdes i et separat felt, `oxygen_sat_pct`, når den finnes. Dette er ikke en funksjon som beregner metningsprosent tilbake fra mg/L eller ml/L. De fire valgene gjelder utdataenheten; de garanterer ikke at alle de samme enhetene støttes som inndata i enhver filparser.

## 6. Konduktivitet og temperatur til salinitet

Inndata er konduktivitet C i mS/cm og temperatur T i °C. Programmet bruker følgende polynom:

```text
C = max(0, C)
hvis C < 0.05: returner 0

r = C / 42.914
u = sqrt(r)
dt = T - 15

base = 0.0080
       - 0.1692*u
       + 25.3851*r
       + 14.0941*r*u
       - 7.0261*r²
       + 2.7081*r²*u

korreksjon = dt / (1 + 0.0162*dt)
             * (0.0005
                - 0.0056*u
                - 0.0066*r
                - 0.0375*r*u
                + 0.0636*r²
                - 0.0144*r²*u)

S = max(0, base + korreksjon)
```

Eksempel: C = 42,914 mS/cm og T = 15 °C gir S = 35 PSU.

Dette er den konkrete polynomimplementasjonen i programmet. Den har ingen trykkparameter og bruker forholdet C/42,914 direkte. Den skal derfor ikke beskrives som en fullstendig implementasjon av alle korreksjoner i en ekstern salinitetsstandard uten en egen kontroll.

Når avkryssingen for salinitetsberegning er på, kan eksportberegningen erstatte en eksisterende salinitetsverdi med den som beregnes fra C + T. Når den er av, beholdes eksisterende salinitet der den finnes.

## 7. Trykk og de fire dybdevalgene

Trykk P forventes i **dbar**. Alle fire eksportmodusene krever et gyldig trykkfelt, også når den innleste raden allerede har en dybdeverdi.

Programmets informasjonstekst oppgir at SAIV-instrumentets P allerede bruker oppstartens lufttrykk AP som referanse. Eksportkoden trekker derfor ikke AP fra P en gang til. Ved støtte for et annet instrument må inndataparseren avklare om trykket er absolutt eller allerede referert til lufttrykk.

### 7.1 Pressure dbar (no calc.)

Returner trykket uendret. Dette valget eksporterer trykk i stedet for en ny dybdeverdi.

### 7.2 Depth (UNESCO 1983)

Dette er standardvalget. Breddegrad φ oppgis i grader:

```text
p = max(0, P)
x = sin(φ * pi / 180)²

g = 9.780318 * (1 + (5.2788e-3 + 2.36e-5*x)*x)
    + 1.092e-6*p

n = (((-1.82e-15*p + 2.279e-10)*p - 2.2512e-5)*p + 9.72659)*p

dybde_m = n / g
```

Negativt trykk begrenses her til 0. Temperatur og salinitet inngår ikke i dette dybdevalget.

### 7.3 Depth = P/(Density x Gravity), fixed position

Bruk brukerens faste temperatur og faste salinitet for alle rader. Beregn tetthet etter kapittel 8 og tyngdeakselerasjon slik:

```text
x = sin(φ * pi / 180)²
g = 9.780318 * (1 + (5.2788e-3 + 2.36e-5*x)*x)

dybde_m = P * 10000 / max(1, tetthet_kg_m3 * g)
```

Faktoren 10000 konverterer dbar til pascal. Denne tyngdeformelen har ikke det trykkavhengige leddet fra UNESCO-modusen.

### 7.4 Depth = P/(Density x Gravity), profiling

Bruk samme formel som i 7.3, men beregn tetthet fra temperatur og salinitet for hver rad etter reglene i kapittel 3. Manglende verdier kan dermed erstattes av de faste innstillingene.

Begge tetthetsbaserte modusene bruker en tetthet uten trykkavhengig kompresjonskorreksjon. De begrenser heller ikke negativt P til 0 slik UNESCO-modusen gjør.

## 8. Tetthet til dybde og µmol/kg

Denne hjelpeberegningen er felles for oksygen i µmol/kg og de to tetthetsbaserte dybdemodusene. Den er ikke et eget eksportvalg for tetthet.

```text
t = clamp(T, -2, 40)
s = max(0, S)

rho_vann = 999.842594
           + 6.793952e-2*t
           - 9.095290e-3*t²
           + 1.001685e-4*t³
           - 1.120083e-6*t⁴
           + 6.536332e-9*t⁵

a = 0.824493
    - 4.0899e-3*t
    + 7.6438e-5*t²
    - 8.2467e-7*t³
    + 5.3875e-9*t⁴

b = -5.72466e-3 + 1.0227e-4*t - 1.6546e-6*t²

tetthet_kg_m3 = rho_vann + a*s + b*s^1.5 + 4.8314e-4*s²
```

Temperaturbegrensningen −2 til 40 °C gjelder denne tetthetsfunksjonen. Den skal ikke automatisk legges på de andre formlene dersom målet er å gjenskape dagens oppførsel.

## 9. Lydhastighet

Programmet bruker polynomet som i kildekoden beskrives som Mackenzie 1981:

```text
t = temperatur i °C
s = salinitet i PSU
d = max(0, dybde i meter)

c = 1448.96
    + 4.591*t
    - 5.304e-2*t²
    + 2.374e-4*t³
    + 1.340*(s - 35)
    + 1.630e-2*d
    + 1.675e-7*d²
    - 1.025e-2*t*(s - 35)
    - 7.139e-13*t*d³
```

Resultatet er i m/s. Funksjonen returnerer NaN hvis temperatur, salinitet eller dybde ikke er en gyldig endelig verdi.

Temperatur og salinitet velges etter kapittel 3. Dybden velges slik:

- Når en dybdemodus er valgt, brukes resultatet av denne modusen.
- Ved «Pressure dbar (no calc.)» brukes radens eksisterende dybde hvis den finnes.
- Hvis denne mangler, men trykket finnes, beregnes UNESCO-dybde for lydhastighetsberegningen.

Når «Calculate sound velocity» er på, forsøkes ny beregning. Hvis resultatet er gyldig, eksporteres dette også når en tidligere lydhastighet finnes. Hvis beregningen ikke lykkes, brukes eksisterende lydhastighet hvis tilgjengelig. Når avkryssingen er av, brukes bare eksisterende verdi.

Eksempel: T = 10 °C, S = 35 PSU og D = 0 m gir c = 1489,8034 m/s.

## 10. Automatisk beregning under innlesing

Konverteringsvinduet arbeider med en allerede innlest dataserie. Noen avledede verdier kan være beregnet før eksportvalgene brukes.

I innlesingsbanen for parsede målerader beregnes blant annet:

- Dybde fra trykk og breddegrad når trykk finnes.
- Salinitet fra konduktivitet og temperatur hvis raden ikke oppgir salinitet.
- Oksygen i ml/L fra metning, temperatur og salinitet når disse finnes.
- Lydhastighet når den mangler og temperatur, salinitet og dybde finnes.

Andre innlesingsbaner, inkludert enkelte CSV- og generiske tekstbaner, har egne reserveverdier og kan bruke syntetiske verdier for manglende felt. Disse er parseroppførsel, ikke egne valg i konverteringsvinduet. Ved portering bør manglende målinger representeres eksplisitt og opprinnelsen til avledede verdier beholdes, slik at reserveverdier ikke presenteres som målte data.

For identiske resultater må det nye programmet derfor både følge formlene og samme prioritet mellom innleste, beregnede og faste verdier.

## 11. Eksportmuligheter

### Full text (.txt)

Skriver kildeinformasjon, antall rader, oksygenenhet, dybdemodus, posisjon og tilgjengelig headerinformasjon. Hver rad får prefiks `S` for schedule-kilder, ellers `N`, etterfulgt av målenummer og eventuelt klokkeslett.

| Verdi | Tekstfelt | Desimaler |
| --- | --- | --- |
| Konduktivitet | C | 3 |
| Temperatur | T | 3 |
| Trykk | P | 2 |
| Salinitet | S | 3 |
| Lydhastighet | V | 2 |
| Oksygenmetning | OX | 2 |
| Valgt oksygenenhet | O2MG=, O2ML=, O2UMOL= eller O2UMOLKG= | 4 |
| Andre sensorverdier | OT, OF, OS | 2 |
| ADC-felt | X, CH1, CH2 | 3 |
| Tilt | TILT= med deg-suffiks | 1 |

Ugyldige eller manglende numeriske verdier utelates fra tekstraden.

**Begrensning i dagens kode:** Full text skriver P, men ikke beregnet dybde som eget radfelt. Valgt dybdemodus står i headeren og kan påvirke beregnet lydhastighet. Velg CSV, XML eller JSON for å få et eksplisitt `depth_m`-felt.

### CSV (.csv)

To varianter støttes:

- **CSV columns:** Vanlig kolonneoverskrift med feltnavn.
- **Compact FIELDS:** En linje som begynner med `FIELDS:` og feltnavn i store bokstaver.

Valgbare skilletegn er mellomrom, semikolon, komma og tabulator. Posisjonen skrives først som kommentarlinjer med `#`. Tall formateres med inntil 10 signifikante sifre i den delte tabellserialiseringen. Manglende celler er tomme. Tekst med skilletegn, anførselstegn eller linjeskift omsluttes av anførselstegn, og interne anførselstegn dobles.

### XML (.xml)

Skriver et `measurement`-element med navn, radantall og posisjon. Hver målerad skrives som et `sample`-element med underfelt. Manglende verdier i beholdte kolonner gir tomme elementer.

### JSON (.json)

Skriver et objekt med `label`, `latitude_deg`, `longitude_deg` og listen `rows`. Manglende verdier i beholdte kolonner skrives som `null`. Numeriske verdier skrives som tall, og klokkeslett som tekst.

### Felles tabellfelt for CSV, XML og JSON

```text
sample
time                      hvis serien inneholder klokkeslett
temperature_c
conductivity_ms_cm
salinity_psu
pressure_dbar
depth_m                   eller pressure_dbar i trykkmodus
oxygen_mg_l / oxygen_ml_l / oxygen_umol_l / oxygen_umol_kg
oxygen_sat_pct
other_sensor_t
other_sensor_f
other_sensor_s
sound_velocity_m_s
x
ch1
ch2
tilt_deg
```

Kolonner uten noen gyldig verdi i hele serien fjernes, bortsett fra `sample`. Andre sensorverdier, ADC-felt og tilt videreføres her uten en egen konvertering i eksportfunksjonen.

**Detalj som bør avklares ved portering:** I trykkmodus legger dagens kode til `pressure_dbar` både som originalt trykkfelt og som valgt trykk-/dybdefelt. Dette kan gi doble kolonnenavn og doble JSON-nøkler. Et nytt program bør eksportere trykkfeltet én gang.

## 12. Forslag til kontroller ved implementering

Følgende eksempler kan brukes til å kontrollere en ny implementasjon mot de dokumenterte reglene:

1. OX = 100 %, T = 10 °C, S = 35 gir omtrent 6,318517911 ml/L.
2. Samme temperatur og salinitet ved 80 % gir 80 % av ml/L-resultatet.
3. En eksisterende verdi på 5 ml/L gir 7,14515 mg/L og 223,298 µmol/L.
4. C = 42,914 mS/cm og T = 15 °C gir 35 PSU.
5. P = 0 gir 0 meter i alle dybdeberegningene med gyldige øvrige inndata.
6. T = 10 °C, S = 35 og D = 0 gir 1489,8034 m/s.
7. En rad med eksisterende ml/L skal beholde denne som grunnlag selv om faste T/S-verdier endres, dersom dagens prioritet skal beholdes.
8. Manglende kildeverdier skal behandles etter de eksplisitte reservereglene, ikke generelt erstattes med null.
9. CSV/XML/JSON skal inneholde valgt oksygenenhet og valgt trykk-/dybdefelt.

Eksemplene dokumenterer forventet oppførsel; dette dokumentasjonsarbeidet endrer ikke beregningskoden.

## 13. Kildereferanser

- `shared/core/instrument/derived_measurements.cpp`: `OxygenSolubilityMlPerL`, `OxygenSaturationToMl`, `ConductivityToSalinity`, `PressureToDepthMeters` og `SoundVelocityMetersPerSecond`.
- `shared/app/instrument_app.cpp`: `ConvertExportState`, `loadConvertExportFileFromPath`, `exportConvertExportFile` og `drawConvertExportWindow`.
- `shared/app/data/series_support.cpp`: innlesing og automatisk utfylling av avledede måleverdier.
