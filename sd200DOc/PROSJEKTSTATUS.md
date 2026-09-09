# Prosjektoverlevering — SAIV Instrument Terminal (tidligere MiniSoft SD200W)

Oppdatert: 9. september 2026. Arbeidsmappe: `C:\cprojects\delphi`.

## Start her neste gang

1. Les dette notatet og brukerens nye oppgave.
2. Nyeste lokale leveranse er **SAIV_Instrument_Terminal_v1.3.5_Sept2026.exe** som EN fil til kunden. Les [LES_MEG_Fahrenheit_PAR_135.md](../LES_MEG_Fahrenheit_PAR_135.md). Innebygd runtime bygger pa bevart 1.3.2, og SIT_Import135.dll er innebygd.
3. Les relevante dokumenter og byggskript i `analysis` før patching. Mange skript krever en bestemt eldre kildefil og SHA-256; de kan ikke ukritisk kjøres på siste utgave.
4. Lag en ny programkopi og behold tidligere leveranser. Verifiser relevante endringer og lever den konkrete EXE-filen.

Vi har ikke original Delphi-kildekode. Arbeidet består av analyse og patching av en 32-bits Delphi Windows-EXE: maskinkode, PE-ressurser og DFM-skjemaer. Dokumentasjonen om instrumentfirmware er en separat kilde og må ikke forveksles med Windows-koden.

## Import all fields - PAUSED

Import all fields er satt på pause etter brukerens beskjed. Omfanget er bare Convert-resultater, ikke Merge. Leveransen frem til 1.3.5 er sikret på main i commit d219703. Denne grenen bevarer den uferdige prøven separat; ingen ny importfunksjon er levert.

## Siste lokale leveranse: 1.3.5 - Fahrenheit og PAR-enhet

T-siden tilbyr Fahrenheit som egen T_degF-kolonne. Haken for original T styrer om Celsius ogsaa beholdes. Standard fortsatt Celsius. Fahrenheit beregnes etter sensorberegningene; disse bruker fortsatt Celsius. PAR-forklaringen viser output-enheten micromol photons/(m2*s), med riktige tegn i GUI. Inngangsarealenhet maa fortsatt velges ved PAR-konvertering.

Valget huskes: nytt preset-format SIT choices 2 leser ogsaa choices 1 fra 1.3.4 (Fahrenheit av). Register/signatur uendret. 35 Fahrenheit-/kompatibilitetstester, 263 preset-tester og 2054 GUI-verdikontroller bestod. Omstart/gjenbruk, Celsius beholdt/utelatt, grafetikett og PAR-tekst er kontrollert. Skjermbilder og rapport under analysis/runtime_test/fahrenheit135. CTD-formelbytes 0x10A000-0x10CFFF er identiske med bevart 1.1.3. Brukeren spurte spesielt om samsvar med gamle SD200W-formler; salinitet/lydhastighet/tetthet bruker fortsatt originalrutinene, Fahrenheit er et nytt tillegg.

En-EXE og automatisk AppData-oppsett viderefores. Bygg analysis/build_single_exe_135.py, DLL SIT_Import135.dll. Kildearkiver sit_import_v134 og sit_single_v134, eldre bygg peker dit. Les LES_MEG_Fahrenheit_PAR_135.md. Tidligere leveranser beholdt. Ingen ny fysisk instrumenttest eller GitHub-push.

## Tidligere lokale leveranse: 1.3.4 - gjenbruk av konverteringsvalg

Etter vellykket Convert lagres kolonnevalg per instrumentfamilie og eksakt kolonneliste/rekkefolge, med PAR-enhetsmetadata. Filnavn, serienummer, dato og maaleverdier ignoreres. Neste passende fil gir Ja/Nei/Avbryt med dato og forrige filnavn. Ja gjenbruker konverteringer/behold-valg, Nei gir vanlig Next-veiviser. Kun vellykket beregning oppdaterer historikken. Skadet historikk gir vanlig veiviser.

GPS og manuelt oppgitte manglende T/S/AP overfores ikke automatisk til en ny fil: GPS-side og bare manglende betingelser vises ved behov. Dette var den oppgitte standardantakelsen mens valgfritt sporsmaal til brukeren stod ubesvart. Lufttrykk fra den nye filen brukes. Lagring: HKCU/Software/MHP/SdInstr/ConvertPresetsV1, uavhengig av versjonscachen. Gjelder ny logger/FIELDS/Full-veiviser; native APB5-gren uendret.

259 lagrings-/signaturtester, GUI-omstart/gjenbruk, ulike oppsett, ny GPS, manglende betingelser, Ja/Nei/Cancel, beregningsfeil og korrupt historikk bestod. 4108 Merge-verdier og GUI-regresjon bestod. Visuelt kontrollert reuse_prompt.png under analysis/runtime_test/presets134. Tester bruker isolert historikk og ikke-elevaterte oppstarter/runtime. Ingen ny fysisk instrumenttest eller GitHub-push.

Bygg analysis/build_single_exe_134.py. Kilde sit_import/presets.h og presets_ui.inc med integrasjon i wizard.inc/sit_import.cpp. conversions.inc uendret. En-EXE, siste COM-port og automatisk AppData-reparasjon viderefores. Kildearkiver sit_import_v131 og sit_single_v133 er opprettet, gamle bygg peker dit. Eldre leveranser beholdt. Les LES_MEG_Convert_Presets_134.md.

## Tidligere lokale leveranse: 1.3.3 - en EXE med automatisk oppsett

Kunden trenger bare SAIV_Instrument_Terminal_v1.3.3_Sept2026.exe. Forste start legger innebygde runtime/DLL i brukerens LocalAppData/SAIV_IT/1.3.3_23c455263801. De beholdes og gjenbrukes; manglende/skadede filer gjenopprettes automatisk. Brukeren presiserte at automatisk oppsett ved forste start/manglende DLL er onsket, og at opprydding ikke er nodvendig.

Ingen administratorrettigheter kreves. Explicit asInvoker, og tester bekrefter TokenElevation=0 for begge prosessene, inkludert reparasjon. Institusjoners egne blokkeringsregler kan fortsatt kreve IT-godkjenning; et lokalt mappevalg er ikke lagt til fordi AppData allerede fungerer uten admin. Signering fortsatt utsatt.

Merge-eksport og Convert-veiviser fra faktisk enkeltfil testet. 4108 eksportverdier bestod. Flytting/nytt navn/norske tegn, gjenbruk uten omskriving, manglende og skadet DLL, manglende runtime og samtidige oppstarter bestod. Rapporter analysis/runtime_test/single133/. Bygg analysis/build_single_exe_133.py, kilde sit_single/. Innebygd runtime er 1.3.2 med kun versjonsressurser/sjekksum endret; DLL identisk med 1.3.1 og dens merge-header viser fortsatt modulversjon 1.3.1. Ingen ny fysisk instrumenttest eller GitHub-push. Tidligere leveranser beholdt. Les LES_MEG_Single_EXE_133.md.

## Tidligere lokale leveranse: 1.3.2 - husk siste COM-port

Bekreftet COM-port lagres alltid ved Setup/Detect-OK, og eksisterende oppstartskode leser den ved neste start. Tidligere hoppet lagringen over naar Detect allerede hadde satt porten. Feilen er reprodusert med 1.3.1: aktiv COM7, lagret COM11. 1.3.2 lagrer COM7 og starter med COM7. Manuelt COM11 og ny omstart, samt Cancel uten endring, bestod. 16 x86-tester bestod.

