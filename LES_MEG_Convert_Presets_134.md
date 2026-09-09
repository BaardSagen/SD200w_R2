# SAIV Instrument Terminal 1.3.4 - husk konverteringsvalg

Leveranse 9. september 2026: **SAIV_Instrument_Terminal_v1.3.4_Sept2026.exe**. Kunden trenger bare denne ene filen. Automatisk AppData-oppsett og reparasjon fra 1.3.3 er beholdt, med ny innebygd SIT_Import134.dll. Ingen administratorrettigheter kreves.

## Slik virker det

1. Velg en fil med **Convert**, og jobb gjennom kolonnene med **Next** som tidligere.
2. Naar konverteringen lykkes, huskes valgene sammen med dato/klokkeslett og kildefil.
3. Velger du senere en fil med samme instrumenttype og kolonneoppsett, kommer **SAIV IT - Previous conversion**.
4. **Ja** bruker samme kolonne- og konverteringsvalg. **Nei** starter vanlig Next-veiviser. **Avbryt** stopper konverteringen.

Dialogen viser tidspunktet for siste vellykkede konvertering (lokal PC-tid) og forrige filnavn. Valgene huskes ogsaa etter omstart, separat for hvert gjenkjent oppsett. Gjenbruk som lykkes blir den nye siste konverteringen.

Kolonnenavn og rekkefolge maa stemme. Instrumentfamilie OSU107, SAIV110 og SurfaceLogger holdes atskilt; ukjent familie behandles som FIELDS. Eksplisitte PAR-arealenheter i metadata inngaar ogsaa. Filnavn, mappe, serienummer, maaledato, radantall og maaleverdier inngaar ikke. Nye eller omordnede kolonner gir vanlig veiviser. Ferdig konverterte eksportfiler med nye avledede kolonner regnes derfor ikke automatisk som samme oppsett som originalfilen.

## Hva som huskes

Konvertering C til S, P til dybde, PAR-valg og inngangsenhet, OX/OxR-valg, lydhastighet og behold/utelat originalverdier for hver kolonne lagres. Tidligere GPS-valg huskes som et valg om aa bruke posisjon, men **selve GPS-posisjonen maa oppgis/bekreftes for den nye filen**. En eventuell posisjon fra den nye filens egen header kan vises.

Tidligere manuelt oppgitt temperatur, salinitet og lufttrykk brukes ikke automatisk paa en ny serie. Kun manglende verdier etterspoerres igjen. Lufttrykk som finnes i den nye filen brukes fra denne filen. Naar ingen slike opplysninger mangler, hopper Ja over kolonneveiviseren og aapner de konverterte dataene direkte. Dersom GPS var valgt, vises P-siden for ny posisjon; deretter etterspoerres eventuelle manglende konverteringsbetingelser.

Avbryt, avviste valg og mislykket beregning overskriver ikke siste vellykkede oppsett. Ugyldig/skadet lagringsdata gir vanlig veiviser. Dersom Windows nekter lagring, vises en melding mens selve vellykkede konverteringen beholdes.

Dette gjelder logger-/FIELDS-/Full-filene som bruker den nye kolonneveiviseren. Den eldre native APB5-importgrenen er uendret.

## Lagring og tester

Valgene ligger per Windows-bruker i **HKCU\Software\MHP\SdInstr\ConvertPresetsV1**. Hvert oppsett har en egen verdi. Hele signaturen verifiseres ved lesing, og lagringsformatet har versjon og lengde-/verdikontroller. Dataene ligger utenfor den versjonsdelte programcachen og forsvinner ikke naar EXE-filen flyttes eller programdelene repareres.

- 259 kontroller av gjenkjenning, ulike instrument-/kolonneoppsett, serialisering, avkuttet/ugyldig lagring og nye maalevilkaar bestod.
- Faktisk GUI-test fra en-EXE-leveransen: foerste konvertering, omstart, ny fil med annen dato/lufttrykk, gjenbruk av verdier, Ja/Nei/Avbryt og ny kolonneliste.
- Ny GPS, nye manglende temperatur-/salinitetsverdier, to ulike lagrede oppsett, mislykket beregning uten overskriving og skadet historikk bestod.
- Dialogen er kontrollert visuelt: analysis/runtime_test/presets134/reuse_prompt.png.
- Merge-regresjon og 4108 eksportverdier bestod med den nye EXE-en.
- Testene brukte isolert konverteringshistorikk. Kundens lagrede valg ble ikke endret. Oppstarter og runtime er kontrollert med TokenElevation=0. Ingen ny fysisk instrumenttest eller GitHub-push.

Rapporter: analysis/runtime_test/presets134/gui_validation.json, analysis/convert_presets_validation.json og analysis/runtime_test/single134/.

## Bygg

**python analysis/build_single_exe_134.py** bygger DLL og en-EXE-leveranse fra bevart 1.3.2-runtime. Portlagringsrettelsen er beholdt. De tre DLL-navnehenvisningene i runtime peker paa SIT_Import134.dll. About, Windows-versjon og nye eksportheadere viser 1.3.4.

Ny kilde: sit_import/presets.h og presets_ui.inc, integrert i wizard.inc og sit_import.cpp. Beregningskoden i conversions.inc er uendret. 1.3.1-modulkilden er bevart i analysis/reference/sit_import_v131; oppstarterkilden til 1.3.3 i analysis/reference/sit_single_v133. De eldre byggskriptene peker paa sine arkiver. Tidligere EXE/DLL-filer er beholdt.
