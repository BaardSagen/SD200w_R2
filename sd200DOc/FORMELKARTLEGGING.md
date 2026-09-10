# Formler og beregninger i MiniSoft SD200W

Dato: 7. september 2026.

Analysert program: `SD200W_SAIV_OSU107_NoHandshake.exe`.
SHA-256: `3908bded6ca05244bee62e4eded3a3042b8cff9bf043c003012b44fd63aa8599`.

## Hva denne kartleggingen dekker

Dette er en kartlegging av beregninger funnet i Windows-programmets maskinkode og skjemaressurser. Programmet er ikke endret under kartleggingen.

De viktigste havvannsberegningene er rekonstruert. Det er **ikke dokumentert at absolutt alle formler i hele EXE-filen er funnet**. Enkelte kalibreringsrutiner, profilbehandling og biblioteksfunksjoner er identifisert, men ikke fullt rekonstruert. Disse er markert nedenfor. Original Delphi-kildekode er ikke tilgjengelig i prosjektet.

Dokumentene i `docs` beskriver også SD204/SD208-instrumentets firmware. Firmwareberegninger og Windows-programmets beregninger må holdes atskilt: en temperatur kan være ferdig beregnet i instrumentet før programmet mottar den. Det samme gjelder målelinjer videresendt av OSU107 og SAIV110. Dokumentasjon om en firmwareformel beviser ikke at samme formel kjøres i Windows-programmet.

### Dokumentasjonsnivå

- **A — rekonstruert og numerisk kontrollert:** formelen er lest fra maskinkoden og sammenlignet med kjøring av den samme maskinkoden i emulator.
- **B — rekonstruert fra kode:** operasjoner og konstanter er fulgt, men egen numerisk sammenligning er ikke gjennomført.
- **C — funksjon eller formelvalg funnet:** støttes av skjemaressurser, hendelsesmetoder eller kall, men hele beregningskjeden er ikke ferdig verifisert.

Adressene nedenfor er virtuelle adresser ved standard innlasting på `0x00400000`. De gjør funnene etterprøvbare, men er ikke originale Delphi-funksjonsnavn.

## Oversikt

| Beregning | Hva den brukes til | Inndata | Resultat | Nivå / adresse |
|---|---|---|---|---|
| Saltholdighet fra konduktivitet | Konvertering, gjenberegning og behandling av måledata | Konduktivitet, temperatur, trykk | Praktisk saltholdighet | A, `0x0050A5B8` |
| Konduktivitet fra saltholdighet | Omvendt konvertering | Saltholdighet, temperatur, trykk | Konduktivitet | B, `0x0050A6E0` |
| Lydhastighet | Lydhastighetsprofil og gjenberegning av STD-data | Saltholdighet, temperatur, trykk | m/s | A, `0x0050A8F0` |
| Sigma T | Tetthetsavvik ved null sjøtrykk | Saltholdighet og temperatur | kg/m³ minus 1000 | A, `0x0050C18C` |
| Trykkavhengig tetthet | Tetthetsvisning og avledede beregninger | Saltholdighet, temperatur, trykk | Tetthetsavvik; legg til 1000 for kg/m³ | A, `0x0050C330` |
| Eldre tetthetsformel | Alternativ gren i tetthetsrutinen | Saltholdighet og temperatur | Tetthetsavvik | A, `0x0050BF08`, alternativ gren |
| Tyngdeakselerasjon | Dybdeberegning | Breddegrad og trykk | m/s² | B, `0x0050CB5C` |
| UNESCO-dybde | Omregning fra dbar til meter | Trykk og breddegrad | Meter | B, `0x0050CEA4` |
| Dybde fra tetthet og gravitasjon | Alternative dybdevalg | Trykk, tetthet, posisjon | Meter | B, `0x0050BCF8` |
| Oksygen ved 100 % metning | Omregning av metningsprosent til konsentrasjon | Temperatur, saltholdighet, lufttrykk | mg/l, deretter andre enheter | B, `0x0050C818` |
| Temperatur fra motstand | Temperaturkalibrering/gjenberegning | Motstand og kalibreringskoeffisienter | °C | B, `0x0052A320` |
| Konduktivitetskalibrering | Tilpasning mot referansemålinger | Instrumentfaktor, referanse og koeffisienter | Kalibrert verdi/koeffisienter | C; fire eksplisitte formelvalg |
| Kalibreringstilpasning og avvik | Finne koeffisienter og vurdere tilpasning | Kalibreringspunkter | Koeffisienter og avvik | C, blant annet `0x0053FC30` |
| Standarddybder og gjennomsnitt | Bearbeide profiler til tabeller og grafer | Målinger og dybdeintervaller | Bearbeidede profiler | C; eksakt vekting/interpolasjon ikke rekonstruert |
| Rinko-oksygenkalibrering | Kalibrering av optisk oksygensensor | Kalibreringsdata | Sensorens kalibrering | C, menyhendelse `0x005AB7D4` |