GUI-testen brukte isolert register og deaktivert fysisk portaapning; Detect-tilstand gjenskapt med native portsetter. Ingen ny fysisk instrumenttest. Brukerinnstillinger uendret. Les LES_MEG_Last_COM_Port_132.md. Bygg: analysis/build_last_com_port.py fra hashbundet 1.3.1. Kode: analysis/last_com_port.s. Tester: analysis/test_last_com_port.py og analysis/check_last_com_port_windows.py. UART/G/formler og Convert/Merge uendret. Bruk fortsatt SIT_Import131.dll; merge-header viser modulversjon 1.3.1. Eldre leveranser beholdt, ingen GitHub-push.

## Tidligere lokale leveranse: 1.3.1 - ryddig Merge-header og Convert

9. september: Brukerens headerendringer er implementert. Forste linje viser versjon, toleranse, dato/tid-valg og M1/M2 matches. Resten har masterheader/kildebane og M1/M2-header/kildebane uten ekstra forklaringer. Ingen semikolon over FIELDS; innleste semikolon blir komma. De to syntetiske testkommentarene utelates fra resultatet. Testfilene er fortsatt syntetiske og uendret.

Ny hake ved toleranse: Include date/time from merged files, standard pa. Av fjerner bare tilleggsfilenes DATE/TIME (og aliaser), mens mastertid og Delta_seconds beholdes. Convert erstatter Import pa knappen og Convert TXT/CSV i File/filvelger. Les LES_MEG_Merge_131.md.

9679 tids-/verdikontroller, 4108 GUI-verdikontroller, 16 Merge- og 10 importhooktester bestod. Egen GUI-test bekrefter dato/tid av/pa, uendrede andre celler, headerrekkefolge, rene kildelinjer og nye navn. PrintWindow-bilde visuelt kontrollert: analysis/runtime_test/merge131/merge_printwindow.png. CTD-formelbytes uendret. Gamle leveranser bevart. Bygg: analysis/build_logger_import_131.py. 1.3.0-kilde arkivert i analysis/reference/sit_import_v130. Ingen fysisk instrumenttest eller GitHub-push.

## Tidligere lokale leveranse: 1.3.0 – Merge med mappeskanning

Ny Merge-knapp under Import. Masterfil med radvis DATE/TIME, valgfri toleranse 0.0–10.0 s (default 0), skanning av valgt mappe i bakgrunn og opptil to tilleggsfiler. Valgfri egen bindestrek-kolonne, default av; filen er alltid semikolonseparert. Nærmeste tidspunkt per masterrad, inklusiv grense og mikrosekundpresisjon; ved lik avstand velges tidligste tid, så første originalrad. Tilleggsrader kan gjenbrukes. Alle masterrader beholdes, manglende treff gir tomme tilleggsceller. M1_/M2_-prefiks, originale datoer/tider og signert Delta_seconds gir sporbarhet. Ingen interpolering eller sensoromregning.

12 syntetiske SAIV110-filer er laget først i data/saiv110, basert på brukerens originale SAIV110-format og OSU107-datoer. De dekker før/etter, få/mange, 0.5/5/10/10.1 sekunder og feil dato. Ved toleranse 0/0.5/10 s finnes 4/6/8 filer. Originalfiler er urørt.

Portabel ZIP-pakke er også pakket ut i en annen mappe og kjørt derfra: Merge og medfølgende testfiler virker (6 treffiler ved 0.5 s).

9679 uavhengige tids-/verdikontroller, 4108 verdikontroller av GUI-eksport, Windows-flyttest og 16 Merge-/10 Import-maskinkodetester bestod. Eksisterende import: 1430 verdikontroller bestod. Dialogen ble kontrollert visuelt med PrintWindow (vanlig desktop-skjermdump viste bakgrunn og brukes ikke som dokumentasjon). Gyldig bilde: analysis/runtime_test/merge130/merge_printwindow.png. Rapporter i merge130 og import130. 1.2.2-kilde arkivert under analysis/reference/sit_import_v122; gammelt byggskript peker dit. Bygg ny versjon med analysis/build_logger_import_130.py.

Merge-resultatet har nye dato-/tekstkolonner og åpnes ikke automatisk i den gamle grafimporten. Les LES_MEG_Merge_130.md for formatgrenser og videre arbeid. docs/merge_filer_dato_tid.md gjelder en annen implementasjon med andre koblingsregler og er bevart uendret. Ingen GitHub-push.

## Tidligere lokale leveranse: 1.2.2 – Import-knapp og valgfri lydhastighet

Import-knapp direkte under Download bruker den eksisterende mnuImportASCIIClick-hendelsen. Log/Print/Setup flyttes til Top 120/152/184; ingen kommunikasjonsrutiner endres. T-siden har Calculate sound velocity (m/s), på som standard når CTD-grunnlaget er komplett. OFF hindrer ny beregnet lydhastighetskolonne; innleste originalkolonner har egne behold-valg.

GPS-reservebreddegrad 45,508368287° er arvet fra SIT og er ikke en faktisk posisjon. Brukerens Google Maps-par er et format-eksempel. Ny import etterspør manglende salinitet og bruker ikke skjult 35. Se LES_MEG_Import_122.md. Windows-knapptest med tre filer, lydhastighet på/av, 1430 verdikontroller og 10 hooktester bestod. CTD-formelbytes er identiske. 1.2.1-kilden er bevart under analysis/reference/sit_import_v121; eldre byggskript peker dit. EXE/DLL/ZIP for eldre leveranser beholdes. Ingen GitHub-push.

## Tidligere lokale leveranse: 1.2.1 – reelle feltvalg og enheter

Alle sensorfelt har **Keep original … values**, på som standard. C kan konverteres til S; P kan konverteres til Real depth (meter), med separat originalkolonne og valgfri GPS-posisjon skrevet som egen linje i eksporthodet. Feltets navn og enhet er tydelige: C Conductivity (mS/cm), T Temperature (°C, Celsius), P Pressure (dbar), OF Fluorescence (µg/L), OT Turbidity (FTU), Par Photosynthetically Active Radiation, OX SAIV205 Oxygen (%), OxR RINKO Oxygen (%). AP er mbar/hPa; brukerens eksempel med 600 mbar/6000 m er korrigert til 600 bar/6000 dbar i forklaringen, uten å legge regneeksemplet i UI.

Real depth bruker original SITs Fixed position-ligning med EOS-80-tetthet fra S/T/P og gravitasjon fra breddegrad/trykk. Native rutiner gjenbrukes. GPS bruker ett Google Maps-felt (`60.3936119227684, 5.29588169849683`) med Maps-lenke og Paste-knapp. Koordinatparet lagres på egen linje i filhodet. Tolv parsertester bestod. Separat automatisert Paste-test ble hoppet over fordi Windows nektet privat window station; brukerutklippstavlen er urørt. GPS har desimalgrader og validerte grenser; uten GPS vises og dokumenteres SITs standardbreddegrad 45,508368287°. Seks numeriske native-sammenligninger bestod. Profiling-grenen er ikke implementert i loggergrenen.

