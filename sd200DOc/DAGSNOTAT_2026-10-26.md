# Arbeidsnotat – 26. oktober 2026

## GitHub ved arbeidsstart

Lokal `main` ble sammenlignet direkte med GitHub. Begge pekte på `fa65342`,
«Merge SIT 1.4.11 firmware updater». Sporede filer var uendret. Omtrent 700
usporede lokale filer var hovedsakelig tidligere analyse-, test- og datafiler.
Disse skal ikke legges til ukritisk ved commit.

## Antivirus og signering

Kunder har meldt malwarevarsler fra antivirus. Ingen konkret deteksjonskode
eller antivirusrapport er mottatt, så årsaken er ikke fastslått.

Gjennomgangen av tilgjengelig kode og byggoppsett fant ikke tegn til
tastaturovervåking, passordinnsamling eller opplasting av kundens filer.
Nettverkskoden for oppdateringer henter filer fra SAIVs programvareserver.
USB/COM-enumerering brukes til instrumentidentifikasjon; utklippstavlen brukes
ved brukerens innliming av GPS. En-EXE-løsningen pakker ut og starter egne
komponenter i AppData, og oppdateringshjelperen erstatter programfilen.
Dette og manglende signering er mulige forklaringer på varsler, ikke en
bekreftet diagnose. Original Delphi-kilde er ikke tilgjengelig; undersøkelsen
er derfor ikke en full sikkerhetsrevisjon av hele binærfilen.

Lokale 1.4.10 og 1.4.11 ble kontrollert som usignerte. 1.4.11 matcher det
tidligere godkjente byggmanifestet. Ingen antivirusinnstillinger er endret.

## SIT 1.4.12: flere filer i Convert

Ny leveranse: `SAIV_Instrument_Terminal_v1.4.12_Oct2026.exe`.
SHA-256: `14fb2a3c451b2c620e3e18394a5f59b0b9d438655f1e693188a77f5823f2c896`.

- Convert og File-menyen støtter valg av flere filer med Ctrl/Shift.
- Flere filer gir separate teksteksporter til valgt mappe, med eget vindu
  for animert fremdrift, resultat og avbrudd.
- Beregningsvalg gjenbrukes for samme instrumenttype og kolonneoppsett.
  GPS og manglende T/S/AP avklares for den enkelte fil. Ingen automatisk
  gjenbruk av første fils GPS-posisjon.
- Originaler og eksisterende utfiler beholdes. Nye navn nummereres ved behov.
  En feil i én fil hindrer ikke behandling av de øvrige.
- Enkeltfilflyten beholder resultatvindu, eksport og Import to SD2.
- Beregnings- og firmwarekilder er bevart. Arbeidertrådene overtar Delphis
  x87-kontrollord for samme avrunding som før. Quick guide er oppdatert.

Alle 15 originalfiler i `data/dataFormCoustomer` er kontrollert uendret.
Samlekonverteringen ga byte-identiske eksporter mot individuell konvertering
i bevart SIT 1.4.11. Enkeltfilflyt, eksisterende utfil, ugyldig fil, avbrudd før
første utfil og etter første ferdige utfil samt manglende betingelser ble testet.
Fysisk serieportåpning var sperret i egne GUI-testkopier; registerinnstillinger
ble simulert i minnet. Ingen instrumentkommando eller firmwareoppdatering.

Brukeren har bekreftet at løsningen fungerer. Ingen kunder har tatt i bruk
1.4.12 ennå; den planlagte signerte leveransen beholder derfor **1.4.12**.
Tidligere leveranser og 1.4.11-kilden er bevart.

Se `LES_MEG_Batch_1412.md`, `analysis/batch1412_release_validation.json`,
`analysis/batch1412_static_validation.json` og den bevarte GUI-rapporten.
Kundedata og genererte dataeksporter inngår ikke i denne Git-leveransen.

## Azure Artifact Signing: status ved avslutning

SAIV bruker et eksisterende, aktivt Azure-abonnement. Signeringskontoen
**saivsigning** er opprettet i ressursgruppen **rg-saiv-signing**, region
**North Europe**, prisnivå **Basic**. West Europe avviste opprettelsen med
melding om at regionen ikke tok imot nye kunder; nøyaktig årsak er ukjent.

Vilkårene ble akseptert, og rollen Artifact Signing Identity Verifier ble
tildelt. En **Public Organization**-identitetsforespørsel for **SAIV AS** er
sendt inn med registrert organisasjonsnummer. Siste observerte status var
**In Progress**. Personlig ID-kontroll av firmaets representant er påbegynt,
men ikke fullført. Brukeren tar med fysisk førerkort **27. oktober 2026**.
Ingen legitimasjonsbilder, innloggingshemmeligheter eller verifiseringslenker
er lagret i prosjektet. Ingen sertifikatprofil eller signering er ferdig.

Brukeren ønsker å bruke tjenesten til flere SAIV-programmer, gjerne over
2–3 måneder. Når alle leveransene er signert og kontrollert, ønsker brukeren
å avslutte selve signeringskontoen for å unngå løpende kostnad. **Ikke slett
noe nå.** Azure-abonnementet og firmaets identitetsgodkjenning skal beholdes.
Godkjenningen har utløpsdato. Ved senere signering må signeringstjenesten
opprettes igjen og godkjenningens gyldighet kontrolleres.

All signering skal ha gyldig tidsstempel. Avslutning av tjenesten opphever
ikke i seg selv tidligere signaturer. Signering er ikke en garanti mot alle
antivirus- eller SmartScreen-varsler.

## Neste arbeidsøkt

1. Fullfør personlig ID-kontroll via forespørselen i Azure-portalen.
2. Følg eventuell Action Required til identitetsgodkjenningen er Completed.
3. Opprett Public Trust-sertifikatprofil og gi riktig bruker/signer rollen
   Artifact Signing Certificate Profile Signer.
4. Avklar og godkjenn nødvendig ekstern filtilgang før installasjon/oppsett
   av signeringsverktøy. Dagens særskilte godkjenning gjelder C:\MinGW og
   C:\Python311 for bygg/test, med testfiler i prosjektet.
5. Signer innebygde komponenter, bygg én-EXE-pakken og signer slutt-EXE-en
   til sist. Behold usignert, testet original og dokumenter nye kontrollsummer.
6. Lag ny ZIP, kundevendt README og latest.json **etter** signering.
   Oppdateringssystemet viser README og kontrollerer ZIP-ens SHA-256.
7. Test oppgradering fra eldre SIT med README-visning, installasjon,
   sikkerhetskopi og omstart. Serveropplasting utføres bare når avtalt;
   ZIP/README først, latest.json sist.

Ingen signering eller serverpublisering er utført i dag. Brukeren ba ved
avslutning om dette sammendraget samt commit og push til GitHub.

## Referanser for signeringsoppsettet

- [Microsoft: oppsett og identitetsgodkjenning](https://learn.microsoft.com/en-us/azure/artifact-signing/quickstart)
- [Microsoft: roller](https://learn.microsoft.com/en-us/azure/artifact-signing/tutorial-assign-roles)
- [Microsoft: avslutning og fakturering](https://learn.microsoft.com/en-us/azure/artifact-signing/faq)
- [Microsoft: sertifikater og tidsstempel](https://learn.microsoft.com/en-us/azure/artifact-signing/concept-certificate-management)
