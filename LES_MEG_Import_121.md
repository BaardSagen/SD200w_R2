# SAIV Instrument Terminal 1.2.1 – feltvalg og enheter

Lokal leveranse 8. september 2026. Start `SAIV_Instrument_Terminal_v1.2.1_Sept2026.exe` med **`SIT_Import121.dll` i samme mappe**. Pakk ut hele `SAIV_IT_v1.2.1_portable.zip`. Tidligere 1.2.0 med sin egen DLL er beholdt og fungerer som før.

## Import CSV/TXT

Hvert sensorfelt har **Keep original … values**, på som standard. Ved konvertering kan originalkolonnen beholdes sammen med den nye. Fjernes haken, utelates originalkolonnen fra det nye datasettet/eksporten. Inngangsfilen endres aldri. Det finnes også en Back-knapp.

| Felt | Visning/enhet | Valg |
|---|---|---|
| C | Conductivity, mS/cm | Behold C eller konverter til S med SITs PSS-78-rutine. Egen hake for å beholde C. |
| S | Salinity, PSS-78 | Behold målt salinitet. Praktisk salinitet er dimensjonsløs. |
| T | Temperature, °C (Celsius) | Behold temperatur. |
| P | Pressure, dbar | Behold trykk eller beregn Real depth i meter. Egen hake for P. |
| OF | Fluorescence, µg/L | Allerede SITs fysiske enhet; ingen ekstra skalering. |
| OT | Turbidity, FTU | Allerede SITs fysiske enhet; ingen ekstra FTU-omregning. |
| Par | Photosynthetically Active Radiation | Behold verdien eller velg konvertering til µmol fotoner/(m²·s), med eksplisitt valg av inngangens arealenhet. |
| OxR | RINKO Oxygen, % saturation | Behold %, legg til mg/L, mL/L eller begge. Originalprosenten har egen hake. |
| OX | SAIV205 Oxygen, % saturation | Samme enhetsvalg, uavhengig av OxR. |
| Tilt / andre ekstra felt | Opprinnelig feltverdi | Behold eller utelat via haken. Ingen ukjent enhet eller kalibrering gjettes. |

**P er dbar, ikke mbar. AP i filhodet er lufttrykk i mbar/hPa.** 600 bar = 6000 dbar; 600 mbar = 0,6 bar. Disse størrelsene skal ikke blandes. UI-en viser enhetene uten et meter-regneeksempel.

Hvis OX/OxR-konverteringen allerede har temperatur, salinitet og lufttrykk fra filen, vises ingen ekstra betingelsesdialog. Bare manglende opplysninger etterspørres. Det samme gjelder temperatur/salinitet som trengs for dybde. Verdier brukeren oppgir merkes i eksporthodet og brukes bare der måleverdier mangler.

## Real depth og GPS

Dybden bruker SITs **Fixed position**-ligning `P × 10000 / (ρ × g)`, der P er dbar, ρ er in-situ-tetthet fra S/T/P i kg/m³, og g er SITs gravitasjon med breddegrad og trykk. De opprinnelige maskinkoderutinene for EOS-80-tetthet og gravitasjon kalles direkte. Dette er ikke en ny gjenskaping av SITs separate, tilstandsavhengige Profiling-gren.

Ved **Use GPS position for depth and save it in the header** brukes ett samlet felt med Google Maps-format, for eksempel `60.3936119227684, 5.29588169849683`. Klikk **Google Maps** for å åpne kartet i standard nettleser, kopier koordinatparet og trykk **Paste**. Paste erstatter hele GPS-feltet. Breddegrad står først, deretter lengdegrad; begge er desimalgrader. Nord/øst er positive, sør/vest negative. Breddegrad påvirker gravitasjonen; begge koordinatene lagres som samme koordinatpar på én egen GPS-linje over FIELDS/dataene, for eksempel `# GPS position: 60.3936119227684, 5.29588169849683; ...`. Posisjon skrevet i dette eksportformatet hentes opp igjen ved ny import. Haken for å bruke posisjonen er fortsatt et bevisst brukervalg.

Uten GPS brukes SITs opprinnelige reservebreddegrad **45,508368287°**, som vises i dialogen og merkes som standardverdi i eksporthodet. Ingen posisjon utgis for å være målt når GPS ikke er valgt. Trykk, temperatur og salinitet tas fra hver måling; ingen oppdiktede CTD-kolonner legges til Surface-filer.

## PAR-enhet må velges riktig

1 µEinstein = 1 µmol fotoner. Omregningen til µmol fotoner/(m²·s) er:

- fra µEinstein/(m²·s): **×1**;
- fra µEinstein/(cm²·s): **×10 000**.

