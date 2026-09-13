# Firmwarekanal

Servermappe: `https://saiv.no/software/firmware/osu107_saiv110/hw_3-1-2/`.

1. readme.txt er ferdigstilt av firmwareagenten. Kontroller at den lastes opp med n?yaktig navnet `readme.txt`, som i latest.json.
2. Legg den signerte BIN-filen og ferdig readme.txt pÃ¥ serveren.
3. Last opp `latest.json` sist, nÃ¥r begge filene er tilgjengelige.

BIN-filen som allerede ligger pÃ¥ den oppgitte URL-en ble lest via HTTPS 13. september 2026: HTTP 200, 635 580 byte, MCUboot-header `3db8f396`, SHA-256 `3e6840e8a3ea84564b635fbcf20e6b6ece48b86551226d14bf2f259bfb30b47c`. latest.json peker pÃ¥ denne eksakte filen. Dette bekrefter nedlasting og filhash, ikke at en fysisk oppdatering virker.

Alle JSON-verdiene er strenger. `filename` skal vÃ¦re et enkelt filnavn, uten mappe eller URL. Versjonen i `version` mÃ¥ stemme med endingen i filnavnet. `hardware` mÃ¥ stemme med bÃ¥de filnavnet og enheten. Bokstavrevisjoner sammenlignes uten forskjell pÃ¥ smÃ¥/store bokstaver. SHA-256 er obligatorisk og mÃ¥ beregnes pÃ¥ nytt hvis BIN-filen byttes, ogsÃ¥ nÃ¥r bare signeringen endres.

PÃ¥ serveren beholdes hele filnavnet. PÃ¥ enheten skriver SIT den som `update\osu_m_update.bin`, slik brukeren har bekreftet. Ingen serveropplasting er utfÃ¸rt her. Dette er en separat kanal fra SIT-programmets `https://saiv.no/software/latest.json`.

Oppdatert prosedyre fra handover 13. september: regenerer bare `config/system.ini` etter verifisert firmwareoppdatering. Behold alle andre config-filer og kalibrering. Enheten fjerner BIN-filen selv; SIT kan fors?ke ?n ekstra reset hvis update-mappen ikke er tom.

Serverkontroll: BIN og latest.json var tilgjengelige; manifestet pekte p? README.txt mens serverfilen heter readme.txt. Lokalt latest.json er rettet. Last opp den rettede latest.json p? nytt f?r test.

Ny kontroll etter brukerens opplasting: latest.json peker n? p? readme.txt. Alle tre serverfiler svarer HTTP 200, manifest/readme matcher lokal pakke og BIN er byteidentisk med korrekt SHA-256. Serverrettelsen er fullf?rt; fysisk oppdatering er ikke startet.
