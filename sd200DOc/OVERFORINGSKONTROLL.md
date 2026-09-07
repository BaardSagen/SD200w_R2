# Kontroll av prosjektoverføring

Dato: 7. september 2026.

Testet i en separat eksport av Git-indeksen, med et nyopprettet Python 3.11 x64-miljø og pakker installert fra `requirements-dev.txt`. Ingen lokal `analysis/python_packages` fulgte med testkopien. Dette er en simulert flytting på samme Windows-PC, ikke en fysisk test på en annen maskin.

| Kontroll | Resultat |
|---|---|
| `verify_transfer.py` | Bestod |
| `test_recovered_formulas.py` | Bestod (24 sammenligninger) |
| `audit_formulas.py` | Bestod |
| `test_no_handshake.py` | Bestod |
| `test_guard.py` | Bestod (10 tester) |
| `test_refresh.py` | Bestod (5 tester) |
| `test_logger_clean.py` | Bestod (10 tester) |
| `test_refresh_reply.py` | Bestod (15 tester) |
| `build_version_1_0_1.py` | Bestod |
| `verify_transfer.py` | Bestod |

Siste versjon ble bygget fra medfølgende NoHandshake og har fortsatt SHA-256 `ebd75cdb4b93ff2e703b518550dfd2bce51490d8f12b6f0cb6f311f0a5f92068`. Alle 29 medfølgende EXE-filer hadde forventet hash både før og etter test/versjonsbygg.

Alle 13 `LES_MEG_*.md` følger med. Alle navngitte EXE-referanser i analyseskriptene finnes i leveransen. Filkontrollen omfatter også dokumentasjon, referanser, testbevis og kildefiler.

Formel-audit ble kjørt og rapporten generert uten feil; auditens referanser er ikke i seg selv en fullstendig faglig godkjenning av formlene. Ingen formelretting eller fysisk instrumenttest er utført under overføringen. Historiske byggtrinn utover siste versjonsbygg er ikke bygget på nytt.
