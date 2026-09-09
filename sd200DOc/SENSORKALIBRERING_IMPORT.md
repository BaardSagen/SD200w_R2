# Sensorgrunnlag for import: PAR og RINKO III

Brukeren har bekreftet at Par er prefikset for en Biospherical PAR-sensor, og OxR gjelder RINKO III-oksygensensor. Begge kalibreringsark er lest og visuelt kontrollert. Dette dokumentet fastsetter ikke at loggfilens tall er rå volt eller at arkets serienummer er montert i alle eksempelfilene.

## PAR – Biospherical QCP2260, serienummer 20678

Kilde: `docs/Cal QCP 20678 4-14-26__.pdf`, én side. Kalibrert 14. april 2026. Mørkespenning 51,1 mV. Tørr faktor 4,35 V/(µEinstein/(cm²·s)); våt faktor 4,05 i samme enhet. Alternativt oppgir arket 7,22·10⁻¹⁸ og 6,72·10⁻¹⁸ V/(kvanta/(cm²·s)). Immersjonskoeffisient 0,9310.

For **ukorrigert sensorspenning i volt**, med dette sensorarket, kan fotonfluksen uttrykkes i µmol/(m²·s):

`PAR = (V − 0,0511) / kalibreringsfaktor × 10000`

Velg tørr eller våt faktor etter måleforhold. Hvis filen allerede inneholder nettospenning, skal mørkespenning ikke trekkes fra på nytt. Den våte faktoren omfatter immersjon; koeffisienten skal ikke påføres en gang til. µEinstein tilsvarer µmol fotoner, og cm² til m² gir faktor 10000.

Kontroll mot lampetesten: (0,118 − 0,0511)/4,35 × 10000 = 153,793 µmol/(m²·s), som samsvarer med arkets avrundede 153,9. Ingen eksempeldata er omregnet automatisk.

## Oksygen – JFE RINKO III, ARO-CAV-SA-R, serienummer 0380

Kilde: `docs/SN380.pdf`, tre sider. Temperaturkalibrering 28. juni 2019, oksygenkalibrering 1. juli 2019, film 191625BA. Arket har også en håndskrevet installasjonsreferanse til SD204 SN1248 og OSU SN0369; dette er ikke de samme identifikatorene som OSU107-eksempelfilens logger 107 og CTD 1240.

Temperatur: `T[°C] = A + B·V + C·V² + D·V³`, V i volt.

- A = −12,47913
- B = 21,17776
- C = −3,483237
- D = 0,6543883

Alle fem spennings-/temperaturparene på kalibreringsarket er kontrollert mot transkriberte koeffisienter og samsvarer innen 0,001 °C.

Oksygenarket angir `DO[%] = G + H·P′` og følgende koeffisienter: A = −43,92753; B = 142,3079; C = −0,2808449; D = 0,010449; E = 0,004; F = 0,0000562; G = 0; H = 1. Det oppgir at P′ bestemmes av A–F, men **viser ikke hele P′-formelen**. Tallene skal derfor ikke legges inn i et antatt polynom. Oksygenenheten på arket er prosent metning, ikke mg/l.

Produsenten beskriver RINKO III som analog 0–5 V på https://www.jfe-advantech.co.jp/eng/products/ocean-rinko.html . Dette dokumenterer sensortypen, men avgjør ikke om loggeren har regnet om OxR før lagring. RBRs tekniske dokumentasjon beskriver flere versjoner av RINKO-ligningen: https://rbr-global.com/wp-content/uploads/2025/10/RBR-Gen-3-L3-Command-Reference-0005199revN.pdf . Riktig variant og signalbehandling må avklares før bruk.

Programmet har allerede en Rinko-kalibreringsdialog, `TDLGRINKOCAL`, men denne tilbyr luftkalibrering og fabrikktilbakestilling av instrumentet; den er ikke i seg selv dokumentasjon for filimportens omregning. Ingen kalibreringskommandoer er sendt.

## Videre import

Behold Par og OxR som separate sensorfelter og originale verdier. Sensorprofiler skal knyttes til riktig sensors serienummer. Filene har ikke oppgitt PAR-/RINKO-serienummer i FIELDS-hodet. Før omregning må det avklares om loggverdiene (eksempelvis Par 4.26 og OxR 0.29) er rå volt eller allerede kalibrerte, og hvilken temperatur som er tilgjengelig ved eventuell RINKO-kompensasjon. Surface-eksemplet har ingen temperaturkolonne.

Maskinlesbare referanser: `analysis/sensor_calibration_profiles.json`. Kontrollberegninger: `analysis/sensor_calibration_verification.json`. Ingen importrettelse er levert i EXE ennå; siste program er fortsatt 1.1.3.

## Avklart bruk i import 1.2.1

Normal OxR og OX-inngang er prosent oksygenmetning, ifølge brukeren. Ingen volt-/sensorkalibrering utføres i importen. Par kan beholdes eller omregnes fra eksplisitt valgt µEinstein/(m²·s) eller µEinstein/(cm²·s) til µmol fotoner/(m²·s). Faktorene er henholdsvis 1 og 10000. Loggerfilens arealenhet er ennå ikke særskilt bekreftet; den kan ikke utledes bare fra sertifikatets spenningsfølsomhet. Historiske avsnitt ovenfor beskriver kartleggingen før denne avklaringen. Les `../LES_MEG_Import_121.md` for levert oppførsel.
