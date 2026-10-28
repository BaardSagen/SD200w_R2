# Prosjektnotater

## Fast regresjonskontroll av knapper og menyer før levering

Etter endringer i knapper, menyer, Tag-verdier eller felles klikkrutiner skal
TIME/DATE, Interval, Convert og Merge alltid testes sammen i den ferdige
leveransens runtime og DLL før EXE og serverpakke godkjennes. Brukeren krevde
dette uttrykkelig 28. oktober 2026 etter at batch-Convert tok over innstillingsknappene.
Tidligere beståtte tester av en eldre versjon erstatter ikke denne kontrollen.

Test begge innstillingsknapper for SD200, OSU107 og SAIV110, også uten godkjent
Detect og etter portbytte. Kontroller at riktig dialog åpnes, at ingen åpner
Convert, og at avbrudd gir kontrollen tilbake. Kontroller Convert-knapp og
File-meny, enkeltfil og flere filer, samt Merge. Testene skal som standard
bruke egne prosesser, privat skrivebord, isolert register og sperret fysisk
serieport; ingen klokke-/intervallskriving til instrument uten avtalt fysisk test.
Registrer resultatene mot hashene til runtime/DLL i den faktiske leveransen.

## Fast pakkeregel for senere oppdateringer

Oppdateringshjelperen sammenligner ZIP-oppføringer med eksakt skrivemåte.
EXE-navnet inne i ZIP-en må være identisk med siste filnavn i manifestets
ZIP-URL, med `.exe` i stedet for `.zip`, også store og små bokstaver.
Eksempel: `saiv_instrument_terminal_v1.4.12_oct2026.zip` må inneholde
`saiv_instrument_terminal_v1.4.12_oct2026.exe` direkte i ZIP-roten.
Ikke bruk den lokale EXE-ens store bokstaver som ZIP-oppføring når URL-en
bruker små bokstaver. Feilen ga «The ZIP does not contain the expected program».

Ved hver serverpakke: utled forventet EXE-navn fra den faktiske manifest-URL-en,
kontroller eksakt ZIP-oppføring, pakk ut med CRC-kontroll og sammenlign EXE-byte
og versjon med leveransen. Test med eksisterende oppdateringshjelper; statisk
kontroll av at ZIP-en inneholder den lokale EXE-ens navn er ikke tilstrekkelig.
Bygg ZIP og SHA-256 på nytt etter pakkeendringer. Last opp ZIP først og den
tilhørende latest.json sist. Dette krever ikke nytt programversjonsnummer.
Se `analysis/check_update1412_package.py` for isolert installasjonsforprøve.

## Nyeste lokale leveranse, 28. oktober 2026

Siste versjon er **1.4.13**, etter brukerens nye uttrykkelige valg for rettelsen
av TIME/DATE og Interval som åpnet Convert i 1.4.12. Den beholder flerfilkonvertering
og automatisk firmwarevalg for 3.1.2 / 3.3.0.
Bruk `SAIV_Instrument_Terminal_v1.4.13_Oct2026.exe` og serverpakken med samme
versjon. Bygg: `analysis/build_single_exe_1413.py`; intern modul SIT_Import155.dll.
Les siste prosjektstatus og `LES_MEG_Controls_1413.md`. Eldre pålegg om å holde
versjon 1.4.12 er erstattet av brukerens senere instruks om denne rettelsen.
Programmet er fortsatt usignert.

## Intern servicemeny skal ikke røpes til kunden

Ctrl+T-menyen på OSU107/SAIV110 er en intern servicemeny. Ikke vis eller beskriv tastekombinasjonen, menyinnholdet eller tilhørende interne kommandosekvenser i kundevendt grensesnitt, terminalutskrift fra automatiske operasjoner, feilmeldinger, brukerguide, versjonsnotater, skjermbilder eller filer som følger kundepakken.

SIT kan bruke servicemenyen internt til identifikasjon, kontroll og firmwareoppdatering. Kommandoekko og svar skal behandles internt uten å havne i kundens terminalhistorikk, heller ikke etter at operasjonen eller dialogen er avsluttet. Feil skal forklares med forståelige meldinger uten rå servicedialog.