PAR kan konverteres til µmol fotoner/(m²·s) etter eksplisitt valg av inngangsenhet: per m² gir ×1, per cm² gir ×10000. Sertifikatet alene bekrefter ikke arealenheten i filen, og brukeren har ennå ikke besvart det særskilt. Derfor brukes ingen skjult faktor. OX og OxR har uavhengige valg for prosent, mg/L, mL/L eller begge. Ekstra betingelsesdialog hoppes over når verdiene er tilgjengelige; bare manglende felt vises.

De 43 OF/OT-verdiparene i APB5 ble importert med original SIT og sammenlignet med OP2: ingen skalering ble funnet, og native kanalnavn angir µg/L og FTU. Download-meldingen er rettet fra «Preforming refresh off disks» til «Performing refresh of disks» i alle tre tekstkopiene. Kommunikasjonskoden er uendret.

Windows-testene gir 1430 verdikontroller, alle originalhaker på som standard, eksplisitt utelatelse av originalkolonner, to PAR-faktorer, begge oksygensensorer, GPS-hode, avvisning av feilinput og Avbryt. 22 parser- og 10 x86-regresjoner bestod. Les `LES_MEG_Import_121.md` og rapportene i `analysis/runtime_test/import121/`. Ny DLL har eget navn; 1.2.0 EXE/DLL/ZIP er beholdt. Kilden til 1.2.0 er arkivert i `analysis/reference/sit_import_v120/`. Fortsatt lokal leveranse, ingen GitHub-push.

## Forrige lokale leveranse: 1.2.0 – Import CSV/TXT

Ny menytekst er **Import CSV/TXT**, etter brukerens siste instruksjon. Både CSV og TXT vises i filfilteret; Burst beholdes. OSU107/FIELDS og Surface importeres i en ny Win32-modul som lastes fra EXE-mappen. Feltvalg kommer før beregning, OxR kan beholdes i prosent eller legges til i mg/L, mL/L eller begge. Par og andre originale verdier beholdes. CTD-resultatene bruker eksisterende SIT-rutiner; ingen formler eller kommunikasjonsrutiner er rettet/endret.

Loggerdata vises i et eget datavindu med tabell, tidskurve og tapfri FIELDS-eksport. Den gamle APB5-grenen er beholdt og kontrollert med 43 rader. Loggerdata er foreløpig ikke koblet til SD2/RF2/OP2-lagring eller hovedvinduets standarddybde-/profileksport. Full-støtten er testet med syntetiske eksempler, ikke med en faktisk Full-fil fra instrument.

Brukeren presiserte at de første 2–3 målingene kan være ute av synk før vanlig intervall; dette skal ikke beskrives som et problem med hele serien. Tidspunktene i filen bevares. OSU-filen blander CR og CRLF, som nå håndteres.

Kontroller: 22 parser-/konverteringstester, 10 x86-gren-/relokeringstester og 483 eksportverdikontroller. Windows-test importerte/eksporterte 79 OSU- og 3 Surface-rader, prøvde Avbryt og original APB5-import. Se `analysis/logger_import_manifest.json`, `analysis/check_logger_*.py` og `analysis/runtime_test/logger_*validation.json`. Tidligere EXE-er og originaldata er beholdt. Ingen GitHub-push.

## Historisk kartlegging før implementeringen: import og konvertering

Brukeren har lagt APB5, OSU107, Surface og gamle test-filer i `data`. APB5 kan importeres; OSU107 og Surface blir ikke gjenkjent. Første formatkartlegging er gjort i [IMPORTKARTLEGGING.md](IMPORTKARTLEGGING.md), med maskinlesbar rapport `analysis/import_format_inventory.json` og leseskript `analysis/map_import_formats.py`.

OSU107-eksemplet har 79 rader med CTD og ekstrasensorer. Surface har tre rader med Par/OxR/Tilt uten CTD. Kolonnenavn og individuelle tidspunkt må bevares. Brukeren har bekreftet Biospherical PAR og RINKO III. Kalibreringsarkene i docs er lest; se [SENSORKALIBRERING_IMPORT.md](SENSORKALIBRERING_IMPORT.md). Brukeren har senere avklart normal inngang som oksygenmetning 0–200 %, PAR beholdes uendret, og CTD-modus/OF/OT håndteres som før. Ingen volt-/kalibreringsspørsmål i normal flyt. Både FIELDS- og Full-format skal støttes. Ingen EXE-importrettelse er laget i denne fasen. Siste leveranse er fortsatt 1.1.3. Originalfiler er urørt.

## Navn og kontroll av konverteringsdokumentet

Brukeren har valgt SAIV IT eller SIT som kortnavn for SAIV Instrument Terminal. Dette gjelder samme program; eldre SD200W-referanser gjelder bevart kode og historiske filer.

`docs/konverteringer_og_eksport.md` er sammenlignet med SIT 1.1.3. Flere funksjonsvalg er like, men salinitet, oksygen, lydhastighet, reserveverdier og eksportflyt er ikke identiske. Syv numeriske sammenligninger er gjort mot EXE-rutiner. Den tidligere dokumentutgavens salinitetsformel gir 35 ved C=42,914 og T=10, mens SIT gir 39,9967. Behold derfor eksisterende CTD-beregninger som avtalt. Se [KONVERTERING_SAMMENLIGNING.md](KONVERTERING_SAMMENLIGNING.md). Ingen EXE er endret i kontrollen.

## Konverteringsdokumentet rettet med SIT som fasit

Brukeren ba om å rette `docs/konverteringer_og_eksport.md` for bruk i et annet program. Dokumentet er omskrevet med SITs salinitet, oksygen, enhetskonstanter, lydhastighet og tetthetsgrener, samt kartlagte dybdeformler og tydelige forbehold om uavklarte kallkjeder. Komplett Python-referansekode er inkludert i Markdown-filen. Det andre programmets eksportformater er skilt fra påstander om eksisterende SIT-eksport. Ingen programkode er endret.

`analysis/check_sit_conversion_document.py` leser koden direkte fra dokumentet: 31 kontroller mot registrerte EXE-resultater bestod. Rapport: `analysis/sit_conversion_document_validation.json`. Tidligere dokument er bevart i `analysis/reference/konverteringer_og_eksport_before_SIT_20260908.md`. Den eldre sammenligningsrapportens `document`-verdier gjelder denne arkiverte utgaven, ikke det korrigerte dokumentet.

## Forrige lokale leveranse: 1.1.3 – SAIV Instrument Terminal

Fil: [SAIV_Instrument_Terminal_v1.1.3_Sept2026.exe](../SAIV_Instrument_Terminal_v1.1.3_Sept2026.exe). SHA-256: `60f8713bfeda9baffdb690e2bc0c2ff2f4e12516ceb1087b35257ec91b110035`.

Programnavnet er endret til SAIV Instrument Terminal i hovedvindu, About, Windows-filbeskrivelse/produktnavn og eksisterende dialogtitler. Bygget oppdaterer navnestrenger, ressursdata, versjon og de tilhørende navnepekerne. Lagrede innstillinger beholder samme registerplassering. Nytt CTD-ikon og kommunikasjonsfunksjoner er videreført.

GUI-kontroll bekreftet hovedtittel, About uten avkutting og uendret disclaimer. Windows-versjonsinformasjon er kontrollert. Se [LES_MEG_SAIV_Instrument_Terminal.md](../LES_MEG_SAIV_Instrument_Terminal.md), `analysis/build_saiv_name.py`, `analysis/saiv_name_manifest.json` og `analysis/runtime_test/credits_saiv_v113_validation.json`. Lokal leveranse; tidligere filer beholdes.

