# Meedoen

Crisus.nl is satire, maar de feiten kloppen. Daar kunt u bij helpen.

**Welkom:**

- Een correctie: een feit dat niet (meer) klopt, een versie, een datum, een status.
  Zet de bron erbij: een advisory, een changelog, een nieuwsbericht.
- Een bron die ontbreekt.
- Een fout in de HTML, de toegankelijkheid of de tooling in `tools/`.
- Een site op het statusbord die terug is of er juist uit ligt, met wat er op die site staat.

**Liever niet:**

- Grappen zonder feit erachter. De grappen staan er al genoeg in.
- Exploitcode, links naar exploits of aanwijzingen hoe je een lek misbruikt.
- Iets over welke servers van wie (on)gepatcht zijn.

**Zo werkt het:**

- Tijdens een crisus werkt een script de pagina elk uur bij en commit het direct op `main`.
  Een pull request kan daardoor achterlopen. Dat is geen probleem: de beheerder merget
  met de hand en lost het op.
- De checks in `.github/workflows/check.yml` draaien ook op uw pull request: REUSE, de
  HTML, de feed, de CSP-regels (geen inline script of style) en de ankers. Draai ze
  gerust lokaal: `python3 -I tools/check-html.py site/index.html` en `reuse lint`.
- Teksten en plaatjes zijn CC BY 4.0, code is MIT. Met een pull request gaat u ermee
  akkoord dat uw bijdrage onder dezelfde licentie valt.

Een beveiligingsprobleem in de site zelf? Meld het niet in een openbaar issue, maar via
een [private security advisory](https://github.com/annejan/crisus/security/advisories/new).