## 1. Saltholdighet fra konduktivitet

**Bekreftet i kode og numerisk kontrollert.** Koeffisientmønsteret identifiserer en PSS-78-beregning.

Symboler: `C` = konduktivitet i mS/cm, `T` = temperaturverdien som tilføres rutinen, `P` = sjøtrykk i dbar. Den historiske PSS-78-algoritmen er definert med eldre temperaturskala; en eventuell korreksjon av temperatur før kall er ikke kartlagt fullstendig.

```text
R = C / 42.914
rt = 0.6766097 + 0.0200564 T + 0.0001104259 T²
     - 6.9698×10⁻⁷ T³ + 1.0031×10⁻⁹ T⁴

Rp = 1 + P(2.07×10⁻⁵ - 6.37×10⁻¹⁰ P + 3.989×10⁻¹⁵ P²)
         / [1 + 0.03426 T + 0.0004464 T² + (0.4215 - 0.003107 T)R]

x = sqrt(abs(R / (rt Rp)))
d = T - 15

S = 0.008 - 0.1692 x + 25.3851 x² + 14.0941 x³ - 7.0261 x⁴ + 2.7081 x⁵
    + d/(1 + 0.0162d) ×
      (0.0005 - 0.0056x - 0.0066x² - 0.0375x³ + 0.0636x⁴ - 0.0144x⁵)
```

Programmet returnerer 0 når `C < 0.01`. Absoluttverdien før kvadratroten er også faktisk til stede i koden. Slike kodegrenser er ikke det samme som et dokumentert fysisk gyldighetsområde.

**Bruk:** menyen for konduktivitet/saltholdighet og flere data-/gjenberegningsrutiner. Kall ved `0x0050B4F1` lagrer resultatet i saltholdighetsfeltet. Kall finnes også i området som behandler instrumentdata.

Den motsatte rutinen, `0x0050A6E0`, starter med `sqrt(S/35)`, bruker den deriverte av saltholdighetspolynomet til iterativ løsning, og beregner konduktivitet tilbake med temperatur- og trykkorreksjon. En toleranse på `10⁻⁹` er funnet. Denne inverse rutinen er ikke numerisk kontrollert her.

## 2. Lydhastighet

**Bekreftet i kode og numerisk kontrollert.**

```text
p = P / 10                       # fra dbar til bar internt
c = W(T,p) + A(T,p)S + B(T,p)sqrt(S³) + D(p)S²
D = 0.001727 - 7.9836×10⁻⁶ p
B = -0.01922 - 4.42×10⁻⁵ T + (7.3637×10⁻⁵ + 1.7945×10⁻⁷ T)p
```

`W` og `A` er polynomer i temperatur og trykk. Alle uttrukne koeffisienter står i Python-vedlegget nederst, funksjonen `sound_velocity`. Resultatet er m/s.

**Bruk:** «Compute Sound velocity», lydhastighetsprofiler, beregning etter konduktivitet/saltholdighetskonvertering og flere gjenberegningsrutiner. Resultatet påvirkes av både temperatur, saltholdighet og trykk; det er ikke bare en temperaturkorreksjon.

## 3. Tetthet og Sigma T

**Bekreftet i kode og numerisk kontrollert.** Programmet har flere grener.

### Sigma T uten trykkorreksjon

```text
ρw = 999.842594 + 0.06793952 T - 0.00909529 T²
     + 0.0001001685 T³ - 1.120083×10⁻⁶ T⁴ + 6.536332×10⁻⁹ T⁵
A = 0.824493 - 0.0040899 T + 7.6438×10⁻⁵ T²
    - 8.2467×10⁻⁷ T³ + 5.3875×10⁻⁹ T⁴
B = -0.00572466 + 0.00010227 T - 1.6546×10⁻⁶ T²
ρ0 = ρw + AS + B S^(3/2) + 0.00048314 S²
SigmaT = ρ0 - 1000
```

`0x0050C18C` bruker `sqrt(S³)`; den trykkavhengige varianten bruker `sqrt(abs(S³))`. Ved normale, ikke-negative saltholdigheter er uttrykkene like.

### Tetthet med trykkorreksjon

```text
p = P / 10
K = K0(S,T) + A(S,T)p + B(S,T)p²
ρ = ρ0 / (1 - p/K)
rutineresultat = ρ - 1000
```

