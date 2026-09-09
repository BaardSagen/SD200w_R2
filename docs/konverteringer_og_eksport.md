# Konvertering av måledata og eksport – SIT som fasit

Revidert 8. september 2026. **SAIV Instrument Terminal (SAIV IT / SIT), tidligere SD200W, er fasit for beregningene.** Dette dokumentet er beregnet for implementering i et annet program som skal gi samme resultater.

Referanseprogram: `SAIV_Instrument_Terminal_v1.1.3_Sept2026.exe`.
SHA-256: `60f8713bfeda9baffdb690e2bc0c2ff2f4e12516ceb1087b35257ec91b110035`.

Den tidligere utgaven beskrev andre C++-beregninger. Dens salinitets-, oksygen- og lydhastighetsformler skal ikke brukes som SIT-kompatible formler. De er erstattet nedenfor. De tidligere oppgitte C++-filene under `shared/core` og `shared/app` er ikke bevis for SITs oppførsel.

## 1. Hva som er bekreftet

| Del | Status |
|---|---|
| Salinitet fra konduktivitet, temperatur og trykk | Rekonstruert fra SIT/SD200W og numerisk kontrollert mot maskinkode |
| Lydhastighet | Rekonstruert og numerisk kontrollert |
| Sigma T, trykkavhengig tetthet og eldre tetthetsgren | Rekonstruert og numerisk kontrollert for de undersøkte tilfellene |
| Oksygenets normalgren og gren med fast salinitet | Rekonstruert og kontrollerte kall numerisk sammenlignet |
| Oksygenets enhetskonstanter | Lest fra kode; hele eksportkjeden er ikke kontrollert for alle valg |
| UNESCO-dybde og gravitasjon | Rekonstruert fra kode; omkringliggende profil-/referansebehandling ikke ferdig kontrollert |
| Alle standardinnstillinger, manglende-data-grener og eksportvarianter | Ikke fullstendig kartlagt; ikke presenter de gamle C++-reglene som bekreftet SIT-atferd |

SIT er her **kompatibilitetsfasit**. Det betyr ikke at alle historiske reserveverdier eller ugyldighetsregler er fysisk riktige. De skal ikke endres skjult når målet er samme oppførsel. Kjente særtilfeller er angitt i kapittel 8.

## 2. Inndata og felthåndtering

CTD/STD-oppsettet står først i instrumenthodet, for eksempel:

```text
CTDOF Par OxR Ser No 1240 AP1006.175
```

`CTDOF` følger eksisterende SIT-oppsett og feltrekkefølge. `Par` og `OxR` er tilleggsfelter. Ikke flytt CTD-verdier mellom kanaler fordi ekstra sensorer finnes.

| Felt | Betydning / behandling |
|---|---|
| C | Konduktivitet i mS/cm til salinitetsberegningen |
| S | Eksisterende praktisk salinitet; bevar originalverdien som kilde |
| T | Temperatur i °C slik den tilføres SIT-rutinen |
| P | Sjøtrykk i dbar til salinitet, lydhastighet og tetthet; ikke erstatt med dybde i meter |
| OX / OxR | Oksygenmetning i prosent i den avtalte normale brukerflyten; OxR er RINKO-oksygen |
| OF | Fluorescens, håndteres som i eksisterende CTD-oppsett |
| OT | Turbiditet, håndteres som i eksisterende CTD-oppsett |
| Par | Biospherical PAR-verdi, beholdes normalt uendret |
| Tilt | Separat tilleggsfelt; bevar uten å tolke det som temperatur |
| DATE / TIME | Individuelt tidspunkt for målingen når dette er tilgjengelig |

Støtt både kolonneformat med `FIELDS:` og Full-format med prefiks direkte foran verdien. Prefikser som `OxR`, `OF`, `OT`, `Par` og `Tilt` må gjenkjennes uten å forveksles med kortere CTD-prefikser. Behold alle ekstra felt, også ukjente, med originalt navn.

Oksygen presenteres normalt i området 0–200 %. Dette er brukerens beskrivelse av normal inndata, ikke tillatelse til å klippe andre verdier automatisk. PARs oppgitte område 1–5000 fastsetter ikke alene enheten. Ikke merk Par som volt eller påfør sensorkalibrering i den vanlige filkonverteringen.

