import { labelFromFamilyMemberOption, labelFromOncologySiteOption } from '../data/familyOncologyOptions'

function kinshipDisplayForRelative(r) {
  if (!r.kinship) return 'Nie wybrano'
  if (r.kinship === 'inne') {
    return r.kinshipCustom?.trim() ? `Inne: ${r.kinshipCustom.trim()}` : 'Inne (uzupełnij dopisek)'
  }
  return labelFromFamilyMemberOption(r.kinship)
}

function siteLineDisplay(s) {
  if (!s.site) return null
  if (s.site === 'inne') {
    const t = s.siteCustom?.trim()
    const base = t ? `Inne: ${t}` : 'Inne (uzupełnij)'
    return s.ageAtDiagnosis?.trim() ? `${base}, wiek ${s.ageAtDiagnosis}` : base
  }
  const base = labelFromOncologySiteOption(s.site)
  return s.ageAtDiagnosis?.trim() ? `${base} (wiek ${s.ageAtDiagnosis})` : base
}

const hypertensionLabels = {
  no: 'Nie',
  yes_controlled: 'Tak — leczę, pod kontrolą',
  yes_uncontrolled: 'Tak — bez stałego leczenia lub niepewna kontrola',
}

const cholesterolLabels = {
  no: 'Nie / nie badano',
  yes: 'Tak',
  unknown: 'Nie wiem',
}

const tri = {
  '0-1': '0–1 dni',
  '2-3': '2–3 dni',
  '4-7': '4–7 dni',
}

const veg = {
  rare: 'Rzadko',
  sometimes: 'Czasami',
  daily: 'Prawie codziennie',
}

const fast = {
  rare: 'Rzadko',
  weekly: 'Kilka razy w tygodniu',
  often: 'Często',
}

const alcohol = {
  none: 'Nie piję',
  occasional: 'Okazjonalnie',
  weekly: 'Regularnie',
}

const tobacco = {
  never: 'Nie palę / nie używam',
  past: 'Palenie w przeszłości',
  current: 'Obecnie palę / e-papieros',
}

const yn = { no: 'Nie', yes: 'Tak' }

/**
 * @returns {{ label: string, value: string }[]}
 */
export function getSurveySummaryItems(form) {
  const p = form.pesel?.replace(/\D/g, '') || ''
  const items = []

  items.push({ label: 'Imię i nazwisko', value: `${form.firstName || '—'} ${form.lastName || ''}`.trim() || '—' })
  items.push({ label: 'PESEL', value: p.length === 11 ? p : form.pesel || '—' })
  items.push({ label: 'E-mail', value: form.email?.trim() || '—' })
  if (form.phone?.trim()) items.push({ label: 'Telefon', value: form.phone.trim() })

  items.push({
    label: 'Pomiary',
    value: [form.heightCm && `${form.heightCm} cm`, form.weightKg && `${form.weightKg} kg`, form.waistCm && `talia ${form.waistCm} cm`]
      .filter(Boolean)
      .join(', ') || '—',
  })

  items.push({ label: 'Aktywność (×/tydz.)', value: tri[form.activityDays] || '—' })
  items.push({ label: 'Warzywa i owoce', value: veg[form.vegetablesFreq] || '—' })
  items.push({ label: 'Fast food / ultra-przetworzone', value: fast[form.fastFoodFreq] || '—' })

  items.push({ label: 'Alkohol', value: alcohol[form.alcohol] || '—' })
  items.push({ label: 'Tytoń / nikotyna', value: tobacco[form.tobacco] || '—' })

  items.push({ label: 'Nadciśnienie', value: hypertensionLabels[form.hypertension] || '—' })
  if (form.hypertension === 'yes_controlled') {
    const bp = [form.hypertensionBpSystolic, form.hypertensionBpDiastolic].filter(Boolean).join('/')
    items.push({
      label: 'Ciśnienie (ostatni pomiar)',
      value: bp ? `${bp} mmHg` : '—',
    })
    if (form.hypertensionTherapyNote?.trim()) {
      items.push({ label: 'Leki na nadciśnienie', value: form.hypertensionTherapyNote.trim() })
    }
  }
  items.push({ label: 'Cholesterol / lipidy', value: cholesterolLabels[form.cholesterolHistory] || '—' })
  if (form.cholesterolHistory === 'yes' && form.cholesterolDetails?.trim()) {
    items.push({ label: 'Wyniki lipidów (wpis)', value: form.cholesterolDetails.trim() })
  }

  items.push({
    label: 'Nowotwór w bliskiej rodzinie',
    value: form.familyOncology === 'yes' ? 'Tak' : form.familyOncology === 'no' ? 'Nie / nie wiem' : '—',
  })
  if (form.familyOncology === 'yes' && Array.isArray(form.familyOncologyRelatives)) {
    form.familyOncologyRelatives.forEach((rel, i) => {
      const n = form.familyOncologyRelatives.length > 1 ? ` (osoba ${i + 1})` : ''
      items.push({ label: `Pokrewieństwo${n}`, value: kinshipDisplayForRelative(rel) })
      const siteLines = rel.sites?.map(siteLineDisplay).filter(Boolean) ?? []
      items.push({
        label: `Nowotwory / narządy${n}`,
        value: siteLines.length ? siteLines.join(' · ') : '—',
      })
      if (rel.notes?.trim()) items.push({ label: `Uwagi do osoby${n}`, value: rel.notes.trim() })
    })
    if (form.familyOncologyDetails?.trim()) {
      items.push({ label: 'Uwagi ogólne (historia rodzinna)', value: form.familyOncologyDetails.trim() })
    }
  }

  items.push({ label: 'Ból klatki / duszność (ostatnie tygodnie)', value: yn[form.chestPainRecent] || '—' })
  items.push({ label: 'Nieplanowana utrata masy', value: yn[form.weightLossUnplanned] || '—' })

  return items
}