## Forrige lokale leveranse: 1.1.2 – nytt instrumentikon

Fil: [SD200W_SAIV_v1.1.2_InstrumentIcon_Sept2026.exe](../SD200W_SAIV_v1.1.2_InstrumentIcon_Sept2026.exe). SHA-256: `e85cdb6119350e249a17b1eda037640a04ee2c12be210f2cc91a474bbd3cf6b7`.

`icon/ctd_in_Cage.ico` er lagt inn som programikon med alle ni størrelser og som 20 × 20-pikslers bilde på `sbtnInstrument` med egen deaktivert variant. GUI-start, tittellinje, knapp og Windows-ikonuttak er kontrollert. Skjermbilde: `analysis/runtime_test/instrument_icon_v112.png`. Bare ressurser, versjon og nødvendig PE-metadata er endret; kommunikasjonskoden fra 1.1.1 er bevart.

Se [LES_MEG_Instrument_Icon.md](../LES_MEG_Instrument_Icon.md), `analysis/build_instrument_icon.py`, `analysis/instrument_icon_manifest.json` og `analysis/instrument_icon_gui_validation.json`. Lokal leveranse, tidligere EXE-er beholdt.

## Forrige lokale leveranse: 1.1.1 – hjelpetekst i Detect-tittelen

Fil: [SD200W_SAIV_v1.1.1_DetectHint_Sept2026.exe](../SD200W_SAIV_v1.1.1_DetectHint_Sept2026.exe). SHA-256: `53841d3d6e515d9a659a93c49b00bacff651a83092c1d4453a866a755778f4e6`.

Tittelen er «Find communication speed - Double-click green ports to open». Bare dialogressurs og versjonsinformasjon er endret; kommunikasjonskoden fra 1.1.0 er byte-identisk. GUI-kontroll bekreftet teksten og plass: 330 piksler tekst i 504 piksler vindu. Se [LES_MEG_Detect_Hint.md](../LES_MEG_Detect_Hint.md), `analysis/build_detect_title.py` og `analysis/detect_title_gui_validation.json`. Lokal leveranse.

## Forrige lokale leveranse: 1.1.0 – G på valgt SD200-port

Fil: [SD200W_SAIV_v1.1.0_SelectG_Sept2026.exe](../SD200W_SAIV_v1.1.0_SelectG_Sept2026.exe). SHA-256: `4ee2d90fe1dc79dd9ef6f3f95ac2102769f4382712f8e8cfb57eea9db8d5f037`.

G ble tidligere sendt før endelig portbytte og kunne gå til forrige terminalport. Rettelsen henter valgt port og UART-format fra søkeresultatet før frigjøring, åpner riktig port og utsetter G til etter UI-behandlingen med en 1100 ms engangstimer. Nytt søk kansellerer ventende G. Bare identifisert, valgt SD200 får G.

32 x86-tester for valg og 18 regresjonstester for oppstartstekst bestod. Fysisk COM7/dobbeltklikk → COM11/OK → COM7/dobbeltklikk → COM7/OK bestod: én vellykket G på hver endelige COM7-forbindelse og ingen ekstra G på COM11. Se `analysis/select_delayed_physical_summary.json`. Les [LES_MEG_SD200_Valg_G_110.md](../LES_MEG_SD200_Valg_G_110.md) for bygg, tester og begrensninger. Show startup text videreføres. Den tidligere AV-en er fortsatt uavklart. Lokal leveranse, ImGui på pause.

## Åpen feil: krasj ved gjentatt autodetekt (8. september 2026)

Brukeren rapporterte AV 0047F9DE, write 00000028, i 1.0.8 etter COM7 (I, deretter H) → velg OSU107/COM11 → nytt søk for SD200/COM7. Feiladressen er `mov byte ptr [ebx+0x28],1` i ClosePort; EBX kommer fra EAX, altså en null objektpeker. Koden for instrumentbytte er også med i 1.0.9. Årsak og kallsted er ennå ikke fastslått, og feilen er **ikke rettet**.

`analysis/probe_switch_crash.py` kjører egen GUI-prosess, legger en midlertidig registrering av null ClosePort-kall i prosessminnet og forsøker fire valg COM11/COM7/COM11/COM7. Ingen EXE på disk endres. Både 1.0.9 og 1.0.8 fant målportene og fikk dobbeltklikk uten registrert null-kall i disse forsøkene. Rapporter: `analysis/switch_crash_probe_v109.json` og `analysis/switch_crash_probe_v108.json`. Dette er ikke en full reproduksjon av brukerens I/H-forløp, og prøven bekrefter ikke terminalrespons etter hvert valg. Resultatet beviser derfor ikke at feilen er borte. Ingen ny programleveranse er laget for denne feilen.

## Forrige lokale leveranse: 1.0.9 — valgfri oppstartstekst

Fil: [SD200W_SAIV_v1.0.9_StartupOption_Sept2026.exe](../SD200W_SAIV_v1.0.9_StartupOption_Sept2026.exe). SHA-256: `0415e50e1f7f72c03d309ee40c7a86217b7c645151025e943c0176659518eefa`.

Setup → Serial port har «Show startup text» rett under Ref inst. Standard på. OK lagrer valget via samme TRegistryIniFile-objekt som serieporten, i HKCU\Software\MHP\SdInstr\Comm\ShowStartupText (0/1). Cancel beholder tidligere valg. Dette er registerbasert lagring, ikke en ny INI-fil. Uten hake undertrykkes oppstartsteksten. Med hake vises den én gang etter tre sekunder uten mottatte data.

18 x86-tester og GUI-prøver av lagring, omstart begge veier og Cancel bestod. Avsluttende test etterlot valget på. Plassering og oppstart med/uten tekst er visuelt kontrollert. Les [LES_MEG_Startup_Option.md](../LES_MEG_Startup_Option.md). Bygg: `analysis/build_startup_hint_option.py`; kode: `analysis/startup_hint_option.s`; rapporter: `analysis/startup_hint_option_validation.json` og `analysis/startup_hint_option_gui_validation.json`.

Native autodetekt, G etter SD200-valg og formler er beholdt. Alle tidligere leveranser beholdes. ImGui på pause. Lokal leveranse, ikke publisert på GitHub.

## Forrige lokale leveranse: 1.0.8 — hjelp ved stille oppstart

Fil: [SD200W_SAIV_v1.0.8_StartupHint_Sept2026.exe](../SD200W_SAIV_v1.0.8_StartupHint_Sept2026.exe). SHA-256: `450ebde32a2ca79331ed6ee1434a38e0f32bbf946554e209477084cb8a1c0550`.

Etter tre sekunder uten mottatte instrumentdata ved oppstart vises én lokal terminaltekst: «Hold <I> to wake the instrument, or use Detect to find connected units.» Teksten sendes ikke til instrumentet og vises ikke dersom data er mottatt før fristen. Portbytte og lukket hovedvindu undertrykker gammel oppstartshjelp. Den gjentas ikke ved senere stillhet eller vindusaktivering.