Behold både logger- og CTD-serienummer, filhode, tidssonebetegnelse og originale måleverdier. Bruk radens DATE/TIME fremfor å konstruere jevne intervaller: OSU107-eksemplet har 4 sekunder mellom de to første radene, deretter 2 sekunder. Surface-eksemplet inneholder ingen CTD-verdier; disse må ikke fylles med oppdiktede nullmålinger.

## 3. Salinitet – samme beregning som SIT

Inndata: C i mS/cm, T i °C, P i dbar. Temperaturverdien må være den samme som SIT tilføres; ikke legg inn en ekstra temperaturskalakonvertering uten å kontrollere innlesingsbanen.

```text
hvis C < 0.01: returner 0
R = C / 42.914
rt = 0.6766097 + 0.0200564*T + 0.0001104259*T²
     - 6.9698e-7*T³ + 1.0031e-9*T⁴
Rp = 1 + P*(2.07e-5 - 6.37e-10*P + 3.989e-15*P²)
         / (1 + 0.03426*T + 0.0004464*T² + (0.4215 - 0.003107*T)*R)
x = sqrt(abs(R / (rt*Rp)))
d = T - 15
S = 0.008 - 0.1692*x + 25.3851*x² + 14.0941*x³ - 7.0261*x⁴ + 2.7081*x⁵
    + d/(1 + 0.0162*d)
      * (0.0005 - 0.0056*x - 0.0066*x² - 0.0375*x³ + 0.0636*x⁴ - 0.0144*x⁵)
```

Ingen generell `max(0, S)` er lagt til denne gjengivelsen. Grensen er **0,01**, ikke 0,05. Både rt og Rp er nødvendige for samsvar. Dokumentets tidligere formel brukte C/42,914 direkte og ga blant annet 35 ved C=42,914, T=10, P=0, mens SIT gir omtrent 39,99671809.

SIT har også invers beregning S → C, med iterativ løsning og toleranse 10⁻⁹. Den inverse algoritmen er ikke fullstendig beskrevet her og skal ikke erstattes av enkel skalering. Tre tidligere inverse rundturer er kontrollert i prosjektet.

## 4. Oksygenmetning til mg/L og mL/L

SITs grunnberegning gir **mg oksygen per liter vann** ved 100 % metning. Den bruker temperatur, salinitet og lufttrykk. Den gamle dokumentasjonens ml/L-formel uten lufttrykk er ikke samme beregning.

```text
K = T + 273.15
L = exp(-139.34411 + 157570.1/K - 66423080/K²
        + 12438000000/K³ - 862194900000/K⁴)
Fs = exp(-S*(0.017674 - 10.754/K + 2140.7/K²))
theta = 0.000975 - 0.00001426*T + 0.00000006436*T²
v = exp(11.8571 - 3840.7/K - 216961/K²)
p = air_mmHg * 0.00131578955679
denominator = (1-v)*(1-theta)
Fp = (1-theta*p)*(p-v)/denominator
hvis denominator er 0: bruk Fp = 1
O100_mg_L = L * Fs * Fp
oxygen_mg_L = O100_mg_L * saturation_percent / 100
```

`exp` er eksponentialfunksjonen med grunntall e. Lufttrykkargumentet her er **mmHg**, ikke sjøtrykket P i dbar. AP i instrumenthodet må enhetsavklares og omregnes før bruk; eksempelverdien `AP1006.175` skal ikke settes direkte inn som 1006,175 mmHg. Den eksakte filmetadata-til-wrapper-kjeden er ikke ferdig dokumentert. En implementering må spore hvilken lufttrykkverdi SIT faktisk bruker på samme fil.

Behold den opprinnelige prosentverdien. Ikke legg inn den tidligere dokumentasjonens `max(0, OX)` som en antatt SIT-regel; negativ-/ugyldighetsbehandling i hele innlesingskjeden er ikke kartlagt.

### Enhetskonstanter fra SIT

La `mgL` være resultatet ovenfor:

| Resultat | Formel |
|---|---|
| mg/L | `mgL` |
| mL/L | `mgL * 22.391 / 31.998` |
| µmol/L | `mgL * 1000 / 31.998` |
| µmol/kg | `mgL * 22.391 * 1000 / (716.467218 * (rho_kg_m3 / 1000))` |

Den siste formelen gjengir de faktiske konstanter som er kartlagt. Ikke bytt dem til andre avrundede faktorer ved portering. Valget av tetthetsgren for alle eksportbaner er ikke ferdig kontrollert; dette må samsvare med SIT før µmol/kg kan erklæres kompatibelt.

