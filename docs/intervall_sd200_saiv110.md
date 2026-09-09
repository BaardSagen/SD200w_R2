# Intervallsetting: SD200 (SD204/SD208) og SAIV110 Surface Logger

Implementasjonsbeskrivelse for et annet program. Gjelder gjeldende dokumenterte firmware, 0.9.9Q for SAIV110, og prosjektets SD204/SD208-protokoll. Kontrollert mot lokale kilder 9. september 2026. Eksemplene er illustrasjoner, ikke nye instrumenttester.

## To forskjellige innstillinger

| Enhet | Hvor intervallet settes | Hvordan det tas i bruk |
| --- | --- | --- |
| SD204/SD208 | SD200-instrumentets intervalldialog | `I` → `Y` → valgkode → Enter |
| SAIV110 Surface Logger | `config/system.ini`, seksjon `[surface]`, nøkkel `intervalSeconds` | Lagre/flush filen, og kjør lokal `U` for MIR + APPLY |

Et SD200-intervall endrer ikke Surface-konfigurasjonen. **`I` på SAIV110 starter/stopper logging** og skal ikke brukes til å åpne SD200-intervalldialogen.

## SD204/SD208: protokoll

Bruk oppdaget port og baudrate. Enkeltbokstaver sendes uten Enter, unntatt den uttrykkelige avslutningen etter valgkoden. Enter er rå `CR` (`0x0D`). Samle fragmenterte svar til forventet meny/prompt er komplett.

1. Stopp eventuell måling og bekreft SD200-hovedmenyen. Via OSU107 må direkte kommunikasjon til instrumentet være aktiv; loggerens administrasjonsmeny er en annen meny.
2. Fra vekkesiden bruker prosjektet `S` til status og `M` videre til hovedmenyen. Fra ukjent undermeny normaliseres forbindelsen med `G` og eventuelt `N`, styrt av svaret.
3. Send `I` fra hovedmenyen.
4. Les gjeldende verdi fra `Measuring interval 2sec` eller tilsvarende, og vent på endringsspørsmålet med Y/N.
5. Send `Y` uten Enter.
6. Vent på `Select measuring interval:` og hele valgmenyen.
7. Send valgkoden fra tabellen. Vent omtrent 120 ms, og send `\r`.
8. Vent på hovedmenyen.
9. Send `I` igjen og les `Measuring interval ...`. Sammenlign med ønsket verdi; send `G` tilbake til hovedmenyen.
10. Rapporter vellykket endring først når tilbakeavlest verdi stemmer og hovedmenyen er bekreftet.

### Valgkoder

| Intervall | Sekunder | Send |
| --- | ---: | --- |
| 1 sek | 1 | `L` |
| 2 sek | 2 | `M` |
| 5 sek | 5 | `N` |
| 10 sek | 10 | `O` |
| 20 sek | 20 | `P` |
| 60 sek | 60 | `Q` |
| 5 min | 300 | `R` |
| 10 min | 600 | `S` |
| 30 min | 1800 | `T` |
| 60 min | 3600 | `V` |
| 180 min | 10800 | `W` |

Tabellen er prosjektets SD200-kodetabell. Bekreft at instrumentets annonserte meny støtter ønsket valg. Det finnes ikke et `U`-valg i denne tabellen; ikke generer kodene som en sammenhengende bokstavserie.

Eksempel: 10 sekunder:

```text
TX: I
RX: Measuring interval 2sec ... Y/N
TX: Y
RX: Select measuring interval: ...
TX: O
    vent ca. 120 ms
TX: <CR>
RX: hovedmeny
TX: I
RX: Measuring interval 10sec ...
TX: G
RX: hovedmeny
```

### Timing og feilbehandling

Prosjektets flyt bruker ro i mottaket i tillegg til menygjenkjenning:

- Hovedmeny: 1000 ms ro, deretter 350 ms før første `I`.
- Y/N-prompt: 300 ms ro, deretter 300 ms før `Y`.
- Valgmeny: 500 ms ro, deretter 450 ms før valgkode; 120 ms videre til Enter.
- Etter skriving: hovedmeny og 500 ms ro, deretter 350 ms før kontroll-`I`.
- Etter bekreftet verdi: 250 ms før `G`; hovedmeny og 500 ms ro avslutter flyten.

Dette er appens robuste forsinkelser, ikke oppgitte absolutte firmwarekrav. Ikke send hele dialogen som én tekststreng. Appen har en kontroll for 12 sekunder uten fremdrift og opptil to nye `G`-forsøk under menynormalisering; et nytt program bør ha en eksplisitt tidsfrist for hver ventetilstand. Ved avvikende tilbakeavlest intervall rapporteres feil, ikke suksess basert på at skrivingen gikk gjennom.

## SAIV110: sett intervalSeconds og les inn konfigurasjonen

Surface-firmware bruker sekunder i `config/system.ini` på loggerens monterte USB-disk. Bruk seksjonsnavnet `[surface]`.

Eksempel på relevant del av en eksisterende fil, for 10 sekunder:

```ini
[surface]
enable=1
intervalSeconds=10

[instrument0]
enable=0
```

