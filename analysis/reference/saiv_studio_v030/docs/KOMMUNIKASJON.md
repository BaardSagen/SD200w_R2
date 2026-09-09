# Kommunikasjon – Studio 0.3.0

7E1 settes faktisk i UART: syv databiter, even-paritet og én stoppbit. `GetCommState` leser innstillingen tilbake. Adaptere som avviser dette gir feil; ingen overgang til softwareparitet foretas. Tidligere softwareparitetskode er fjernet.

Autodetect prøver 9600/8N1 og 9600/7E1, lytter og gjenkjenner komplette instrumentmenyer eller loggeridentitet. Valgt port og innstillinger brukes ved tilkobling. Andre baudrater velges i Setup. Søk sender ikke start-, slette- eller kalibreringskommandoer.

Terminal-/downloadprotokollen venter minst 250 ms etter mottatt tekst. S brukes fra oppstartsmeny, M fra status. G undersøker en stille port; avgrenset I-vekking brukes bare uten mottatt tekst, med minst 50 ms mellom I. Delvis/ukjent meny tillater ikke blind videre vekking. Avslutt et automatisk forløp med Cancel før manuell terminaltasting.

Download sender F. Et komplett Refresh disk Y/N besvares med ett Y. Feil, manglende bekreftelse og timeout vises. SD200-data og terminaltekst beholdes. Loggerfiler kopieres fra USB-disken under Instrument > Logger files.

Interval og TIME/DATE krever valgt Autodetect-resultat og aktiv forbindelse. Protokollkoden fra SIT bruker komplett respons, mottaksro og tilbakeavlesning. Klokkeekko håndteres tegnvis med egne ventetider. Innstillingsjobben kjører i bakgrunnen med eksklusiv bruk av serialtransporten; terminalkommandoer sperres under jobben. Loggerstatus kan kreve kontrollert gjenåpning av porten, med ny kontroll av identitet og serienummer.

SD200-intervallet settes fra den annonserte menyen og leses tilbake. SD200-klokken skrives én gang med tidskompensasjon. OSU107 setter SD200- og loggerklokken separat. Surface stoppes før klokke/intervall; intervallet endres i valgt USB `config/system.ini`, med sikkerhetskopi, flush, venting og bekreftet U/APPLY.

GUI-testen bruker filtransport og sender ikke til fysisk instrument. Fysisk akseptanse av Studio 0.3.0 gjenstår. Tidligere fysiske SIT-resultater gjelder den utgaven og kan ikke automatisk overføres til Studio.