For tilleggsfeltet OxR skal brukeren kunne beholde % eller velge mg/L, mL/L eller begge. Dette er avtalt utvidelse, ikke en påstand om at SIT 1.1.3 allerede importerer de nye loggerfilene.

## 5. Lydhastighet

SIT bruker **S, T og sjøtrykk P i dbar**. Det bruker ikke dokumentets tidligere Mackenzie-formel med dybde som argument.

```text
p = P / 10
c = W(T,p) + A(T,p)*S + B(T,p)*sqrt(S³) + D(p)*S²
```

Alle koeffisientene står i den kjørbare referansekoden i kapittel 12, `sound_velocity`. Resultatet er m/s. Ikke bruk en valgt eksportdybde i stedet for P, og ikke klipp P med `max(0, P)` uten at dette er dokumentert i den aktuelle SIT-kallkjeden.

## 6. Tetthet og Sigma T

SIT har flere grener. De er gjengitt i kapittel 12:

- `density0(S,T)`: full tetthet ved null sjøtrykk; Sigma T = resultat − 1000.
- `density_anomaly(S,T,P)`: trykkavhengig tetthetsavvik; full tetthet = resultat + 1000.
- `legacy_sigma(S,T)`: separat eldre tetthetsgren.

Ikke bland tetthetsavvik med full tetthet. Et avvik på 26 betyr 1026 kg/m³. Ikke begrens temperaturen til −2…40 °C slik den gamle dokumentasjonen gjorde; en slik begrensning er ikke påvist i de kartlagte rutinene.

Referansefunksjonen `density0` i vedlegget bruker `sqrt(abs(S³))` for å være felles med den trykkavhengige grenen. Den selvstendige Sigma T-rutinen bruker `sqrt(S³)` uten absoluttverdi. De er like for normale S ≥ 0. Vedlegget er derfor ikke en full emulering av ugyldige negative saliniteter i alle grener.

## 7. Trykk, dybde og breddegrad

Disse fire valgtekstene finnes i SIT:

1. Pressure dbar (no calc.)
2. Depth (Unesco 1983)
3. Depth = P/(Density x Gravity) Fixed position
4. Depth = P/(Density x Gravity) Profiling

Den kartlagte gravitasjonsfunksjonen er:

```text
x = sin(latitude_deg * pi/180)²
g = 9.780318*(1 + (0.0052788 + 0.0000236*x)*x) + 0.000001092*P
```

UNESCO-hovedformelen er:

```text
depth_m = (((-1.82e-15*P + 2.279e-10)*P - 2.2512e-5)*P + 9.72659)*P / g
```

Den alternative hovedberegningen er `10000*P/(rho_kg_m3*g)`.

**Grense for hva som er bekreftet:** SIT har et eget trykk-/referanseledd før valg av dybdeberegning og omkringliggende profilbehandling. Hele forskjellen mellom Fixed position og Profiling er ikke ferdig rekonstruert. Ikke beskriv begge som bare én uavhengig beregning per rad. Det er heller ikke bekreftet at alle grener følger den gamle dokumentasjonens klipping av negativt trykk eller utelatelse av trykkleddet i g.

Breddegrad påvirker g. Ikke gjør den tidligere oppgitte standardposisjonen 63,43°/10,40° til en SIT-standard; denne kom fra beskrivelsen av det andre programmet. AP skal heller ikke trekkes fra trykkfeltet på nytt uten å kontrollere trykkets referanse og SITs metadatahåndtering.

## 8. Valg, reserveverdier og rekkefølge

Formellikhet alene gir ikke samme resultat hvis programmene bruker ulik temperatur, salinitet, lufttrykk, kanalmaske eller referanseverdi.

**Bekreftet særtilfelle:** Oksygenwrapperen ved 0x0050BC10 erstatter salinitetsargumentet med **34,5** når et kanalflagg er null. Flagget settes fra `mask & 3` ved 0x0045B4B3. En målebehandlingsgren bruker denne wrapperen. Samme inngang og samme gren må gjenskapes ved kompatibilitetstest. Dette må ikke forveksles med en generell regel om at alle filer uten S skal bruke 34,5; full fil-/UI-forrang er ikke kartlagt.

Ved T=20, AP=760 mmHg og 100 %:

| Innkommende S | S/C-flagg satt, mg/L | S/C-flagg ikke satt, mg/L |
|---:|---:|---:|
| 0 | 9,092427 | 7,417910 |
| 5 | 8,828125 | 7,417910 |
| 35 | 7,396060 | 7,417910 |

