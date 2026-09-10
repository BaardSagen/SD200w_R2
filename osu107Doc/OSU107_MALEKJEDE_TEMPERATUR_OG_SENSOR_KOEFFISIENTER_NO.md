# OSU107: fra ADC-måling til temperaturkompensert spenning og sensorverdi

## Formål og grunnlag

Dette dokumentet er et arbeidsgrunnlag for AI-assistert programvareutvikling. Det beskriver hvordan OSU107 først fungerer som en kalibrert spenningsmåler, korrigerer for temperaturdrift i elektronikken, og deretter beregner en fysisk sensorverdi med koeffisientene til den aktuelle kanalen.

Beskrivelsen er kontrollert mot lokal kildekode etter GitHub-oppdatering 10. september 2026, commit `9680773`. Aktivt prosjekt er `osu107/`. PCB 3.1.2 og 3.3.0 håndteres med maskinvareprofiler i dette prosjektet; gamle prosjektmapper skal ikke brukes som implementasjonsgrunnlag.

Omfanget er den analoge spenningskjeden gjennom ADS1263 og kanalpolynomet. Separat motstandsmåling, NTC-omregning og data som allerede er beregnet av et tilkoblet instrument, må behandles etter sine egne målekjeder.

Formler og «dagens oppførsel» nedenfor beskriver implementasjonen. Avsnittene om kalibreringsarbeid og akseptansekriterier er krav/anbefalinger for videre arbeid. Dokumentet angir ingen garantert nøyaktighet: denne må dokumenteres med målinger for aktuell enhet, sensor, måleområde og temperaturintervall.

## 1. Hele målekjeden

```text
Sensorens analoge spenning
  -> inngang og valgt ADG708-multiplekserkanal
  -> ADS1263, settling og gjennomsnitt av ADC-prøver
  -> signert råkode
  -> referanseskalering og volt_drift_gain
  -> global spenningskalibrering: a + b*x + c*x²
  -> temperaturkompensasjon av elektronikken
  -> kalibrert og temperaturkompensert spenning i mV
  -> kanalens polynom: c0 + c1*x + ... + cn*xⁿ
  -> sensorverdi i kanalens enhet
  -> formatering og logging
```

Det er to forskjellige sett med koeffisienter:

| Lag | Konfigurasjon | Formål |
|---|---|---|
| Instrumentkalibrering | `adc_core.ini` | Gjøre OSU107 til en kalibrert spenningsmåler og kompensere temperaturdrift |
| Kanal-/sensorkalibrering | `adc_channels.ini` | Omregne den ferdig korrigerte spenningen til sensorens utgangsverdi |

Kanalpolynomet mottar **mV**, etter både global spenningskalibrering og temperaturkompensasjon. Det mottar hverken råkode eller volt.

## 2. Måling, nullpunkt og referanser

Den aktuelle spenningsbanen bruker ADS1263. Referansemålingen bruker ADR4525 via ADG708 CH7/S8 til AIN9, og ADS1263 REFOUT på AIN4. I PCB 3.1.2-profilen er CH6/S7 nullreferansen mot AINCOM/AGND. Bruk valgt maskinvareprofil og `gnd_ref_ch`; ikke bland nullbasert CH-nummer med S-nummer.

`startup_calsys_enable` styrer systemets offsetkalibrering. Konfigurasjonsmodellen beskriver CALSYS ved første eksterne måling i en logisk loggerøkt. Ved SYSTEMOFF-oppvåkninger i samme økt gjenbrukes øktens lagrede OFCAL-profil. En ny offsetkalibrering for hver rad skal derfor ikke innføres som en antatt eksisterende funksjon.

Eksterne sensorer og analogkretsen har felles oppvarmingstid, `sensor_preheat_seconds` (standard i modellen: 2 sekunder). Settling etter kanalskifte og gjennomsnittsmåling er også en del av måleresultatet. Runtime-planen velger 50 eller 100 SPS etter tidsbudsjett, med 8 forkastede konverteringer etter multiplekserskifte og et tilpasset antall prøver. Bruk eksisterende samplingplan fremfor å anta et fast antall målinger for alle loggerintervaller.

### Lagret referanse ved kalibrering

`INTREF.CAL` beregner:

```text
ratio_cal = raw_AIN4 / raw_AIN9_ADR4525
vref_int_mV = adr4525_mV * ratio_cal
```

Baseline lagres som `intref_ratio_cal`, sammen med den interne referansespenningen og kalibreringstemperaturen. Kommandoen setter driftfaktoren tilbake til 1.

`INTREF.ADJ` bruker en ny referansemåling:

```text
volt_drift_gain = ratio_now / intref_ratio_cal
```

Dette er en egen referansejustering. Temperaturformelen nedenfor må ikke omtales som om den automatisk gjør en slik ny referansejustering for hver sensorprøve.

