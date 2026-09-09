# Klokkesetting: OSU107, SD200 (SD204/SD208) og SAIV110

Implementasjonsbeskrivelse for et annet program. Gjelder gjeldende dokumenterte firmware, 0.9.9Q for OSU107/SAIV110, og prosjektets SD204/SD208-protokoll. Kontrollert mot lokale kilder 9. september 2026. Eksemplene er protokollillustrasjoner, ikke nye målinger på instrument.

## Velg riktig klokke og metode

| Mål | Metode | Datoformat på forbindelsen |
| --- | --- | --- |
| SD204/SD208, instrumentets egen klokke | Instrumentets hovedmeny → `S` | `YY-MM-DD-HH-MM-SS` |
| OSU107/SAIV110, loggerens egen klokke | Direkte `X` | `YY-MM-DD-HH-MM-SS` |
| Loggerens RTC gjennom administrasjonsmenyen | Ctrl+T → hovedmeny → `RTC` → `SET` | `YYYY-MM-DD HH:MM:SS` |

OSU107 kan ha et tilkoblet SD200-instrument med en separat klokke. `X` setter bare loggerklokken. `S` i SD200-hovedmenyen setter instrumentklokken. Ikke rapporter begge som synkronisert etter bare én av operasjonene.

Direkte `X` er felles for OSU107 Instrument Logger og SAIV110 Surface Logger.

## Seriekommunikasjon og tilstand

- Bruk det oppdagede instrumentets port og baudrate. Ikke hardkod en COM-port. OSU-testverktøyet bruker som standard 9600 baud, 8 databiter, ingen paritet, 1 stoppbit.
- Ctrl+T er én rå byte `0x14`, ikke teksten `Ctrl+T`. Enter er `CR`, byte `0x0D`; Esc er `0x1B`; Backspace er `0x08`.
- Enkeltkommandoer som `X`, `S`, `Y` og `N` sendes uten Enter når ikke annet er angitt. RTC-tekstkommandoer avsluttes med `\r`.
- Stopp logging og vent på bekreftet stopp før klokkesetting. Identifiser aktuell meny før sending. På SAIV110 starter/stopper `I` logging; den skal ikke brukes som generell vekkesekvens.
- Samle mottatte fragmenter til hele forventede prompten foreligger. Ikke bruk en kort pause i mottaket som bevis på at dialogen er ferdig. Ha tidsfrister og begrensede forsøk.

## Metode 1: direkte X på OSU107 og SAIV110

Denne metoden krever ikke Ctrl+T. OSU107 kan ta imot `X` lokalt også når det eksterne instrumentet sover eller mangler. Et aktivt instrument-undermenyfelt kan eie tastene; avslutt dette før lokal klokkesetting.

1. Send rå `X`.
2. Vent på `Format: YY-MM-DD-HH-MM-SS`. Dersom `X` avvises, stopp uten å sende dato eller vilkårlige returtaster til en ukjent meny.
3. Beregn ønsket klokkeslett først nå, og send for eksempel `26-09-09-14-30-00\r`. Hele feltet kan sendes samlet i denne lokale dialogen. År 00–99 betyr 2000–2099; valider faktisk kalenderdato og klokkeslett.
4. **Enter setter klokken med en gang:** ekstern RV3028 oppdateres og intern nRF-klokke synkroniseres.
5. Vent på hele tidssonespørsmålet, for eksempel `Current timezone is (LT) change to GMT? (Y/N)`.
6. Send `N` hvis gjeldende etikett er ønsket, ellers `Y`. Spørsmålet kan også gå motsatt vei, fra GMT til LT.
7. Vent på sluttbekreftelse eller kjent menyhint. En observert bekreftelse er `OK: logger clock 2026-09-07 17:35:33 LT`.

**Y/N endrer bare den lagrede LT/GMT-etiketten, ikke timetallet.** For GMT må programmet allerede ha sendt et GMT/UTC-klokkeslett. For LT sendes lokal tid. Dette prosjektet beregner GMT ved å trekke valgt GMT-offset fra PC-lokaltid; ikke hardkod samme offset gjennom sommer- og vintertid.

Eksempel: sette lokal tid når loggeren allerede står i LT:

```text
TX: X
RX: Format: YY-MM-DD-HH-MM-SS
TX: 26-09-09-14-30-00<CR>
RX: Current timezone is (LT) change to GMT? (Y/N)
TX: N
RX: sluttbekreftelse / menyhint
```

### Avslutning, avbrudd og kontroll

- OSU107 bruker `G`/`g` for retur; Surface bruker Esc. Ikke send automatisk `G` etter vellykket `X`: dette kan vekke eller spørre det eksterne instrumentet.
- OSU107 viser `<G> for Menu` når dialogen er avsluttet innen 60 sekunder, ellers `Hold I to wake instrument`. SAIV110 kan vise `<ESC> Menu:` eller returnere Surface-menyen.
- Avbrudd før Enter endrer ikke tiden. Avbrudd eller tidsavbrudd etter Enter beholder den nye tiden og gjeldende tidssoneetikett. Firmware-dialogen har 120 sekunders inaktivitetstimeout; appens utveksling har 8 sekunders frist per steg.
- Ved manglende tidssoneprompt etter datoen: opplys at tiden kan være skrevet. Etter bekreftet lokal formatdialog kan `G` (OSU107) eller Esc (Surface) brukes til avslutning. Les klokken før nytt forsøk.
- Gjør en separat avlesning av loggerstatus for uavhengig kontroll. Sammenlign dato, tid og LT/GMT med forventet tid ved avlesning. En skrivebekreftelse alene er ikke uavhengig tilbakeavlesning.
- Ny USB-status kan gi `Date/time: YYYY-MM-DD HH:MM:SS (LT|GMT)`. Ved kontroll gjennom lukking/gjenåpning av CDC ble 750 ms mellomrom brukt i prosjektets Surface-test; umiddelbar gjenåpning kunne gi bare en blank linje.