Alle koeffisientene for kompresjonsleddet `K` står i vedleggets `density_anomaly`. Det er viktig at rutinen returnerer **tetthetsavvik**, ikke hele tettheten. Eksempelvis betyr resultat 26 at tettheten er 1026 kg/m³.

### Eldre alternativ

En tredje gren i `0x0050BF08` beregner:

```text
s = S - 35
q = 28.1263 + 0.806s + 0.00023s² + 0.0000068s³
a = (4.7867T - 0.098185T² + 0.0010843T³) × 0.001
b = (18.03T - 0.8164T² + 0.01667T³) × 0.000001
w = -(T+283)(T-3.98)² / [503.57(T+67.26)]
resultat = [1-a+(q-0.1324)b](q+0.1324)+w
```

Dette er en separat beregningsgren. Den er ikke trykkavhengig. Den nøyaktige koblingen mellom alle lagrede modusverdier og dagens menyvalg er ikke ferdig kartlagt.

## 4. Dybde og gravitasjon

**Rekonstruert fra kode; ikke numerisk kontrollert i emulator i denne gjennomgangen.**

Skjemaet «Depth calculation» inneholder fire valg:

1. Pressure dbar (no calc.)
2. Depth (Unesco 1983)
3. Depth = P/(Density x Gravity) Fixed position
4. Depth = P/(Density x Gravity) Profiling

Gravitasjon:

```text
x = sin(latitude × π/180)²
g = 9.780318[1 + (0.0052788 + 0.0000236x)x] + 0.000001092P
```

UNESCO-dybde:

```text
z = [((-1.82×10⁻¹⁵P + 2.279×10⁻¹⁰)P - 2.2512×10⁻⁵)P + 9.72659]P / g
```

Alternativ beregning fra tetthet:

```text
z = 10000P / (ρg)
  = 10P / [(1 + tetthetsavvik/1000)g]
```

Koden legger til et separat trykk-/referanseledd før valg av dybdeberegning. Det finnes også behandling av profildata rundt rutinen. Forskjellen mellom «Fixed position» og «Profiling» må derfor vurderes i hele profilbehandlingen; de to menyvalgene beviser ikke at begge bare bruker én enkelt uavhengig beregning per rad.

## 5. Oksygen

**Rekonstruert fra kode; ikke numerisk kontrollert her.**

`0x0050C818` beregner konsentrasjonen ved 100 % metning, korrigert for saltholdighet og lufttrykk. Wrapperkoden multipliserer med mottatt metningsprosent og deler på 100.

```text
K = T + 273.15
L = exp(-139.34411 + 157570.1/K - 66423080/K²
        + 12438000000/K³ - 862194900000/K⁴)
Fs = exp[-S(0.017674 - 10.754/K + 2140.7/K²)]
θ = 0.000975 - 0.00001426T + 0.00000006436T²
v = exp(11.8571 - 3840.7/K - 216961/K²)
p = lufttrykk_i_mmHg × 0.00131578955679
Fp = (1-θp)(p-v) / [(1-v)(1-θ)]
O100 = L × Fs × Fp
O_mg/l = O100 × metning_prosent / 100
```

Dersom nevneren i trykkorreksjonen er null, bruker programmet korreksjonsfaktor 1.

Enhetsgrener som er funnet:

```text
mg/l → ml/l:   × 22.391 / 31.998
mg/l → µmol/l: × 1000 / 31.998
mg/l → µmol/kg: × 22.391 × 1000 / [716.467218 × (ρ/1000)]
```

Det siste uttrykket er gjengitt med programmets faktiske konstanter. Det bør ikke forenkles ved å bytte inn en annen avrundet omregningsfaktor dersom målet er identiske resultater.

**Bruk:** «Calc values», valg av oksygenenhet og oppdatering av barometrisk trykk. Programmet kan bruke angitt saltholdighet når instrumentet ikke leverer den. Den interne wrapperen har også en fast reserveverdi i én gren; hele forrangen mellom innstillinger, filmetadata og målinger er ikke kartlagt.

## 6. Temperatur og kalibrering

**Temperaturformelen er rekonstruert fra kode.** Med `r = ln(R)` beregner `0x0052A320`:

```text
T = 1 / (a + br + cr² + dr³) - K0
```

`R` er motstandsverdien som tilføres rutinen. En variant ved `0x0052A2EC` setter andregradsleddet `c` til null:

```text
T = 1 / [a + b ln(R) + d ln(R)³] - K0
```

