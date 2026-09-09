# Kildegrunnlag

Studio er et eget C++-program og laster ikke Delphi-EXE-en. Grensesnittet er laget etter brukerens bestilling og gjennomgang av kjørende SIT 1.4.3; se prosjektets `sd200DOc/SIT_GUI_GJENNOMGANG.md`.

`src/sit/` inneholder egne kopier av prosjektets SIT-moduler for loggerfiler, konverteringsvalg, presets, Merge, native filformat og innstillingsprotokoll. Originalene under `sit_import/` er beholdt. Dialogene bruker Studio-navn, moderne Windows-kontroller/Segoe UI og egen preset-registersti.

`sit_compat.cpp` implementerer dokumenterte SIT-beregninger i C++ med registrerte maskinkoderesultater som testreferanser. Merk callback-rekkefølgen: `sitFormula(0,C,T,P)`, mens SITs konverteringsmodul bruker `sitConversionFormula(0,P,C,T)`. Real depth bruker SITs fixed-position uttrykk med EOS-80-tetthet og gravity, ikke en alternativ trykkpolynom- eller TEOS-10-gren.

ImGui og GSW er versjonsfestet i THIRD_PARTY_NOTICES.md. GSW og eldre kjernetester er beholdt, men standardkonverteringen i 0.3.0 bruker SIT-rutinene. Brukerens instrumentikon er beholdt.

Bygg med `build.cmd`. Historiske engangsskript i `analysis` er ikke den generelle byggprosessen. 0.2.0 er arkivert i `analysis/reference/saiv_studio_v020`. Bevar ekte UART 7E1, komplette menyer, mottaksro, skillet C/c og tapfri CSV-rundtur.

Windows-vinduer, fildialoger og serieporttilgang må tilpasses eller erstattes ved senere Linux-/Mac-portering. Beregnings-, fil- og protokollkjernen er skilt fra grensesnittet; denne leveransen har bare Windows-EXE.