## Metode 2: via Ctrl+T og RTC-menyen

Dette er administrasjonsveien til loggerens RTC. Bekreft administrasjonsmenyen og `[RTC]>` før sending. Kildegrunnlaget viser RTC-sekvensen for OSU107, men dokumenterer ikke en tilsvarende aktuell Surface-test av Ctrl+T/RTC. For SAIV110 er direkte `X` bekreftet. Et annet program må derfor behandle Ctrl+T/RTC på SAIV110 som menyavhengig, ikke som ubetinget verifisert støtte.

1. Send rå Ctrl+T (`0x14`). Dette kan først stoppe direkte instrumentkommunikasjon uten å vise hovedmenyen.
2. Les svaret. Ved behov bruker prosjektets OSU-testsekvens Backspace og `M\r`; deretter `Q\r` og `M\r` som begrenset gjenoppretting hvis menyen fortsatt mangler. Ikke send hele sekvensen blindt.
3. Bekreft loggerens administrasjonshovedmeny. OSU-koden kjenner blant annet `Menu: OSU-107`, `System voltage:` og `RTC RV-3028:`.
4. Send `RTC\r`, og vent på `[RTC]>`.
5. Send `GMT LOCAL\r` for LT eller `GMT GMT\r` for GMT. Les tilbake `GMT=0` henholdsvis `GMT=1` når dette tilbys.
6. Send `SET 2026-09-09 14:30:00\r`, med ønsket klokkeslett i valgt tidssone. Denne veien bruker firesifret år, mellomrom mellom dato/tid og kolon i tiden.
7. Send `SHOW\r`. Kontroller avlest RTC mot ønsket tidspunkt og se etter `RTC updated` i svaret fra skrivingen.
8. Send `Q\r`. OSU-flyten krever `Direct instrument communication: REACTIVATED`; hvis svaret fortsatt er RTC-prompt, tillates ett nytt `Q\r`. For Surface må avslutningen bekreftes mot menyen/statusen som faktisk tilbys i den modusen; ikke tolk manglende CTD-reaktivering alene som mislykket tidssetting.

Den eksisterende OSU-appen beregner tidsstempelet like før `SET` og legger til ett sekund. Et nytt program bør måle sin egen forsinkelse og kontrollere resultatet, fremfor å anta at samme tillegg passer alle forbindelser.

## SD200: sette klokken i SD204/SD208

Start fra bekreftet **SD200-hovedmeny**, også når forbindelsen går gjennom OSU107. Fra vekkesiden går prosjektets flyt via `S` til status, deretter `M` til hovedmeny. Fra ukjent undermeny brukes tilstandsbasert `G`/eventuelt `N` for å komme tilbake. Avslutt en pågående måling først.

1. Send `S` fra hovedmenyen.
2. Vent på klokkeendringsspørsmålet `Change: Y/N`; send `Y` uten Enter.
3. Vent på `Format: YY-MM-DD-HH-MM-SS`.
4. Send for eksempel `26-09-09-14-30-00` **tegnvis**, med omtrent 60 ms mellom tegn og synkronisering mot ekko. Avslutt med `\r`. Den raske, samlede `X`-overføringen skal ikke overføres ukritisk til SD200.
5. Vent på GMT/LT-spørsmålet. Send `N` hvis gjeldende tidssone er riktig, ellers `Y`.
6. Vent på hovedmenyen.
7. Åpne igjen med `S`, svar `N` på endringsspørsmålet og kontroller avlest `Date ...` / `Time ... LT|GMT`.

Ved syntaksfeil eller ulovlig dato: vent på riktig formatprompt før et begrenset nytt forsøk. Rapporter feil hvis dato, tid eller sone ikke stemmer ved kontroll. Beregn toleranse ut fra overføringstiden; tegnvis overføring tar merkbar tid.

### Egen operasjon: synkronisere OSU107 fra CTD

OSU107 har også `Q` i brukervalgene for synkronisering **fra CTD til logger**. Gå til riktig brukermeny, send `Q`, vent på synkroniseringsspørsmålet og svar `Y`. Vent på eksplisitt vellykket synkronisering og endelig CTD-meny; appen bruker inntil 25 sekunder.

Dette er en separat operasjon etter eventuell SD200-klokkesetting. Den er ikke lokal PC-til-logger-setting og er ikke tilgjengelig i Surface-modus. `Q` betyr avslutning i RTC-administrasjonsmenyen, så menykonteksten er avgjørende.

## Kilder i prosjektet

- [Lokal klokke, firmwarekontrakt](../osu107Doc/HANDOVER_2026-09-07_LOCAL_CLOCK.md)
- [Gjeldende app-integrasjon](../osu107Doc/APP_Q_HANDOVERS_2026-09-07.md)
- [Surface-test og tilbakeavlesning](../osu107Doc/SURFACE_TEST_2026-09-07.md)
- [Lokal X-dialog](../shared/core/instrument/logger_clock.hpp)
- [OSU-klokke, RTC og CTD-synkronisering](../shared/app/workflows/osu107_actions.inl)
- [SD200-klokkeflyt](../shared/app/workflows/process_flows.inl)
- [Instrumentets meny- og klokkeregler](../INSTRUMENT_BEHAVIOR.md)
- [OSU RTC-testverktøy](../tests/osu_clock_set_check.py)
