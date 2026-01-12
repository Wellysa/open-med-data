# NLM Clinical Tables - Pobrane Dane

Ten folder zawiera dane pobrane z NLM Clinical Tables Search Service API.

## Status Pobierania

### ✅ FAZA 1 - Małe tabele referencyjne (UKOŃCZONA)

| Tabela | Plik | Rekordy | Status |
|--------|------|---------|--------|
| UCUM | `ucum.csv` | 759/759 | ✅ 100% |
| Cytogenetic locations | `cytogenetic_locations.csv` | 862/862 | ✅ 100% |
| PharmVar Star Alleles | `pharmvar_star_alleles.csv` | 970/1019 | ✅ 95% |
| Drug ingredients | `drug_ingredients.csv` | 2329/2329 | ✅ 100% |
| RxTerms | `rxterms.csv` | 8760/9366 | ✅ 94% |

### ✅ FAZA 2 - Średnie tabele kliniczne (UKOŃCZONA)

| Tabela | Plik | Rekordy | Status |
|--------|------|---------|--------|
| ICD-9-CM diagnoses | `icd9cm_diagnoses.csv` | 14567/14567 | ✅ 100% |
| ICD-9-CM procedures | `icd9cm_procedures.csv` | 3882/3882 | ✅ 100% |
| ICD-11 Codes | `icd11_codes.csv` | 31041/34194 | ✅ 91% |
| Medical conditions | `medical_conditions.csv` | 2418/2418 | ✅ 100% |
| Major surgeries and implants | `major_surgeries_implants.csv` | 284/284 | ✅ 100% |

## Statystyki

- **Łączna liczba plików CSV:** 10
- **Łączna liczba rekordów:** ~73,000+
- **Łączny rozmiar:** ~2.5 MB
- **Data pobrania:** 2026-01-09

## Uwagi

- **ICD-11 Codes:** Pobrano 31,041 zamiast 34,194 rekordów (91%) - prawdopodobnie limit API
- **RxTerms:** Pobrano 8,760 zamiast 9,366 rekordów (94%) - prawdopodobnie limit API
- **PharmVar Star Alleles:** Pobrano 970 zamiast 1,019 rekordów (95%) - prawdopodobnie limit API

## Źródło

Wszystkie dane zostały pobrane z:
- **API:** https://clinicaltables.nlm.nih.gov/
- **Skrypt:** `download_clinical_table.py`
- **Data:** 2026-01-09

## Następne Kroki

Zgodnie z planem (`scraping_plan_clinicaltables.md`), następne do pobrania:
- **FAZA 3:** Human Phenotype Ontology (HPO) - 19,903 rekordy
- **FAZA 4:** Tabele genomiki (Genetic diseases, NCBI Genes, RefSeq, etc.)

## Struktura Folderu

```
nlm/
├── *.csv                    # Pobrane tabele CSV
├── docs/                    # Dokumenty NLM (ICD-10-CM, etc.)
└── README.md                # Ten plik
```
