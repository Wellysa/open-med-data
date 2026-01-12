# Plan Scrapowania Clinical Tables Search Service (NLM)

## Status Obecny
✅ **Już mamy:**
- ICD-10-CM (w `nlm/docs/` jako markdown)
- LOINC (skrypty: `download_loinc.py`, `download_all_loinc.py`)
- HCPCS (skrypt: `crawl_cms_hcpcs.py`)
- Genes/HGNC (skrypt: `download_nlm_genes.py`)

---

## Proponowana Kolejność Scrapowania

### FAZA 1: Małe tabele referencyjne (łatwe, szybkie)
**Priorytet: WYSOKI** - Podstawowe tabele referencyjne, małe rozmiary

1. **UCUM** (759 rekordów)
   - API: `/api/ucum/v3/search`
   - Rozmiar: ~759 rekordów
   - Czas: ~5-10 minut
   - Uwagi: Mała tabela, łatwa do pobrania w jednym zapytaniu

2. **Cytogenetic locations** (862 rekordy)
   - API: `/api/cytogenetic_locs/v3/search`
   - Rozmiar: ~862 rekordy
   - Czas: ~5-10 minut
   - Uwagi: Mała tabela, podstawowa dla genomiki

3. **PharmVar Star Alleles** (1,019 rekordów)
   - API: `/api/star_alleles/v3/search`
   - Rozmiar: ~1,019 rekordów
   - Czas: ~10 minut
   - Uwagi: Ważne dla farmakogenomiki

4. **Prescribable drug ingredients** (2,329 rekordów)
   - API: `/api/drug_ingredients/v3/search`
   - Rozmiar: ~2,329 rekordów
   - Czas: ~15 minut
   - Uwagi: Podzbiór RxTerms/RxNorm

5. **RxTerms drug names & strength lists** (9,366 rekordów)
   - API: `/api/rxterms/v3/search`
   - Rozmiar: ~9,366 rekordów
   - Czas: ~30-45 minut
   - Uwagi: Wymaga strategii paginacji (limit 7,500)

---

### FAZA 2: Średnie tabele kliniczne (ważne, umiarkowany rozmiar)
**Priorytet: WYSOKI** - Kluczowe tabele diagnostyczne i proceduralne

6. **ICD-9-CM diagnoses** (14,567 rekordów)
   - API: `/api/icd9cm_dx/v3/search`
   - Rozmiar: ~14,567 rekordów
   - Czas: ~1-2 godziny
   - Uwagi: Wymaga strategii wielokrotnego pobierania (limit 7,500)

7. **ICD-9-CM procedures** (3,882 rekordy)
   - API: `/api/icd9cm_sg/v3/search`
   - Rozmiar: ~3,882 rekordy
   - Czas: ~30 minut
   - Uwagi: Łatwe do pobrania

8. **ICD-11 (Codes)** (34,194 rekordy)
   - API: `/api/icd11_codes/v3/search`
   - Rozmiar: ~34,194 rekordy
   - Czas: ~2-3 godziny
   - Uwagi: Wymaga strategii wielokrotnego pobierania

9. **Medical conditions** (2,418 rekordów)
   - API: `/api/conditions/v3/search`
   - Rozmiar: ~2,418 rekordów
   - Czas: ~20 minut
   - Uwagi: Regenstrief Institute derivative, ręcznie edytowane

10. **Major surgeries and implants** (284 rekordy)
    - API: `/api/procedures/v3/search`
    - Rozmiar: ~284 rekordy
    - Czas: ~10 minut
    - Uwagi: Bardzo mała, łatwa

---

### FAZA 3: Duże tabele ontologiczne (ważne, większe rozmiary)
**Priorytet: ŚREDNI-WYSOKI** - Ontologie i klasyfikacje medyczne

11. **Human Phenotype Ontology (HPO)** (19,903 rekordy)
    - API: `/api/hpo/v3/search`
    - Rozmiar: ~19,903 rekordy
    - Czas: ~2-3 godziny
    - Uwagi: Wymaga strategii wielokrotnego pobierania

12. **HCPCS** (8,628 rekordów) - ✅ JUŻ MAMY
    - Status: Już pobrane przez `crawl_cms_hcpcs.py`
    - Uwagi: Można zaktualizować do najnowszej wersji (październik 2025)

13. **ICD-10-CM** (74,719 rekordów) - ✅ JUŻ MAMY (wersja 2022)
    - Status: Już mamy w `nlm/docs/icd10cm-tabular-2022-April-1.md`
    - Uwagi: Można zaktualizować do wersji 2026 z API

