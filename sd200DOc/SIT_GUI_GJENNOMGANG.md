# SIT – gjennomgang av kjørende program, 9. september 2026

SIT 1.4.3 ble startet på det interaktive Windows-skrivebordet fra en byteidentisk kopi av leveransen. Menyer og dialoger ble faktisk åpnet. Denne rapporten bygger på skjermbilder, vindustilstand og menytre fra den kjørende prosessen, ikke bare prosjektbeskrivelser.

EXE: `SAIV_Instrument_Terminal_v1.4.3_Sept2026.exe`. SHA-256: `b6e8598e55e7f24f9e545ecd9fc980b85fb37a774decf93330d85755f4595232`.

Dette er et undersøkelsesgrunnlag for en tro gjenskaping. Ingen ny Studio-utgave er bygget i denne gjennomgangen.

## Hva den kjørende utgaven viser

- Hovedvinduet har File, View, Display, Util og Help, en kompakt ikonlinje på blå bakgrunn og statuslinje nederst. Terminalen opptar hovedflaten.
- Terminalen har en fast blå knapperekke til høyre: Detect, Download, Convert, Merge, Interval, TIME/DATE, Print, Save text og Setup.
- Vanlige lister, standardtabeller og parvise grafer bruker hovedvinduet. Multigraph er et eget vindu med kanalvalg, skalaer, trykk/tid og visningsvalg.
- Setup har seks faner: Serial port, CU901 files, Modem, e-mail, Options og Calc values.
- Convert bruker en feltvis veiviser. Resultatet åpnes i et separat loggervindu med tabell, tidskurve, Export all fields og Import to SD2.
- Menyinnhold og tilgjengelighet endres med instrument-/datatype. Klassisk SD2 og importerte loggerdata må undersøkes hver for seg.

## Faktisk gjennomført

En kopi av data/test.SD2 med RF2/OP2 ble åpnet, måleutvalget bekreftet og de sju radene vist. Standardtabeller og tilgjengelige tid-/dybdegrafkommandoer ble åpnet. Eksportdialogene og verktøydialogene ble undersøkt. Multigraph ble åpnet med det gamle datasettet.

Merge ble åpnet med data/2026_09_03_20-28-52_C.txt som master og data/saiv110 som søkemappe. Ved 0,0 sekunder viste den faktiske dialogen 79 masterrader, 12 skannede filer og fire treffiler. Ingen merge-utfil ble skrevet.

Convert ble gjennomført med samme 79-raders loggerfil. Alle sju feltsteg (C, T, P, OF, Par, OxR og Tilt) ble åpnet med standardvalg. Resultatvinduet ble undersøkt. Import to SD2 opprettet logger_review.SD2 og følgefiler i gjennomgangens egen datamappe. Den importerte filen ble vist med SITs native Multigraph.

Setup-fanene, hovedmenyene, eksport-/tabell-/grafundermenyene, About, Disclaimer, SMTP notice, manuell oppdateringsdialog og utskriftsdialog ble åpnet. Ingen utskriftsjobb eller oppdateringshenting ble startet.

## Visuelle hovedreferanser

| Tilstand | Bilde |
|---|---|
| Terminal ved oppstart | [Åpne bilde](../analysis/runtime_test/sit_live_review/start_1788985839559484500_0.png) |
| Klassisk SD2-liste | [Åpne bilde](../analysis/runtime_test/sit_live_review/click_1788986054119812400_0.png) |
| Parvis tidskurve | [Åpne bilde](../analysis/runtime_test/sit_live_review/command_1788986062925542900_0.png) |
| Standarddybdetabell (grunn dataserie gir ingen nivåtreff) | [Åpne bilde](../analysis/runtime_test/sit_live_review/command_1788986056602351700_0.png) |
| Klassisk Multigraph | [Åpne bilde](../analysis/runtime_test/sit_live_review/button_1788986172347430000_0.png) |
| Merge med faktisk søkeresultat | [Åpne bilde](../analysis/runtime_test/sit_live_review/click_1788986244630183400_0.png) |
| Loggerdata etter Convert | [Åpne bilde](../analysis/runtime_test/sit_live_review/caption_1788986318435864700_0.png) |
| Multigraph med importerte felt | [Åpne bilde](../analysis/runtime_test/sit_live_review/button_1788986355372504600_0.png) |
| About – direkte skjermbilde | [Åpne bilde](../analysis/runtime_test/sit_live_review/command_1788986602854761800_0_screen.png) |
| Utskriftsdialog | [Åpne bilde](../analysis/runtime_test/sit_live_review/command_1788986575691482000_0_screen.png) |

