# SIT 1.4.7 - valg av beregningsmetoder

Leveranse: **SAIV_Instrument_Terminal_v1.4.7_Sept2026.exe**. Kunden trenger bare denne EXE-filen. Tidligere utgaver er bevart.

Convert har egne Next-sider for m?leparametrene, metodevalg for avledede sj?vannsegenskaper og en avsluttende gjennomgang av st?tteverdier, temperaturskala og posisjon. Quick guide ?pner relevant emne direkte, og valgene beholdes n?r guiden lukkes.

- Salinitet: opprinnelig SIT PSS-78, GSW PSS-78 med modifisert Hill under SP=2, samt separat SA/CT. Kunden kan velge at beregnet S fra C skal brukes videre selv n?r filen ogs? inneholder S.
- Temperatur: Celsius/Fahrenheit og eksplisitt ITS-90/IPTS-68 for beregningene. Standardvalget beholder den historiske SIT-konvensjonen. Steinhart-Hart/Kelvin forklares; mottatt temperatur kalibreres ikke p? nytt.
- Dybde: trykk beholdes, SIT Fixed position/EOS-80, UNESCO, SIT-lignende endepunktsintegrasjon, GSW referansehav eller TEOS-10 profilintegrasjon. Profilene har eksplisitt fremover/bakover-retning og m? v?re ?n sammenhengende profil.
- Tetthet: EOS-80 in-situ-anomali, Sigma T ved null sj?trykk, eldre SD200W-formel eller TEOS-10 eksakt tetthet og sigma0.
- Lydhastighet: SIT, TEOS-10 eksakt Gibbs, Mackenzie, Del Grosso eller NPL/Leroy.
- Oksygen: SIT med atmosf?retrykk eller GSW Garcia-Gordon ved ?n standardatmosf?re, og mg/L, mL/L, mikromol/L eller mikromol/kg. OX og OxR velges separat.
- PAR beholder eksplisitt arealenhet; OF og OT beholdes med sine m?le-/enhetsforklaringer. Ingen vilk?rlig FTU/NTU/FNU-omregningsfaktor.

Metode, temperaturskala, salinitetskilde, posisjon/sammensetningsantakelse og referansetrykk skrives i eksporten. Originalkolonner beholdes som standard. GSWs atlasvalg krever oppgitt posisjon; alternativet bruker eksplisitt referansesammensetning SA=SR. Valgte metoder huskes per instrument-/kolonneoppsett, med lesing av tidligere lagringsformat. St?tteverdier og GPS gjennomg?s p? nytt.

Convert st?tter n? ogs? eldre CTD/STD-tekst med Date/Time og heltalls Interval. Tidspunktene bygges fra header og radrekkef?lge og merkes som rekonstruerte. Den gamle File > Import-grenen er bevart. FIELDS-eksporten er den fullstendige dokumentasjonen av beregningene; sidefilen SF2 beholder feltene ved Import to SD2. Ny beregnet lydhastighet og valgt S-fra-C tas med i projeksjonen. En eksisterende feil i C/T/P-argumentrekkef?lgen ved projeksjon uten S er rettet.

Help > Quick guide har 31 emner, inkludert enkle forklaringer av PSS-78, EOS-80 og TEOS-10, regneeksempler, sammenligninger, fullstendige rekonstruerte kjerneformler, akustikkfunksjoner, offentlige dokumentasjonslenker og GSW-lisens. Eksemplene oppgir ikke m?lefil eller utplasseringssted. SAIVs anbefaling om CTD fremfor STD st?r nederst i conductivity/salinity-emnet.

## Avgrensninger som guiden forklarer

De gamle Delphi-menyene for Compute, kalibrering og historiske omberegninger bruker fortsatt sine gamle rutiner. Metodevalgene gjelder Convert. SIT-lignende profilberegning f?lger den rekonstruerte normalregelen, ikke alle gamle maske-/offset-/fallback-grener. GSW referansehav bruker ikke automatisk lokal fjordstratifisering. GSW oksygen er en l?selighetsmodell med definert referanse, ikke en trykk-/tidsresponskorreksjon av r? sensorsignal. Kelvin-valgets tidsskille per instrument/firmware er ikke etablert. Fysiske instrumentm?linger og kalibreringsn?yaktighet er ikke sertifisert av programtestene.

## Bygg og kontroll

Bygg: analysis/build_single_exe_147.py med C:\MinGW\bin i PATH. Bygggrunnlaget er bevart 1.4.6-runtime; 1.4.5- og 1.4.6-kildene er arkivert. GSW-C er statisk lenket fra uendrede vendor-filer; lisens og kildehasher f?lger prosjektet. Ingen ekstra kundedll eller nettverksnedlasting er n?dvendig for beregningene.

Tester: analysis/verify_conversion_models147.py, analysis/check_conversion_models147_gui.py og analysis/check_formula_guide147_gui.py. Sluttrapporten samler testresultater og filhasher i analysis/models147_release_validation.json. Ingen instrumentkommandoer, serverpublisering, commit eller push i dette arbeidet.

Atlasreferansen er GSW 3.06.16. Den gamle gsw_SA_from_SP-nettsidens 3.05-eksempel avviker omtrent 0,0000154 g/kg ved SP=34,5487, P=10, lon=188, lat=4. Atlasberegningen er derfor kontrollert mot de tilh?rende 3.06.16-referansevektorene, ikke ved ? kreve identitet med den eldre nettsiden. Eksakt tetthet/lydhastighet, PSS-78, O2sol og z_from_p er ogs? kontrollert mot publiserte eksempelverdier.

SD2-gjen?pning av eksplisitte 1.4.7-modellresultater beholder FIELDS-kolonnene uten automatisk gammel lydhastighetsetikett eller ekstra EOS-80-kolonne. Native grafvalg finner ogs? de nye navngitte lyd-/tetthetsfeltene. Temperaturkonvensjonen tas hensyn til hvis SD2-projeksjonen m? beregne S fra bevart C/T/P.

Sluttkontroll best?tt: 409 numeriske/integrasjonskontroller, alle 31 guideemner med full tekst, Next/konteksthjelp, opprinnelige og moderne resultater, lagrede valg, eldre STD, st?tteverdier/atlas og SD2-import/gjen?pning. Faktiske vinduer er visuelt kontrollert. EXE SHA-256: `1f97b68f7fb7ba5b18cc0ce369fbc202abd7d5b14217245ab0e41bf7ecdc865e`.
