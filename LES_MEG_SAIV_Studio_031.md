# SAIV Studio 0.3.1 – rettet oppstartsvisning

Kjør `SAIV_Studio_v0.3.1_Sept2026.exe`.

0.3.0 presset terminalen sammen til en smal stripe ved vanlig oppstart uten måledata. En ubetinget SameLine før valgfrie overskriftsknapper flyttet også arbeidsområdet til høyre. SameLine brukes nå bare når en knapp faktisk skal vises.

Feilen er gjenskapt i bevart 0.3.0. 0.3.1 er åpnet normalt uten demodata eller testtransport og visuelt kontrollert ved 1180×780, 920×600 og 1450×900. Terminalfeltet fyller nå venstresiden. Demovisning er også kontrollert. Alle tre CTest-grupper består (182 + 50 + 932 kontroller).

Ingen instrumentport er åpnet under testen. Endringen gjelder oppstartsoppsett og versjonsmerking. Øvrig funksjonsstatus og begrensninger står i `saiv-studio/docs/FUNKSJONSSTATUS.md`.

Tidligere EXE/ZIP og 0.3.0-kilde er beholdt. Kildearkiv: `analysis/reference/saiv_studio_v030`. Bygg: `saiv-studio/build.cmd`. Skjermbilder og regresjonsrapport: `saiv-studio/test-results/v031`.
