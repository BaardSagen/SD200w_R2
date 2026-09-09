# MiniSoft 1.0.7 — G etter valg av SD200

Program: `SD200W_SAIV_v1.0.7_SelectG_Sept2026.exe`.

Når kunden bekrefter et funnet SD200-instrument med dobbeltklikk eller OK, sender programmet én stor `G` etter at terminalporten er åpnet med funnet hastighet og paritet. Porten får 1100 ms til å stabilisere seg først. Ingen Enter eller andre tegn legges til.

Dette gjelder bare valgt instrument med vellykket SD200-gjenkjenning og komplett hovedmeny. OSU107 og SAIV110/SurfaceLogger får ikke denne ekstra G-kommandoen. Vanlig merkeklikk, avbryt, uferdig søk og mislykket portåpning utløser ikke sendingen. Eksisterende kommandoer inne i autodetekt er uendret.

## Bygg og tester

Bygget fra uendret 1.0.6 (`4b7c492d8fa64b9bf2ffd939ef629d2d82cde7243d766aecb757810e27056b53`). Original og tidligere leveranser beholdes. Native UART/autodetekt fra 1.0.6 er bevart byte for byte.

```powershell
python analysis/build_sd200_selection_g.py
python analysis/test_sd200_selection_g.py
```

Maskinkode: `analysis/sd200_selection_g.s`. Manifest: `analysis/sd200_selection_g_manifest.json`. Resultat: `analysis/sd200_selection_g_validation.json`.

24 x86-tester består: SD200, OSU107, SurfaceLogger, ukjent/delvis svar, ikke valgt SD200, avbryt, uferdig søk, mislykket åpning og beskyttelse mot dobbel sending. Register/stakk og alternativ lasteadresse er kontrollert. Fysisk COM7-test bestod: dobbeltklikk på SD200, native 9600 7E1, og én G på den gjenåpnede terminalforbindelsen. Windows bekreftet én sendt byte. Rapport: `analysis/com7_select_g_validation.json`. OSU107/SurfaceLogger-avgrensningen er testet i emulator, uten fysiske kommandoer til disse portene.

SHA-256: `3cb193bdad4975c99a784b2cf6a9cf9f54031b52ae74746c72aa2cb81380017f`.

Utgaven er lokal og ikke publisert på GitHub. ImGui-arbeidet er fortsatt satt på pause. Formelarbeidet er uendret; les egne kartleggings- og kontrollnotater.

Typekontrollen skjer før FormClose frigir søkearbeiderne. Bare et bekreftet SD200-valg aktiverer sendingen og åpner terminalporten dersom den tidligere var lukket. Etter sending eller åpningsfeil nullstilles engangsflagget. Native autodetekt og formlene er bevart.