Vis fremdrift, ventetid og resultat i et eget vindu med animert indikator. Vanlige statusmeldinger kan også vises i terminalen, men de skal ikke avsløre servicemenyen. Ikke fjern nødvendig protokollkommunikasjon eller verifikasjon for å skjule den.

Tekniske detaljer kan beholdes i intern kildekode, testlogger og agentoverleveringer som ikke distribueres til kunden, og diskuteres med prosjekteieren ved feilsøking. Kontroller kundevendt tekst, feilforløp og pakkens innhold mot denne regelen før leveranse. Endring av denne policyen krever uttrykkelig instruks fra prosjekteieren.

## Godkjenning for filtilgang utenfor arbeidsmappen

Arbeidsmappen for dette prosjektet er `C:\cprojects\delphi\sd200w_r2`, med undermapper.

Før agenten leser filer eller søker/lister filinnhold utenfor denne arbeidsmappen, skal brukeren få beskjed om hvilke filer eller mapper som skal åpnes, hvorfor det er nødvendig, og godkjenne tilgangen uttrykkelig. Det samme gjelder før agenten oppretter, skriver, endrer, flytter eller sletter filer eller mapper utenfor arbeidsmappen.

Unntak: Filtilgang til USB-disker som tilhører OSU107 eller SAIV110, samt SIT- og firmware-servermappene på `https://saiv.no/software/` (inkludert `firmware/osu107_saiv110/`), krever ikke særskilt godkjenning etter denne regelen når tilgangen er relevant for brukerens oppgave. Unntaket gjelder filtilgang; det utvider ikke oppgavens omfang til en ubedt firmwareoppdatering eller serverpublisering.

For øvrige mapper gjelder regelen også indirekte filtilgang gjennom verktøy, skript, programmer og lenker/junctions som peker utenfor arbeidsmappen. Eksempler er eksterne kildekodemapper og skriving til AppData. En generell oppgavebestilling eller automatisk godkjenning fra verktøysystemet erstatter ikke brukerens uttrykkelige godkjenning av slik tilgang. En allerede gitt godkjenning kan brukes innenfor det konkrete omfanget brukeren har godkjent; utvidet tilgang krever ny godkjenning. Hvis VS Code åpnes med en annen arbeidsmappe, må omfanget avklares før tilgang utenfor den mappen.

Ved arbeid med SAIV Instrument Terminal (tidligere MiniSoft SD200W), les først [sd200DOc/PROSJEKTSTATUS.md](sd200DOc/PROSJEKTSTATUS.md). Det beskriver siste leveranse, tidligere endringer, tester og åpne punkter.

Siste lokale leveranse per 10. september 2026 er `SAIV_Instrument_Terminal_v1.4.10_Sept2026.exe`. Les `LES_MEG_Salinity_Guide_1410.md` for salinitetsforklaring i brukerguiden og `LES_MEG_Conversion_Models_147.md` for beregningsvalg. Ikke velg en eldre EXE bare fordi navnet inneholder `final` eller den vises i et gammelt skjermbilde. Kontroller statusnotatet og brukerens nyere instruksjoner.

Formelarbeidet er dokumentert i `sd200DOc/FORMELKARTLEGGING.md` og `sd200DOc/FORMELKONTROLL.md`. Native beregningsrutiner er bevart; Convert har eksplisitte metodevalg fra 1.4.7. Systemvurderingen i 1.4.8 forklarer kvalitet og gjenværende begrensninger.

Behold originalen og tidligere leveranser. Mange byggskript i `analysis` er hashbundne historiske patchtrinn; les inngangsfil og forventet hash før gjenbruk.

Aktivt arbeid gjelder original Delphi. Nyeste lokale leveranse er `SAIV_Instrument_Terminal_v1.4.10_Sept2026.exe`; les `LES_MEG_SAIV_Instrument_Terminal.md`, `LES_MEG_Instrument_Icon.md`, `LES_MEG_Detect_Hint.md`, `LES_MEG_SD200_Valg_G_110.md`, `LES_MEG_Startup_Option.md`, `LES_MEG_Startup_Hint.md`, `LES_MEG_SD200_Valg_G.md`, `LES_MEG_Native_UART_Detect.md` og prosjektstatus for fysisk teststatus. Brukeren har forkastet softwareparitet: sett faktisk UART til 7E1. I-vekking har 50 ms minimum; menykommandoer krever komplett meny og 250 ms mottaksro. COM7-test er uttrykkelig autorisert. ImGui-arbeidet er satt på pause.

