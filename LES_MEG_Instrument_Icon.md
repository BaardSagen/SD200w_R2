# MiniSoft 1.1.2 – nytt instrumentikon

Start `SD200W_SAIV_v1.1.2_InstrumentIcon_Sept2026.exe`.

Brukerens `icon/ctd_in_Cage.ico` er brukt som programikon og på Instrument-knappen i verktøylinjen. Programikonet inneholder alle ni størrelsene fra 16 til 256 piksler. Instrumentknappen bruker 20 × 20 piksler med separat nedtonet bilde når knappen er deaktivert.

Bare ikon-/skjemaressurser, nødvendig PE-metadata og versjonsinformasjon er endret. Kommunikasjonskoden er uendret fra 1.1.1. G etter SD200-valg, hjelpeteksten i Detect og Show startup text er videreført.

Kontroll: programmet startet, nytt ikon i tittellinjen og på knappen er visuelt kontrollert, og Windows hentet ut både stort og lite programikon. Skjermbilde: `analysis/runtime_test/instrument_icon_v112.png`. Rapport: `analysis/instrument_icon_gui_validation.json`.

Bygg: `python analysis/build_instrument_icon.py`. Krever Python med pefile og Pillow, ikonfilen og bevart 1.1.1. Kontroll: `python analysis/check_instrument_icon.py`. SHA-256: `e85cdb6119350e249a17b1eda037640a04ee2c12be210f2cc91a474bbd3cf6b7`.

Tidligere leveranser beholdes. Lokal leveranse, ikke publisert på GitHub.
