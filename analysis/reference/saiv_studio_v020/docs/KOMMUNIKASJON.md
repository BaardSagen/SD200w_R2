# Kommunikasjon og programvareparitet

8N1 og 7E1 bruker begge ti bit per tegn inkludert start/stopp. For valgt 7E1 åpnes Windows-porten fysisk som **8N1**. Ved mottak maskeres bit 7 med `& 0x7f`; paritetsfeil kontrolleres ikke. Ved sending kodes even-paritet i bit 7. Vanlig 8N1 går uendret. Instrumentets og PC-ens baudrate må samsvare. Innstillingen Even + 7 bits er den logiske instrumentprotokollen, ikke fysisk UART-konfigurasjon.

Detect prøver 9600 med begge logiske formater. Satt åttende bit i første 8N1-forsøk går videre til programvareparitet; dette alene er ikke positiv identifikasjon. En kjent meny, målerad eller loggeridentitet må fortsatt finnes. Ved valg av funnet resultat overføres port og logisk paritet til forbindelsen. Andre baudrater kan velges manuelt.

Søket lytter først. G brukes for å spørre en stille port før I-vekkeforsøk. I gjentas bare mens ingen tekst mottas. S brukes fra gjenkjent oppstartsmeny, M fra gjenkjent status/start-meny. Gjenkjent hovedmeny eller måling avslutter søket. Ingen start-, slette- eller kalibreringskommando hører til Detect. Ny kommando venter minst 250 ms etter siste mottatte tekst. Ukjent/uavsluttet tekst sperrer blind videre vekking.

Første oppstartsmeny kan automatisk starte etter ti sekunder. I betyr vekking, start eller intervall avhengig av tilstand; M betyr hovedmeny eller koeffisienter. Menugjenkjenning er derfor nødvendig også når baud og paritet er riktige. Ikke legg tilbake en fast blind kommando-sekvens.

Fysiske mottak 8. september: COM7 ga paritetskodede CTD N-rader ved 9600 8N1 og lesbare rader ved 9600 7E1. COM11 er OSU107; COM18 har ikke instrument. Disse portnumrene er kun testmiljø. Et nytt aktivt søk ble stoppet av automatisk godkjenningskontroll. Full fysisk test av siste programvareparitetsbygg gjenstår. Ingen aktiv sending ble brukt for å omgå dette.

Registrerte mottaksfiler inneholder datapayload etter eventuell fjerning av programvareparitetsbit. Dette er ikke et rått elektrisk opptak. Bruk alltid sikkerhetskopi og kontroller instrumentresultater.