## Setup og Convert, side for side

| Side | Bilde |
|---|---|
| Setup / Serial port | [Åpne bilde](../analysis/runtime_test/sit_live_review/click_1788985893256122800_0.png) |
| Setup / CU901 files | [Åpne bilde](../analysis/runtime_test/sit_live_review/mouse_1788985942713947900_0.png) |
| Setup / Modem | [Åpne bilde](../analysis/runtime_test/sit_live_review/mouse_1788985944065659000_0.png) |
| Setup / e-mail | [Åpne bilde](../analysis/runtime_test/sit_live_review/mouse_1788985945342420800_0.png) |
| Setup / Options | [Åpne bilde](../analysis/runtime_test/sit_live_review/mouse_1788985946620008500_0.png) |
| Setup / Calc values | [Åpne bilde](../analysis/runtime_test/sit_live_review/mouse_1788985947871916600_0.png) |
| Convert / C | [Åpne bilde](../analysis/runtime_test/sit_live_review/command_1788986267109818400_0.png) |
| Convert / T | [Åpne bilde](../analysis/runtime_test/sit_live_review/click_1788986276301514200_0.png) |
| Convert / P | [Åpne bilde](../analysis/runtime_test/sit_live_review/caption_1788986303657958200_0.png) |
| Convert / OF | [Åpne bilde](../analysis/runtime_test/sit_live_review/caption_1788986305015451100_0.png) |
| Convert / Par | [Åpne bilde](../analysis/runtime_test/sit_live_review/caption_1788986306341798100_0.png) |
| Convert / OxR | [Åpne bilde](../analysis/runtime_test/sit_live_review/caption_1788986307688727100_0.png) |
| Convert / Tilt | [Åpne bilde](../analysis/runtime_test/sit_live_review/caption_1788986309043604200_0.png) |

## Åpnede menykommandoer

Tabellen viser åpningsresponsen. Den er ikke dokumentasjon på at alle beregninger, eksportformater eller lagreoperasjoner er validert. En dialog som krever valg av fil ble undersøkt til filvalget; enkelte verktøy lukker det aktive datasettet og krever ny åpning.

