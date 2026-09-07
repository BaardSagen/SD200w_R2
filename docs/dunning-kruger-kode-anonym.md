# Erfaringsnotat: Langvarig systemvedlikehold og kompetanserisiko

Dette dokumentet er bevisst anonymisert for ekstern deling. Det beskriver erfaringer fra et langvarig vedlikeholds- og utviklingsarbeid på et eldre, innebygd system, med fokus på observerte arbeidsmønstre, risikoer og anbefalte tiltak.

## Sammendrag (kort)
- Koden bærer preg av copy?paste uten analytisk modellering eller systematisk forbedring.
- Tekniske og organisatoriske valg indikerer Dunning?Kruger-mønstre: høy selvsikkerhet, lav reell kompetanseutvikling.
- Forveksling av eierskap/ansiennitet med ledelses- og fagekspertise skaper styringsproblemer.
- Konsekvensene er lav endringshastighet, vedlikeholdsrisiko, og sårbarhet ved nøkkelperson-avhengighet.
- Anbefalingene omfatter enkle prosessforbedringer, tydelig rolleavklaring og gradvis teknisk gjeldsnedbygging.

## Kontekst (anonymisert)
- Systemtype: Eldre, innebygd styringssystem, lavnivå/assembly-nær kodebasis.
- Organisasjon: Liten virksomhet med få utviklere og stor historisk personavhengighet.
- Tidslinje: Lang periode med kontinuerlig vedlikehold og små endringer.

## Tekniske observasjoner
- Kontrollflyt: Utstrakt bruk av hopp-kjeder og spesialhåndtering fremfor tabell-/datadrevet logikk.
- Gjenbruk: Copy?paste av kodeblokker uten konsolidering i felles rutiner.
- Navngiving og konstanter: «Magic numbers» og sparsommelig bruk av symbolske konstanter/etiketter.
- Struktur: Manglende modulære grenser og få veldefinerte grensesnitt mellom deler av systemet.
- Kvalitetssikring: Svak dokumentasjon, få/ingen enkle test- eller verifikasjonsrutiner.
- Sum: Koden fungerer, men er vanskelig å forstå, endre og validere uten uforholdsmessig risiko.

## Organisatoriske observasjoner
- Rollenivå: Overvekting av «leder»-titler i en liten organisasjon skaper byråkrati uten merverdi.
- Styringsgrunnlag: Eierskap/ansiennitet blandes med faglig beslutningsmyndighet og lederkompetanse.
- Arbeidsflyt: Hyppige avbrytelser, urealistiske tidsestimater og «hurtig-løsninger» presser ut god engineering.
- Konflikthåndtering: Formelle prosesser tas i bruk uten reell forståelse av konsekvenser eller målbilder.

## Psykologiske mønstre (Dunning?Kruger kort forklart)
- Personer med lav/utdatert kompetanse kan overvurdere egen evne, undervurdere andres, og mangle verktøy for selvevaluering.
- I praksis ses dette som sterk selvsikkerhet, motstand mot læring og preferanse for kjente (men svake) mønstre.

## Risikobilde
- Nøkkelperson-avhengighet (bus factor): Kritisk kunnskap er ikke dokumentert eller delt.
- Feilintroduksjon: Copy?paste uten abstraksjon forplanter feil og teknisk gjeld.
- Vedlikeholdshastighet: Små endringer krever stor mental last og regresjonsfare.
- Omdømme/kunde: Ustrukturert kommunikasjon og løfter kan gi leveranse- og tillitsutfordringer.

## Anbefalinger (lav risiko, høy nytte)
- Roller og beslutninger
  - Skil mellom eierskap og leder-/fagkompetanse i beslutningslinjer.
  - Formaliser ansvar for kodekvalitet, endringsstyring og akseptkriterier.
- Arbeidsprosesser
  - Innfør lette kodegjennomganger (to-par øyne) og korte status-/planmøter.
  - Etabler enkel endringslogg med estimat, risiko, teststeg og «definition of done».
  - Reduser avbrudd: Tidsbokser fokusperioder og avtal faste sjekktidspunkter.
- Teknikk og kvalitet
  - Begynn med mikrouttrekk: Konsolider 1?2 gjentatte mønstre til felles rutiner per iterasjon.
  - Innfør symbolske konstanter og tabell-/datadrevet logikk der det er trygt.
  - Skriv mini-testrutiner for kritiske baner (selv manuelt skript er bedre enn ingenting).
  - Lag «runbook» for bygg/flash/diagnose og legg i repo.
- Kunnskap og kultur
  - Rotasjonsordning på oppgaver for å spre kunnskap.
  - Kort opplæring i estimering, feilhåndtering og grunnleggende designprinsipper.
  - Belønn forbedringer (små refaktoreringer) i stedet for kun «hurtig-fiks».

## Hva man kan måle (enkle indikatorer)
- Andel endringer som gjenbruker felles rutiner fremfor ny copy?paste.
- Antall «magic numbers» som erstattes av navngitte konstanter per sprint.
- Tid brukt på avbrudd vs fokus (selvrapportert) og andel endringer med test-/sjekkliste.
- Antall personer som kan bygge/flash/teste systemet uten hjelp.

## Avslutning
Dette notatet beskriver observerte mønstre som ofte oppstår i langvarige vedlikeholdsmiljøer. Tiltakene over er bevisst små og praktiske. Poenget er å redusere sårbarhet, øke forutsigbarhet og gradvis betale ned teknisk gjeld ? uten store reorganiseringer eller teknologiskifte.

---

Kort definisjon: Dunning?Kruger-effekten beskriver tendensen til at personer med lav kompetanse overvurderer egne ferdigheter og ikke ser sine begrensninger.

## Kilder og referanser (åpne kilder)
- Kruger, J., & Dunning, D. (1999). Unskilled and unaware of it: How difficulties in recognizing one?s own incompetence lead to inflated self-assessments. Journal of Personality and Social Psychology, 77(6), 1121?1134. doi:10.1037/0022-3514.77.6.1121
- Stripe (2018). The Developer Coefficient ? How software can drive growth in the 21st century. https://stripe.com/reports/developer-coefficient-2018
- SEI/CMU (Software Engineering Institute). What is Technical Debt? (blog/overview). https://insights.sei.cmu.edu/blog/what-is-technical-debt/
- Ward Cunningham Wiki. Technical Debt (original metaphor discussion). https://wiki.c2.com/?TechnicalDebt
- HBR (2013). The Price of Incivility (Porath & Pearson) ? om kostnader ved ufin kultur. https://hbr.org/2013/01/the-price-of-incivility
- Wikipedia. Bus factor ? konsept for nøkkelperson-avhengighet. https://en.wikipedia.org/wiki/Bus_factor