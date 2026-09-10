# SD208: konduktivitet, salinitet, lydhastighet og driftkompensasjon

Gjennomgått 2026-09-10. Dette er en beskrivelse av legacy-fastvaren i
`sd208-as`, med beregninger i `SD48MAT.ASM` og den inkluderte
`SD48MAT1.ASM`. `SD249.ASM` inkluderer `SD49CL.ASM` og inneholder
målesekvens og utdataformatering. Byggefilen angir 2023-04-13.
`sd208-c` er et C-skjelett; `sd208_a2` er en ufullstendig refaktor med
stub-rutiner. De er ikke grunnlaget for beregningene nedenfor.

Dette er kontrollert mot kildekode, ikke mot firmware lest fra et fysisk
instrument eller mot instrumentets gjeldende EEPROM-koeffisienter.

Etter mottak av to databladbilder er rapporten utvidet med avsnitt
12–16: PSS-78-identifikasjon, parameterenheter, opsjonsformler,
alle lydhastighetskoeffisienter, datablad og praktisk måleområde.

## Konklusjon om «lineære rådata» og offsetkalibrering

Ja: konduktivitetens rådata er allerede omregnet og driftkompensert før
vertsprogramvaren mottar dem. De er ikke ubehandlede ADC-tellinger.
Fastvaren forsøker å produsere en verdi N som omtrent følger
konduktiviteten, men på en skala omkring **10 000 tellinger per mS/cm**.

Den avsluttende kalibreringen er:

```text
C [mS/cm] = A3 + B3*N + C3*N²
```

Dermed er offsetkalibrering bare et spesialtilfelle. Koden støtter også
korreksjon av stigning og krumning, og de innebygde koeffisientene bruker
begge deler. Hvis x = N/10000, blir den innebygde kalibreringen:

```text
C = 0.000044712882942 + 0.98257908671*x + 0.00009993300482*x²
```

| N, behandlet råverdi | N/10000 | Kalibrert C med innebygde koeffisienter |
|---:|---:|---:|
| 100000 | 10 | 9.8358288805 mS/cm |
| 300000 | 30 | 29.5673570185 mS/cm |
| 400000 | 40 | 39.4631009890 mS/cm |
| 600000 | 60 | 59.3145487328 mS/cm |

Dette er regneeksempler, ikke målte kalibreringsavvik. Koeffisientene i
instrumentet kan være andre enn de innebygde startverdiene. En ren offset
kan bare begrunnes dersom målinger mot referanse viser omtrent konstant
restfeil over det aktuelle konduktivitets- og temperaturområdet.

## 1. Målekjeden og navnene som skifter betydning

```text
Konduktivitetskortets ASCII-svar m
  -> grensekontroll
  -> motstandsmodell exp(CA + CB*ln(m))
  -> BA*10^7 / motstand = N0
  -> temperaturavhengig korreksjon = N
       |-> rådatafelt C: seks sifre, heltallsdelen av N
       -> A3 + B3*N + C3*N² = konduktivitet C [mS/cm]
            -> salinitet S sammen med kalibrert T og P
                 -> lydhastighet c sammen med samme T og P
```

Kilder: `SD249.ASM:1028` (`da_cond`), `SD48MAT1.ASM:431`
(`cond_flyt`), `SD48MAT.ASM:842` (`conduct_cal`),
`SD48MAT1.ASM:737` (`raw_data`), `SD249.ASM:1684` (`raw_reorg`).

Den samme variabelen **cob_c** inneholder først kortets svar m og blir
senere overskrevet med behandlet råverdi N. **con_c** inneholder den
kalibrerte konduktiviteten. **cond_raw** og **cal_c** er tekstutgaver av
henholdsvis N og C. Man må derfor kjenne tidspunktet i målekjeden for å
tolke `cob_c` riktig.

Konduktivitetskortet leses via intern seriell forbindelse ved 9600 baud,
uten paritet, med kommando liten `s`. Svaret samles frem til komma og
tolkes som flyttall. Kortets egen firmware og eventuelle behandling før
dette svaret fremgår ikke av dette prosjektet. Fysisk enhet for m kan
derfor ikke fastslås bare fra denne kildekoden.

Trykk, intern temperaturindikator RB, ADC-referanse og vanntemperatur
leses via andre målebaner. `sdat_out` henter 20 bit. Konduktiviteten i
den aktive banen kommer altså fra det separate kortet, selv om eldre
kommentarer omtaler `cond_bin` og ADC-rådata.

## 2. Referansekompensasjon av ADC-målingene

`factor_temp` (`SD48MAT1.ASM:664`) beregner:

```text
F = factor_kald / aktuell_ADC_referanse
```

`factor_kald` etableres av `factor_cals` ved referansemåling og kan
lagres/hentes fra EEPROM. Dette er en lagret referanse, ikke nødvendigvis
en ny måling ved hver oppstart. `ref_mal`/`sensor` kan etablere den på nytt.

`bin_flyt` multipliserer temperatur- og RB-tellingene med F.
`pressure_cal` multipliserer også sin trykkverdi med F.
Dette motvirker endringer som fanges opp av referansekanalen. Det er ikke
en algoritme som måler instrumentets aldring mot en ekstern sann verdi.