Se [LES_MEG_Startup_Hint.md](../LES_MEG_Startup_Hint.md), `analysis/build_startup_wake_hint.py`, `analysis/startup_wake_hint.s` og `analysis/startup_wake_hint_validation.json`. 1.0.7-funksjonen med G etter SD200-valg, native UART/autodetekt og formler er beholdt. ImGui fortsatt på pause. Lokal leveranse, ikke publisert på GitHub.

## Forrige lokale leveranse: 1.0.7 — G etter SD200-valg

Fil: [SD200W_SAIV_v1.0.7_SelectG_Sept2026.exe](../SD200W_SAIV_v1.0.7_SelectG_Sept2026.exe). SHA-256: `3cb193bdad4975c99a784b2cf6a9cf9f54031b52ae74746c72aa2cb81380017f`.

Etter dobbeltklikk eller OK på et funnet SD200 sendes én G på terminalforbindelsen etter portåpning og 1100 ms stabilisering. Ekstra G gjelder ikke OSU107 eller SurfaceLogger. Avbryt, uferdig/ukjent resultat og mislykket åpning sender ikke. Typekontrollen gjøres før FormClose frigir søkeresultatets arbeiderobjekter. SD200-valg åpner terminalporten også dersom den tidligere var lukket.

24 x86-tester bestod, inkludert frigjorte arbeiderobjekter, utelukkelse av loggerne og engangssending. Fysisk dobbeltklikk på COM7 bestod; WriteFile rapporterte én G på gjenåpnet terminalhåndtak. Se [LES_MEG_SD200_Valg_G.md](../LES_MEG_SD200_Valg_G.md), `analysis/sd200_selection_g_validation.json` og `analysis/com7_select_g_validation.json`.

Bygg: `analysis/build_sd200_selection_g.py`; kode: `analysis/sd200_selection_g.s`. Bygger fra 1.0.6. Native autodetekt og formelkode er bevart. Tidligere leveranser er beholdt. Lokal leveranse, ingen GitHub-publisering i denne økten. ImGui fortsatt på pause.

## Forrige lokale leveranse: 1.0.6 NativeUART

Fil: [SD200W_SAIV_v1.0.6_NativeUART_Sept2026.exe](../SD200W_SAIV_v1.0.6_NativeUART_Sept2026.exe). SHA-256: `4b7c492d8fa64b9bf2ffd939ef629d2d82cde7243d766aecb757810e27056b53`.

Bygg og tester er beskrevet i [LES_MEG_Native_UART_Detect.md](../LES_MEG_Native_UART_Detect.md). About/Disclaimer fra 1.0.3 beholdes med oppdatert versjon. Alle tidligere leveranser beholdes. 1.0.5 SoftwareParity skal ikke velges videre. Ingen GitHub-publisering er utført i denne økten.

## Aktivt arbeid: original Delphi og native UART (8. september)

Brukerens siste instruksjoner overstyrer eldre SoftParity-plan: sett 7E1 fysisk i UART, bruk 50 ms mellom vekke-I, og vent på komplett meny og minst 250 ms mottaksro. ImGui-arbeidet er satt på pause. Brukeren har uttrykkelig autorisert fysisk COM7-test og bekreftet at instrumentet kan ligge og måle.

Kandidat: `SD200W_SAIV_v1.0.6_NativeUART_Sept2026.exe`, bygget direkte fra 1.0.3. Ingen softwareparitet. Begge førstemenyer håndteres: «measurement will start in 10 sec.» og «instrument will go passive in 10 sec.». N-målelinjer stoppes med I; deretter komplett førstemeny -> S -> komplett status -> M -> komplett hovedmeny.

Fysisk test avdekket at gammel overgang fra 8N1 til 7E1 lukket/gjenåpnet porten og mistet oppstartsmenyen. Kandidaten setter nå faktisk UART til 7E1 på allerede åpent håndtak. Se `LES_MEG_Native_UART_Detect.md` for oppdatert teststatus. Fysisk COM7-kontroll er bestått: oppvåkning fra passiv, korrekt 9600/e i raden, full hovedmeny og valg med OK. 557 x86-tester består. Se `analysis/com7_native_final_selection.json`. Download og andre fysiske instrumenter er ikke prøvd i denne sluttkontrollen.

Testkopien sperrer alle porter unntatt COM7; Busy på COM11/18 i disse rapportene betyr testsperre. Produktexe har ingen COM7-hardkoding. Windows-sporet viser ca. 62–63 ms mellom I med 50 ms minimum på grunn av timeroppløsning; emulatoren har eksakt 50 ms.

## Historisk status: 1.0.5 og ImGui før siste presisering

Nyeste lokale Delphi-testutgave: [1.0.5 SoftParity](../SD200W_SAIV_v1.0.5_SoftParity_Sept2026.exe). Se [LES_MEG_Software_Parity.md](../LES_MEG_Software_Parity.md). 1.0.4 MenuDetect beholdes som inngangsfil. Etter brukerens presisering bruker 7E1 fysisk 8N1 med software-AND ved RX og beregnet even-paritet ved TX. Menutester (326) og paritetstester (38, alle bytes) består. 1.0.3 beholdes som siste tidligere verifiserte leveranse. Menustyring og paritet er rettet i testutgaven; full fysisk godkjenning av siste bygg gjenstår.

COM7 er standard CTD, COM11 OSU107, COM18 uten instrument. Mottakstester 8. september bekreftet COM7-data ved 9600 **7E1**. 8N1 gir tegn med paritetsbit. Ikke hardkod disse portene i produktet.

Brukerens firmwarekunnskap: I vekker passivt instrument, men starter fra status/start-meny og endrer intervall fra hovedmeny. S går fra første oppstartsmeny til status; M går derfra til hovedmeny, men endrer koeffisienter fra hovedmenyen. R starter fra hovedmeny. Vent på komplett meny og minst 250 ms ro. Oppstartsmenyen kan automatisk starte etter 10 sekunder.

Et nytt aktivt fysisk søk ble avvist av automatisk godkjenningskontroll på grunn av risikoen ved I. Videre mottakstester sendte ingen kommandoer. Gjenta ikke avslått søk via andre verktøy. Fullfør simulerte tester og dokumentasjon; avklar fysisk prøve separat.

Det separate C++/Dear ImGui-programmet ligger i `saiv-studio/`, med egen kildekode, brukerens ikon, offisielle ImGui/GSW-avhengigheter, tester og byggskript. Dette er en første funksjonsutgave, ikke dokumentert full funksjonslikhet med Delphi-programmet. Det laster ikke gammel EXE. Les mappens README og funksjonsoversikt før videre arbeid.

## ImGui-grensesnitt korrigert til terminalflyt (0.2.0)

Brukeren avviste 0.1.0-grensesnittet: programmet skal åpne direkte i terminal, ha enkel Autodetect/Download og sende tegn direkte ved tasting. Dette er rettet i 0.2.0. Sidepanel og målekort-startside er fjernet. Terminaltastatur bruker WM_CHAR; Enter=CR og kontrolltegn beholdes. Oppsett-dialog og øvrige sider er sperret mot instrumenttasting. Download henter hovedmenyen først ved behov. Tidligere portable 0.1.0 og kildearkiv beholdes.

Leveranse: `saiv-studio/dist/SAIVStudio-0.2.0/SAIVStudio.exe`, portable- og kilde-ZIP i `saiv-studio/releases/` med 0.2.0 i navnet. Bygg/CTest og Windows-tastaturtest bestod uten fysisk instrument. Se `saiv-studio/test-results/terminal_input_validation.json`. Ikke gå tilbake til dashboard-/sidepaneloppsettet uten at brukeren ber om det.

