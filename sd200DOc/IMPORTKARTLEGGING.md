# Kartlegging av dataimport – 8. september 2026

Historisk kartlegging med utgangspunkt i SAIV Instrument Terminal 1.1.3. Import er nå implementert i 1.2.0; se `../LES_MEG_Import_CSV_TXT.md`. Eksempelfilene er urørt.

| Fil | Format | Målinger | Innhold |
|---|---|---:|---|
| `26090606_18.11.51.txt` | APB5-metadata + gamle N-linjer | 43 | S, T, P, OX, OF, OT |
| `2026_09_03_20-28-52_C.txt` | OSU107 med FIELDS og semikolon | 79 | COUNT, C, T, P, OF, Par, OxR, Tilt, DATE, TIME |
| `2026_09_07_19-34-42_C.txt` | SAIV110 SurfaceLogger med FIELDS | 3 | COUNT, Par, OxR, Tilt, DATE, TIME |
| `test.SD2` + `.RF2` + `.OP2` | Gammelt binært datasett | 7 | CTD og to ekstraverdier i dette eksemplet |
| `test.txt` | Eksport: List, semikolon, desimalkomma | 7 | Ser, Meas, Sal., Cond., Temp, F, T, Density, S. vel., Press, Date, Time |

Brukeren opplyser at test ble laget fra APB5. Filene som ble analysert er likevel ikke identiske måleserier: APB5-hodet sier Ser No 1237 og dato 2026-09-06, mens test sier instrument 1756 og dato 1997-04-11. Dette må ikke brukes som en sammenligning av like måleverdier. Eksporten og binærfilene i test samsvarer i radantall og undersøkte felt.

## Hvorfor en ny importgren trengs

APB5 bruker instrumentets gamle tekstformat, med Date/Time, instrumenthode og merkede N-linjer. Loggerfilene har egne innledninger og en FIELDS-linje som bestemmer kolonnenavn og rekkefølge. Surface-eksemplet inneholder ingen CTD. Det er derfor utilstrekkelig bare å fjerne loggerhodet eller legge til N foran radene.

Original hendelse `mnuImportASCIIClick` ligger på 0x5A593C og kaller filinnlesing på 0x5A5F40. Innlesingen har eksisterende grener for blant annet `burst data` og `Station no:` og et generelt forløp via 0x54953C. Dette er et utgangspunkt for videre sporing, ikke en fullstendig analyse av parseren. Utdrag: `analysis/ascii_import_disassembly.txt`.

## Regler for neste implementering

- Gjenkjenn OSU107 og SAIV110(S-L), og les kolonnene fra FIELDS. Ikke anta fast rekkefølge eller at alle loggerfiler har CTD.
- Behold alle måleverdier og sensornavn. Manglende CTD må ikke bli oppdiktede nullmålinger eller grunnlag for beregnet salinitet/lydhastighet.
- Bruk DATE/TIME fra hver loggerrad. I OSU-eksemplet er første avstand 4 sekunder, deretter 2 sekunder. Et fast interval på 2 sekunder vil endre tidspunktene.
- Behold loggerens LT og CTD-hodets GMT som separate metadata. CTD-hodet 18:29:02 GMT og første loggerrad 20:28:52 LT er ikke bare samme tidspunkt skrevet med to timers forskjell. Ingen skjult tidskorreksjon.
- Behold serienummer for både logger og CTD; OSU-eksemplet sier logger 107 og CTD 1240.
- Ikke gjenbruk F/OT-kolonner til Par/OxR/Tilt med feil etikett eller enhet. Sensorene er identifisert som Biospherical PAR og RINKO III. Se SENSORKALIBRERING_IMPORT.md; brukeren avklarte senere at normal OxR-inngang er prosent og at Par skal beholdes uendret.
- Gammel APB5-import og tre-filformatet må fortsatt virke. Nye filer må ikke overskrive originalene.

## Kontrollverktøy

`python analysis/map_import_formats.py` leser eksemplene og lager `analysis/import_format_inventory.json` med hashes, filhoder, kolonner, radantall, tidssteg og første/siste rad. Loggerkolonner valideres som endelige tall og gyldige dato/tidspunkter. Binæreksemplet undersøkes mot eksportverdier. Observasjonen 52 byte hode + 52 byte per SD2-rad og 8 byte per OP2-rad gjelder dette eksemplet; det er ikke dokumentasjon for alle historiske varianter.
