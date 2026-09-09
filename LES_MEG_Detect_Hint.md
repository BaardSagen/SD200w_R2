# MiniSoft 1.1.1 – hjelp i søkevinduet

Start `SD200W_SAIV_v1.1.1_DetectHint_Sept2026.exe`.

Tittelen i Detect er nå:

> Find communication speed - Double-click green ports to open

Bare tittelressursen og versjonsinformasjonen er endret fra 1.1.0. G etter SD200-valg, native UART og Show startup text videreføres. Tidligere leveranser beholdes.

Den faktiske Windows-tittelen er kontrollert. Teksten måler 330 piksler i systemets tittelfont og passer i vinduet på 504 piksler, med plass til lukkeknappen.

Bygg: `analysis/build_detect_title.py`, hashbundet til bevart 1.1.0. Kontroll: `analysis/check_detect_title.py` og `analysis/detect_title_gui_validation.json`. SHA-256: `53841d3d6e515d9a659a93c49b00bacff651a83092c1d4453a866a755778f4e6`.

Lokal leveranse, ikke publisert på GitHub.
