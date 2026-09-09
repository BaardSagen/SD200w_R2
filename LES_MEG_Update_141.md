# SAIV IT 1.4.1 - oppdateringer fra saiv.no

Ny leveranse: SAIV_Instrument_Terminal_v1.4.1_Sept2026.exe paa branch update. Kunden trenger bare EXE-en. Tidligere leveranser er bevart.

## Bruk

Ved oppstart vises et sporsmaal foer nettkontakt. Check now henter versjonsinformasjon og README fra https://saiv.no/software/latest.json. Later lukker uten sjekk. Haken Do not check for updates at startup lagres i HKCU/Software/MHP/SdInstr/SoftwareUpdate, DisableStartupCheck. Help > Update software gir manuell sjekk og tilgang til samme hake.

Vinduet viser installert versjon, serverversjon og README i et rullbart tekstfelt. Versjoner sammenlignes numerisk. Like eller eldre serverversjoner tilbys ikke som oppdatering. Manglende README vises som en melding og blokkerer ikke installasjon av en tilgjengelig oppdatering.

Install update krever bekreftelse. ZIP lastes ned og SHA256 verifiseres foer programmet lukkes. Brukeren bes om aa lagre arbeid og avslutte instrumentoperasjoner. Den innebygde hjelperen kontrollerer pakken igjen, trekker bare ut den forventede EXE-en, kontrollerer ZIP CRC og programversjon, og klargjor filen i samme mappe som kundens EXE. Programmet faar normal WM_CLOSE, og eventuelle lagringsdialoger maa avsluttes. Etter at runtime og launcher har avsluttet, byttes EXE-en med ReplaceFileW. Filnavn og plassering beholdes, slik at snarveier fortsetter aa virke. Gammel EXE beholdes som .previous-<nummer>.bak. Programmet startes igjen.

Administratorrettigheter brukes ikke i en mappe kunden kan skrive til. Hvis klargjoring ved EXE-en gir Access denied, tilbyr Windows UAC via runas. Ved avvist UAC fortsetter gammel utgave. Etter hevet installasjon forsokes omstart med opprinnelig brukertoken; hvis Windows nekter dette, vises beskjed om aa starte programmet selv. Administratorgrenen er implementert, men ikke fysisk provd i en beskyttet kundemappe her.

Versjon 1.4.0 og eldre har ingen oppdateringssjekk. Kunden maa ta i bruk 1.4.1 manuelt EN gang; senere oppdateringer kan installeres fra programmet.

## Kommunikasjon og begrensninger

Windows WinINet med brukerens proxyinnstillinger og vanlig HTTPS-sertifikatkontroll. Ingen nettforesporsler foer Check now; ingen automatisk installasjon. Versjonsfil, README og ZIP maa ligge under https://saiv.no/software/. Redirects folges ikke. Responsstorrelser og ventetider er begrenset. Installasjonen krever SHA256 i manifestet. Nedlastede pakker ligger i den lokale versjonscachen; kundedata og innstillinger flyttes ikke.

En intern lesefeil, feil hash, feil ZIP/programversjon eller annen EXE paa maalstien avbryter oppdateringen. Oppdateringen venter maksimalt 120 sekunder paa normal programavslutning og tvangsavslutter ikke kundens program. Kortvarige dele-/fillaasfeil proeves paa nytt i inntil fem sekunder, bare mens original, kandidat og backupstatus fortsatt er uendret. Filbytte har sikkerhetskopi og forsoker aa legge den tilbake hvis et mislykket bytte har fjernet maalfilen. Andre aapne programkopier kan hindre filbyttet; feilen rapporteres.

## Tester og bygg

29 JSON/versjon/URL-kontroller, 932 eksisterende innstillingskontroller og 20 native/ASLR-kontroller. Faktisk enkelt-EXE er GUI-testet med oppstartssporsmaal, Help-meny, README fra server, lagret hake, omstart og reaktivering. Separat installasjonstest bekrefter at feil hash lar gammel EXE og prosess staa, korrekt pakke erstatter samme sti, backup er byteidentisk og omstart er uten heving.

En isolert testklient satt til 1.3.9 bruker samme oppdateringskode mot faktisk servertilbud 1.4.0. Testen dekker nyere-versjon-vindu, Nei/Ja, full nedlasting og installasjon, egendefinert filnavn Field station.exe, backup og omstart. Kundens arbeids-EXE er ikke erstattet av testene. Se analysis/runtime_test/update141/*.json. Ingen nye instrumentkommandoer er sendt i denne oppgaven.

Bygg: analysis/build_single_exe_141.py. Sluttkontroll: analysis/validate_release141.py. UI/protokoll: sit_import/update_*. Helper og launcher: sit_update/install.cpp og launcher141.cpp. miniz 3.0.2 er statisk innebygd, med opphav og lisens i sit_update/miniz; lisensen folger ogsaa begge EXE-ressurser og distribusjons-ZIP. 1.4.0-kilden er bevart i analysis/reference/sit_import_v140, og historisk bygg peker dit. Ingen GitHub-push.
