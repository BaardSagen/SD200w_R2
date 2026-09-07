# Lederoppsummering (1 side)

Denne siden gir et raskt, ikke-teknisk overblikk for beslutningstakere. Fokus er risiko, tiltak og effekt ? uten å endre teknologi eller organisasjonskart.

## Hvor står vi nå?
- Kode og praksis bærer preg av copy?paste, lite modellering og svak dokumentasjon.
- Endringer går sakte og med høy risiko fordi samme mønstre gjentas og feil forplanter seg.
- Personavhengighet (bus factor) er høy: få kan bygge, teste og forklare helheten.

## Hva er risikoen?
- Leveranser: Små endringer kan velte store tidsplaner (regresjon, feilretting).
- Kvalitet/omdømme: Uklare prosesser gir variable resultater og usikker kundedialog.
- Kontinuitet: Fravær/avgang hos nøkkelpersoner stopper arbeidet.

## Hva bør vi gjøre (neste 4?8 uker)?
- Roller/ansvar
  - Skill eierskap fra faglige beslutninger i daglig drift.
  - Utpek en «kodekvalitetsansvarlig» med myndighet til å si stopp.
- Arbeidsprosesser
  - Innfør to-par-øyne-kodegjennomgang på alle endringer > 30 linjer.
  - Definer «definition of done»: endringslogg, teststeg, og kort dokumentasjon.
  - Tidsbokser fokusperioder (2×90 min daglig) for å redusere avbrytelser.
- Teknikk (lav risiko)
  - Erstatt 5?10 «magic numbers» pr. uke med navngitte konstanter.
  - Konsolider 1?2 gjentatte kodeblokker til felles rutiner pr. iterasjon.
  - Skriv mini-testrutiner for 2 kritiske baner (bygge/flash-sjekk inkludert).
- Kunnskap
  - Lag en 1-sides «runbook» for bygg/flash/diagnose og legg i repo.
  - Roter oppgaver for å spre kunnskap (minst 2 personer kan hver kjerneoppgave).

## Hva måles (enkle indikatorer)
- Andel endringer som gjenbruker felles rutiner (> 60% innen 2 måneder).
- Antall «magic numbers» erstattet (mål: 50+ på 8 uker).
- Antall personer som kan bygge/flash/teste uten hjelp (mål: ? 3).
- Endringslogg-etterlevelse (mål: 100%).

## Forventet effekt (0?3 måneder)
- Lavere regresjonsrate, raskere kodegjennomganger, mindre personrisiko.
- Bedre forutsigbarhet i leveranser og tydeligere ansvarslinjer.

## Kilder (kort)
- SEI/CMU: Technical debt ? begrepsrammeverk.
- Kruger & Dunning (1999): Overvurdering vs. reell kompetanse.
- Stripe (2018): Developer Coefficient ? tid tapt på gjeld/vedlikehold.
