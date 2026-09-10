# Kontroll av mulige formelfeil i SD200W

Dato: 7. september 2026. Analysert: `SD200W_SAIV_OSU107_NoHandshake.exe`.

## Konklusjon

Ingen regnefeil er påvist i saltholdighetsformelen for de kontrollerte referansetilfellene. Det er derimot funnet svakheter i bruk av standardverdier og ugyldige inndata. Den viktigste er en oksygengren som bruker fast saltholdighet 34,5 når filens kanaler mangler saltholdighet/konduktivitet.

Dette er kontroll av beregningsrutiner og utvalgte kallkjeder. Det er ikke dokumentert at brukerens aktuelle målefiler gir feil. Ingen EXE eller kalibrering er endret.

## 1. Oksygen: fast saltholdighet kan gi feil konsentrasjon

**Bekreftet kodeatferd og numerisk gjenskapt. Prioritet: høy når data mangler saltholdighet/konduktivitet.**

Ved `0x0050BC10` undersøkes flagget på `0x005C60FE`. Flagget settes fra kanalbitene `mask & 3` ved `0x0045B4B3`. Når flagget er null, forkastes saltholdighetsargumentet og erstattes med **34,5** før kall til oksygenformelen `0x0050C818`.

Et kall fra måledatabehandlingen ved `0x0050D7EE` bruker denne wrapperen og multipliserer resultatet med oksygenmetningen / 100.

Kontroll ved T=20 °C, lufttrykk=760 mmHg, 100 % metning:

| Saltholdighet som sendes inn | Kanalflagget er satt | Kanalflagget er ikke satt |
|---|---:|---:|
| 0 | 9,092427 mg/l | 7,417910 mg/l |
| 5 | 8,828125 mg/l | 7,417910 mg/l |
| 35 | 7,396060 mg/l | 7,417910 mg/l |

For ferskvannseksemplet blir verdien **18,42 % for lav** dersom denne grenen brukes. Dette er ikke en feil i selve oksygenløselighetsformelen, men en fast antakelse om vannets saltholdighet.

Tetthetswrapperen ved `0x0050BB94` har til sammenligning en gren som henter saltholdighet fra filmetadata. Oksygenwrapperen gjør ikke det samme.

**Gjenstår:** teste en konkret fil uten S/C-kanal gjennom brukergrensesnittet og endre saltholdighetsinnstillingen. Det avgjør hvilke visninger/eksporter som faktisk rammes. En forsvarlig rettelse bør hente korrekt konfigurert saltholdighet og beholde eksplisitt skille mellom målt og antatt verdi.

## 2. Ugyldig konduktivitet kan bli et gyldig utseende resultat

**Bekreftet i rutinen. Prioritet: høy ved manglende eller ugyldige målinger.**

`0x0050A5B8` returnerer 0 for alle C < 0,01. Det omfatter også negative verdier:

```text
C=-999  → S=0
C=-1    → S=0
C=0     → S=0
```

Det skiller ikke mellom null konduktivitet og en ugyldig negativ verdi.

Kallkjeden ved `0x0050AE33–0x0050AE62` sender beregnet saltholdighet rett videre til lydhastighetsformelen, uten lokal gyldighetskontroll mellom kallene. Ved T=20 °C og P=0 gir S=0 lydhastighet **1482,343308 m/s**, også dersom S=0 opprinnelig skyldtes negativ konduktivitet.

**Begrensning:** testene beviser oppførselen dersom en slik verdi når beregningen. Innleseren eller andre tidligere ledd kan filtrere den. Det er ikke bekreftet at -999 brukes som konduktivitetsmarkør i brukerens filer.

Tetthetsrutinen `0x0050C330` aksepterer dessuten negativ S gjennom `sqrt(abs(S³))` og gir et endelig tall. For S=-999, T=20, P=0 gir den tetthetsavvik -423,458553, tilsvarende 576,541447 kg/m³. En endelig tallverdi er derfor ikke i seg selv bevis på gyldige målinger.

**Anbefalt retning:** la ugyldighet følge dataene gjennom beregningene i stedet for å gjøre ugyldige innganger om til null. Kontroller filformatets faktiske markører før endring.

## 3. Lav saltholdighet: algoritmen brukes uten særskilt korreksjon

**Bekreftet begrensning i den undersøkte rutinen.**

Ved T=20, P=0:

```text
C=0,00999 mS/cm → S=0
C=0,01000 mS/cm → S=0,0128275264
```

Det er et sprang ved den hardkodede grensen. Rutinen fortsetter med ordinær PSS-78 ved lave saltholdigheter; det er ikke funnet en Hill-korreksjon i denne kallkjeden.