Andre kjente kompatibilitetspunkter:

- C < 0,01 gir S=0 også for negative C i selve rutinen. Dette er ikke bevis på at innleseren godtar enhver negativ verdi.
- T68/T90 påvirker salinitet. Ikke konverter temperaturskala en ekstra gang uten å følge SITs innlesing.
- Det er ikke bevist at SIT følger den gamle regelen «allerede beregnet oxygenMlL vinner alltid». Skill mellom originalt innlest konsentrasjon og en mellomlagret beregning fra prosent.
- De gamle opplysningene om automatisk gjennomsnitt, standard T=10, S=35, automatisk salinitetsoverskriving og faste eksportstandarder er ikke dokumenterte SIT-regler.
- Behold rådata og beregningsgrunnlag separat. Endret beregningsgrunnlag må ikke stille gjenbruke en gammel beregnet oksygenverdi og samtidig påstå at den bygger på nye innstillinger.

For loggerutvidelsen presenteres nye felt og valg før konvertering. CTD/STD/OF/OT behandles som før. Ved manglende nødvendige T/S/lufttrykkopplysninger vises hva som mangler eller hvilket eksplisitt grunnlag som brukes. Dette er et krav til den nye løsningen; full samsvarserklæring for historiske SIT-reservegrener krever egne filtester.

## 9. Eksport: beregninger og filformat er separate

SITs eksisterende eksportmeny inneholder blant annet List, Standard depths, Standard Depth Sectioned, Standard temperatures, Sonar file, Lybin file (Bathy data.xml) og Tide data. List-dialogen tilbyr alle målinger i én fil, serier i separate filer eller utvalgte målinger, skilletegn og Standard/MSDOS. Eksemplet `test.txt` har semikolon, desimalkomma, instrumentnummer, serieinformasjon og dato/tid.

Disse eksportene må testes mot samme data, valgte enheter, utvalg og formatering når målet er identiske SIT-filer. Eksakt interpolasjon, vekting, avrunding og alle spesialformater er ikke ferdig kartlagt her. Lybin XML er et bestemt format og er ikke det samme som generisk XML.

### Full text, CSV, XML og JSON i det andre programmet

Disse formatene kan beholdes som **egne eksportmuligheter i det andre programmet**, men de er ikke dokumentert som samme formatutvalg eller brukerflyt som SIT. Felles beregningsgrunnlag og SIT-formlene ovenfor skal brukes uansett serialisering.

Følgende er eksportkrav for utvidelsen, ikke en beskrivelse av alle eksisterende SIT-eksporter:

- Behold original metningsprosent og tydelig merkede mg/L-/mL/L-kolonner etter brukerens valg. Konverter aldri bare ved å endre kolonnenavnet.
- Skriv trykk og eventuell dybde i separate felt, med enheter. Ikke skriv `pressure_dbar` to ganger eller dupliser JSON-nøkler.
- Ta med individuell dato/tid og kjent tidssoneinformasjon, kildefil, logger-/CTD-identitet og beregningsgrunnlag. Syntetiske reserveverdier må ikke presenteres som målinger.
- CSV: siter felt som inneholder skilletegn, anførselstegn eller linjeskift; doble interne anførselstegn. Desimalskilletegn må være eksplisitt, særlig når komma kan være feltskilletegn.
- Full-format: bruk entydige prefikser og enhetsangivelse for nye felter. Bevar OF/OT/Par/OxR som ulike kanaler. Avrunding skal dokumenteres og kontrolleres, ikke antas identisk med SIT.
- XML/JSON: behold numeriske verdier som numeriske der formatet tillater det; manglende verdier håndteres eksplisitt. Ikke erstatt dem generelt med null.
- PAR videreføres uten ny omregning som standard. Ikke bruk en udokumentert enhetsbetegnelse basert bare på verdiområdet.

De tidligere tabellnavnene som `oxygen_ml_l`, `oxygen_mg_l`, `depth_m` og `oxygen_sat_pct` kan brukes som et eksplisitt schema i det andre programmet. De er ikke bekreftet å være SITs interne feltnavn eller filkolonner. Samme beregning betyr ikke automatisk byte-identisk eksportfil.

## 10. Kontrollverdier fra kjøring av SIT 1.1.3

Tallene nedenfor er lest fra beregningsrutinene i EXE via x86-emulator. Oksygenprøvene bruker S/C-flagg satt, slik at S=35 ikke overstyres av 34,5.