Konduktivitetskortets svar m multipliseres **ikke direkte** med F.
Konduktiviteten påvirkes indirekte gjennom den korrigerte RB-verdien.

## 3. Temperatur og intern RB-verdi

`mot_mal` (`SD48MAT.ASM:776`) brukes både for temperaturføleren og RB:

```text
q = ADC_telling * F
R(q) = S1 + S2*q + S3*q²
```

Resultatet omtales som motstand i koden. RB er den interne
temperaturavhengige motstandsverdien som brukes til kompensasjon.
RB er **ikke vanntemperaturen i °C**, og `rb_kald` er en referanse på
samme motstandsskala. `con_kald` setter startverdien for `rb_kald` til
1000; den kan senere endres og lagres.

For vanntemperaturen bruker `temp_cal` (`SD48MAT.ASM:1411`):

```text
l = ln(R_temperature)
T = 1 / (A1 + B1*l + C1*l² + D1*l³) - 273.15
```

Formelen over gjelder positiv følermotstand. Ved R_temperature <= 0
går koden via `tem100` direkte til lagring av **T=0**, selv om kommentaren
sier at feilen skal gi -273.15. Null temperatur er dermed heller ikke
en entydig bekreftelse på en gyldig temperaturmåling.

T lagres i `temp_t`. Koden bruker T direkte videre; ingen eksplisitt
omregning mellom ITS-90 og IPTS-68 finnes i salinitets- eller
lydhastighetsrutinen. Hvilken temperaturskala kalibreringskoeffisientene
representerer, må avklares fra kalibreringen av det aktuelle instrumentet.

## 4. Konduktivitet før sluttkalibrering

### 4.1 Grensekontroll og omregning

`conduct_cal` fortsetter med logaritmen når m > 100. Ved m <= 100 settes
både N og C til null; A3 legges ikke til i denne grenen.
Grensefortolkningen følger samme `dpcmp`/`dec a`-mønster som positivtesten
i temperatur-, trykk- og salinitetsrutinene. Matematikklibraryets egen
binære implementasjon er ikke kjørt i denne gjennomgangen.

For m > 100:

```text
Rcell = exp(CA + CB*ln(m))
N0 = BA * 10000000 / Rcell
   = BA * 10000000 * exp(-CA) * m^(-CB)
```

Den faktiske double-konstanten **comil er 10^7**. Kommentaren ved
multiplikasjonen sier 10^8, men det er feil. Bytefølgen er
`00 00 00 00 D0 12 63 41`, tolket som little-endian double.

Startverdier i `SD49INIT.ASM:263` (`coef_tbl1`):

| Koeffisient | Innebygd verdi | Rolle |
|---|---:|---|
| BA | 3.0 | Faktor i omregningen fra modellert motstand |
| CA | 14.723797125 | Konstantledd i logaritmisk motstandsmodell |
| CB | -0.99927832602 | Eksponent/stigning i logaritmisk modell |
| A3 | 0.000044712882942 | Offset i sluttkalibrering |
| B3 | 0.000098257908671 | Stigning i sluttkalibrering |
| C3 | 0.00000000000099933004820 | Annengradsledd i sluttkalibrering |

Eksponenten -CB ligger nær 1 med disse verdiene. Dette gir en nesten
lineær transformasjon, men er ikke et bevis på at sensorens fysiske
respons eller restfeil er helt lineær.

### 4.2 Temperaturavhengig driftkompensasjon

La r være aktuell korrigert RB-motstand og r0 = `rb_kald`.

```text
Hvis r > r0:
    A(N0) = H1 + H2*N0 + H3*N0²
    B(r)  = HA + HB*r + HC*r²
Ellers, også ved likhet:
    A(N0) = Z1 + Z2*N0 + Z3*N0²
    B(r)  = LA + LB*r + LC*r²

N = N0 + A(N0)*B(r)
```

Kilde: `SD48MAT.ASM:889–997`. Symbolene for H-koeffisientene heter
`coin_h1` osv.; de andre bruker `cobin_*`.

Viktige detaljer:

- r-r0 velger bare gren. Polynomet B evalueres med **r**, ikke r-r0.
- Korreksjonen adderes. Koeffisientene bestemmer om den øker eller
  reduserer verdien.
- Det finnes ingen eksplisitt begrensning av korreksjonens størrelse her,
  selv om kommentaren bruker uttrykket «maks drift».
- Kontinuitet ved r=r0 og nullkorreksjon ved referansen følger ikke
  automatisk av koden; koeffisientene må gi ønsket oppførsel.
- Alle tolv koeffisienter Z1–Z3, LA–LC, H1–H3 og HA–HC er null i den
  innebygde tabellen. Med disse verdiene er temperaturkorreksjonen null.
  Et kalibrert instrument kan ha andre verdier i EEPROM.
- Koden velger etter motstandens størrelse. H-grenen bør ikke uten
  sensorkunnskap oversettes til «varmere enn referansen».