Dette er et **utdrag**, ikke en komplett erstatning for filen. Ved ren intervallendring endres bare `[surface].intervalSeconds`; behold øvrige nøkler, seksjoner, kanaler og kalibrering. Ikke skift loggermodus som en skjult del av intervallsettingen. Eksempelet forutsetter at enheten allerede er Surface Logger.

Prosjektets filomskriver validerer intervallet som heltall fra **1 til 86400 sekunder**. GUI-en tilbyr den samme listen med 11 intervaller som ovenfor; dette er et snevrere utvalg enn filomskriverens verdiområde. Eventuelle firmwarefeil under innlesing må fortsatt håndteres.

### Anbefalt arbeidsflyt

1. Bekreft `SAIV110 Surface logger` og gjeldende stoppstatus. Er loggeren i gang, stopp den og vent på `Surface-logger: Stopped`. Ikke send `I` blindt: fra stoppet tilstand starter den logging.
2. Sørg for at firmware har frigitt disken og at vertens diskvisning er oppdatert. Etter logging kan eksplisitt disk-refresh være nødvendig før verten kan skrive. Bruk firmwaremenyens `F` og bekreftelsesdialog når den tilbys, eller etablert refresh/gjentilkobling, og vent til disk og CDC er tilbake.
3. Finn loggerens faktiske monteringspunkt, og les hele `config/system.ini`. Ta vare på originalinnholdet for gjenoppretting.
4. Endre kun `[surface].intervalSeconds`, for eksempel til `10`. Valider at verdien er et heltall i støttet område.
5. Skriv og lukk filen, og flush til disk. En vellykket filskriving er ikke det samme som at loggerens aktive innstillinger er endret. Appen venter 10 sekunder etter skriving før normal innlesing.
6. Fra bekreftet Surface-kontekst send rå `U` («Update config»). Dette utfører lokal **MIR + APPLY**: konfigurasjonen leses/valideres og tas i bruk/lagres i NVS.
7. Fortsett å lese gjennom pauser og mellomresultater. Vent på den eksplisitte sluttmarkøren **`OK SAIV110_UPDATE_CONFIG`**, eller en eksplisitt feil. Et foreløpig MIR/APPLY-OK eller stillhet er ikke nok.
8. Kontroller intervallet mot fersk konfigurasjons-/statusavlesning der firmware viser det. Tilbakeavlesning av filen alene bekrefter bare diskverdien; den må kombineres med vellykket APPLY. Ved behov kan en kontrollert ny loggesesjon bekrefte tidsavstanden mellom målinger.
9. La loggeren være stoppet etter konfigurasjonen, med mindre brukeren også har bedt om å starte. Surface bruker et fast konfigurasjonsøyeblikksbilde gjennom sesjonen; endringen skal være ferdig før neste start.

Eksempel på programlogikk:

```text
bekreft Surface + Stopped
bekreft skrivbar, oppdatert USB-disk
les system.ini
oppdater surface.intervalSeconds = 10
skriv, lukk, flush; vent på at filendringen er tilgjengelig
send U
les til OK SAIV110_UPDATE_CONFIG eller feil/tidsfrist
kontroller ny verdi; behold stoppet tilstand
```

### Feilsituasjoner

- Ved «USB disk needs refresh» må disktilgangen oppdateres, filen leses og ønsket endring skrives/flushes på nytt før nytt innlesingsforsøk. Ikke gjenta `U` ubegrenset mot utdatert vertscache.
- Under logging avviser firmware konfigurasjonsoppdateringen; stopp først.
- Firmware 0.9.9Q avviser samtidig `[surface] enable=1` og `[instrument0] enable=1`. Ved dette avviket er konfigurasjonen ikke anvendt; ikke rapporter at intervallet er endret.
- Ikke omgå valideringsfeil eller formater disken for å løse en intervallfeil. Vis firmwarefeilen og behold originalfilen tilgjengelig.

## Kilder i prosjektet

- [SD200-valgkoder, verdier og parser](../shared/core/instrument/intervals.cpp)
- [SD200-intervalldialog og timing](../shared/app/workflows/process_flows.inl)
- [Surface-konfigurasjon og verdiområde](../shared/core/instrument/osu_disk_manifest.cpp)
- [Filskriving, flush, U og gjenoppretting](../shared/app/workflows/osu107_actions.inl)
- [Surface-navn og USB-status](../osu107Doc/HANDOVER_2026-08-26_SURFACE_USB_DTR_SOFTWARE_INTEGRATION.md)
- [Intervall, sesjoner og diskeierskap](../osu107Doc/HANDOVER_2026-08-28_INTERVAL_POWER_PREHEAT.md)
- [Lokal U-oppdatering](../osu107Doc/HANDOVER_2026-09-07_HIDDEN_UPDATE_CONFIG.md)
- [Q-validering av gjensidig utelukkende modi](../osu107Doc/HANDOVER_2026-09-07_LOCAL_CLOCK.md)
- [Surface U-test og nødvendig sluttmarkør](../osu107Doc/SURFACE_TEST_2026-09-07.md)