Sertifikatets kalibreringsfaktor bruker cm², men det beviser ikke at verdiene i loggerfilen fortsatt er per cm². Loggeren kan allerede ha skalert verdien. Importen velger derfor ikke faktor 10 000 automatisk. Brukeren må velge inngangens arealenhet når PAR-konvertering velges. Valg og faktor skrives i eksporthodet; råverdien kan beholdes ved siden av. Ingen volt-, mørkestrøm- eller immersjonskalibrering gjentas.

Enhetsgrunnlaget støttes av [Biosphericals produktdokumentasjon](https://www.biospherical.com/wp-content/uploads/2025/04/QSR2150_2025.pdf), som angir begge arealvariantene og sammenhengen mellom µEinstein og µmol. Kalibreringen for den aktuelle QCP-sensoren ligger i `docs/Cal QCP 20678 4-14-26__.pdf`. Filenes arealenhet er fortsatt ikke bekreftet særskilt av brukeren.

OxR er merket **RINKO Oxygen** uten modellnummer: tidligere kalibreringsark beskriver III, mens brukerens nyeste formulering nevnte II. Importen bruker allerede beregnet prosent metning og utfører ikke en modellspesifikk spenningskalibrering.

## Download-tekst

Alle tre bevarte tekstkopiene av `Preforming refresh off disks` i denne EXE-en er rettet til **Performing refresh of disks**. Kommunikasjonsforløpet er ikke endret.

## Verifikasjon

- Windows-test med 79 OSU-rader, 3 Surface-rader og 3 syntetiske rader med C/T/P/OF/OT/Par/OX/OxR.
- 1430 kontroller av eksportverdier, inkludert salinitet, reell dybde, GPS-hode, begge PAR-faktorer, begge oksygensensorer og beholdte/utelatte originalkolonner.
- Alle feltbokser kontrollert som på som standard; kjent CTD-data hopper over ekstra betingelsesdialog, Surface spør bare etter manglende verdier.
- Ugyldig breddegrad, lengdegrad og uvalgt PAR-arealenhet avvises; Avbryt virker også etter slike meldinger. Tolv tester kontrollerer Google Maps-format, anførselstegn, mellomrom og ugyldige koordinater.
- Seks numeriske kontroller mot original SIT for dybde og gravitasjon, med/uten GPS, flere trykk og saliniteter.
- Alle 43 OF/OT-verdipar i APB5 kontrollert mot original SITs lagrede OP2: verdiene er ikke reskalert. Native kanaltekster bekrefter µg/L og FTU.
- 22 parser-/rundtur-/feilinputtester og 10 x86-gren-/relokeringstester bestod.
- Rettet download-tekst, Windows-versjon og uendrede 1.2.0-filer kontrollert.

Den særskilte, automatiserte Paste-testen på en isolert Windows-utklippstavle ble hoppet over fordi Windows avviste opprettelse av en privat window station. Brukerens utklippstavle ble ikke endret. GPS-innlesing/eksport og tilstedeværelse av Maps/Paste-kontrollene er testet; nettleseren ble ikke automatisk åpnet under testen.

Rapporter: `analysis/runtime_test/import121/`, `analysis/native_depth_import_validation.json`, `analysis/native_optical_units_validation.json`, `analysis/runtime_test/logger_hook_121_validation.json`.

## Videre arbeid / ny PC

Kildekode: `sit_import/logger.h`, `conversions.inc`, `wizard.inc`, `sit_import.cpp`, `import_hook_121.s`. Bygg med `python analysis/build_logger_import_121.py` fra prosjektroten. Krav: Python/pefile og 32-bits MinGW GCC med GNU as/ld/objcopy. Kjøring krever bare Windows og de to leverte programfilene, ikke Python eller kompilator.

1.2.0-kilden er bevart i `analysis/reference/sit_import_v120/`, og dens byggskript peker nå på den bevarte kilden. Original Delphi-kildekode finnes fortsatt ikke; 1.2.1-byggingen er hashbundet til den bevarte 1.1.3-EXE-en.

Loggerdata har fremdeles eget datavindu og FIELDS-teksteksport. SD2/RF2/OP2-lagring og de gamle standarddybde-/profileksportene er ikke utvidet til loggergrenen. Full-formatet er testet med syntetiske eksempler; det mangler fortsatt en faktisk Full-fil fra instrument. Se også `LES_MEG_Import_CSV_TXT.md` for første implementering. Ingen GitHub-push er utført.

## SHA-256

EXE: `b73a26bc18e982c9561baadea6846d02dd3c36fe3c52d48b3d5a4abca3bdde48`

DLL: `9dddad8bb4805ae4bfce71c1a5a55d62fcf5cccccf24403784c6fe5621135365`
