# MiniSoft 1.1.0 – G etter gjentatt SD200-valg

Start `SD200W_SAIV_v1.1.0_SelectG_Sept2026.exe`. SHA-256: `4ee2d90fe1dc79dd9ef6f3f95ac2102769f4382712f8e8cfb57eea9db8d5f037`.

Etter valg av SD200 i Detect, med dobbeltklikk eller OK, sendes én G på den valgte terminalporten. Dette gjelder også ved gjentatt valg og bytte fra OSU107 tilbake til SD200. OSU107 og SurfaceLogger får ikke denne ekstra G-en.

Tidligere kunne G bli sendt på den gamle terminalporten før Setup hadde fullført portbyttet. Ny kode tar portnummer, baudrate og paritet fra det valgte søkeresultatet før arbeiderobjektet frigjøres, bruker disse ved gjenåpning og sender G fra en engangstimer tidligst 1100 ms senere. Et nytt søk avbryter en ventende G; lukket eller endret port, feil åpning og avbrutt valg sender ikke.

Show startup text, lagring av serieportinnstillinger og native UART-paritet er beholdt. Ingen softwareparitet. ImGui er fortsatt på pause. Tidligere EXE-filer beholdes.

## Kontroll

Fysisk prøve: COM7 SD200 (dobbeltklikk) → COM11 OSU107 (OK) → COM7 SD200 (dobbeltklikk) → COM7 SD200 (OK). Windows WriteFile bekreftet én byte G på den endelige COM7-forbindelsen ved hvert SD200-valg; ingen ekstra G på COM11 etter valg. Se `analysis/select_delayed_physical_summary.json` og full sendelogg `analysis/select_delayed_physical_validation.json`. Prøven bekrefter sending; menyrespons etter G er ikke automatisk kontrollert.

X86-tester dekker klassifisering, frigjorte søkeresultater, gammel terminalport COM11 versus valgt COM7, gjentatt valg, engangssending, endret/lukket port, avbrudd og relokering. Bygg: `analysis/build_sd200_selection_g_delayed.py`; kode: `analysis/sd200_selection_g_delayed.s`; test: `analysis/test_sd200_selection_g_delayed.py`. Bygget er hashbundet til bevart 1.0.9. Fysisk diagnosekopi bygges ved å kopiere den nye EXE til `analysis/runtime_test/SELECT_DELAYED_TRACE.exe`, kjøre `analysis/add_select_delayed_tx_trace.py` og deretter `analysis/check_select_delayed_physical.py analysis/runtime_test/SELECT_DELAYED_TRACE.exe`. Dette siste steget bruker de tilkoblede instrumentene.

Den tidligere meldte AV ved portlukking er ikke gjenskapt eller dokumentert rettet av denne endringen. Brukeren har heller ikke fått den igjen. Leveransen er lokal, ikke publisert på GitHub.