| Menykommando | Faktisk vist | Bevis |
|---|---|---|
| File > Export > List | Export data | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986089741248900_0.png) |
| File > Export > Standard depths | Export data | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986091846853300_0.png) |
| File > Export > Standard Depth Sectioned | Export data | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986093975390300_0.png) |
| File > Export > Standard temperatures | Export data | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986096128520000_0.png) |
| File > Export > Sonar file | Output to | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986098309752200_0.png) |
| File > Export > Lybin file (Bathy data.xml) | Export data to bathy file, Export EM1002/EM3000 data to file | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986100572884100_0.png), [Bilde](../analysis/runtime_test/sit_live_review/command_1788986100572884100_1.png) |
| File > Export > Tide data | Export data to tide file | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986102816864600_0.png) |
| File > Set scaling... | Scaling parameters | [Bilde](../analysis/runtime_test/sit_live_review/command_1788985957706979600_0.png) |
| File > Page setup.. | Page setup | [Bilde](../analysis/runtime_test/sit_live_review/command_1788985959856864500_0.png) |
| View > Tables > Standard Depth | SAIV Instrument Terminal - SCTDOFOTc 204 - C:\cproject\delphi\SD200w_R2\analysis\runtime_test\sit_live_review\data\test | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986056602351700_0.png) |
| View > Tables > Standard Depth Sectioned | SAIV Instrument Terminal - SCTDOFOTc 204 - C:\cproject\delphi\SD200w_R2\analysis\runtime_test\sit_live_review\data\test | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986058712382000_0.png) |
| View > Tables > Standard Temp | SAIV Instrument Terminal - SCTDOFOTc 204 - C:\cproject\delphi\SD200w_R2\analysis\runtime_test\sit_live_review\data\test | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986060799563700_0.png) |
| View > Graph > Time > Salinity / Temperature | SAIV Instrument Terminal - SCTDOFOTc 204 - C:\cproject\delphi\SD200w_R2\analysis\runtime_test\sit_live_review\data\test | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986062925542900_0.png) |
| View > Graph > Time > Conductivity / Temperature | SAIV Instrument Terminal - SCTDOFOTc 204 - C:\cproject\delphi\SD200w_R2\analysis\runtime_test\sit_live_review\data\test | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986065057976900_0.png) |
| View > Graph > Time > Sound velocity / Density | SAIV Instrument Terminal - SCTDOFOTc 204 - C:\cproject\delphi\SD200w_R2\analysis\runtime_test\sit_live_review\data\test | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986067160539000_0.png) |
| View > Graph > Time > Oxygen | SAIV Instrument Terminal - SCTDOFOTc 204 - C:\cproject\delphi\SD200w_R2\analysis\runtime_test\sit_live_review\data\test | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986069307754000_0.png) |
| View > Graph > Time > Optional sensor | SAIV Instrument Terminal - SCTDOFOTc 204 - C:\cproject\delphi\SD200w_R2\analysis\runtime_test\sit_live_review\data\test | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986071383426200_0.png) |
| View > Graph > Time > Depth | SAIV Instrument Terminal - SCTDOFOTc 204 - C:\cproject\delphi\SD200w_R2\analysis\runtime_test\sit_live_review\data\test | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986073476699000_0.png) |
| View > Graph > Depth > Salinity / Temperature | SAIV Instrument Terminal - SCTDOFOTc 204 - C:\cproject\delphi\SD200w_R2\analysis\runtime_test\sit_live_review\data\test | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986075706210500_0.png) |
| View > Graph > Depth > Conductivity / Temperature | SAIV Instrument Terminal - SCTDOFOTc 204 - C:\cproject\delphi\SD200w_R2\analysis\runtime_test\sit_live_review\data\test | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986078019483600_0.png) |
| View > Graph > Depth > Sound velocity / Density | SAIV Instrument Terminal - SCTDOFOTc 204 - C:\cproject\delphi\SD200w_R2\analysis\runtime_test\sit_live_review\data\test | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986080120769800_0.png) |
| View > Graph > Depth > Oxygen | SAIV Instrument Terminal - SCTDOFOTc 204 - C:\cproject\delphi\SD200w_R2\analysis\runtime_test\sit_live_review\data\test | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986082217811100_0.png) |
| View > Graph > Depth > Optional sensor | SAIV Instrument Terminal - SCTDOFOTc 204 - C:\cproject\delphi\SD200w_R2\analysis\runtime_test\sit_live_review\data\test | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986084381088700_0.png) |
| Display > Depth calculation... | Depth calculation | [Bilde](../analysis/runtime_test/sit_live_review/command_1788985962053136100_0.png) |
| Display > Select oxygen unit | Oxygen unit | [Bilde](../analysis/runtime_test/sit_live_review/command_1788985964156053200_0.png) |
| Display > Select turbidity unit | Turbidity unit | [Bilde](../analysis/runtime_test/sit_live_review/command_1788985966277490400_0.png) |
| Display > Avg all passes in Std Depth Sectioned... | Setup multiple pass standard depth | [Bilde](../analysis/runtime_test/sit_live_review/command_1788985968607522400_0.png) |
| Display > Graph color settings... | Set graphics parameters | [Bilde](../analysis/runtime_test/sit_live_review/command_1788985971169526100_0.png) |
| Display > Select export file date/time format | Export file date / time format | [Bilde](../analysis/runtime_test/sit_live_review/command_1788985973386205300_0.png) |
| Util > Remove spikes... | Select file | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986105023752500_0.png) |
| Util > Split data file... | Split measurement file | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986107202059700_0.png) |
| Util > Compute Sound velocity... | Confirm | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986187161614200_0.png) |
| Util > Convert salinity to conductivity | SAIV Instrument Terminal - SCTDOFOTc 204 - C:\cproject\delphi\SD200w_R2\analysis\runtime_test\sit_live_review\data\test | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986200648618100_0.png) |
| Util > Update barometric pressure... | Update barometric pressure | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986189264821400_0.png) |
| Util > Update measurement position... | Update measurement position | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986191450494400_0.png) |
| Util > Change standard depths... | Set standard depths | [Bilde](../analysis/runtime_test/sit_live_review/command_1788985975543750200_0.png) |
| Util > Change standard depth sections... | Change standard depth sections | [Bilde](../analysis/runtime_test/sit_live_review/command_1788985977692015100_0.png) |
| Util > Change standard temperatures... | Set standard temperatures | [Bilde](../analysis/runtime_test/sit_live_review/command_1788985979802614800_0.png) |
| Util > Recalculate calibration coefficients... | Recalculate calibration coefficients | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986116337475400_0.png) |
| Util > Iso-line data for SURFER... | Iso line data for SURFER | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986118986294300_0.png) |
| Util > Calibration from RAW data... | Calibrate from raw data | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986121232055300_0.png) |
| Util > Rinko oxygen calibration | Rinko oxygen sensor calibration | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986123662909900_0.png) |
| Util > Set heading and unit for optional channel... | Optional channel parameters | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986193589702400_0.png) |
| Util > Edit starting time | Edit starting time | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986195757620700_0.png) |
| Util > Automatic readouts | Automatic readout | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986130244071200_0.png) |
| Util > Adjust measurement values | Adjust measurement values | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986198149136700_0.png) |
| Util > Set minimum depth mask | Set minimum depth mask  | [Bilde](../analysis/runtime_test/sit_live_review/command_1788986134555004200_0.png) |
| Help > About... | About | [Bilde](../analysis/runtime_test/sit_live_review/command_1788985981936555300_0.png) |
| Help > Update software... | SAIV IT - Update software | [Bilde](../analysis/runtime_test/sit_live_review/command_1788985984056572600_0.png) |