14. **LOINC** (108,248 rekordów) - ✅ JUŻ MAMY
    - Status: Już pobrane przez `download_all_loinc.py`
    - Uwagi: Wersja 2.81 (2025-08-12), można zaktualizować

---

### FAZA 4: Tabele genomiki - średnie (ważne dla badań genetycznych)
**Priorytet: ŚREDNI** - Dane genetyczne i genomowe

15. **Genetic diseases** (46,108 rekordów)
    - API: `/api/disease_names/v3/search`
    - Rozmiar: ~46,108 rekordów
    - Czas: ~3-4 godziny
    - Uwagi: Podzbiór ClinVar, wymaga strategii wielokrotnego pobierania

16. **NCBI Genes** (193,685 rekordów)
    - API: `/api/ncbi_genes/v3/search`
    - Rozmiar: ~193,685 rekordów
    - Czas: ~6-8 godzin
    - Uwagi: Bardzo duża, wymaga zaawansowanej strategii

17. **RefSeq** (82,202 rekordy)
    - API: `/api/refseqs/v3/search`
    - Rozmiar: ~82,202 rekordy
    - Czas: ~4-5 godzin
    - Uwagi: Wymaga strategii wielokrotnego pobierania

18. **Genes (HGNC)** (44,695 rekordów) - ✅ JUŻ MAMY
    - Status: Już pobrane przez `download_nlm_genes.py`
    - Uwagi: Można zaktualizować do najnowszej wersji (2025-12-09)

---

### FAZA 5: Bardzo duże tabele genomiki (wymagają specjalnej strategii)
**Priorytet: ŚREDNI-NISKI** - Ogromne zbiory danych, wymagają specjalnego podejścia

19. **ClinVar Variants** (4,203,186 rekordów) ⚠️
    - API: `/api/variants/v4/search`
    - Rozmiar: ~4.2M rekordów
    - Czas: ~20-30 godzin (z przerwami)
    - Uwagi: 
      - Wymaga bardzo zaawansowanej strategii (limit 7,500)
      - Możliwe pobieranie po chromosomach/genach
      - Rozważyć pobieranie tylko części danych lub okresowe aktualizacje

20. **COSMIC Structural Genomic Rearrangements** (643,608 rekordów)
    - API: `/api/cosmic_struct/v3/search`
    - Rozmiar: ~643K rekordów
    - Czas: ~10-15 godzin
    - Uwagi: Wymaga strategii wielokrotnego pobierania

21. **dbVar** (49,186,082 rekordy) ⚠️⚠️
    - API: `/api/dbvar/v3/search`
    - Rozmiar: ~49M rekordów
    - Czas: ~200+ godzin (kilka dni)
    - Uwagi: 
      - **BARDZO DUŻA** - rozważyć czy potrzebna cała
      - Możliwe pobieranie tylko wybranych zakresów
      - Wymaga bardzo zaawansowanej strategii

22. **COSMIC** (88,392,165 rekordów) ⚠️⚠️⚠️
    - API: `/api/cosmic/v4/search`
    - Rozmiar: ~88M rekordów
    - Czas: ~350+ godzin (kilka tygodni)
    - Uwagi: 
      - **NAJWIĘKSZA TABELA** - rozważyć czy potrzebna cała
      - COSMIC ma własne licencje - sprawdzić przed pobieraniem
      - Możliwe pobieranie tylko wybranych genów/mutacji
      - Wymaga bardzo zaawansowanej strategii

---

### FAZA 6: Tabele NPI (bardzo duże, ale ważne dla praktyki)
**Priorytet: NISKI-ŚREDNI** - Dane o dostawcach usług medycznych

23. **NPI - organizations** (1,875,833 rekordy) ⚠️
    - API: `/api/npi_org/v3/search`
    - Rozmiar: ~1.8M rekordów
    - Czas: ~15-20 godzin
    - Uwagi: 
      - Wymaga strategii wielokrotnego pobierania
      - Możliwe pobieranie po stanach/specjalnościach
      - Dane są publicznie dostępne z CMS - rozważyć bezpośrednie pobieranie z CMS

24. **NPI - individuals** (7,072,969 rekordów) ⚠️⚠️
    - API: `/api/npi_idv/v3/search`
    - Rozmiar: ~7M rekordów
    - Czas: ~60-80 godzin (kilka dni)
    - Uwagi: 
      - **BARDZO DUŻA** - rozważyć czy potrzebna cała
      - Dane są publicznie dostępne z CMS - **ZALECANE: pobrać bezpośrednio z CMS**
      - CMS oferuje pełne pliki do pobrania (szybsze niż przez API)

