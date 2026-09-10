# SIT 1.4.10 – salinitet i Quick guide

Leveranse: **SAIV_Instrument_Terminal_v1.4.10_Sept2026.exe**. Kunden trenger fortsatt bare én EXE.

Help > Quick guide > Conductivity and salinity forklarer nå at SD208 selv beregner salinitet S fra målt C, T og P med PSS-78. Guiden bruker S i symbolforklaringer og eksempler, og forklarer én gang at SP er fagbetegnelsen for den samme praktiske saliniteten. Absolutt salinitet SA i g/kg holdes tydelig atskilt.

Teksten forklarer også forskjellen mellom instrumentets lagrede S og ny beregning i Convert. Metodevalget i Convert endrer beregningen i SIT, ikke instrumentets beregningsmetode. System evaluation nevner SD208s PSS-78-metode direkte.

Kun hjelpetekst og programversjon er endret. Tidligere 1.4.9-EXE og kilde er bevart; kildearkiv: `analysis/reference/sit_import_v149`.

Bygg: `analysis/build_single_exe_1410.py` med `C:\MinGW\bin` i PATH. Intern DLL heter `SIT_Import150.dll` for å beholde lengden på DLL-navnet i Delphi-runtime; den er innebygd og skal ikke leveres separat. Runtime viser `1.4.10 Sept2026` for å beholde ressurslengden.

Kontroller: `analysis/salinity_guide1410_validation.json` og `analysis/runtime_test/guide1410/gui_validation.json`. GUI-testen leser alle 26 emnene fra den ferdige EXE-filen og kontrollerer tastatur, rulling og lukking. Ingen instrumentkommandoer eller serverpublisering inngår.