## Komplett hovedmenytre ved oppstart

Hentet fra den kjørende EXE-en, med undermenyene rekursivt. Tilgjengelighet er bevart i rå JSON-rapportene.

```text
File
  Open...
  Export
    List
    Standard depths
    Standard Depth Sectioned
    Standard temperatures
    Sonar file
    Lybin file (Bathy data.xml)
    Tide data
  Import CSV/TXT...
  Convert CSV/TXT...
  Set range...
  Set scaling...
  Page setup..
  Print...
  Close file
  Exit	Alt+X
View
  List
  Tables
    Standard Depth
    Standard Depth Sectioned
    Standard Temp
  Graph
    Time
      Salinity / Temperature
      Conductivity / Temperature
      Sound velocity / Density
      Oxygen
      Optional sensor
      Depth
    Depth
      Salinity / Temperature
      Conductivity / Temperature
      Sound velocity / Density
      Oxygen
      Optional sensor
  Instrument
Display
  Toolbar
  Statusbar
  Legend
  GPS position
  Only selected series
  Average
  Density
  Calculated density for TD instruments
  Depth calculation...
  Select oxygen unit
  Select turbidity unit
  Avg columns in Std Depth Sectioned
  Avg all passes in Std Depth Sectioned...
  Graph color settings...
  Select export file date/time format
Util
  Remove spikes...
  Split data file...
  Compute Sound velocity...
  Convert salinity to conductivity
  Update barometric pressure...
  Update measurement position...
  Change standard depths...
  Change standard depth sections...
  Change standard temperatures...
  Recalculate calibration coefficients...
  Iso-line data for SURFER...
  Calibration from RAW data...
  Rinko oxygen calibration
  Set heading and unit for optional channel...
  Edit starting time
  Automatic readouts
  Adjust measurement values
  Set minimum depth mask
Help
  About...
  Update software...
```

## Menytilstand etter åpning av data

Begge menytrær er lagret. Dette er observerte programtilstander, ikke en antakelse om at alle instrumenttyper har samme menyer.

### Klassisk SD2

```text
File
  Open...
  Export
    List
    Standard depths
    Standard Depth Sectioned
    Standard temperatures
    Sonar file
    Lybin file (Bathy data.xml)
    Tide data
  Import CSV/TXT...
  Convert CSV/TXT...
  Set range...
  Set scaling...
  Page setup..
  Print...
  Close file
  Exit	Alt+X
View
  List
  Tables
    Standard Depth
    Standard Depth Sectioned
    Standard Temp
  Graph
    Time
      Salinity / Temperature
      Conductivity / Temperature
      Sound velocity / sigma T
      Optional sensor
      Depth
    Depth
      Salinity / Temperature
      Conductivity / Temperature
      Sound velocity / sigma T
      Optional sensor
      T-S diagram
  Instrument
Display
  Toolbar
  Statusbar
  Legend
  GPS position
  Only selected series
  Average
  Density
  Calculated density for TD instruments
  Depth calculation...
  Select oxygen unit
  Select turbidity unit
  Avg columns in Std Depth Sectioned
  Avg all passes in Std Depth Sectioned...
  Graph color settings...
  Select export file date/time format
Util
  Remove spikes...
  Split data file...
  Compute Sound velocity...
  Convert salinity to conductivity
  Update barometric pressure...
  Update measurement position...
  Change standard depths...
  Change standard depth sections...
  Change standard temperatures...
  Recalculate calibration coefficients...
  Iso-line data for SURFER...
  Calibration from RAW data...
  Rinko oxygen calibration
  Set heading and unit for optional channel...
  Edit starting time
  Automatic readouts
  Adjust measurement values
  Set minimum depth mask
Help
  About...
  Update software...
```