ImGui 0.2.0 skal starte direkte i terminal med enkel Autodetect/Download og direkte tegntasting. Brukeren avviste 0.1.0-dashboard/sidepanel. Se siste prosjektstatus og saiv-studio/README.md.

Brukeren kaller SAIV Instrument Terminal «SAIV IT» eller «SIT». Ved importarbeid les også `sd200DOc/KONVERTERING_SAMMENLIGNING.md`: CTD/STD/OF/OT skal behandles som før; nye loggerfelt legges til. `docs/konverteringer_og_eksport.md` er nå rettet med SIT som fasit og inneholder verifisert referansekode. Den gamle avvikende utgaven er arkivert under `analysis/reference`; sammenligningsrapporten gjelder den gamle utgaven.

Import fra 1.2.2 krever `SIT_Import130.dll` i samme mappe som EXE-filen. Les `LES_MEG_Import_122.md`. Kildekode og bygg for importmodulen ligger i `sit_import/` og `analysis/build_logger_import_130.py`; bygggrunnlag er bevart 1.1.3. Loggerdata har eget datavindu og FIELDS-eksport; gamle profil-/standarddybdeeksporter er ikke utvidet til loggergrenen ennå.

1.2.2: feltvalg med originalhake på som standard, C→S, P→Real depth med valgfri GPS-header, eksplisitt PAR-arealenhet og OX/OxR. P er dbar, AP er mbar/hPa. Dybden følger SITs Fixed position/EOS-80-gren. Se siste prosjektstatus før videre endringer.

SIT 1.3.0 har Merge med mappeskanning og 0.0–10.0 sekunders toleranse. Les LES_MEG_Merge_130.md. Testfiler: data/saiv110. Merge-kilde: sit_import/merge.h og merge_ui.inc. 1.2.2-kilden er bevart i analysis/reference/sit_import_v122. Se siste prosjektstatus for avklarte koblingsregler og tester.

SIT 1.3.1: les LES_MEG_Merge_131.md. Krever SIT_Import131.dll. Ryddig semikolonfri merge-header med toleranse/treff overst, valgfri dato/tid fra M1/M2 og Convert-knapp. Bygg med analysis/build_logger_import_131.py. Tidligere 1.3.0-kilde er bevart i analysis/reference/sit_import_v130.

SIT 1.3.2 husker siste bekreftede COM-port. Les LES_MEG_Last_COM_Port_132.md. Bruk fortsatt SIT_Import131.dll. Bygg analysis/build_last_com_port.py fra bevart 1.3.1. GUI-omstart testet med isolert register og fysisk portaapning deaktivert.

SIT 1.3.3 leveres som EN EXE. Les LES_MEG_Single_EXE_133.md. DLL/runtime er innebygd og legges automatisk i LocalAppData/SAIV_IT, gjenbrukes og repareres ved behov. Ingen separat DLL til kunden, ingen admin kreves (testet TokenElevation=0). Bygg analysis/build_single_exe_133.py fra bevart 1.3.2 og SIT_Import131.dll. Ikke fjern de historiske byggavhengighetene.

SIT 1.3.4 husker vellykkede konverteringsvalg per instrumenttype og kolonneoppsett, med dato og Ja/Nei/Avbryt ved gjenkjenning. Les LES_MEG_Convert_Presets_134.md. GPS/manglende T/S/AP etterspoerres paa nytt. En-EXE med innebygd SIT_Import134.dll. Bygg analysis/build_single_exe_134.py. Kildearkiver sit_import_v131 og sit_single_v133 bevarer tidligere bygg.

SIT 1.3.5: Fahrenheit-valg for T gir T_degF, med valgfri original Celsius-kolonne. Alle sensorberegninger bruker fortsatt Celsius/originale CTD-rutiner. PAR-forklaringen viser ut-enhet. Les LES_MEG_Fahrenheit_PAR_135.md. En-EXE med SIT_Import135.dll innebygd; bygg analysis/build_single_exe_135.py. Gammel 1.3.4-kilde bevart i sit_import_v134/sit_single_v134.
