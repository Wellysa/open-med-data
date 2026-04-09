/**
 * Listy do ankiety — choroby onkologiczne w rodzinie.
 * Podmień wartości, gdy dostaniesz oficjalną listę od medycznego / NFZ.
 */

export const FAMILY_MEMBER_OPTIONS = [
  { value: '', label: '— wybierz z listy —' },
  { value: 'matka', label: 'Matka' },
  { value: 'ojciec', label: 'Ojciec' },
  { value: 'siostra', label: 'Siostra' },
  { value: 'brat', label: 'Brat' },
  { value: 'babcia_matki', label: 'Babcia (linia matki)' },
  { value: 'dziadek_matki', label: 'Dziadek (linia matki)' },
  { value: 'babcia_ojca', label: 'Babcia (linia ojca)' },
  { value: 'dziadek_ojca', label: 'Dziadek (linia ojca)' },
  { value: 'ciotka', label: 'Ciotka' },
  { value: 'wujek', label: 'Wujek' },
  { value: 'corka', label: 'Córka' },
  { value: 'syn', label: 'Syn' },
  { value: 'inne', label: 'Inne pokrewieństwo — doprecyzuj poniżej' },
]

export const ONCOLOGY_SITE_OPTIONS = [
  { value: '', label: '— wybierz z listy —' },
  { value: 'piers', label: 'Piersi' },
  { value: 'jajnik', label: 'Jajniki' },
  { value: 'macica', label: 'Macica / endometrium' },
  { value: 'jelito_grube', label: 'Jelito grube / odbytnica' },
  { value: 'zoladek', label: 'Żołądek' },
  { value: 'prostata', label: 'Gruczoł krokowy (prostata)' },
  { value: 'pluca', label: 'Płuca' },
  { value: 'wtroba', label: 'Wątroba' },
  { value: 'trzustka', label: 'Trzustka' },
  { value: 'nerka', label: 'Nerka' },
  { value: 'pecherz', label: 'Pęcherz moczowy' },
  { value: 'tarczyca', label: 'Tarczyca' },
  { value: 'skora_czerniak', label: 'Skóra (czerniak)' },
  { value: 'mozg', label: 'Ośrodkowy układ nerwowy (mózg)' },
  { value: 'bialczak_chloniak', label: 'Białaczka / chłoniak' },
  { value: 'inny_niepewny', label: 'Inny typ / nie znam szczegółów' },
  { value: 'inne', label: 'Inny narząd / opis — wpisz poniżej' },
]

export function labelFromFamilyMemberOption(value) {
  const o = FAMILY_MEMBER_OPTIONS.find((x) => x.value === value)
  return o ? o.label.replace(' — doprecyzuj poniżej', '') : value || '—'
}

export function labelFromOncologySiteOption(value) {
  const o = ONCOLOGY_SITE_OPTIONS.find((x) => x.value === value)
  return o ? o.label.replace(' — wpisz poniżej', '') : value || '—'
}

function newLocalId(prefix) {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) return `${prefix}-${crypto.randomUUID()}`
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

/** Jedna choroba / narząd u danej osoby (wiek opcjonalnie — przy wielu nowotworach może się różnić). */
export function createEmptyOncologySiteRow() {
  return { id: newLocalId('site'), site: '', siteCustom: '', ageAtDiagnosis: '' }
}

/** Jedna osoba z listą nowotworów. */
export function createEmptyFamilyOncologyRelative() {
  return {
    id: newLocalId('rel'),
    kinship: '',
    kinshipCustom: '',
    sites: [createEmptyOncologySiteRow()],
    notes: '',
  }
}

export function resolveKinshipForApi(kinship, kinshipCustom) {
  if (!kinship) return undefined
  if (kinship === 'inne') return kinshipCustom?.trim() || undefined
  return labelFromFamilyMemberOption(kinship)
}

export function resolveSiteForApi(site, siteCustom) {
  if (!site) return undefined
  if (site === 'inne') return siteCustom?.trim() || undefined
  return labelFromOncologySiteOption(site)
}