### Importerte loggerdata

```text
File
  Open...
  Export
    List
    Standard depths
    Standard Depth Sectioned
    Standard temperatures
    Sonar file
    Lybin file (Bathy data.xml)
    Tide data
  Import CSV/TXT...
  Convert CSV/TXT...
  Set range...
  Set scaling...
  Page setup..
  Print...
  Close file
  Exit	Alt+X
View
  List
  Tables
    Standard Depth
    Standard Depth Sectioned
    Standard Temp
  Graph
    Time
      Salinity / Temperature
      Conductivity / Temperature
      Sound velocity / sigma T
      Optional sensor
      Depth
    Depth
      Salinity / Temperature
      Conductivity / Temperature
      Sound velocity / sigma T
      Optional sensor
      T-S diagram
  Instrument
Display
  Toolbar
  Statusbar
  Legend
  GPS position
  Only selected series
  Average
  Density
  Calculated density for TD instruments
  Depth calculation...
  Select oxygen unit
  Select turbidity unit
  Avg columns in Std Depth Sectioned
  Avg all passes in Std Depth Sectioned...
  Graph color settings...
  Select export file date/time format
Util
  Remove spikes...
  Split data file...
  Compute Sound velocity...
  Convert salinity to conductivity
  Update barometric pressure...
  Update measurement position...
  Change standard depths...
  Change standard depth sections...
  Change standard temperatures...
  Recalculate calibration coefficients...
  Iso-line data for SURFER...
  Calibration from RAW data...
  Rinko oxygen calibration
  Set heading and unit for optional channel...
  Edit starting time
  Automatic readouts
  Adjust measurement values
  Set minimum depth mask
Help
  About...
  Update software...
```

## Avgrensning og bildekvalitet

Instrumentkommunikasjon, Detect-søk, Download, Interval, TIME/DATE og fysisk kalibrering er ikke utført i denne gjennomgangen. Det er heller ikke gjort en full numerisk validering eller prøvd alle kombinasjoner av enheter, datatyper og underdialoger. Disse må ikke merkes ferdigtestet ut fra skjermbilder.

Bilder er tatt med PrintWindow og, der skrivebordstilgangen tillot det, direkte skjermfangst. PrintWindow kan mangle innhold fra egendegnede kontroller og vise andre vindusrammer enn skjermen. About er derfor også kontrollert med direkte skjermfangst. Svarte fangster inngår ikke som visuelle bevis i denne indeksen.

Originalleveransene og originaldataene er beholdt. Gjennomgangen brukte egne testfiler under analysis/runtime_test/sit_live_review/data. Den ordinære EXE-en kan oppdatere sine vanlige brukerinnstillinger (for eksempel sist brukt filmappe og bekreftede Convert-valg); dette var ikke en isolert registertest.

## Konsekvens for saiv-studio

Neste implementering må bruke disse konkrete vinduene og arbeidsflytene som fasit. Studios fem toppsider, generelle grafvisning og samlede Utilities-side gjenskaper ikke SITs organisering. Visuell likhet alene gir heller ikke fil- eller beregningslikhet; dette må kontrolleres separat mot SIT. Ingen nye GSW-/TEOS-10-resultater må presenteres som identiske med de originale SIT-beregningene uten sammenligning.

Rå bilder, fullstendige vindus-/kontrollrapporter og datasett ligger i analysis/runtime_test/sit_live_review. Inspeksjonsverktøy: analysis/inspect_sit_live.py. Denne indeksen genereres av analysis/build_sit_gui_review.py.
