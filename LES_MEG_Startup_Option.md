# MiniSoft 1.0.9 — valgfri oppstartstekst

Program: `SD200W_SAIV_v1.0.9_StartupOption_Sept2026.exe`.

Åpne **Setup → Serial port**. Rett under **Ref inst** ligger avkrysningsboksen **Show startup text**.

- På: Etter tre sekunder uten instrumentdata ved oppstart vises «Hold <I> to wake the instrument, or use Detect to find connected units.»
- Av: Ingen hjelpetekst ved oppstart.
- OK lagrer valget. Cancel beholder tidligere valg. Standard er på når innstillingen ikke finnes.

Valget bruker samme innstillingsobjekt som serieporten: `TRegistryIniFile`, seksjon `Comm`, nøkkel `ShowStartupText` med verdi 0/1. I dette programmet lagres det i Windows-registeret under `HKEY_CURRENT_USER\Software\MHP\SdInstr\Comm`, ikke i en separat INI-fil. Det opprettes ingen egen innstillingsfil. Valget følger Windows-brukeren på denne PC-en; på en ny PC brukes standardverdien dersom innstillingene ikke er flyttet.

## Bygg og verifisering

Bygget fra bevart 1.0.8, SHA-256 `450ebde32a2ca79331ed6ee1434a38e0f32bbf946554e209477084cb8a1c0550`.

```powershell
python analysis/build_startup_hint_option.py
python analysis/test_startup_hint_option.py
```

Kode: `analysis/startup_hint_option.s`. Manifest: `analysis/startup_hint_option_manifest.json`.

18 x86-tester bestod for aktivert/deaktivert hjelp, mottatte data, engangsvisning, portbytte, levetid og alternativ lasteadresse. GUI-test bekreftet lagring av/på, av/på etter omstart og Cancel uten lagring. Skjermbilder bekreftet plassering under Ref inst og tekst bare når valget er på. Rapporter: `analysis/startup_hint_option_validation.json` og `analysis/startup_hint_option_gui_validation.json`.

Lagringskroken kjøres også når baudraten er uendret. Den eksisterende registerlagringen for serieporten er bevart. Ingen formelfunksjoner, native UART-autodetekt eller G etter SD200-valg er endret. Tidligere leveranser beholdes; ImGui er fortsatt på pause. Ingen GitHub-publisering i denne økten.

SHA-256: `0415e50e1f7f72c03d309ee40c7a86217b7c645151025e943c0176659518eefa`.