ADR4525s nominelle 2500 mV er ikke alene dokumentasjon på absolutt nøyaktighet for hele instrumentet. Den ferdige spenningsbanen må kalibreres mot kjente eksterne spenninger.

## 3. Hvordan temperaturen måles

Kompensasjonen bruker **ADS1263s interne temperaturføler**. Den beskriver temperaturen i ADC-en og brukes som indikator på elektronikkens temperaturdrift. Den er ikke en måling av sjøtemperatur eller automatisk av temperaturen i en ekstern sensor.

`Ads1263Service::readTemperatureSensor()` leser den interne TEMP-banen og returnerer en gjennomsnittlig råkode. Tjenesten håndterer midlertidige registerinnstillinger og gjenoppretter dem etter lesingen.

Den felles temperaturfunksjonen beregner:

```text
temp_uV = raw_temp * vref_mV * 1000 / 2147483648 * volt_drift_gain
T_ads_C = (temp_uV - 122400) / 420 + 25
```

Konstantene `122400 µV` ved 25 °C og `420 µV/°C` er de som brukes i firmware. Global spenningskalibrering med `volt_cal_a_mV`, `volt_cal_b` og `volt_cal_c_per_mv` brukes ikke i denne temperaturberegningen.

Ved `INTREF.CAL` lagres temperaturen som `intref_cal_temp_uv` og `intref_cal_temp_c`. Sistnevnte er temperaturmodellens referansepunkt, `T0`.

I instrument- og surface-loggeren tas runtime-temperaturen med 8 prøver ved 50 SPS når kompensasjonen er klar. Temperaturcache forsøkes oppdatert når den mangler eller er minst 10 sekunder gammel. Servicekommandoer kan bruke andre prøveantall eller ADC-hastigheter.

Hvis en ny temperaturlesing feiler, kan loggeren bruke tidligere cache. Uten gyldig cache blir verdien ikke temperaturkorrigert. Dette må tas med når kvaliteten på en måling vurderes; en aktivert innstilling betyr ikke at en fersk temperaturmåling alltid foreligger.

## 4. Fra råkode til kalibrert voltmeter

Følgende er den faktiske rekkefølgen i `ads1263_channel_math.hpp`.

### Trinn A: råkode til referanseskalert mV

```text
V_true_mV = raw * vref_mV / 2147483648 * volt_drift_gain
```

`raw` er signert 32-bits ADC-kode. Nevneren er `2^31`, ikke `2^32` eller `2^31 - 1`. Beregningen gjøres med `double`.

Fellesfunksjonen bruker `vref_int_mV` når `vref_valid` er sann og verdien er positiv, ellers 2500 mV. Den bruker konfigurert `volt_drift_gain` når `0 < gain <= 100`, ellers 1. Disse fallbackene gjør beregning mulig, men dokumenterer ikke gyldig kalibrering.

Navnet `true` er et mellomresultat i firmware; det betyr ikke at alle korreksjoner allerede er utført. Formelen har ingen egen PGA-divisor. Endring av ADC-gain eller inngangsskalering krever derfor kontroll av hele måleprofilen og matematikken.

### Trinn B: global spenningskalibrering

```text
V_base_mV = volt_cal_a_mV
          + volt_cal_b * V_true_mV
          + volt_cal_c_per_mv * V_true_mV²
```

| Parameter | Enhet | Betydning |
|---|---|---|
| `volt_cal_a_mV` | mV | Offsetkorreksjon |
| `volt_cal_b` | dimensjonsløs | Lineær skalafaktor |
| `volt_cal_c_per_mv` | 1/mV | Andregradsledd |

Identitetskalibrering er `a=0`, `b=1`, `c=0`. Andregradsleddet finnes i oppdatert kode og må tas med selv om eldre dokumenter bare viser en lineær modell.

### Trinn C: temperaturkompensasjon

```text
dT = T_ads_C - intref_cal_temp_c
V_tcomp_mV = V_base_mV + dT * (
    volt_temp_comp_a_mV_per_c
    + volt_temp_comp_b_per_c * V_base_mV
)
```

Temperaturens offsetkoeffisient har enhet mV/°C. Temperaturens gainkoeffisient har enhet 1/°C. Begge er korreksjonskoeffisienter: hvis målefeilen øker med temperaturen, må korreksjonen motvirke denne økningen. Ikke kopier fortegnet fra et feilplott uten å definere hva feilen betyr.

`volt_comp_ready()` krever aktivert `volt_temp_comp_enable`, positiv `intref_ratio_cal` og endelig `intref_cal_temp_c`. `apply_volt()` krever i tillegg en gyldig runtime-temperatur og endelig inngangsverdi. Ellers returneres `V_base_mV` uten temperaturkorreksjon.