| Beregning / inngang | SIT-resultat |
|---|---:|
| S: C=42,914; T=15; P=0 | 34.99999992413 |
| S: C=42,914; T=10; P=0 | 39.99671808750 |
| S: C=30; T=10; P=100 | 26.82414973414 |
| S: C=0,02; T=20; P=0 | 0.01702767147 |
| Lydhastighet: S=35; T=10; P=0, m/s | 1489.82233601566 |
| Oksygen 100 %: S=35; T=10; AP=760 mmHg, mg/L | 9.02425974628 |
| Oksygen 100 %: S=35; T=10; AP=700 mmHg, mg/L | 8.30363060978 |

Ved 80 % metning brukes 0,8 ganger 100 %-resultatet med samme øvrige grunnlag. For enhetskontroll kan en konsentrasjon på nøyaktig 5 mg/L brukes med konstantene i kapittel 4; ikke bruk den gamle testens 5 mL/L som om grunnberegningen var den samme.

Sammenlign før presentasjonsavrunding. For tidligere kontrollerte kjernefunksjoner er `rel_tol=1e-9` og `abs_tol=1e-8` brukt mot maskinkoden. Toleransen dokumenterer rekonstruksjonens samsvar, ikke instrumentets målenøyaktighet eller godkjenning av alle fysiske innganger.

## 11. Test- og kildegrunnlag

Følgende prosjektfiler følger dokumentet ved overlevering:

- `sd200DOc/FORMELKARTLEGGING.md`: adresser, formler og bevisnivå.
- `sd200DOc/FORMELKONTROLL.md`: reserveverdier, ugyldige data og temperaturskala.
- `analysis/recovered_formulas.py`: rekonstruerte normaldatagrener.
- `analysis/test_recovered_formulas.py` og `analysis/formula_numeric_validation.json`: 24 opprinnelige sammenligninger.
- `analysis/audit_formulas.py` og `analysis/formula_audit_tests.json`: særtilfeller og referanser.
- `analysis/conversion_document_comparison.json`: sju prøver mot SIT 1.1.3. Feltet `document` i denne historiske rapporten gjelder **dokumentet før rettelsen**, mens `exe` er fasiten.
- `analysis/check_sit_conversion_document.py`: leser referansekoden fra denne filen og kontrollerer den mot SIT-resultatene.

Originaldokumentet er bevart som `analysis/reference/konverteringer_og_eksport_before_SIT_20260908.md`. Sammenligningsnotatet `sd200DOc/KONVERTERING_SAMMENLIGNING.md` beskriver denne eldre dokumentutgaven.

For å bekrefte at det andre programmet er enig med SIT, må det kjøre samme kjerneprøver og deretter de samme filene gjennom import, valgte beregninger og eksport. Det andre programmets kode er ikke endret eller verifisert av denne dokumentrettelsen. SIT-programfilen er heller ikke endret.

## 12. Komplett referansekode for kartlagte normaldatagrener

Koden under er inkludert slik at koeffisientene følger med også når denne Markdown-filen kopieres til det andre prosjektet. Funksjonsargumentene og enhetene er beskrevet ovenfor. Koden implementerer ikke hele SITs filinnlesing, kanalvalg eller profilbehandling. `gravity` og `depth_unesco` er kodeavleste hovedformler, ikke fullstendig eksportverifikasjon. Negative og manglende data må håndteres etter riktig SIT-gren, ikke etter vilkårlig ny klipping.