## Forrige leveranse (1.0.3)

Fil: [SD200W_SAIV_v1.0.3_Sept2026.exe](../SD200W_SAIV_v1.0.3_Sept2026.exe).

- About: klientmål 448 × 279, mot 640 × 310 i 1.0.2 (bredde −30 %, høyde −10 %). Vindusrammen kommer i tillegg.
- `OSU017 / SurfaceLogger` er lagt til under «for», med OSU017 skrevet slik brukeren ba om.
- Disclaimeren er omtrent 70 % smalere ved hjelp av nye linjeskift. Ordlyd og avsnitt er bevart; vinduet blir høyere slik at hele teksten vises.
- About og Windows-versjon: `1.0.3 Sept.2026`, numerisk `1.0.3.0`.
- SHA-256: `b817a5898aa2780dbfd502f22de28fbda7b1d4b0a1f8a0f50e0f564b56fdc2c9`.
- Bygg: `analysis/build_compact_about.py`; manifest: `analysis/compact_about_manifest.json`.
- GUI-test: `analysis/check_compact_about_windows.py --live`. Begge dialoger åpnet/lukket og skjermbilder visuelt kontrollert. PrintWindow ga periodevis tomt About-panel; sluttkontrollen bruker faktisk skjermopptak av egen testdialog.
- Siste bilder: `analysis/runtime_test/about_v1_0_3.png`, `disclaimer_v1_0_3.png`.
- Tidligere leveranser er beholdt. Formel- og kommunikasjonskode er bevart. Filen er lokal, ikke publisert på GitHub.
- Se [LES_MEG_Compact_About.md](../LES_MEG_Compact_About.md).

## Forrige leveranse (1.0.2)

Fil: [SD200W_SAIV_v1.0.2_Sept2026.exe](../SD200W_SAIV_v1.0.2_Sept2026.exe).

Oppdatert 8. september 2026 etter brukerens nye kreditering og disclaimer:

- Developer-feltet er erstattet av tre krediteringslinjer: konsept/spesifikasjon og videreutvikling/vedlikehold hos SAIV AS, original programutvikling hos Morten Hammersland Programvare.
- Disclaimer-knappen viser brukerens komplette engelske tekst med tre avsnitt.
- About-vinduet er utvidet slik at alle krediteringslinjene er synlige.
- About og Windows-versjon: `1.0.2 Sept.2026`, numerisk `1.0.2.0`.
- SHA-256: `e9f6a7fef0c34537ab32e1d0797d74716e67cd701587de66b3b5a305262424e6`.
- Bygg: `analysis/build_credits_disclaimer.py`; manifest: `analysis/credits_disclaimer_manifest.json`.
- Inngangsfil: 1.0.1 nedenfor. Alle tidligere leveranser er beholdt.
- PE-sjekksum, DFM, strenginnhold og eksisterende relokasjon er kontrollert. I eksisterende instruksjonskode er bare adressen til disclaimer-strengen endret. Formler og kommunikasjonsrutiner er bevart.
- About og Disclaimer er åpnet/lukket i egen GUI-testprosess. Skjermbilder er visuelt kontrollert: `analysis/runtime_test/about_v1_0_2.png` og `disclaimer_v1_0_2.png`. Privat desktop ga svarte bilder; de endelige bildene er fra egen kortvarig test på vanlig desktop.
- Ingen instrumentsøk eller instrumentkommandoer ble bestilt av GUI-testen.
- Se [LES_MEG_Credits_Disclaimer.md](../LES_MEG_Credits_Disclaimer.md) for ordrett tekst.

## Forrige leveranse (1.0.1)

Fil: [SD200W_SAIV_v1.0.1_Sept2026.exe](../SD200W_SAIV_v1.0.1_Sept2026.exe).

- About: `Version: 1.0.1 Sept.2026`.
- Windows FileVersion og ProductVersion: `1.0.1 Sept.2026`.
- Numerisk Windows-versjon: `1.0.1.0`.
- SHA-256: `ebd75cdb4b93ff2e703b518550dfd2bce51490d8f12b6f0cb6f311f0a5f92068`.
- Bygg: `analysis/build_version_1_0_1.py`.
- Manifest: `analysis/version_1_0_1_manifest.json`.
- Kilde for denne leveransen: `SD200W_SAIV_OSU107_NoHandshake.exe`.
- Sist endret bare About-ressursen og versjonsmetadata med nødvendige PE-headerendringer. Ingen instruksjonskode endret i versjonsoppdateringen.
- Windows VersionInfo og PE-sjekksum kontrollert. GUI startet i Instrument-vinduet uten feildialoger.

**Ikke bruk eldre `SelectInstrument`, `final` eller `Instrument` som om de var nyeste fil.** Brukeren viste tidligere skjermbilde av SelectInstrument som fortsatt hadde gammelt copyright-felt. Nyeste versjon har SAIV A/S i dette feltet.

## Brukerens arbeidsmåte og preferanser

- Kommuniser på norsk, enkelt og konkret.
- Brukeren vil ha faktiske endringer og testbare EXE-kopier.
- Tekster i programmets nye feilmeldinger skal være på engelsk. Tidligere norske tekster fikk tegnkodingsproblemer.
- Behold tidligere filer; ingen opprydding/sletting er avtalt.
- Ikke endre formler eller kalibrering bare fordi en analyse har funnet et problem. Den siste formeloppgaven var dokumentasjon og kontroll, ikke retting.
- Hardware på portene og instrumenttilstand kan ha endret seg siden sist. Kontroller dette før nye tester.

## Implementerte funksjoner

### Instrument-vindu og utseende

- Programmet åpner Instrument/terminal automatisk etter at initialisering er ferdig.
- Den første direkte oppstartspatchen krasjet med access violation rundt `0059B007`, read `00000A61`. Den senere utsatte oppstarten fungerer. Ikke gjeninnfør direkte åpning under tidlig initialisering.
- Større terminalhistorikk: tidligere dokumentert økning til 2000/18000 linjer for de to grensene.
- Blå paneler `#508CC6`, lys terminalbakgrunn, opprinnelig svart Fixedsys-terminaltekst.
- Rammer rundt paneler og ikoner; svart skillelinje ved terminalens rullefelt.
- Call og Receive er skjult/frakoblet.
- Detect ligger øverst på plassen til gamle Setup. Setup ligger under Print på plassen til gamle Detect.
- Fra 1.0.2: tre krediteringslinjer erstatter Developer, og disclaimeren omtaler både SAIV AS og Morten Hammersland Programvare etter brukerens tekst.

### Detect

- Søk på flere porter parallelt.
- Baud/paritet prioriteres 9600 None, 9600 Even, 4800 None, 4800 Even før øvrige eldre alternativer.
- OSU107 og SAIV110 gjenkjennes fra banner ved åpning av porten. For disse USB-enhetene er baud/paritet ikke tilsvarende fysisk UART-krav.
- Passiv lytting etter portåpning før vanlige søkekommandoer. Det finnes forsinkelse mellom lukking/åpning for at USB/DTR-hendelsen skal registreres.
- Lysegrønn markering gjelder bare funnet instrumentrad; tidligere feil med full grønn flate og rader som forsvant er behandlet.
- Klikk på rad velger «Use as Instr». De tre gamle valgene Instrument/Aux/None er skjult. OK bekrefter, dobbeltklikk gjør det samme. Valg skal ikke tas i bruk før bekreftelse.

