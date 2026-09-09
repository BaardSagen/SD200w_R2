# SAIV Instrument Terminal 1.3.1 - Merge og Convert

Lokal leveranse 9. september 2026. Pakk ut hele **SAIV_IT_v1.3.1_portable.zip** og start **SAIV_Instrument_Terminal_v1.3.1_Sept2026.exe**. **SIT_Import131.dll** skal ligge i samme mappe. Tidligere EXE/DLL/ZIP-filer er beholdt.

## Endringer

- Knappen heter **Convert**, og File-menyen og filvelgeren heter **Convert TXT/CSV**.
- **Include date/time from merged files** ved toleransefeltet er pa som standard. Fjern haken for a utelate DATE/TIME-kolonnene fra M1 og M2. Masterens dato/tid, alle andre verdier og Delta_seconds beholdes. Valget gjelder begge tilleggsfiler og krever ingen ny skanning. DATE/TIME, Date/Time og DATO/TID behandles likt.
- Forste headerlinje viser program, 1.3.1, toleranse i sekunder, om tilleggsfilenes dato/tid er beholdt eller fjernet, og treffantall for M1/M2.
- Deretter kommer masterens header og kildebane, sa M1-header og kildebane, og eventuelt M2-header og kildebane. Ingen forklaringer eller treffantall etter filbanene.
- Den separate SAIV IT merge-linjen er fjernet. De to syntetiske fixture-kommentarene om SYNTHETIC TEST DATA og Based on ... generated for OSU107 timestamp matching kopieres ikke til merge-resultatet. Testdata er fortsatt syntetiske; originalfilene og deres merking er beholdt.
- Ingen semikolon over FIELDS-linjen. Semikolon i innlest headertekst eller kildebane vises som komma i eksportheaderen. FIELDS og dataradene beholder semikolon som separator.

Eksempel med fjernet dato/tid:

```text
# SAIV IT merged data 1.3.1 - tolerance 2 seconds (removed merged file date/time) - M1 matches 79/79
# [masterens originale instrumentheader]
# Master source: C:\data\master.txt
# M1_header: # [tilleggsfilens originale instrumentheader]
# M1_source: C:\data\logger.csv
FIELDS: ...
```

Mappeskanning, toleranse 0.0-10.0 s, opptil to tilleggsfiler, naermeste tidspunkt, gjenbruk av tilleggsrader og tomme felter ved manglende treff er viderefort fra 1.3.0. Se LES_MEG_Merge_130.md for koblingsreglene og testfilene; headerbeskrivelsen og Import-navnet der gjelder eldre versjon.

## Verifikasjon

9679 uavhengige tids-/verdikontroller, 4108 verdikontroller av GUI-eksport og 16 Merge-/10 Convert-hooktester bestod. Windows-dialogen er testet med dato/tid pa og av for to tilleggsfiler, med uendrede andre celler. Kontroller dekker headerrekkefolge, semikolonfri header, treffantall overst, rene kildebaner, begge separatorvalg, max to filer, avbryt, toleransegrenser og overskrivingsvern. Convert-knapp og File-meny er kontrollert. Dialogen er visuelt kontrollert med PrintWindow pa en egen testprosess.

Rapporter og bilde: analysis/runtime_test/merge131/. CTD-formelbytes er uendret. Ingen fysisk instrumenttest eller GitHub-push i denne leveransen.

Bygg: python analysis/build_logger_import_131.py. Bygggrunnlag: bevart 1.1.3. Kilde: sit_import/merge.h, merge_ui.inc og import_hook_131.s. 1.3.0-kilden er bevart i analysis/reference/sit_import_v130, og det gamle byggskriptet peker dit.