`K0` leses fra en global innstilling. Kalibreringsskjemaet har valgene «4 coefficients» og «Old Kelvin constant». Derfor bør man ikke anta at alle filer og innstillinger bruker samme Kelvin-konstant uten å følge innstillingen. Andre kodedeler bruker uttrykkelig 273.15.

**Bruk:** temperaturkalibrering fra motstands- og referanseverdier og kontroll/gjenberegning av kalibrering. Dette betyr ikke at hver tekstlinje i terminalen regnes om med denne formelen.

## 7. Konduktivitetskalibrering

Fire uttrykk er eksplisitt lagret i programmets formelvelger ved `0x006038A6`:

```text
y = a + bx + cx² + dx³
y = a + bx + cx²
y = 1 / (a + b x^2.5 + c/x)
y = a + bx
```

Programmet omtaler alternativene som blant annet «3p formula», «2p formula», «SAIV 1/x formula» og «Linear formula». Skjemaene har felter for instrumentets konduktivitetsfaktor og målt referansekonduktivitet.

**Hva de er til:** beskrive sammenhengen mellom instrumentets kalibreringsinngang og ønsket konduktivitet, og finne koeffisienter fra referansepunkter. Dette er noe annet enn PSS-78-formelen som beregner saltholdighet fra ferdig konduktivitet.

**Begrensning:** uttrykkene er bekreftet som formelvalg. Skalaen til `x`, eventuelle transformasjoner og alle koeffisientknytninger til instrumentkommandoene er ikke fullt rekonstruert.

## 8. Andre beregninger og uavklarte deler

| Område | Hva som faktisk er funnet | Hva som ikke er ferdig avklart |
|---|---|---|
| Kalibreringstilpasning | LSQFIT-valg, ssq-tekst, numerisk tilpasningskall fra `0x0053FC30` | Nøyaktig målfunksjon, vekter og stoppkriterier for alle alternativer |
| Temperaturdrift | Kalibreringsskjema med driftstabell og `CalcBtn7Click` ved `0x0054771C` | Full driftformel og koeffisienttolkning |
| Rinko | Egen kalibreringsmeny og hendelse ved `0x005AB7D4` | Sensorformelen og alle koeffisienter |
| Standarddybder | Menyer for standarddybder, dybdeseksjoner og gjennomsnitt over passeringer | Interpolasjonsmetode, vekting, tomme intervaller og maskeringsregler |
| Temperatur-/trykkoffset | Programtekst om automatisk justering av saltholdighet og lydhastighet | Full kjede fra offsetinnstilling til hver berørt datakolonne |
| Rettelse av gamle filer | Egen funksjon for feil saltholdighet/konduktivitet i eldre innlesning | Eksakte vilkår og korreksjonsfaktor |
| Grafer og generelle biblioteker | Blant annet polynomgrad 1–20 og andre graf-/matematikktekster | Om hver biblioteksfunksjon er i aktiv bruk i programmet |
| Turbiditet/fluorescens | Målekanaler i programmet; firmwaredokumentasjon omtaler koeffisientgrupper | Ikke bekreftet at firmwareformlene også er implementert som PC-beregninger |

Det er ikke satt inn generiske formler for disse områdene som om de var verifisert programkode.

## 9. Numerisk kontroll

24 sammenligninger mellom rekonstruert Python-formel og original maskinkode fra den analyserte EXE-filen bestod med toleranse `rel_tol=10⁻⁹`, `abs_tol=10⁻⁸`:

- Lydhastighet: 5 kombinasjoner av saltholdighet, temperatur og trykk.
- Trykkavhengig tetthetsavvik: 5 kombinasjoner.
- Sigma T: 5 kombinasjoner.
- Eldre tetthetsgren: 5 kombinasjoner.
- Saltholdighet: 4 kombinasjoner, inkludert null konduktivitet.

Testene omfattet temperaturer 0–20 °C, saltholdighet 0–40 og trykk 0–4000 dbar i de valgte kombinasjonene. Dette er en kontroll av rekonstruksjonen, ikke en dokumentasjon av målenøyaktighet eller hele algoritmens gyldighetsområde.

Testene ble kjørt i emulator. Ingen kommandoer ble sendt til instrumentene.

Filer med etterprøvbar dokumentasjon:

- [Testresultater](../analysis/formula_numeric_validation.json)
- [Testprogram](../analysis/test_recovered_formulas.py)
- [Rekonstruerte formler i Python](../analysis/recovered_formulas.py)
- [Lydhastighetens maskinkode med konstanter](../analysis/formula_sound_code.txt)
- [Tetthet, oksygen og dybde: maskinkode](../analysis/formula_math_disassembly.txt)
- [Saltholdighet: maskinkode og konstanter](../analysis/formula_salinity_sound_disassembly.txt)
- [Tekstfunn fra programmet](../analysis/formula_strings.txt)