`temp_5` med aktuell RB beregnes i `mat_comp`, som kalles fra
`pressure_cal`. Den normale sekvensen i `tem_mes` er derfor viktig:
`factor_temp` -> `pressure_cal` -> `conduct_cal`. En portering må gi
konduktivitetsberegningen den aktuelle RB-verdien, selv uten trykkutdata.

### 4.3 Sluttkalibrering

Etter korreksjonen lagres N i `cob_c`. Deretter beregnes:

```text
con_c = A3 + B3*N + C3*N²
```

Utdataenheten er mS/cm, også kalt mmho/cm i firmwaremenyen
(`SD49MOD1.ASM:200`). C er konduktivitet ved måleforholdene. Denne banen
normaliserer ikke C til 25 °C eller 15 °C, og har ikke et eget
trykkledd eller en korreksjon for vannets temperaturforsinkelse.
RB-kompensasjonen gjelder den interne målekjeden; den erstatter ikke
salinitetsformelens behandling av vannets T og P.

## 5. Trykkkompensasjon som påvirker salinitet og lydhastighet

Kilder: `SD48MAT.ASM:381` (`pressure_cal`) og `:549` (`mat_comp`).

Trykkmålingene summeres i `sum_data`. Den vanlige banen tar tre
målinger og multipliserer summen med `fp_333`; profilen som tar én
måling, hopper over dette. Deretter multipliseres med F. Denne verdien
nP lagres i `cob_t` og er trykkets rådata før trykkpolynomene.

```text
u = A2 + B2*nP + C2*nP² + D2*nP³ + E2*nP⁴ + F2*nP⁵ + G2*nP⁶

For J = K, L, M, N, O, P, Q:
    J(r) = J0 + J1*r + J2*r² + J3*r³

p_abs_bar = K(r) + L(r)*u + M(r)*u² + N(r)*u³
              + O(r)*u⁴ + P(r)*u⁵ + Q(r)*u⁶

p_dbar = 10 * max(p_abs_bar - press_atmos, 0)
```

Andretrinnet er slik koden faktisk kombinerer polynomene: det er ikke
automatisk `u + et separat driftledd`. `press_atmos` er lagret i bar;
manuell innskriving/presentasjon bruker mbar. Atmosfærebanen bruker
egne flagg for å lagre atmosfærereferansen før normal subtraksjon.
Salinitet får normalt dette relative, ikke-negative trykket i dbar.

## 6. Salinitet

`salinity_cal` (`SD48MAT.ASM:1169`) implementerer PSS-78-formen omtalt
i koden som UNESCO 44, 1983. Den bruker **kalibrert** C fra `con_c`,
temperatur `temp_t` og relativt trykk `press_p` i dbar.

For C <= 0 returnerer fastvaren S=0. For C > 0:

```text
R = C * 0.023302418

rt35 = 0.6766097 + 0.0200564*T + 0.0001104259*T²
         - 0.00000069698*T³ + 0.0000000010031*T⁴

AX = 0.4215 - 0.003107*T
BX = 1 + 0.03426*T + 0.0004464*T²
CX = p * (0.0000207 - 0.000000000637*p + 0.000000000000003989*p²)
Rp = 1 + CX/(BX + AX*R)
x = sqrt(R/(rt35*Rp))

S0 = 0.008 - 0.1692*x + 25.3851*x² + 14.0941*x³
       - 7.0261*x⁴ + 2.7081*x⁵
dS = (T-15)/(1 + 0.0162*(T-15)) *
       (0.0005 - 0.0056*x - 0.0066*x² - 0.0375*x³
          + 0.0636*x⁴ - 0.0144*x⁵)
S = S0 + dS
```

Praktisk salinitet er dimensjonsløs; dette er ikke absolutt salinitet i
g/kg. Konstanten `fp_conr` er faktisk 0.023302418, en avrundet
tilnærming til 1/42.914. Bruk den lagrede konstanten ved reproduksjon.

