# Sammenligning: konverteringer_og_eksport.md mot SAIV IT (SIT)

Dato: 8. september 2026. Brukeren bruker heretter SAIV IT / SIT som kortnavn for SAIV Instrument Terminal. Henvisninger til SD200W i sammenligningen gjelder beregningskoden som fortsatt er bevart i SIT 1.1.3.

## Konklusjon

Dokumentet deler flere funksjoner og begreper med SIT, men beskriver **ikke identiske beregninger eller samme eksportflyt**. Det viser til C++-filer under `shared/core` og `shared/app`; disse kildene ble ikke funnet i denne prosjektmappen. Dokumentets påstander om «dagens program» kan derfor ikke uten videre tilordnes Delphi-programmet SIT. Sammenligningen under bruker formlene slik de står i dokumentet, mot faktisk kjøring av SITs beregningsrutiner i x86-emulator.

Historisk sammenligning: den undersøkte dokumentutgaven er nå bevart i `analysis/reference/konverteringer_og_eksport_before_SIT_20260908.md`. `docs/konverteringer_og_eksport.md` er etter brukerens instruksjon rettet med SIT som fasit. Avvikene nedenfor gjelder utgaven før rettelsen.

## Bekreftede forskjeller

| Område | Dokumentet | SITs eksisterende kode | Vurdering |
|---|---|---|---|
| Salinitet | C/42,914 direkte; C < 0,05 gir null; ingen trykkinndata | Temperaturfunksjon rt og trykkfunksjon Rp før polynomet; C < 0,01 gir null | Ikke samme algoritme; kan gi store forskjeller |
| Oksygen | Beregner ml/L fra T og S; ingen lufttrykkorreksjon | Beregner mg/L fra T, S og lufttrykk, deretter enhetsvalg | Ikke identisk, særlig ved annet lufttrykk |
| Oksygenenheter | ml/L × 1,42903 til mg/L; ml/L × 44,6596 til µmol/L | mg/L × 22,391/31,998 til ml/L; mg/L × 1000/31,998 til µmol/L | Samme typer enheter, ulike eksakte konstanter og beregningsretning |
| Lydhastighet | Mackenzie-polynom i T, S og dybde | Annet polynom i T, S og trykk | Resultatene er ikke identiske |
| Tetthet | Tetthet ved null trykk, T begrenset til −2…40 | Både Sigma T, trykkavhengig tetthet og eldre alternativ | Delvis samme grunnlag; ikke alle grenene samsvarer |
| UNESCO-dybde | Samme hovedpolynom og gravitasjonsledd | Samme kartlagte hoveduttrykk, pluss omkringliggende referanse-/profilbehandling | Hovedformel samsvarer; full kjede ikke bekreftet lik |
| Faste reserveverdier | Faste T/S-verdier med dokumentert prioritet | Andre grener; blant annet hardkodet S=34,5 i en oksygengren uten S/C-kanaler | Ikke samme forrangsregler; eksisterende svakhet er tidligere dokumentert |
| Eksport | Full text, CSV, generisk XML og JSON; Convert and export-vindu | Eksportmenyen har blant annet List, Standard depths, Standard Depth Sectioned, Standard temperatures, Sonar file, Lybin XML og Tide data | Ikke samme brukerflyt; Lybin XML er et spesialformat og ikke bevis på dokumentets generiske XML-støtte |

## Tallkontroll mot SIT 1.1.3

Tabellen sammenligner samme inndata. Oksygenkallet bruker grenen der målt S/C er tilgjengelig, slik at reserveverdien 34,5 ikke overstyrer S=35.

| Beregning og inndata | Dokumentet | SIT |
|---|---:|---:|
| S: C=42,914; T=15; P=0 | 35.00000000 | 34.99999992 |
| S: C=42,914; T=10; P=0 | 35.00000000 | 39.99671809 |
| S: C=30; T=10; P=100 | 23.55343140 | 26.82414973 |
| S: C=0,02; T=20; P=0 | 0.00000000 | 0.01702767 |
| Lydhastighet: T=10; S=35; P/D=0, m/s | 1489.80340000 | 1489.82233602 |
| Oksygen 100 %: T=10; S=35; AP=760 mmHg, mg/L | 9.02935165 | 9.02425975 |
| Oksygen 100 %: T=10; S=35; AP=700 mmHg, mg/L | 9.02935165 | 8.30363061 |

Ved C/42,914 = 1 blir dokumentets ekstra temperaturledd null, slik at det gir 35 også ved 10 °C. SIT korrigerer selve konduktivitetsforholdet for temperaturen og gir omtrent 39,9967. Dette er en avgjørende forskjell, ikke bare avrunding.

Disse prøvene avgjør samsvar med eksisterende program, ikke hvilken fysisk modell som er best for alle bruksområder. De er ikke fullstendige filimport-/eksportprøver. Formelkodeområdet RVA 0x10A000–0x10CFFF er også kontrollert byte-identisk med den tidligere kartlagte NoHandshake-utgaven.

Reprodusering: `python analysis/compare_conversion_document.py`. Rapport: `analysis/conversion_document_comparison.json`. Tidligere grunnlag: `sd200DOc/FORMELKARTLEGGING.md` og `sd200DOc/FORMELKONTROLL.md`.

## Konsekvens for det avtalte importarbeidet

Behold SITs eksisterende håndtering av CTD/STD-modusene, inkludert OF (fluorescens) og OT (turbiditet). Dokumentets formler skal ikke erstatte CTD-beregningene som del av utvidelsen for loggerfiler.

Brukerens avklaringer er nå:

- CTD-modus kommer først, f.eks. `CTDOF Par OxR Ser No 1240 AP1006.175`. CTDOF behandles som før; Par/OxR er ekstra felt.
- Støtt både semikolonkolonner med FIELDS og Full-filer med prefiks direkte foran verdien, f.eks. Par, OxR, OF og OT. Felt må identifiseres uten å forskyve CTD-kanalene.
- Oksygen presenteres normalt som 0–200 % metning. Vanlig import skal ikke spørre om volt eller instrumentspesifikk kalibrering. Tilby å beholde % eller konvertere ekstra oksygenfelt til mg/L, mL/L eller begge.
- PAR beholdes normalt uendret, med oppgitt vanlig verdiområde 1–5000. Området alene fastsetter ikke enhetsbetegnelsen.
- Vis tilleggsfeltene og konverteringsvalgene før oppstart. Nødvendige T/S-data for oksygen skal komme fra filen eller tydelig angitte brukerverdier; Surface-eksemplet mangler CTD.
- Ikke gjør manglende målinger om til null, og ikke påfør sensorkalibrering på allerede presenterte metningsverdier.

Dokumentets påpekninger om tomme felt, opprinnelse til beregnede verdier, eksport av enheter, doble pressure_dbar-felt og gjenbruk av tidligere beregnet oksygen er nyttige kontrollpunkter. De er ikke alle bekreftede feil i SIT. Nye eksportmuligheter kan vurderes separat; ingen programendring er gjort i denne dokumentkontrollen.
