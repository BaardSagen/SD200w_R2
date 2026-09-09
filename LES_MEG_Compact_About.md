# SD200W 1.0.3 – mindre About og Disclaimer

8. september 2026.

Program: [SD200W_SAIV_v1.0.3_Sept2026.exe](SD200W_SAIV_v1.0.3_Sept2026.exe).

- About-klientområdet er redusert fra 640 × 310 til 448 × 279 (30 % smalere, 10 % lavere).
- OSU017 / SurfaceLogger er lagt til i instrumentlisten under «for».
- Disclaimeren er omtrent 70 % smalere. Linjeskift er tilpasset; ingen ord eller avsnitt er fjernet. Høyden øker for å vise hele teksten.
- Krediteringene fra 1.0.2 er beholdt.

Bygg: `python analysis/build_compact_about.py`, med 1.0.2 som hashbundet inngang. GUI-kontroll: `python analysis/check_compact_about_windows.py --live`. Dette starter og avslutter egen testprosess. Begge dialogene og skjermbildene er kontrollert; ingen instrumenttest er utført. PE-sjekksum og versjonsfelt er kontrollert, og øvrig instruksjonskode er bevart bortsett fra adressen til disclaimer-strengen.

SHA-256: `b817a5898aa2780dbfd502f22de28fbda7b1d4b0a1f8a0f50e0f564b56fdc2c9`.

Original og tidligere leveranser er beholdt. Denne leveransen er lokal; GitHub-opplasting er ikke utført.