Ingen Hill-utvidelse for lav salinitet eller kontroll av et gyldig
T/P/S-område finnes i denne rutinen. Ved C>0 kan et negativt beregnet
S derfor passere videre til lydhastighetsberegningens kvadratrot.
Et generelt bibliotek er ikke nødvendigvis numerisk identisk:
[GSW SP_from_C](https://www.teos-10.org/pubs/gsw/html/gsw_SP_from_C.html)
tar ITS-90-temperatur og har en lavsalinitetsutvidelse under S=2.

## 7. Lydhastighet

`sound_velocity` (`SD48MAT.ASM:1510`) kjøres når `sound_bit` er satt.
Den bruker beregnet salinitet og kalibrert temperatur/trykk; dette er
ikke en selvstendig akustisk måling i denne beregningsbanen.

Med p = p_dbar/10 i **bar**:

```text
c [m/s] = X(T,p) + Y(T,p)*S + Z(T,p)*sqrt(S³) + W(p)*S²

X = poly(T, l1..l6) + p*poly(T, l7..l11)
      + p²*poly(T, l12..l16) + p³*poly(T, l17..l19)
Y = poly(T, l20..l24) + p*poly(T, l25..l29)
      + p²*poly(T, l30..l33) + p³*poly(T, l34..l36)
Z = l37 + l38*T + (l39 + l40*T)*p
W = l41 + l42*p
```

Her betyr `poly(T, a,b,c,...) = a+b*T+c*T²+...`.
Alle 42 koeffisienter er gjengitt i den vedlagte
[Python-referansen](sd208-calculations-reference.py), som følger
`fp_l1..fp_l42` i `SD48MAT1.ASM:106–147`.

Formen er Chen/Millero/UNESCO. Bruk koeffisientene i denne fastvaren
for å gjenskape instrumentets tall: nyere varianter kan ha andre
temperaturkoeffisienter. Eksempelvis er l2 her 5.03711, mens
[NPLs publiserte tabell](https://resource.npl.co.uk/acoustics/techguides/soundseawater/underlying-phys.html)
har 5.03830 i den tilsvarende posisjonen.

Fastvaren endrer midlertidig `press_p` fra dbar til bar og gjenoppretter
dbar før retur. Sluttresultatet formateres direkte til `cal_sound`;
variabelen `sound_vel` inneholder fortsatt mellomresultatet X, ikke hele c.
Dette er viktig ved portering eller inspeksjon av internminnet.

## 8. Hva vertsprogramvaren faktisk mottar

| Kontekst/felt | Innhold | Hva verten skal gjøre |
|---|---|---|
| Vanlig måleutskrift `C` | Kalibrert konduktivitet i mS/cm | Ikke legg på samme kalibrering eller RB-kompensasjon igjen |
| Vanlig måleutskrift `S` | Beregnet praktisk salinitet | Behold som instrumentberegning; skill fra egen etterberegning |
| Vanlig måleutskrift liten `c` | Beregnet lydhastighet i m/s | Ikke forveksle med stor `C` |
| Rådatautskrift `C` | Behandlet N før A3/B3/C3 | Bruk `A3+B3*N+C3*N²` én gang |
| Rådatautskrift `T`, normal råmodus | Temperaturfølerens beregnede motstand | Bruk temperaturformelen med A1–D1 |
| Rådatautskrift `T`, råkalibreringsmodus | ADC-temperaturverdi multiplisert med F | Bruk først S1–S3, deretter A1–D1 |
| Rådatautskrift `P` | Trykkverdi etter summering/midling og F | Krever trykkpolynomer, RB og atmosfærereferanse |
| Rådatautskrift `RE` | Aktuell ADC-referanse uten F-korreksjon | Diagnose/referansegrunnlag |
| Rådatautskrift `R` | Aktuell korrigert RB-motstand | Intern kompensasjonsverdi, ikke lydhastighet |

`rawpek` velger «Raw data calibration». Dette endrer blant annet T,
men **fjerner ikke linearisering eller driftkompensasjon fra rådata-C**.
Begge råmoduser skriver C fra samme `cob_c`.

`raw_data` overskriver `cal_sound` med RB for råutskriften. At et
internt tekstbuffer heter `cal_sound`, betyr derfor ikke at det alltid
inneholder lydhastighet. Identifiser alltid både utdataformat og felt.

For normale positive verdier som passer i feltet skriver rå-C-banen
seks heltallssifre med ledende nuller (`raw_desu`/`raw_reorg9`).
Den sender ikke alle desimalene fra intern N. Den siste feltutvelgelsen
tar heltallsdelen, selv om en tidligere rutine heter `truncate`.
Ikke behandle dette som et generelt flyttallsformat med ubegrenset
område eller fortegn.

Vanlig SD208-utdata har tre desimaler for C/S og temperatur, og to
for P/lydhastighet. SD204-valget bruker to for C/S. Intern S/c-beregning
bruker flyttallsverdiene før denne presentasjonsreduksjonen.
Etterberegning fra de utskrevne T/C/P-feltene kan derfor avvike litt
fra utskrevet S/c selv med samme formler.

Verten bør lagre måleteksten, instrumentidentitet, firmwareversjon,
modus og gjeldende koeffisientsett sammen med målingene. Ved egen
kalibrering bør instrumentets beregnede verdier beholdes separat.
Etter en korreksjon av C eller T/P må også S og c beregnes på nytt
dersom de skal representere de korrigerte målingene.

## 9. Drift: hva som er og ikke er implementert

Tre mekanismer er synlige i denne målekjeden:

1. ADC-kalibreringskommandoer og målinger av referansekanalen.
2. Multiplikasjon med forholdet mellom lagret og aktuell ADC-referanse.
3. Faste temperaturavhengige polynomer basert på RB, separat for
   trykk og konduktivitet.

Ingen automatisk estimering av langsiktig konduktivitetsdrift fra
tidligere vannmålinger, ingen kontinuerlig oppdatering av A3/B3/C3,
og ingen eksplisitt kompensasjon for begroing, endret cellegeometri,
saltavleiring eller temperaturforsinkelse er funnet i disse rutinene.
Slike feil korrigeres ikke bare fordi funksjonene omtales som
«driftkompensasjon».

## 10. Funn som bør følges opp ved integrasjon

- **Dokumentasjonsfeil:** `comil` er 10^7, ikke 10^8. `fp_273` er
  -273.15 selv om en kommentar sier -273.16. Flere kommentarer
  omtaler eldre rådatabaner. Bruk instruksjonene og bytekonstantene.
- **Koeffisientroller:** CA/CB og LA/LB/LC tilhører denne
  konduktivitetsbanen. Den eldre `docs/coefficients.md` betegner
  flere roller som «likely» eller «optional»; bruk kartleggingen her.
- **Timeoutbane:** `da_condfeil` kaller `cond_null`, men returnerer
  til `da_cond`, som likevel kaller `cond_flyt`. Sistnevnte tolker
  `co_z`, som ved timeout kan være ufullstendig eller inneholde eldre
  data. Nullingen alene garanterer derfor ikke at feilavlesningen
  forblir null. Dette er et statisk funn, ikke en reprodusert enhetsfeil.
- **Mottaksbuffer:** `da_cond2` flytter skrivepekeren for hvert tegn
  frem til komma; ingen eksplisitt lengdesjekk er synlig i denne sløyfen.
- **Null er tvetydig:** m<=100 blir C=0 og S=0; dersom lyd er aktivert,
  beregnes fortsatt en ferskvannslydhastighet fra S=0. En plausibel
  lydhastighet bekrefter derfor ikke at konduktivitetsmålingen lyktes.
- **Feilformat:** `truncate` kan skrive `1023  ` ved enkelte
  formatteringsfeil. Dette er ikke en universell feilstatus for alle
  sensorer; tolk det med felt/modus og behold originalteksten.
- **Ingen garanti for bare offset:** kontroller restfeil over flere
  konduktiviteter og relevante temperaturer før stigning/krumning låses.

Fastvaren er ikke endret som del av denne gjennomgangen.

## 11. Referanseberegninger og verifikasjon

[sd208-calculations-reference.py](sd208-calculations-reference.py) gir
funksjoner for sluttkalibrering av rå-C, hele banen fra modulsvar,
salinitet og lydhastighet. Den har ingen tredjepartsavhengigheter og
endrer ikke instrumentet. Kjør fra prosjektroten:

```powershell
python docs/sd208-calculations-reference.py
```

Eksempler med temperatur brukt direkte som i fastvaren:

| C (mS/cm) | T (°C) | P (dbar) | Beregnet S | Beregnet c (m/s) |
|---:|---:|---:|---:|---:|
| 42.914 | 15 | 0 | 34.9999985947 | 1506.6632609708 |
| 40 | 10 | 1000 | 36.4998896192 | 1508.1732975726 |
| 0 | 15 | 0 | 0 | 1465.9309705475 |

For å kontrollere utledningen ble referansefunksjonene sammenlignet
mot en midlertidig, begrenset tolk som leste aritmetikk, kall og grener
direkte fra assembly-koden, og dekodet dens double-konstanter:

- 100 kombinasjoner av C/T/P for salinitet og 100 for lydhastighet.
- 18 konduktivitetstilfeller med begge RB-grener, likhet ved referansen,
  m=0, grensen m=100 og gyldige svar. Begge kompensasjonsgrener fikk
  syntetiske ikke-null-koeffisienter for å prøve mer enn standardtilfellet.
- Alle 218 sammenligninger stemte innen flyttallsavrunding.
  Maksimalt absolutt avvik: S 3.55e-14, c 6.82e-13 m/s, N 1.46e-11.

Dette verifiserer utledningen av disse tre beregningsrutinene. Det er
ikke en full 8051-emulering, test av serielle feilbaner eller bekreftelse
av fysisk nøyaktighet. Referanseprogrammet bruker Python-matematikk,
annen summeringsrekkefølge og desimaltolkede koeffisienter; det lover
ikke bitidentitet med det eksterne 8051-matematikklibraryet. Trykk- og
temperaturformlene er gjennomgått statisk, ikke inkludert i de 218
numeriske sammenligningene.


## 12. PSS-78: identifikasjon og gyldighet

**Ja, fastvaren bruker PSS-78 for praktisk salinitet.** Identifikasjonen
bygger på forholdet mot 42.914 mS/cm, temperatur- og trykkpolynomene,
kvadratroten av det korrigerte forholdet, samt de karakteristiske
koeffisientrekkene i S0 og dS. De fullstendige formlene står i avsnitt 6.

Resultatet er dimensjonsløs praktisk salinitet SP. Databladene sier ppt;
vertsprogramvaren bør bruke «Praktisk salinitet (PSS-78)», eventuelt
med visningsetiketten PSU. Dette er ikke en direkte måling av saltmasse
i g/kg eller absolutt salinitet SA.

GSW oppgir gyldighet 2 < SP < 42 for PSS-78 og bruker en egen
lavsalinitetsutvidelse under 2. Denne SD208-koden har ingen slik utvidelse
og ingen kontroll av øvre salinitetsgrense. C<=0 blir S=0; alle positive
C-verdier kjøres gjennom samme polynom. Databladets 0–50 ppt dokumenterer
derfor ikke samme gyldighet eller nøyaktighet i hele intervallet.
[Kilde: TEOS-10/GSW](https://www.teos-10.org/pubs/gsw/html/gsw_SP_from_C.html).

SP=2 kan ikke oversettes til én fast konduktivitet uten temperatur og
trykk. Et område på 30–50 mS/cm er heller ikke det samme som SP=30–50.

## 13. Parameterkart og enheter for kalibrert serieutdata

Tabellen gjelder `data_reorg` i `SD249.ASM:116`, med opsjonsgrener
rundt linje 305–389. Enheten står ikke nødvendigvis i hver målelinje.
Råutskriften er et annet format, beskrevet i avsnitt 8.

| Felt | Parameter | Enhet/tolkning |
|---|---|---|
| `C` | Konduktivitet | mS/cm = mmho/cm, bekreftet av meny og beregning |
| `S` | Praktisk salinitet | Dimensjonsløs SP, PSS-78; databladene sier ppt |
| `T` | Vanntemperatur | °C |
| `P` | Trykk relativt til lagret atmosfærereferanse | dbar |
| `c` | Beregnet lydhastighet | m/s; merk liten bokstav |
| `O` | SAIV205-oksygen, separat kanal | % metning etter sensorens kalibrering |
| `X` / `V` | Turbiditet, opsjon 1 / 2 | FTU |
| `Y` / `W` | Fluorescens, opsjon 1 / 2 | µg/l, med stoff/sensor bestemt av kalibreringen |
| `Q` / `U` | Oksygen/optrode, opsjon 1 / 2 | Avhenger av sensorens utgang og koeffisientsett; databladet sier mg/l |
| `Z` / `R` | Annen sensor, opsjon 1 / 2 | Konfigurasjonsavhengig; ingen universell fysisk enhet |

`R` er kontekstavhengig: RB-motstand i råutskriften, men kan være
opsjonskanal 2 av typen «other» i vanlig måleutskrift.

Viktige regler for vertsprogramvaren:

- 1 mS/cm = 0.1 S/m = 1000 µS/cm. Stor S betyr siemens.
- C er konduktivitet ved måleforholdene, ikke automatisk normalisert
  til 25 °C. Referansetemperert konduktivitet må merkes separat.
- Databladets «dbar (m)» gjør ikke trykk og dybde til identiske enheter.
  Koden sender P i dbar, uten en egen dybdeomregning basert på
  tetthet og lokal tyngdeakselerasjon.
- FTU er ikke mg/l suspendert stoff. Ikke bytt etikett til NTU uten
  avklaring av målemetode og sensorkalibrering.
- µg/l for fluorescens må knyttes til kalibrert stoff, for eksempel
  klorofyll eller rhodamin. Signalet er ikke en universell konsentrasjon.
- **O-kanalen sender prosent, selv om databladet beskriver mg/l.**
  Menyen sier «Oxygen (OX) in per cent» (`SD49MOD1.ASM:201`), og
  `oxygen_cal` regner prosent. Ingen mg/l-omregning er funnet mellom
  denne rutinen og utskriften. Eventuell ekstern omregning er ikke
  verifisert her.
- Optrodekanalene Q/U bruker generiske kalibreringspolynomer. mg/l
  skal bekreftes fra sensorens signal og kalibrering, ikke antas fra
  feltbokstaven alene.

FTU og µg/l er bekreftet direkte i områdemenyene
`SD49MODE.ASM:623–631`, ikke bare i databladene.

## 14. Tilleggsformler og full koeffisienttabell for lydhastighet

### SAIV205-oksygen

Kilder: `SD48MAT1.ASM:819` (`ox_mvolt`), `:375` (`calo_o2`),
`SD48MAT.ASM:1047` (`oxygen_cal`).

```text
n = oxygen_ADC * F
v = X1 + X2*n + X3*n² + X4*n³
O_percent = 100*v / V

Ved kalibrering med oppgitt referansemetning O_ref_percent:
V = 100*v_ref / O_ref_percent
```

Koden omtaler v som mV. X1–X4 brukes faktisk i denne oksygenbanen,
selv om kommentaren i starttabellen sier «Pressure sensor from keller».
Dette er enda et tilfelle der instruksjonene må prioriteres over
kommentarene. Det finnes ikke et eksplisitt løselighetspolynom for
T/S/P i `oxygen_cal`. Eventuell kompensasjon inne i sensoren er ikke
synlig i denne beregningsbanen.

### Turbiditet, fluorescens og andre opsjoner

Kilder: `SD48MAT.ASM:5–69`, `optional_cal`, `optional2_cal`,
`SD48MAT1.ASM:909` (`other_cal`) og `:958` (`other_cal1`).

```text
n = optional_ADC * F
v = Y4 + Y5*n + Y6*n² + Y7*n³

Turbiditet/fluorescens, opsjon 1:
resultat = A4 + B4*v + C4*v² + D4*v³

Turbiditet/fluorescens, opsjon 2:
resultat = A5 + B5*v + C5*v² + D5*v³

Optrode/other, opsjon 1:
resultat = AO + BO*v + CO*v² + DO*v³

Optrode/other, opsjon 2:
resultat = EO + FO*v + GO*v² + HO*v³
```

A4–D4/A5–D5 fylles med valgt områdes AT–DT- eller AF–DF-koeffisienter.
Områdene er 0–12.5, 0–62.5, 0–250 og 0–750 FTU for turbiditet, og
0–2.5, 0–7.5, 0–25 og 0–75 µg/l for fluorescens.
Automatisk områdevalg bytter område/koeffisienter; det er ikke
automatisk korreksjon av langsiktig sensordrift.
Disse tilleggsformlene er gjennomgått statisk, ikke inkludert i de
218 numeriske sammenligningene fra første gjennomgang.

### Lydhastighet: alle 42 koeffisientene til formelen i avsnitt 7

Tabellen gjengir desimalverdiene til `fp_l1..fp_l42`.
Rekkefølgen innen hver rad er fra konstantledd til høyeste T-potens.
Her er p i bar, altså P_dbar/10.

| Ledd | Koeffisienter i stigende potens av T |
|---|---|
| X, p⁰: l1–l6 | 1402.388; 5.03711; -5.80852e-2; 3.3420e-4; -1.47800e-6; 3.1464e-9 |
| X, p¹: l7–l11 | 0.153563; 6.8982e-4; -8.1788e-6; 1.3621e-7; -6.1185e-10 |
| X, p²: l12–l16 | 3.1260e-5; -1.7107e-6; 2.5974e-8; -2.5335e-10; 1.0405e-12 |
| X, p³: l17–l19 | -9.7729e-9; 3.8504e-10; -2.3643e-12 |
| Y, p⁰: l20–l24 | 1.389; -1.262e-2; 7.164e-5; 2.006e-6; -3.21e-8 |
| Y, p¹: l25–l29 | 9.4742e-5; -1.2580e-5; -6.4885e-8; 1.0507e-8; -2.0122e-10 |
| Y, p²: l30–l33 | -3.9064e-7; 9.1041e-9; -1.6002e-10; 7.988e-12 |
| Y, p³: l34–l36 | 1.100e-10; 6.649e-12; -3.389e-13 |
| Z, p⁰: l37–l38 | -1.922e-2; -4.42e-5 |
| Z, p¹: l39–l40 | 7.3637e-5; 1.7945e-7 |
| W(p) | l41=1.727e-3; l42=-7.9836e-6; W=l41+l42*p |

## 15. Sammenligning av vedlagte databladbilder

Første bilde behandles som SD208 og andre som SD204, i samsvar med
brukerens beskrivelse. Utsnittene viser ikke modelloverskrift, dato
eller revisjon. Tabellen gjengir bildene, ikke en kontrollkalibrering.

| Parameter | SD208: område; oppløsning; nøyaktighet | SD204: område; oppløsning; nøyaktighet |
|---|---|---|
| Konduktivitet | 0–80 mS/cm; 0.0008 mS/cm; ±0.003 mS/cm | 0–70 mS/cm; 0.01 mS/cm; ±0.02 mS/cm |
| Salinitet | 0–50 ppt; 0.0008 ppt; ±0.003 ppt | 0–40 ppt; 0.01 ppt; ±0.02 ppt |
| Temperatur | -2 til +40 °C; 0.0002 °C; ±0.003 °C | -2 til +40 °C; 0.001 °C; ±0.01 °C |
| Trykk | Ønsket dybde bestilles; oppgitt 500/1000/2000/…6000 m; 0.01 dbar (m); ±0.01 % FS | Oppgitt 500/1000/2000/…6000 m; 0.01 dbar (m); ±0.01 % FS |
| Lydhastighet | 1300–1700 m/s; 0.5 cm/s; ±2 cm/s | 1300–1700 m/s; 1 cm/s; ±5 cm/s |
| Oksygen SAIV205 | 0–20 mg/l; 0.01 mg/l; ±0.2 mg/l | 0–20 mg/l; 0.01 mg/l; ±0.2 mg/l |
| Oksygen AADI-optrode | 0–20 mg/l; 0.08 mg/l; ±0.5 mg/l | Ikke oppgitt i utsnittet |
| Fluorescens | Områder 2.5/7.5/25/75 µg/l; oppløsning 0.03 µg/l | Samme områder og oppgitt oppløsning |
| Turbiditet | Områder 12.5/62.5/250/750 FTU; linearitet <2 % | Samme områder og oppgitt linearitet |

Presiseringer:

- Første bilde sier **0–80**, ikke 0–70 mS/cm.
- ±0.01 % FS er prosent av fullskala, ikke avlest verdi eller
  ±0.01 dbar. For fullskala 1000 dbar tilsvarer det ±0.1 dbar.
- SD208s 0.5 cm/s er 0.005 m/s; ±2 cm/s er ±0.02 m/s.
  SD204s tilsvarende tall er 0.01 og ±0.05 m/s.
- Undersøkt SD208-serieutdata har trinn 0.001 for C/S/T og 0.01 m/s
  for lydhastighet. Det bevarer ikke alle trinnene som første bilde
  angir som oppløsning. Sensoroppløsning, intern beregningsoppløsning
  og utdataoppløsning må skilles.
- «Linearitet <2 %» er ikke en fullstendig nøyaktighetsspesifikasjon;
  bildet presiserer ikke prosentgrunnlaget.
- SD208-bildets «Temp. & Press. Comp.» identifiserer ikke hvilken
  del av systemet som kompenserer. Hovedfastvaren viser RB-korreksjon
  av C og trykkkorreksjon i salinitetsformelen, men ingen egen P-term
  i `conduct_cal`. Eventuell kompensasjon i kortet/sensoren er ikke
  avklart ved gjennomgangen av hovedfastvaren.

SD204-tallene er mindre ambisiøse for flere parametere, men er heller
ikke verifisert for det aktuelle instrumentet her. Vi kan vurdere
teknikken og dokumentasjonen; den enkelte ingeniørens motiver eller
årsaken til spesifikasjonsforskjellene kan ikke fastslås fra materialet.

## 16. Praktisk konduktivitetsområde og referansegrunnlag

Brukeren oppgir følgende erfaringer. «Ikke lavere enn 4» tolkes
foreløpig som **4 mS/cm**, ikke SP=4. Tallene er erfaringsgrunnlag,
ikke sertifiserte måleusikkerheter.

| Område | Oppgitt erfaring | Dokumentasjonsstatus |
|---|---|---|
| 30–50 mS/cm | Omtrent ±0.005 mS/cm | Foretrukket område; må knyttes til kalibrering/instrument |
| Utenfor 30–50, innen praktisk brukt område | Omtrent ±0.01 mS/cm | Nøyaktige yttergrenser og temperaturbetingelser er ikke oppgitt |
| Helt ved ytterkantene | Omtrent ±0.03–0.04 mS/cm | Ytterkantene er ikke tallfestet; ikke innfør skarpe programgrenser |
| Under 4 mS/cm | Ikke oppgitt som godkjent bruksområde | Utenfor brukerens foreløpige valideringsområde |

Det er faglig riktig å skille et bredt avlesningsområde fra et smalere
område med dokumentert nøyaktighet. Koden alene kan ikke bevise
±0.003, ±0.005 eller ±0.02 mS/cm i et fysisk instrument. Det krever
målinger mot referanse med kjent usikkerhet, temperaturbetingelser og
en definisjon av om tallene gjelder maksimal feil, repeterbarhet
eller utvidet måleusikkerhet.

En foreslått foreløpig formulering er:

> Databladet oppgir et bredt måleområde. Brukererfaring peker på
> 30–50 mS/cm som foretrukket område, med restfeil omkring ±0.005 mS/cm.
> Utenfor dette området øker observert avvik. Ytelse under 4 mS/cm
> er ikke bekreftet for den beskrevne bruken. Grensene må knyttes til
> dokumenterte kalibreringer før de brukes som garantier.

Dette er en formulering av brukerens erfaring, ikke et sitat fra et
kalibreringssertifikat. **±0.03–0.04 ved ytterkantene er også dårligere
enn SD204-databladets ±0.02.** Å velge SD204-tallene alene løser
derfor ikke spørsmålet om garanti over hele området.

Ferskvann betyr heller ikke nøyaktig null konduktivitet; naturlig
ferskvann inneholder oppløste ioner. Et lavt fysisk signal må holdes
atskilt fra null som fastvaren produserer etter grensekontroll/feil.
[Kilde: USGS](https://www.usgs.gov/water-science-school/science/conductivity-electrical-conductance-and-water?qt-science_center_objects=0).

### Portasal: elektrisk område versus salinitetsområde

Brukerens Portasal-modell, sertifikat og laboratoriets validerte
område er ikke oppgitt. Nedre grense kan derfor ikke overføres til
alle Portasal-instrumenter.

For **Guildline 8410A** oppgir produsentmanualen 0.004–76 mS/cm som
elektrisk måleområde, 2–42 som salinitetsområde og ±0.003 ekvivalent
PSU som nøyaktighet under angitte standardiserings- og temperaturbetingelser.
Det elektriske området er ikke en garanti for samme salinitetsnøyaktighet
helt ned til 0.004 mS/cm.
[Kilde: Guildline 8410A, avsnitt 2.2](https://www.guildline.com/media/k2/attachments/OM8410A-J-00.pdf).

Laboratoriets brukbare referanseområde kan godt være smalere enn
det elektriske området, men 4 mS/cm er ikke dokumentert som en
generell Portasal-grense i denne manualen. Referansemåling ved
Portasal-badets temperatur må dessuten sammenlignes med CTD ved
samme T/P eller via konsistent beregnet SP; konduktiviteter ved
forskjellige temperaturer kan ikke trekkes direkte fra hverandre.

Vertsprogramvaren bør lagre databladområde, faktisk kalibrert område,
erfaringsområde og utdataoppløsning separat. Behold og merk målinger
utenfor validert område fremfor å klippe dem. Ikke innfør en automatisk
garanti på ±0.005 mS/cm bare fordi C ligger mellom 30 og 50.