Disse kontrollene er ikke en full kvalitetskontroll av temperaturbaseline. Eksempelvis kan `INTREF.CAL` lagre null i temperaturfeltene etter en mislykket temperaturlesing. Videre programvare bør skille mellom modellens tekniske aktiveringsvilkår og dokumentert gyldig kalibrering.

Etter dette trinnet er OSU107s spenningsresultat `V_tcomp_mV`. Voltvisning fås som `V_tcomp_mV / 1000`.

## 5. Fra voltmeter til sensorverdi

Kanalens `meas_id` peker på måledefinisjonen som velger målebane. Kanal-ID, indeks i INI-filen og fysisk multiplekserkanal er forskjellige begreper; forbindelsen må følges gjennom konfigurasjonen.

For den valgte kanalen settes `x = V_tcomp_mV`, og firmware beregner:

```text
y = c0 + c1*x + c2*x² + ... + cn*xⁿ
```

Koeffisientene ligger i stigende potensrekkefølge. `cal.order` er høyeste grad; parseren tillater 0–6. Oppgi eksplisitt alle `order + 1` koeffisienter, og skriv `cal.order` før `cal.cN`. Beregningen bruker Horners metode.

Eksempel på kanaloppføringer for en ren voltvisning, som utdrag av `[channel]`:

```ini
channel.0.unit=V
channel.0.cal.order=1
channel.0.cal.c0=0
channel.0.cal.c1=0.001
```

For mV-visning brukes `c0=0`, `c1=1`. Feltet `unit` er metadata og konverterer ikke tallet i seg selv. Full konfigurasjon trenger også system-, måle-, kanal- og scan-definisjonene.

For en sensor må koeffisientene passe sensorens serienummer, måleområde og inngangsenheten mV. Hvis sertifikatet gir `y = a0 + a1*V + a2*V²` med V i volt, blir mV-koeffisientene:

```text
c0 = a0
c1 = a1 / 1000
c2 = a2 / 1000000
generelt: ci = ai / 1000^i
```

Sertifikatet må også angi riktig funksjonsretning. En formel for spenning som funksjon av fysisk størrelse kan ikke brukes direkte som fysisk størrelse som funksjon av spenning.

Det eksisterende kanalpolynomet har én inngangsvariabel, spenning. En sensor som trenger en egen temperaturkorreksjon med ekstern temperatur, trenger en eksplisitt sensormodell i tillegg. ADC-temperaturkompensasjonen erstatter ikke en slik modell.

`channel_value_or_vcal_from_raw()` faller tilbake til korrigert mV hvis polynomet ikke kan evalueres på grunn av ugyldig orden eller for få koeffisienter. Ny programvare må ikke presentere en slik fallback som en validert sensorverdi med fysisk enhet. Formatering med `fmt.frac_digits` endrer visningen, ikke målenøyaktigheten.

## 6. Regneeksempel

Tallene er syntetiske for å vise regnerekkefølgen, ikke produksjonskoeffisienter.

```text
raw = 858993459
vref_mV = 2500
volt_drift_gain = 1
V_true_mV ≈ 1000

volt_cal_a_mV = 0.2
volt_cal_b = 0.9998
volt_cal_c_per_mv = 0.0000001
V_base_mV ≈ 1000.1

T_ads_C = 35
intref_cal_temp_c = 25
volt_temp_comp_a_mV_per_c = -0.002
volt_temp_comp_b_per_c = -0.000001
V_tcomp_mV ≈ 1000.069999

Sensorpolynom: y = -10 + 0.05*x
y ≈ 40.00349995 sensorenheter
```

En ren voltkanal med `c1=0.001` ville i stedet gitt omtrent `1.000069999 V` fra samme korrigerte spenning.

## 7. Kalibreringsarbeid og dokumentasjon av nøyaktighet

1. Registrer OSU107-serienummer, PCB-profil, firmwareversjon, sensoridentitet, område og alle konfigurasjonsfiler.
2. Stabiliser instrumentet ved en referansetemperatur. Etabler nullpunkt, intern referansebaseline og en vellykket temperaturbaseline.
3. Kalibrer spenningsbanen mot kjente eksterne spenningspunkter over arbeidsområdet. Tilpass `a`, `b` og eventuelt `c`; behold så lav grad som måledata forsvarer.
4. Hold eksterne spenningsstandarder stabile og varier temperaturen til OSU107. Logg ADC-temperatur og spenningsfeil ved flere spenningsnivåer og temperaturer. Tilpass temperaturkoeffisientene til nødvendig korreksjon etter global kalibrering.
5. Valider med uavhengige målepunkter og både oppvarming og avkjøling. Ikke redefiner baseline under en temperaturserie som skal undersøke drift mot den opprinnelige baseline.
6. Legg inn sensorens kanalpolynom med mV som inngang. Verifiser hele kjeden mot sensorens referansepunkter og aktuelle områder.
7. Dokumenter største absolutte feil, repeterbarhet, temperaturintervall og referanseinstrumentets usikkerhet. Bruk absolutt feil nær null; relativ ppm-feil er ikke definert ved null referanseverdi.

