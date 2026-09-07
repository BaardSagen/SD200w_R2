# MiniSoft med blått uttrykk

Bruk `SD200W_SAIV_OSU107_Blue.exe`.

- Lyse blå paneler og dialogbakgrunner.
- Nesten hvit terminalbakgrunn med mørk blå tekst.
- Segoe UI i dialogene og Consolas i terminalen.
- Flatere verktøylinje og færre rammer rundt panelene.
- Grønn instrumentrad og tidligere funksjonsendringer er beholdt.

Dette er en oppdatering av Delphi-formenes utseende. Programmets opprinnelige
kjørbare kode er kontrollert uendret. Den forrige EXE-filen er bevart.
55 formressurser har fått farge-/skriftjusteringer. Terminal, Setup og Detect
er visuelt kontrollert; øvrige dialoger er ikke individuelt gjennomgått.

Test: instrumentet ble funnet på COM7 mens COM18 fortsatte søket.
Vekselvis radvalg beholdt begge rader synlige. En synlig test fikk dialogen
lukket før testskriptets planlagte avbryt og endte med en tilgangsfeil etter
at skriptet forsøkte å lukke den igjen. Skriptet er rettet til å stoppe ved
tidlig lukking og bare lukke synlige dialoger. Årsaken til den tidlige
lukkingen er ikke fastslått. Siste isolerte kjøring av endelig EXE bestod
oppstart, Detect/avbryt og Setup/avbryt uten feilmeldinger.

Bygg: `analysis/build_blue_look.py`.
Testlogg: `analysis/runtime_test/SD200W_SAIV_OSU107_Blue.json`.
