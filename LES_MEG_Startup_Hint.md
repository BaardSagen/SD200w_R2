# MiniSoft 1.0.8 — hjelpelinje ved stille oppstart

Program: `SD200W_SAIV_v1.0.8_StartupHint_Sept2026.exe`.

Hvis det ikke er mottatt instrumentdata tre sekunder etter at terminalen åpnes ved programstart, vises én lokal hjelpelinje:

> Hold <I> to wake the instrument, or use Detect to find connected units.

Teksten sendes ikke på serieporten. Mottatte data før fristen undertrykker hjelpen. Den gjentas ikke ved reaktivering eller senere pauser i datastrømmen. Hvis valgt COM-port er endret før fristen, vises ikke oppstartshjelpen for den gamle porten.

## Bygg og kontroll

Bygges fra bevart 1.0.7, SHA-256 `3cb193bdad4975c99a784b2cf6a9cf9f54031b52ae74746c72aa2cb81380017f`:

```powershell
python analysis/build_startup_wake_hint.py
python analysis/test_startup_wake_hint.py
```

Kode: `analysis/startup_wake_hint.s`. Manifest: `analysis/startup_wake_hint_manifest.json`. Testresultat: `analysis/startup_wake_hint_validation.json`.

14 x86-tilfeller bestod: stille port, tidlige/senere mottatte data, engangsvisning, byttet port, lukket hovedvindu og mislykket timeropprettelse. Stakk/register og alternativ lasteadresse er kontrollert. GUI-kontroll kjøres med `analysis/check_startup_hint_windows.py` uten autodetekt eller nye seriekommandoer.

1.0.7-funksjonen med G etter SD200-valg og native UART-autodetekt er beholdt. Ingen endring i formler. Tidligere leveranser beholdes. ImGui er fortsatt på pause. Lokal leveranse, ikke publisert på GitHub.

SHA-256: `450ebde32a2ca79331ed6ee1434a38e0f32bbf946554e209477084cb8a1c0550`.