Den offisielle GSW-dokumentasjonen angir PSS-78 for området 2 < SP < 42 og bruker en tilpasset Hill-formel under 2. Dette gjør lavsalinitetsbruk til et særskilt kontrollpunkt, særlig i ferskvann og svakt brakkvann. Det betyr ikke at alle resultater under 2 automatisk har et stort avvik. [Kilde: gsw_SP_from_C](https://www.teos-10.org/pubs/gsw/html/gsw_SP_from_C.html).

## 4. Temperaturskala må avklares før eventuell rettelse

**Påvist avhengighet, ikke bekreftet feil i hele programmet.**

Seks publiserte GSW-eksempler stemmer med EXE-rutinen når temperaturen konverteres til den eldre skalaen med T68=T90×1,00024. Uten konvertering blir saltholdigheten omtrent 0,00115–0,00289 høyere i disse eksemplene.

Eksempel:

```text
C=34,5487 mS/cm, T90=28,7856 °C, P=10 dbar
Publisert SP:                        20,009869599086951
EXE med T90×1,00024:                 20,009869599086947
EXE med T90 direkte:                 20,012741722649743
```

Den undersøkte konverteringskjeden sender lagret temperatur direkte til rutinen. Det er imidlertid ikke fastslått hvilken temperaturskala de lagrede verdiene representerer, eller om en korreksjon allerede skjer ved innlesning/kalibrering. En ekstra korreksjon må ikke legges inn før dette er avklart.

Referanseeksemplene bruker ITS-90. [Kilde: GSW, inndata og eksempler](https://www.teos-10.org/pubs/gsw/html/gsw_SP_from_C.html).

## Det som bestod kontrollen

- Seks uavhengig publiserte saltholdighetseksempler stemte etter riktig temperaturskalatilpasning, med absolutt forskjell under 10⁻¹⁰.
- Tre tester S → C → S kom tilbake til opprinnelig saltholdighet med absolutt forskjell under 10⁻¹⁰.
- Oksygenets rekonstruerte normalgren stemte med binærkjøring i tre prøver. Dette kontrollerer rekonstruksjonen; det er ikke en uavhengig faglig validering av oksygenmodellen.
- De tidligere 24 sammenligningene av rekonstruerte formler og EXE-kode bestod. Disse alene beviser heller ikke at opprinnelig programkode er faglig feilfri.

En feil argumentrekkefølge i den første inverse testkjøringen ble oppdaget og korrigert før rapportering. Den endelige testen bruker rutinen med stakkargumentene P,S,T. Det var en testfeil, ikke en programfeil.

## Testgrunnlag

- [Resultater fra denne kontrollen](../analysis/formula_audit_tests.json)
- [Testskript](../analysis/audit_formulas.py)
- [Oksygengrenens maskinkode](../analysis/formula_audit_oxygen_branch.txt)
- [Kanalflaggets maskinkode](../analysis/formula_audit_channel_flags.txt)
- [Videreføring til lydhastighet](../analysis/formula_audit_sound_callers.txt)
- [Opprinnelig formeloversikt](FORMELKARTLEGGING.md)

Testene ble kjørt i emulator uten kommunikasjon med instrumentene. Kalibreringskoeffisienter, Rinko, profilinterpolasjon og alle eksporter er ikke ferdig kontrollert for feil.


## Tillegg 10. september 2026: valgbare metoder og kontroller

1.4.7 endrer ikke de gamle maskinkoderutinene. Standardkonverteringen beholder historiske resultater. Convert gir n? eksplisitt temperaturskala, GSWs lavsalinitetsbehandling, TEOS-10-alternativer, navngitte oksygenreferanser og tetthets-/lyd-/dybdemetoder. Metoder og n?dvendige antakelser lagres i eksporten. Dette retter ikke automatisk gamle filer eller firmwarekalibrering.

analysis/verify_conversion_models147.py kontrollerer b?de publiserte GSW-eksempler, de tilh?rende 3.06.16-atlasvektorene, gamle konverteringsresultater, kildeprioritet for S/C, retning/interpolasjon i profiler, enheter, feilgrenser/atomisk feilretur, eldre CTD/STD-parser og migrering av lagrede valg. Data ved 4000 dbar inng?r. analysis/check_conversion_models147_gui.py kontrollerer faktisk EXE/Next/hjelp/eksport/lagrede valg og SD2; analysis/check_formula_guide147_gui.py kontrollerer de 31 guideemnene. Endelig resultat med filhasher: analysis/models147_release_validation.json.

Gammelt Kelvin-valg og profilnormalregel har f?tt ytterligere native-kontroll, se FORMELKARTLEGGING.md. Eksakt instrument-/firmwaretidsskille for Kelvin-konvensjonen, full r? Rinko-/trykksensorkalibrering, maske-/offsetgrener og alle gamle standarddybde-/middelverdieksporter gjenst?r. Tester uten instrument erstatter ikke fysiske referanse-/kalibreringsm?linger.