### Download og disk-refresh for loggerne

- Gjenkjenner `Refresh disk Y/N` i en aktiv Download-sekvens.
- Avslutter gammel nedlastingsflyt og sender **én Y uten CR/LF** gjennom eksisterende serierutine.
- Leser instrumentsvaret etter Y, med Windows-meldingsbehandling aktiv i ventetiden (omtrent 5 sekunder).
- Svar som starter med `System disk refresh will start in 3 seconds.` gir meldingen `Preforming refresh off disks` som lukker seg etter 3 sekunder. Den engelske stavemåten er beholdt fra brukerens ønske.
- Svar som starter med `ERR: stop surface-logger and wait for the current sample to finish` gir:
  `Stop logging and wait for the current sample to finish before refreshing the disk. Then click Download again.`
- Ukjent/manglende svar gir: `Disk refresh was not confirmed. Check the terminal response.`
- Et gjentatt Y/N i feilsvaret skal ikke sende enda en Y.
- Programmet stopper ikke logging automatisk og gjenåpner ikke automatisk porten etter USB-refresh.
- Loggernes refresh-prosa filtreres ut av den gamle måleparseren slik at teksten ikke utløser «Error in ref line».
- Eksisterende Log og vanlig instrumentnedlasting må bevares.

### CTS/DSR og COM-port

- Alle fire SetCommState-kall går nå gjennom wrapper som nuller `fOutxCtsFlow`, `fOutxDsrFlow`, `fDsrSensitivity`.
- Masken er `DCB.Flags &= 0xFFFFFFB3`.
- DTR/RTS og øvrige innstillinger beholdes. De må ikke deaktiveres vilkårlig: USB-loggernes oppstartsbanner bruker portåpnings-/DTR-hendelser.
- CTS/DSR kan fortsatt vise «on» i søkeresultatet fordi det er fysisk signalstatus, ikke flytkontrollinnstilling.
- COM7 svarte i en fysisk vekketest ved 9600 8N1 uten CTS/DSR-flytkontroll.
- Brukeren bekreftet at NoHandshake-utgaven fungerte.

## Åpne punkter i kommunikasjon

### Treg OK i Setup

Brukeren rapporterte treghet. Ikke gjenskapt med uendrede innstillinger: dialogen lukket etter omtrent 15 ms i eldre utgave og 31 ms i NoHandshake. Dette måler bare dialoglukking, ikke fullført portbytte/etterbehandling. Det er **ikke levert en dokumentert separat rettelse for denne forsinkelsen**.

### SD200 vekking etter H/Download/Cancel

Brukeren opplevde at porten virket låst. Tidligere tester kunne ikke gjenskape problemet når passiv tilstand var bekreftet. Ikke erklær dette som endelig løst.

- `I` har ulik betydning avhengig av meny/tilstand: gjentatt I etter at menyen er nådd kan åpne intervallinnstilling.
- `H` i meny/remote kan sette instrumentet passivt. H i løpende målestrøm ble ignorert i tidligere test.
- Ikke fortsett å sende vekke-I etter gjenkjent meny.
- Tidligere fysisk test brukte COM7 for SD200, COM11 for SAIV110. Dette er historiske portnumre, ikke en garanti om dagens oppkobling.
- Noen tidligere prøveskript gikk utilsiktet inn i intervallmeny. Les skriptene før gjenbruk; ingen kalibreringsendring var tilsiktet.
- Sist dokumenterte vekketest lot instrumentet være vekket; menyen varsler mulig automatisk målestart etter 10 sekunder. Ikke anta at instrumentet fremdeles er passivt.

## Formelarbeidet

Les:

- [FORMELKARTLEGGING.md](FORMELKARTLEGGING.md): formler, bruksområder, kodeadresser, sikkerhetsnivå i identifikasjon og komplett Python-vedlegg for kjerneformlene.
- [FORMELKONTROLL.md](FORMELKONTROLL.md): svakheter, referansetester og hva som fortsatt ikke er bekreftet.

Analysert formelfil var NoHandshake. Siste 1.0.1-utgave endrer bare versjonsressurser, så formelkoden er bevart.

### Funn

1. **Oksygen:** wrapper `0x0050BC10` tvinger S=34,5 når filens S/C-kanalflagg er null. Numerisk test ved 20 °C, 760 mmHg og 100 % metning: ferskvann 9,0924 mg/l, tvunget 34,5 gir 7,4179 mg/l (18,42 % lavere). Kodeatferden er bekreftet. Det er ikke bekreftet at brukerens aktuelle filer/visninger går gjennom denne grenen.
2. **Ugyldige inndata:** saltholdighetsrutinen returnerer 0 for C<0,01, også negative verdier. Videre beregning kan da produsere tilsynelatende gyldig lydhastighet. Det gjenstår å kontrollere hvilke ugyldighetsmarkører innleseren slipper igjennom.
3. **Lav salinitet:** ordinær PSS-78 uten funnet Hill-korreksjon i undersøkt rutine. Sprang ved C=0,01 mS/cm. Vurder ferskvann/brakkvann særskilt.
4. **Temperaturskala:** seks GSW-referanser stemmer når T68=T90×1,00024. Ikke avklart om instrument-/filtemperaturen allerede har riktig skala; ikke legg inn dobbel korreksjon.

**Ingen av disse formelforholdene er rettet i EXE.**

### Verifisering

- 24 sammenligninger av rekonstruert Python og binær maskinkode bestod for lydhastighet, saltholdighet og tre tetthetsgrener.
- Seks eksterne saltholdighetsreferanser bestod med korrekt temperaturskala.
- Tre rundturer S→C→S bestod.
- Tre oksygenprøver stemte mellom rekonstruksjon og maskinkode.
- Samsvar mellom rekonstruksjon og EXE beviser ikke alene faglig riktighet i opprinnelig kode.
- Alle disse prøvene var emulatorbaserte, uten instrumentkommandoer.
- En innledende feil i argumentrekkefølgen i invers-testen ble korrigert. Det var en testfeil, ikke en programfeil.

Kilde/testfiler: `analysis/recovered_formulas.py`, `analysis/test_recovered_formulas.py`, `analysis/audit_formulas.py`, `analysis/formula_numeric_validation.json`, `analysis/formula_audit_tests.json`.

## Navn og signering

- Fra 1.0.2 krediteres Morten Hammersland Programvare uttrykkelig for original programutvikling, etter brukerens nye instruksjon. Dette erstatter tidligere mål om å fjerne navnet fra About/disclaimer. Historikken om Clean nedenfor beskriver eldre utgaver.
- I Clean-steget ble rester av gammelt sertifikat fjernet, copyright og innebygde e-posttekster endret. Søk i NoHandshake etter gamle navneord i ASCII, UTF-16LE og UTF-16BE ga ingen treff.
- Dette er ikke en garanti for at programmets historiske opprinnelse er umulig å identifisere fra maskinkode. Eldre programkopier og historiske analyseskript inneholder fortsatt gamle navn.
- Signering/SmartScreen er **utsatt av brukeren**. Ikke opprett betalte tjenester eller publiser programmet som del av rutinearbeid.
- Originalen hadde et innebygd sertifikat, men Windows stolte ikke på sertifikatkjeden i tidligere sjekk. Nyeste endrede program er usignert.
- Hosting på egen HTTPS-server fjerner ikke i seg selv SmartScreen-varsel. Ingen serverpublisering eller signeringstjeneste er satt opp.