25. **SNPs** (650,265,778 rekordów) ⚠️⚠️⚠️⚠️
    - API: `/api/snps/v3/search`
    - Rozmiar: ~650M rekordów
    - Czas: **NIEMOŻLIWE przez API** (kilka miesięcy)
    - Uwagi: 
      - **NAJWIĘKSZA TABELA** - praktycznie niemożliwe do pobrania przez API
      - **ZALECANE: pobrać bezpośrednio z dbSNP/NCBI**
      - NCBI oferuje pełne pliki do pobrania (szybsze i bardziej efektywne)

---

## Strategie Pobierania

### Dla tabel < 7,500 rekordów:
- Proste paginowanie (offset + count)
- Jedno lub kilka zapytań

### Dla tabel 7,500 - 50,000 rekordów:
- Strategia wielokrotnego pobierania:
  - Paginacja (do limitu 7,500)
  - Wyszukiwanie alfabetyczne (a*, b*, c*, ...)
  - Wyszukiwanie po kategoriach (jeśli dostępne)
  - Merge wyników

### Dla tabel > 50,000 rekordów:
- Zaawansowana strategia:
  - Wyszukiwanie po kategoriach/genach/chromosomach
  - Wyszukiwanie po zakresach dat
  - Wyszukiwanie po kodach/ID
  - Rozważyć alternatywne źródła danych (bezpośrednio od dostawcy)

### Dla tabel > 1M rekordów:
- **ZALECANE: Pobieranie bezpośrednio od źródła**
  - NPI → CMS (pełne pliki)
  - SNPs → NCBI dbSNP (pełne pliki)
  - COSMIC → Sanger Institute (wymaga licencji)
  - dbVar → NCBI (pełne pliki)

---

## Rekomendacje

1. **Zacznij od FAZY 1-2** - szybkie zwycięstwa, małe tabele
2. **FAZA 3** - ważne tabele ontologiczne
3. **FAZA 4** - tabele genomiki średnie
4. **FAZA 5-6** - rozważyć alternatywne źródła dla bardzo dużych tabel

5. **Dla bardzo dużych tabel (>1M rekordów):**
   - NPI → Pobierz bezpośrednio z CMS
   - SNPs → Pobierz bezpośrednio z NCBI dbSNP
   - COSMIC → Sprawdź licencję i pobierz bezpośrednio
   - dbVar → Pobierz bezpośrednio z NCBI

6. **Aktualizacje:**
   - Zaplanuj okresowe aktualizacje dla tabel, które już masz
   - Niektóre tabele aktualizowane są co miesiąc

---

## Szacowany Czas Całkowity

- **FAZA 1:** ~2-3 godziny
- **FAZA 2:** ~6-8 godzin
- **FAZA 3:** ~4-6 godzin (część już mamy)
- **FAZA 4:** ~13-17 godzin
- **FAZA 5:** ~380+ godzin (kilka tygodni) - **NIEZALECANE przez API**
- **FAZA 6:** ~75-100 godzin (kilka dni) - **NIEZALECANE przez API**

**Łącznie (FAZY 1-4):** ~25-34 godziny (1-2 dni pracy)

**FAZY 5-6:** Rozważyć alternatywne źródła danych

---

## Uwagi Techniczne

1. **Limit API:** 7,500 wyników (offset + count)
2. **Rate limiting:** Dodać opóźnienia między zapytaniami (1-2 sekundy)
3. **Retry logic:** Implementować retry z exponential backoff
4. **Error handling:** Logować błędy i kontynuować
5. **Progress tracking:** Zapisywać postęp dla długich operacji
6. **Deduplication:** Usuwać duplikaty przy merge wyników
7. **Storage:** Rozważyć kompresję dla dużych plików CSV

---

## Linki do Dokumentacji API

- Główna strona: https://clinicaltables.nlm.nih.gov/
- Dokumentacja API: https://clinicaltables.nlm.nih.gov/apidoc/{table}/v3/doc.html
- FAQ: https://clinicaltables.nlm.nih.gov/faq.html

---

## Alternatywne Źródła Danych

### NPI (National Provider Identifier)
- **CMS:** https://www.cms.gov/Regulations-and-Guidance/Administrative-Simplification/NationalProvIdentStand/DataDissemination.html
- Pełne pliki do pobrania (szybsze niż API)

### SNPs (dbSNP)
- **NCBI dbSNP:** https://www.ncbi.nlm.nih.gov/snp/
- Pełne pliki do pobrania (szybsze niż API)

### COSMIC
- **Sanger Institute:** http://grch37-cancer.sanger.ac.uk/cosmic
- Wymaga licencji - sprawdzić przed użyciem

### dbVar
- **NCBI dbVar:** https://www.ncbi.nlm.nih.gov/dbvar/
- Pełne pliki do pobrania

---

*Ostatnia aktualizacja: 2025-12-12*