## 10. Kilder og tolkning

Hovedkilden er den lokale EXE-filen, dens x87-regneinstruksjoner, konstanter, funksjonskall og Delphi-skjemaressurser. Norske beskrivelser og navn på rekonstruerte Python-funksjoner er laget for denne rapporten.

PSS-78/EOS-80 er navn på de historiske beregningssystemene som koeffisientmønstrene peker på. UNESCO-materiale er tilgjengelig via den offisielle [oversikten over UNESCO 1983-algoritmer](https://www.teos-10.org/preteos10_software/unesco_44.html) og [PSS-78/EOS-80-dokumentasjonen](https://www.teos-10.org/preteos10_software/unesco_36.html). Dette er bakgrunn for identifikasjon; formlene i denne rapporten er hentet fra programmet.

Den lokale [koeffisientoversikten for firmware](../docs/coefficients.md) merker selv flere forbindelser som antakelser. De er derfor ikke brukt som bevis på eksakte Windows-formler.

## Vedlegg: komplette rekonstruerte kjerneformler

Koden nedenfor gjør alle koeffisientene for blant annet lydhastighet og trykkavhengig tetthet tilgjengelige i denne ene Markdown-filen. Normaldatagrenene er gjengitt; programmenes øvrige feilhåndtering og globale innstillingsvalg er ikke fullstendig gjenskapt. Oksygen og dybde er foreløpig kodeavleste, ikke numerisk validerte.

```python
"""Reconstructed measurement formulas from NoHandshake EXE; see FORMELKARTLEGGING.md.
Not a replacement for production calibration or the original program.
"""
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

```

## Etterf?lgende kontroll av mulige feil

Se [FORMELKONTROLL.md](FORMELKONTROLL.md) for referansetester og funn om oksygenets faste saltholdighet, ugyldige inndata, lavsalinitet og temperaturskala. Den inverse saltholdighetsrutinen er n? kontrollert i tre numeriske rundturer. Oksygenets normalgren er ogs? sammenlignet med rekonstruksjonen i tre pr?ver.


## Tillegg 10. september 2026: guide og metodevalg 1.4.6/1.4.7

Temperaturhandleren cbKelvinCelsiusClick er identifisert ved 0x00545FF4. Avkrysset Old Kelvin constant skriver 273,16 (0x00546009); uten hake skrives 273,15 (0x0054601D). Handleren starter ogs? ny tilpasning av koeffisientene. Firekoeffisient-rutinen 0x0052A320 bruker 1/(a+b*ln(R)+c*ln(R)^2+d*ln(R)^3)-K0; trekoeffisient-rutinen 0x0052A2EC utelater c-leddet. Samme motstand og koeffisienter gir 0,01 C lavere T med gammel konstant. ?rsgrense/serienummergrense etter 2000 er ikke bevist av Windows-koden.

Profilgrenen 0x0050D5A4/mode 3 bygger dybdetabell via 0x0050D374. Ved nye trykkmaksima bruker 0x0050D1E0 endepunktsregelen z_i=z_prev+10000*(P_i-P_prev)/(rho_i*g_i); f?rste positive punkt skaleres fra null. 0x0050D024 interpolerer mellom trykk-/dybdeknuter ved trykk innenfor tabellen. Retningen kan reverseres. Normalregel og interpolasjon er kontrollert med native kode og kontrollerte tetthets-/gravitasjonskall; alle maske-/offset-/profilavgrensningsgrener er ikke validert.

45 kontroller inklusive tidligere kjerneformler: analysis/formula_guide146_validation.json og analysis/verify_formula_guide146.py. Guidens Python-referanse i docs/SIT_FORMULA_REFERENCE.md inneholder alle rekonstruerte kjernekoeffisienter.

1.4.7 tilbyr eksplisitte alternativer i Convert: GSW PSS-78/Hill, SA/CT, TEOS-10 eksakt tetthet/lydhastighet, flere dybdemetoder, Garcia-Gordon oksygen og akustiske alternativer. Implementasjonen og begrensningene beskrives i ../LES_MEG_Conversion_Models_147.md og ../docs/SIT_CONVERSIONS_AND_FORMULAS.md. Den gamle Delphi-kjernen bruker fortsatt sine opprinnelige formler. Ny SIT-lignende profilmodus er en dokumentert implementasjon av normalregelen, ikke et l?fte om identitet med alle native profiler.
