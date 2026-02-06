# LOINC Release Notes — wersja 2.81 i archiwum

Źródło: `https://loinc.org/kb/loinc-release-notes/`

---

Knowledge Base – LOINC

[NOW AVAILABLE: LOINC version 2.81](https://loinc.org/news/loinc-version-2-81-release-highlights/)

# LOINC Release Notes

This section last updated: 2025-08-27 (5 months ago)

## Version 2.81, August 2025

Table of contents:

- RELMA Changes
- Updates
- Parts
- Panels and forms
- Component Hierarchy By System
- LOINC Universal lab orders value set
- LOINC/RSNA radiology playbook
- LOINC/IEEE medical device code mapping table
- Linguistic variants
- Imaging document codes
- Groups
- Document ontology OWL
- Document ontology
- Consumer names
- Change snapshot
- Answer lists
- LOINC table
- LOINC table core
- [Special Workgroups](https://loinc.org/workgroups/)

## LOINC table core

There were no structural changes to the core table in this release, and no future changes to announce at this time. See the Readme included in the LOINC Table Core download file for information about its current file structure.

See the LOINC table notes below for information on content updates included in this release.

## LOINC table

### Numbers

#### New Concepts and totals by type

| Type | New concepts | Total |
| --- | --- | --- |
| Laboratory (type 1) | 3282 | 66,497 |
| Clinical (type 2) | 190 | 28,073 |
| Attachments (type 3) | 0 | 1,161 |
| Survey (type 4) | 104 | 12,517 |
| Total | 3576 | 108,248 |

#### Totals by Status

| Status | Number of concepts |
| --- | --- |
| Active | 96241 |
| Deprecated | 4957 |
| Discouraged | 1590 |
| Trial | 5460 |

#### Concept Status changes

| Old Status | New Status | Number of concepts | Type |
| --- | --- | --- | --- |
| Active | Deprecated | 8 | Type 1 |
| Trial | Discouraged | 85 | Type 2 |
| Active | Discouraged | 3 | Type 2 |
| Discouraged | Active | 2 | Type 1 |
| Trial | Active | 262 | Type 2 |
| Discouraged | Deprecated | 1 | Type 2 |
| Active | Discouraged | 1 | Type 1 |

#### Edits by change type

| Change type (field name CHNG_TYP) | CHNG_TYP definition | Number of concepts |
| --- | --- | --- |
| NAM | Component update | 85 |
| MAJ | Update to one of 5 other primary axes other than Component | 68 |
| MIN | Update to a secondary field - see Updates file Readme for the full list | 438 |
| DEL | Status changed to Deprecated | 9 |
| UND | Status changed from Deprecated to Active | 0 |
| PANEL | Change in the child elements or conditionality of one or more child elements in the panel or a sub-panel contained in the panel | 47 |
| Total | 647 |

### Content highlights

A summary of changes and additions to LOINC concepts is no longer included within these release notes. Instead, please refer to the [LOINC version 2.81 release announcement](https://loinc.org/news/loinc-version-2-81-release-highlights/) for this information. Notable terminology and technical changes specific to individual release artifacts and accessory files follow below.

We also encourage you to review guidance regarding the [LABORDERS.ONTOLOGY concepts](https://loinc.org/kb/users-guide/new-orderable-grouper-concepts) added in the version 2.81 release.

## (pozostała część sekcji 2.81)

Poniżej zapisano opis zmian strukturalnych i treściowych dla poszczególnych artefaktów dystrybucji LOINC (Answer Lists, Change Snapshot, Consumer Names, Document Ontology, Groups, Imaging Document Codes, Linguistic Variants, LOINC IEEE Medical Device Code Mapping Table, LOINC RSNA Radiology Playbook, LOINC Universal Lab Orders Value Set, Component Hierarchy By System, Panels and Forms, Parts, Updates, RELMA Changes). Treść odpowiada sekcji „LOINC Release Notes” na stronie źródłowej i opisuje:

- brak zmian strukturalnych w wielu plikach przy dodaniu nowej treści,
- status alfa/beta wybranych artefaktów (np. Consumer Names, Document Ontology OWL, Groups),
- znane problemy (np. dotyczące pól VersionEffective, PartSequenceOrder),
- aktualizacje i nowo dodane językowe warianty terminów.

---

## Knowledge Base — Release Notes Archive

Na końcu strony znajduje się lista linków do archiwalnych wydań:

- [LOINC Release Notes, June 2020 (Version 2.68) & earlier](https://loinc.org/kb/release-notes-archive/archive)
- [LOINC Release Notes, December 2020 (Version 2.69)](https://loinc.org/kb/release-notes-archive/2.69)
- [LOINC Release Notes, June 2021 (Version 2.70)](https://loinc.org/kb/release-notes-archive/2.70)
- [LOINC Release Notes, August 2021 (Version 2.71)](https://loinc.org/kb/release-notes-archive/2.71)
- [LOINC Release Notes, February 2022 (Version 2.72)](https://loinc.org/kb/release-notes-archive/2.72)
- [LOINC Release Notes, August 2022 (Version 2.73)](https://loinc.org/kb/release-notes-archive/2.73)
- [LOINC Release Notes, February 2023 (Version 2.74)](https://loinc.org/kb/release-notes-archive/2.74)
- [LOINC Release Notes, August 2023 (Version 2.75)](https://loinc.org/kb/release-notes-archive/2.75)
- [LOINC Release Notes, September 2023 (Version 2.76)](https://loinc.org/kb/release-notes-archive/2.76)
- [LOINC Release Notes, February 2024 (Version 2.77)](https://loinc.org/kb/release-notes-archive/2.77)
- [LOINC Release Notes, August 2024 (Version 2.78)](https://loinc.org/kb/release-notes-archive/2.78)
- [LOINC Release Notes, February 2025 (Version 2.79)](https://loinc.org/kb/release-notes-archive/2.79)
- [LOINC Release Notes, February 2025 (Version 2.80 Hotfix)](https://loinc.org/kb/release-notes-archive/2.80)