```python
import math

def salinity(C,T,P):
    if C<.01:return 0.
    R=C/42.914
    rt=.6766097+.0200564*T+.0001104259*T**2-6.9698e-7*T**3+1.0031e-9*T**4
    rp=1+P*(2.07e-5-6.37e-10*P+3.989e-15*P**2)/(1+.03426*T+.0004464*T*T+(.4215-.003107*T)*R)
    x=math.sqrt(abs(R/(rt*rp)));d=T-15
    return .008-.1692*x+25.3851*x*x+14.0941*x**3-7.0261*x**4+2.7081*x**5+d/(1+.0162*d)*(.0005-.0056*x-.0066*x*x-.0375*x**3+.0636*x**4-.0144*x**5)

def sound_velocity(S,T,P):
    p=P/10
    D=.001727-7.9836e-6*p
    B=-.01922-4.42e-5*T+(7.3637e-5+1.7945e-7*T)*p
    A=1.389-.01262*T+7.164e-5*T*T+2.006e-6*T**3-3.21e-8*T**4
    A+=(9.4742e-5-1.258e-5*T-6.4885e-8*T*T+1.0507e-8*T**3-2.0122e-10*T**4)*p
    A+=(-3.9064e-7+9.1041e-9*T-1.6002e-10*T*T+7.988e-12*T**3)*p*p
    A+=(1.1e-10+6.649e-12*T-3.389e-13*T*T)*p**3
    W=1402.388+5.03711*T-.0580852*T*T+.0003342*T**3-1.478e-6*T**4+3.1464e-9*T**5
    W+=(.153563+.00068982*T-8.1788e-6*T*T+1.3621e-7*T**3-6.1185e-10*T**4)*p
    W+=(3.126e-5-1.7107e-6*T+2.5974e-8*T*T-2.5335e-10*T**3+1.0405e-12*T**4)*p*p
    W+=(-9.7729e-9+3.8504e-10*T-2.3643e-12*T*T)*p**3
    return W+A*S+B*math.sqrt(S**3)+D*S*S

def density0(S,T):
    w=999.842594+.06793952*T-.00909529*T*T+.0001001685*T**3-1.120083e-6*T**4+6.536332e-9*T**5
    a=.824493-.0040899*T+7.6438e-5*T*T-8.2467e-7*T**3+5.3875e-9*T**4
    b=-.00572466+.00010227*T-1.6546e-6*T*T
    return w+a*S+b*math.sqrt(abs(S**3))+.00048314*S*S

def density_anomaly(S,T,P):
    p=P/10
    kw=19652.21+148.4206*T-2.327105*T*T+.01360477*T**3-5.155288e-5*T**4
    k0=kw+(54.6746-.603459*T+.0109987*T*T-6.167e-5*T**3)*S+(.07944+.016483*T-.00053009*T*T)*math.sqrt(abs(S**3))
    a=3.239908+.00143713*T+.000116092*T*T-5.77905e-7*T**3+(.0022838-1.0981e-5*T-1.6078e-6*T*T)*S+.000191075*math.sqrt(abs(S**3))
    b=8.50935e-5-6.12293e-6*T+5.2787e-8*T*T+(-9.9348e-7+2.0816e-8*T+9.1697e-10*T*T)*S
    K=k0+a*p+b*p*p
    return density0(S,T)/(1-p/K)-1000

def legacy_sigma(S,T):
    s=S-35
    q=28.1263+.806*s+.00023*s*s+6.8e-6*s**3
    a=(4.7867*T-.098185*T*T+.0010843*T**3)*.001
    b=(18.03*T-.8164*T*T+.01667*T**3)*1e-6
    w=-(T+283)*(T-3.98)**2/(503.57*(T+67.26))
    return (1-a+(q-.1324)*b)*(q+.1324)+w

def gravity(latitude,P):
    x=math.sin(math.radians(latitude))**2
    return 9.780318*(1+(.0052788+2.36e-5*x)*x)+1.092e-6*P

def depth_unesco(latitude,P):
    return (((-1.82e-15*P+2.279e-10)*P-2.2512e-5)*P+9.72659)*P/gravity(latitude,P)

def oxygen_saturation_mg_l(S,T,air_mmHg):
    k=T+273.15
    a=math.exp(-139.34411+157570.1/k-66423080/k**2+12438000000/k**3-862194900000/k**4)
    b=math.exp(-S*(.017674-10.754/k+2140.7/k**2))
    theta=.000975-1.426e-5*T+6.436e-8*T*T
    vapor=math.exp(11.8571-3840.7/k-216961/k**2)
    p=air_mmHg*.00131578955679
    divisor=(1-vapor)*(1-theta)
    correction=(1-theta*p)*(p-vapor)/divisor if divisor else 1
    return a*b*correction


def oxygen_from_percent(saturation_percent, S, T, air_mmHg):
    # S must be the salinity selected by the matching SIT caller/branch.
    return oxygen_saturation_mg_l(S, T, air_mmHg) * saturation_percent / 100


def oxygen_units_from_mg_l(mgL, rho_kg_m3=None):
    result = {
        "mg_L": mgL,
        "mL_L": mgL * 22.391 / 31.998,
        "umol_L": mgL * 1000 / 31.998,
    }
    if rho_kg_m3 is not None:
        result["umol_kg"] = mgL * 22.391 * 1000 / (716.467218 * (rho_kg_m3 / 1000))
    return result
```