## Viktige byggfiler og rekkefølge

Seneste kjede:

```text
Refresh → Clean → RefreshReply → RefreshReply_EN → NoHandshake → v1.0.1 Sept.2026
```

| Område | Filer |
|---|---|
| Siste versjonsmetadata | `analysis/build_version_1_0_1.py` |
| CTS/DSR | `analysis/build_no_handshake.py`, `analysis/test_no_handshake.py` |
| Engelske refresh-tekster | `analysis/build_refresh_reply_en.py` |
| Refresh-svar | `analysis/build_refresh_reply.py`, `analysis/refresh_reply.s`, `analysis/test_refresh_reply.py` |
| Loggerprosa og navneopprydding | `analysis/build_logger_clean.py`, `analysis/logger_refresh_clean.s`, `analysis/test_logger_clean.py` |
| Klikk/dobbeltklikk i Detect | `analysis/build_select_instrument.py`, `analysis/select_instrument.s` |
| USB-loggerdeteksjon | `analysis/build_logger_detect.py`, `analysis/logger_detect.s` |
| Utsatt Instrument-oppstart | `analysis/build_deferred_start.py`, `analysis/start_instrument_deferred.s` |
| Utseende | `analysis/build_blue_look.py` og manifestene for hver utgave |
| Full gammel disassemblering | `analysis/original-disassembly.txt` — original, ikke alle nyere patcher |
| Ny målrettet disassemblering | `analysis/disasm_formulas.py` — hardkodet NoHandshake som kilde |

Før nye kodeendringer: les filens forventede hash, inngangsfil og manifest. Mange tidligere skript er historiske trinn, ikke en samlet byggpipeline.

## Teknisk oppslagsdel

PE image base: `0x00400000`. GUI-programmet er 32-bits; 64-bits testverktøy må lese WOW64-PEB korrekt. Bruk RVA ved flyttet innlasting.

- MainForm: global peker ved base+`0x1C8964`.
- Instrument-serieobjekt: MainForm+`0x510`; aux +`0x514`.
- Serieobjekt: openflag +`0x24`, handle +`0x2C`, baud +`0x30`, port +`0x34`, paritet +`0x4C`.
- Portåpning `0x0047E8F8`, lukking `0x0047F9C4` (allerede hooket, bevar), sending `0x0047FFC4`.
- Opprinnelig SetCommState-stub `0x00407B5C`.
- Fire SetCommState-kallsteder `0x0047E6B2`, `0x0047E87A`, `0x0047E8EE`, `0x0047F427` er omdirigert i NoHandshake.
- Setup-handler `0x005A109C`, OK-handler `0x00513C0C`; Setup+`0x45D` instrumentendret, +`0x45E` auxendret.
- Download-knapp MainForm+`0x374` er en native TButton: bruk BM_CLICK på HWND ved test.
- Detect gjenbruker gammel TSpeedButton MainForm+`0x4EC`: parent-koordinatklikk ved test.
- HWND for relevante Delphi-kontroller finnes ved +`0x14C` i tidligere analyser; verifiser klassetype.
- Download/receive-hook ved `0x0059B308`; completed-line-parserkall ved `0x005496AA`.
- Eksisterende meldingspumpe `0x00502078`; `0x00583510` er ikke ProcessMessages.
- About-versionens opprinnelige caption-setter ved RVA `0x1A47C9` er NOP-et for å bevare egen versjonstekst.

## Testmiljø og kjente begrensninger

Python-pakker for Unicorn/Capstone ligger i `analysis/python_packages`. Skriptene legger dette inn i sys.path. `pefile` er også tilgjengelig i brukt Python-miljø.

`analysis/check_startup_windows.py` starter og avslutter sin egen programinstans, normalt på privat Windows-desktop. `--look-only` er en kort oppstartssjekk. `--live-rows` bruker brukerens desktop. `--detect` utfører instrumentsøk. Les testsekvensen før kjøring.

Kjent svakhet i kopierte GUI-harness: `--live-rows` uten `--detect` kan likevel gå inn i detect-kontroll ved sekund 6 og avslutte med `detection_closed_early`. Dette er ikke i seg selv en programfeil. `check_setup_latency.py` har denne arven og måler dialoglukking, ikke nødvendigvis fullført portbehandling.

GUI-/hardwaretester har ofte krevd eskalert verktøytilgang. Avslutt bare testprosessen som eget skript startet, ikke brukerens åpne program. Kjør ikke gamle fysiske wake-skript blindt.

## Mulig neste arbeid — avhengig av brukerens nye oppgave

- Reprodusere oksygenproblemet med en konkret fil uten S/C og brukerens valgte saltholdighet.
- Kartlegge ugyldighetsmarkører fra instrument/fil til avledede verdier.
- Avklare temperaturskala før noen formelkorreksjon.
- Undersøke Setup-forsinkelse ved faktisk endring/bytte av port.
- Eventuelt fortsette gjennomgang av kalibreringsformler, Rinko og profilberegninger.

Ikke anta at noe av dette er bestilt implementert. Bevar siste fungerende program som referanse.

## GitHub og overføring til annen PC

Repository: https://github.com/BaardSagen/SD200w_R2

Første publisering 7. september 2026, commit `cb86897`, inneholdt bare siste EXE, README og to skjermbilder. Brukeren har deretter uttrykkelig bedt om alle LES_MEG-filer, formelkartlegging, prosjektstatus og resten av arbeidet slik at prosjektet kan videreføres på en annen PC. Dette erstatter den tidligere begrensningen av publiseringsinnholdet.

Den utvidede leveransen omfatter alle lokale prosjekt-/referansedokumenter, analyseskript, assemblerkilder, manifester, testresultater, skjermbilder og originale/historiske EXE-filer som byggene avhenger av. Se [OPPSTART_NY_PC.md](../OPPSTART_NY_PC.md) for installasjon, tester og begrensninger, og `analysis/transfer_inventory.json` for fillisten. Python-avhengigheter er versjonsfestet i `requirements-dev.txt`.

Siste leverte program er uendret. Formelproblemer er fortsatt bare dokumentert. Firmwarekildekode som omtales i separate referansedokumenter finnes ikke i denne arbeidsmappen og inngår ikke i overføringen.

Lokal gren `local-project` bevarer tidligere lokal historikk. Ingen tidligere leveranser eller grener er slettet. Bruk konkrete filvalg ved senere publisering; ikke `git add .`, `git clean` eller `push --all`.

Overføringen er kontrollert med rent Python-miljø i en separat eksport av Git-innholdet. Formel- og kommunikasjonstestene bestod, og siste versjonsbygg ga identisk EXE-hash. Se [OVERFORINGSKONTROLL.md](OVERFORINGSKONTROLL.md). Ingen fysisk instrumenttest ble utført.

GitHub-status ved denne leveransen: den komplette overføringen ligger i lokal commit `b17ce46`. Push ble stoppet av automatisk godkjenningskontroll og er fortsatt ikke utført. Den nye 1.0.2-leveransen og tilhørende dokumentasjon er foreløpig lokale filer. Ikke anta at GitHub har disse filene.
