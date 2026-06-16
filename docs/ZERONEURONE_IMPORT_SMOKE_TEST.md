# ZeroNeurone import smoke test

Compatibility target checked on 2026-06-15:

- ZeroNeurone source version: 2.41.9
- import documentation version: 2.19.0
- documented formats: GraphML and unified CSV
- native archive structure reference: user-supplied ZeroNeurone `1.1.0`
  dossier export inspected on 2026-06-15

## Preconditions

1. Open an active Synthesix investigation containing:
   - one saved page;
   - one validated entity;
   - one rejected entity;
   - one evidence capture.
2. Generate a default ZeroNeurone export.
3. Generate another export with both optional checkboxes enabled.

## Native ZIP import

1. In ZeroNeurone, import `zeroneurone.zip`.
2. Confirm that the dossier opens without invalid element, link, or asset
   references.
3. Verify:
   - elements are arranged in readable type columns;
   - every link resolves through `fromId` and `toId`;
   - recognized Synthesix aliases use exact ZeroNeurone TagSet names:
     `Person`/`Personne` becomes `Personne`, `Company`/`Organisation` becomes
     `Entreprise`, while custom tags remain unchanged;
   - the first recognized analyst TagSet controls the exported native visual;
   - all 26 built-in ZeroNeurone 2.41.9 TagSets are available as Synthesix tag
     suggestions on investigations, saved pages, and extracted entities;
   - the investigation root displays only its title and is visually identifiable
     as the large central hexagon at the graph origin;
   - when explicit investigation entities exist, linked saved pages appear as
     source properties rather than URL or domain nodes;
   - extracted SIREN/SIRET values attached to a company appear as properties on
     that company;
   - standalone date candidates use the `Événement` TagSet;
   - person, company, site, account, search, and evidence elements use distinct
     shapes, colors, or icons;
   - URL elements expose `URL`, `Domaine`, and `Date d'accès` properties;
   - the default archive contains no evidence assets.
4. Import the explicit full export and verify that evidence files appear as
   assets attached to their evidence elements.

## GraphML import

1. In ZeroNeurone, create an empty investigation.
2. Choose **Import** and select `investigation.graphml`.
3. Confirm that the preview reports no invalid node or link references.
4. Place the imported graph.
5. Verify:
   - the investigation and saved page are present;
   - the validated entity is linked with `MENTIONS`;
   - the rejected entity is absent from the default export;
   - search provenance uses `FOUND_BY`;
   - every relationship is directed and labelled;
   - coordinates appear on the entity when applicable.

## CSV import

1. Create another empty ZeroNeurone investigation.
2. Import `zeroneurone.csv`.
3. Verify that both `element` and `lien` rows are accepted.
4. Confirm that source and target labels resolve without missing links.

## Explicit options

Import the second native ZIP and GraphML export and verify:

- proposed and rejected candidates are included;
- evidence nodes and `CAPTURED_AS` links are included;
- evidence files appear as native assets only in this explicit export.

Record the tested ZeroNeurone version and any importer warning in the release
notes before marking manual compatibility as validated.