Ved oppdatering av global spenningskalibrering setter dagens konfigurasjonsmanager `volt_temp_comp_enable=false`. Temperaturkompensasjonen må derfor kontrolleres og eventuelt aktiveres på nytt etter at kalibreringen er oppdatert og verifisert.

Anbefalte sporingsfelt er tidsstempel, kanal/målebane, råkode, referansespenning, driftfaktor, `V_true_mV`, `V_base_mV`, `T_ads_C`, temperaturens alder/status, `V_tcomp_mV`, kanalresultat, enhet og kalibreringsidentitet. Dette er et forslag til diagnostikk; ikke alle feltene er nødvendigvis med i dagens vanlige logglinjer.

## 8. Instruks til AI-utvikleren

Bruk eksisterende fellesfunksjoner for matematikken. Hold maskinvarelesing, instrumentkalibrering, sensormodell og presentasjon adskilt. Bevar rekkefølgen og enhetene fra dette dokumentet, og bruk `double` frem til endelig formatering.

Ikke legg inn koeffisienter fra et annet serienummer som universelle konstanter. Ikke korriger samme feil både globalt og i sensormodellen uten en dokumentert kalibreringsprosedyre. Hvis inngangsformat, sensortype, måleområde eller koeffisientenes enheter er ukjent, må det avklares før sensorresultatet kan godkjennes.

Ved implementasjonsendringer skal relevante tester minst dekke:

- Identitetskalibrering og positive, negative og null råkoder.
- Andregradsleddet og riktig nevner `2^31`.
- Null temperaturkorreksjon ved `T=T0`, og riktig fortegn over/under `T0`.
- Avslått kompensasjon, manglende temperatur og gammel cache etter lesefeil.
- mV-til-V-konvertering og sensorpolynom av flere grader.
- At instrumentlogger, surface-logger og aktuelle servicekommandoer gir samme matematiske resultat for samme input og konfigurasjon.
- Feilstatus ved manglende kalibrering og ugyldige koeffisienter, slik at fallback ikke forveksles med godkjent sensorresultat.

Programvaretester bekrefter beregningene. Nøyaktigheten til fysisk instrument og sensor krever i tillegg måleverifikasjon.

## 9. Kildekart i prosjektet

Alle lenker er relative til dette dokumentet. Kontroller oppdatert kildekode hvis prosjektet har endret seg siden angitt commit.

| Kilde | Hva den beskriver |
|---|---|
| [ads1263_channel_math.hpp](../osu107/src/hardware/ads1263/ads1263_channel_math.hpp) | Råkode, global kalibrering og kanalpolynom |
| [ads1263_temp_comp.hpp](../osu107/src/hardware/ads1263/ads1263_temp_comp.hpp) | Temperaturkonvertering og kompensasjonsvilkår/formler |
| [ads1263_regs.hpp](../osu107/src/hardware/ads1263/ads1263_regs.hpp) | Temperaturkonstanter |
| [ads1263_service.cpp](../osu107/src/hardware/ads1263/ads1263_service.cpp) | Fysisk temperaturlesing og registerhåndtering |
| [ads1263_runtime_sampling.hpp](../osu107/src/hardware/ads1263/ads1263_runtime_sampling.hpp) | Samplingplan og forkastede prøver |
| [multi_ini_models.hpp](../osu107/src/config/multi_ini_models.hpp) | Kalibreringsfelt, standardverdier og kanalmodell |
| [multi_ini_config_manager.cpp](../osu107/src/config/multi_ini_config_manager.cpp) | Parsing, lagring og endring av kalibrering |
| [ads1263_submenu.cpp](../osu107/src/menu/submenus/ads1263/ads1263_submenu.cpp) | INTREF.CAL, INTREF.ADJ og serviceberegninger |
| [sd204_8_instrument.cpp](../osu107/src/instruments/sd204_8/sd204_8_instrument.cpp) | Temperaturcache og omregning ved instrumentlogging |
| [system_surface_service.cpp](../osu107/src/hardware/system_surface/system_surface_service.cpp) | Temperaturcache og omregning ved surface-logging |
| [HARDWARE_VARIANTS.md](../osu107/HARDWARE_VARIANTS.md) | PCB-profiler |
| [OSUM_MULTI_INI_APP_SPEC.md](../osu107/OSUM_MULTI_INI_APP_SPEC.md) | INI-struktur og eksempelkonfigurasjon |

Eldre strategidokumenter og kommentarer kan beskrive tidligere versjoner. Den kontrollerte beregningskoden er grunnlaget for formlene her.
