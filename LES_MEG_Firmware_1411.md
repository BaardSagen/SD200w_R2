# SIT 1.4.11 ? manuell firmwareoppdatering

Utviklingskandidat: `SAIV_Instrument_Terminal_v1.4.11_Sept2026.exe`, branch `feature/firmware-update`. Tidligere leveranser og 1.4.10-kilde er bevart. Kunden trenger ?n EXE.

## Bruk

Help > Firmware ?pner et eget vindu. Check firmware identifiserer den tilkoblede SAIV110/OSU107-enheten og henter nyeste versjon og versjonsnotat fra saiv.no. Ingen automatisk firmwarekontroll ved oppstart eller ?pning av vinduet.

Update device krever bekreftelse. Vinduet viser gjeldende trinn, animert fremdriftsindikator, medg?tt tid og beskjed om ? beholde USB og str?m tilkoblet. Under omstart brukes en animasjon, ikke en beregnet prosent. Firmware tar normalt omtrent to minutter, deretter kommer kontroll og regenerering av system.ini. Lukking er sperret mens arbeidet p?g?r.

## Kontrollert oppdateringsl?p

1. Match aktiv COM-port og loggerdisk med samme fysiske USB-identitet. Kontroller serienummer, driftsmodus og HW 3.1.2 mot config/system.ini og fersk lokal meny. Kontroller ogs? fersk VER.
2. Hent latest.json og readme.txt fra firmwarekanalen. Bare kompatibel nyere firmware tilbys. Store/sm? bokstaver i versjonssuffikset regnes likt.
3. Hent BIN, kontroller SHA-256 og MCUboot-header, og sikkerhetskopier alle config-filer til LocalAppData/SAIV_IT/FirmwareBackups.
4. Opprett update ved behov. Overskriv update/osu_m_update.bin, ogs? hvis den gamle filen er lengre. Flush, lukk og les hele filen tilbake. Vent ti sekunder og kontroller hele innholdet igjen. Dialogen viser eksakt antall bekreftede byte. Les tilbake p? nytt rett f?r FWU. Avvik stopper oppdateringen.
5. Send Ctrl+T / CFG / FWU gjennom SITs eksisterende terminal. Vent p? komplett meny og mottaksro f?r kommandoer. Observer at b?de disk og COM-port forsvinner og returnerer p? samme USB-enhet; tidsfrist fem minutter.
6. Kontroller ny kj?rende firmware med lokal meny og VER. Krev FWUST CLEAR og tom update-mappe. Enheten fjerner BIN selv. SIT fors?ker maksimalt ?n ekstra reset hvis opprydding gjenst?r, og stopper f?r config-endring hvis det ikke hjelper.
7. Sikkerhetskopier config p? nytt f?r regenerering. Slett bare config/system.ini og send SLP / RESET. Ingen annen config- eller kalibreringsfil slettes.
8. Vent p? enheten og regenerert system.ini. Kontroller ny versjon i INI og fersk VER, korrekt identitet og modus, bevart innhold i ?vrige config-filer og bevarte INI-innstillinger. Kontroller FWUST CLEAR og tom update-mappe igjen f?r suksessmelding.

Sikkerhetskopien beholdes ved feil. Ingen automatisk ny flashing eller gjenoppretting over en ukjent tilstand. Samme versjon/nedgradering tilbys ikke. Kj?r Detect f?r neste ordin?re instrumentoperasjon etter oppdatering.

## R-pakke og fysisk test

Les `osu107Doc/TIL_OPPDATERINGSAGENT_0.9.9R.txt`. R l?ser Q-feilen der USB-eierskap hindret automatisk opprydding. R-BIN er 635648 byte med SHA-256 d557327dae4af7bc90ef2555c800184a6cc08296622cada0f6fc347d30af24a6. Serverens latest.json, readme.txt og BIN er kontrollert mot lokal pakke; alle svarer HTTP 200.

Tidligere P-til-Q-test installerte Q, men stoppet korrekt f?r system.ini-sletting fordi oppryddingen ikke var fullf?rt. Den testen er dokumentert i `osu107Doc/SIT_FIRMWARE_TEST_2026-09-13.md`. Se prosjektstatus og `analysis/firmware1411_validation.json` for siste fysiske resultat.

## Bygg og tester

Bygg med `analysis/build_single_exe_1411.py` og C:/MinGW/bin i PATH. Intern modul: SIT_Import151.dll. Native beregningskode er bevart; runtime-kilden og kontrollsummer fremg?r av `analysis/single_exe_1411_manifest.json`. Historisk 1.4.10-bygg bruker arkivert kilde.

- `analysis/test_firmware1411.cpp`: versjon, manifest, identitet, VER/FWUST, bevarte innstillinger, oppdateringsrekkef?lge og feilforl?p.
- `analysis/test_firmware1411_windows.cpp`: full filskriving/overskriving, bytevis kontroll, config-bevaring og USB-enumerering. Serielle kommandoer er sperret i testverten.
- `analysis/check_firmware1411_gui.py`: faktisk EXE, manuell Help-meny, minimumsst?rrelse, feilh?ndtering og ?vrig hjelp.
- `analysis/check_firmware1411_physical.py --install`: autorisert P-til-R-test p? SN107/COM11. Kontrollerer full oppdatering og bevart config.

SAIV110 og andre maskinvarevarianter er ikke fysisk verifisert i denne SIT-testen. Kanalen gjelder kun HW 3.1.2. Ingen serveropplasting, commit eller push er gjort av SIT-arbeidet.
