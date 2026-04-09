import { useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { ChevronLeft, ChevronRight, Loader2, Plus, Trash2 } from 'lucide-react'
import ModalShell from './ModalShell'
import TurnstileField from '../TurnstileField'
import { submitLandingSurvey, isDemo } from '../../lib/adminApi'
import { isTurnstileConfigured, isTurnstileDevTestKey } from '../../lib/turnstileConfig'
import { saveLandingIdentity } from '../../lib/identityStorage'
import {
  FAMILY_MEMBER_OPTIONS,
  ONCOLOGY_SITE_OPTIONS,
  createEmptyFamilyOncologyRelative,
  createEmptyOncologySiteRow,
  resolveKinshipForApi,
  resolveSiteForApi,
} from '../../data/familyOncologyOptions'
import { getSurveySummaryItems } from '../../lib/surveySummary'

const initialForm = {
  firstName: '',
  lastName: '',
  pesel: '',
  email: '',
  phone: '',
  heightCm: '',
  weightKg: '',
  waistCm: '',
  activityDays: '',
  vegetablesFreq: '',
  fastFoodFreq: '',
  alcohol: '',
  tobacco: '',
  hypertension: '',
  hypertensionBpSystolic: '',
  hypertensionBpDiastolic: '',
  hypertensionTherapyNote: '',
  cholesterolHistory: '',
  cholesterolDetails: '',
  familyOncology: '',
  familyOncologyRelatives: [],
  familyOncologyDetails: '',
  chestPainRecent: '',
  weightLossUnplanned: '',
  consentRodo: false,
  consentMarketing: false,
}

const STEP_LABELS = [
  'Dane i kontakt',
  'Pomiary',
  'Ruch i jedzenie',
  'Alkohol i tytoń',
  'Serce i metabolizm',
  'Nowotwory w rodzinie',
  'Objawy alarmowe',
  'Podsumowanie',
]

function validEmail(s) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s)
}

export default function MojeZdrowieSurveyModal({ open, onClose }) {
  const [step, setStep] = useState(0)
  const [form, setForm] = useState(initialForm)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState(null)
  const [turnstileToken, setTurnstileToken] = useState('')
  const [turnstileMountId, setTurnstileMountId] = useState(0)
  const turnstileRef = useRef(null)

  useEffect(() => {
    if (!open) return
    setStep(0)
    setMessage(null)
    let id = null
    try {
      id = JSON.parse(localStorage.getItem('wellysa_landing_identity') || 'null')
    } catch {
      id = null
    }
    setForm({
      ...initialForm,
      firstName: id?.firstName || '',
      lastName: id?.lastName || '',
      pesel: id?.pesel || '',
      email: id?.email || '',
      phone: id?.phone || '',
      familyOncologyRelatives: [createEmptyFamilyOncologyRelative()],
    })
    setTurnstileToken('')
  }, [open])

  useEffect(() => {
    if (!open || step !== 7) return
    setTurnstileToken('')
    setTurnstileMountId((k) => k + 1)
  }, [open, step])

  useEffect(() => {
    if (form.familyOncology !== 'yes') return
    if (form.familyOncologyRelatives?.length) return
    setForm((f) => ({ ...f, familyOncologyRelatives: [createEmptyFamilyOncologyRelative()] }))
  }, [form.familyOncology, form.familyOncologyRelatives?.length])

  const update = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const patchRelative = (rid, patch) =>
    setForm((f) => ({
      ...f,
      familyOncologyRelatives: f.familyOncologyRelatives.map((r) => (r.id === rid ? { ...r, ...patch } : r)),
    }))

  const patchSite = (rid, sid, patch) =>
    setForm((f) => ({
      ...f,
      familyOncologyRelatives: f.familyOncologyRelatives.map((r) =>
        r.id !== rid
          ? r
          : { ...r, sites: r.sites.map((s) => (s.id === sid ? { ...s, ...patch } : s)) },
      ),
    }))

  const addRelative = () =>
    setForm((f) => ({
      ...f,
      familyOncologyRelatives: [...f.familyOncologyRelatives, createEmptyFamilyOncologyRelative()],
    }))

  const removeRelative = (rid) =>
    setForm((f) => ({
      ...f,
      familyOncologyRelatives:
        f.familyOncologyRelatives.length <= 1
          ? f.familyOncologyRelatives
          : f.familyOncologyRelatives.filter((r) => r.id !== rid),
    }))

  const addSiteRow = (rid) =>
    setForm((f) => ({
      ...f,
      familyOncologyRelatives: f.familyOncologyRelatives.map((r) =>
        r.id === rid ? { ...r, sites: [...r.sites, createEmptyOncologySiteRow()] } : r,
      ),
    }))

  const removeSiteRow = (rid, sid) =>
    setForm((f) => ({
      ...f,
      familyOncologyRelatives: f.familyOncologyRelatives.map((r) => {
        if (r.id !== rid) return r
        if (r.sites.length <= 1) return r
        return { ...r, sites: r.sites.filter((s) => s.id !== sid) }
      }),
    }))

  /** Wymagane tylko przy wysyłce (nawigacja między krokami jest dowolna). */
  const canSubmit = () => {
    if (!form.consentRodo) return false
    if (isTurnstileConfigured() && !turnstileToken) return false
    const p = form.pesel.replace(/\D/g, '')
    return (
      form.firstName.trim() &&
      form.lastName.trim() &&
      p.length === 11 &&
      validEmail(form.email.trim())
    )
  }

  const handleSubmit = async () => {
    setSaving(true)
    setMessage(null)
    const identity = {
      firstName: form.firstName.trim(),
      lastName: form.lastName.trim(),
      pesel: form.pesel.replace(/\D/g, ''),
      email: form.email.trim(),
      phone: form.phone.trim() || undefined,
    }
    const survey = {
      heightCm: Number(form.heightCm),
      weightKg: Number(form.weightKg),
      waistCm: Number(form.waistCm),
      activityDays: form.activityDays,
      vegetablesFreq: form.vegetablesFreq,
      fastFoodFreq: form.fastFoodFreq,
      alcohol: form.alcohol,
      tobacco: form.tobacco,
      hypertension: form.hypertension,
      hypertensionBpSystolic: form.hypertensionBpSystolic.trim() || undefined,
      hypertensionBpDiastolic: form.hypertensionBpDiastolic.trim() || undefined,
      hypertensionTherapyNote: form.hypertensionTherapyNote.trim() || undefined,
      cholesterolHistory: form.cholesterolHistory,
      cholesterolDetails: form.cholesterolDetails.trim() || undefined,
      familyOncology: form.familyOncology,
      ...(function () {
        const relativesPayload =
          form.familyOncology === 'yes'
            ? (form.familyOncologyRelatives ?? [])
                .map((r) => {
                  const kinship = resolveKinshipForApi(r.kinship, r.kinshipCustom)
                  const cancerSites = (r.sites ?? [])
                    .map((s) => {
                      const site = resolveSiteForApi(s.site, s.siteCustom)
                      if (!site) return null
                      return {
                        site,
                        ageAtDiagnosis: s.ageAtDiagnosis?.trim() || undefined,
                      }
                    })
                    .filter(Boolean)
                  const notes = r.notes?.trim() || undefined
                  if (!kinship && cancerSites.length === 0 && !notes) return null
                  return { kinship, cancerSites, notes }
                })
                .filter(Boolean)
            : undefined
        const first = relativesPayload?.[0]
        const firstSite = first?.cancerSites?.[0]
        return {
          familyOncologyRelatives: relativesPayload?.length ? relativesPayload : undefined,
          familyCancerKinship: first?.kinship,
          familyCancerSite: firstSite?.site,
          familyCancerAge: firstSite?.ageAtDiagnosis,
          familyOncologyDetails: form.familyOncology === 'yes' ? form.familyOncologyDetails.trim() || undefined : undefined,
        }
      })(),
      chestPainRecent: form.chestPainRecent,
      weightLossUnplanned: form.weightLossUnplanned,
      consentMarketing: form.consentMarketing,
    }
    try {
      await submitLandingSurvey(
        { identity, survey },
        isTurnstileConfigured() ? turnstileToken : undefined,
      )
      saveLandingIdentity(identity)
      setMessage(
        isDemo()
          ? 'Zapisano lokalnie (tryb demo). Ustaw VITE_ADMIN_API_BASE_URL, aby wysłać dane do panelu admina.'
          : 'Dziękujemy — dane zostały przekazane. Nasz zespół kontaktuje się na podany e-mail.',
      )
    } catch (e) {
      turnstileRef.current?.reset()
      setTurnstileToken('')
      setMessage(e.message || 'Błąd wysyłki. Spróbuj ponownie.')
    } finally {
      setSaving(false)
    }
  }

  const radioGroup = (name, label, options) => (
    <fieldset className="space-y-2">
      <legend className="mb-2 block text-sm font-medium text-charcoal">{label}</legend>
      <div className="space-y-2">
        {options.map((o) => (
          <label
            key={o.value}
            className={`flex cursor-pointer items-center gap-3 rounded-xl border px-4 py-3 text-sm ${
              form[name] === o.value ? 'border-wellysa-green bg-wellysa-green/10' : 'border-slate-200 hover:border-slate-300'
            }`}
          >
            <input
              type="radio"
              name={name}
              value={o.value}
              checked={form[name] === o.value}
              onChange={() => update(name, o.value)}
              className="h-4 w-4 border-slate-300 text-wellysa-green"
            />
            {o.label}
          </label>
        ))}
      </div>
    </fieldset>
  )

  const body = (
    <div className="space-y-6">
      <p className="rounded-xl bg-section px-4 py-3 text-xs leading-relaxed text-slate-600">
        Wzory pytań zbliżone do ankiety <strong>Profilaktyka 40+ / Moje Zdrowie w IKP</strong> (pomiary, styl życia,
        ryzyko sercowo‑naczyniowe, nowotwory w rodzinie) — układ i treść są uproszczone pod pre‑screening Wellysa.
        To <strong>nie</strong> zastępuje oficjalnego formularza NFZ.
      </p>

      <div className="flex flex-wrap gap-2 text-[11px] font-medium">
        {STEP_LABELS.map((lb, i) => (
          <button
            key={lb}
            type="button"
            onClick={() => {
              setStep(i)
              setMessage(null)
            }}
            className={`rounded-full px-2.5 py-1 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-wellysa-green focus-visible:ring-offset-2 ${
              i === step
                ? 'bg-wellysa-green text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {i + 1}. {lb}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={step}
          initial={{ opacity: 0, x: 8 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -8 }}
          transition={{ duration: 0.2 }}
          className="space-y-4"
        >
          {step === 0 ? (
            <>
              <div className="grid gap-3 sm:grid-cols-2">
                <label className="text-sm">
                  <span className="mb-1 block text-slate-600">Imię</span>
                  <input
                    value={form.firstName}
                    onChange={(e) => update('firstName', e.target.value)}
                    className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                    autoComplete="given-name"
                  />
                </label>
                <label className="text-sm">
                  <span className="mb-1 block text-slate-600">Nazwisko</span>
                  <input
                    value={form.lastName}
                    onChange={(e) => update('lastName', e.target.value)}
                    className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                    autoComplete="family-name"
                  />
                </label>
              </div>
              <label className="block text-sm">
                <span className="mb-1 block text-slate-600">PESEL</span>
                <input
                  inputMode="numeric"
                  maxLength={11}
                  value={form.pesel}
                  onChange={(e) => update('pesel', e.target.value.replace(/\D/g, '').slice(0, 11))}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                />
              </label>
              <label className="block text-sm">
                <span className="mb-1 block text-slate-600">E-mail (do panelu i kontaktu)</span>
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => update('email', e.target.value)}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                  autoComplete="email"
                />
              </label>
              <label className="block text-sm">
                <span className="mb-1 block text-slate-600">Telefon (opcjonalnie)</span>
                <input
                  type="tel"
                  value={form.phone}
                  onChange={(e) => update('phone', e.target.value)}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                />
              </label>
            </>
          ) : null}

          {step === 1 ? (
            <>
              <p className="text-sm text-slate-600">Jak w IKP — bez presji „na już”: dokładne pomiary pomagają ocenić ryzyko metaboliczne.</p>
              <div className="grid gap-3 sm:grid-cols-3">
                <label className="text-sm">
                  <span className="mb-1 block text-slate-600">Wzrost (cm)</span>
                  <input
                    type="number"
                    min={120}
                    max={230}
                    value={form.heightCm}
                    onChange={(e) => update('heightCm', e.target.value)}
                    className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                  />
                </label>
                <label className="text-sm">
                  <span className="mb-1 block text-slate-600">Masa (kg)</span>
                  <input
                    type="number"
                    min={30}
                    max={250}
                    value={form.weightKg}
                    onChange={(e) => update('weightKg', e.target.value)}
                    className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                  />
                </label>
                <label className="text-sm">
                  <span className="mb-1 block text-slate-600">Obwód talii (cm)</span>
                  <input
                    type="number"
                    min={50}
                    max={200}
                    value={form.waistCm}
                    onChange={(e) => update('waistCm', e.target.value)}
                    className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                  />
                </label>
              </div>
            </>
          ) : null}

          {step === 2 ? (
            <>
              {radioGroup('activityDays', 'Ile dni w tygodniu min. 30 min umiarkowanej aktywności?', [
                { value: '0-1', label: '0–1 dni' },
                { value: '2-3', label: '2–3 dni' },
                { value: '4-7', label: '4–7 dni' },
              ])}
              {radioGroup('vegetablesFreq', 'Warzywa i owoce — jak często?', [
                { value: 'rare', label: 'Rzadko (rzadziej niż 5 porcji tygodniowo)' },
                { value: 'sometimes', label: 'Czasami' },
                { value: 'daily', label: 'Prawie codziennie' },
              ])}
              {radioGroup('fastFoodFreq', 'Fast food / wysoko przetworzona żywność', [
                { value: 'rare', label: 'Rzadko' },
                { value: 'weekly', label: 'Kilka razy w tygodniu' },
                { value: 'often', label: 'Często' },
              ])}
            </>
          ) : null}

          {step === 3 ? (
            <>
              {radioGroup('alcohol', 'Alkohol', [
                { value: 'none', label: 'Nie piję' },
                { value: 'occasional', label: 'Okazjonalnie' },
                { value: 'weekly', label: 'Regularnie (co najmniej kilka razy w tygodniu)' },
              ])}
              {radioGroup('tobacco', 'Tytoń / nikotyna', [
                { value: 'never', label: 'Nie palę / nie używam' },
                { value: 'past', label: 'Palenie w przeszłości' },
                { value: 'current', label: 'Obecnie palę lub używam e-papierosa' },
              ])}
            </>
          ) : null}

          {step === 4 ? (
            <>
              <p className="text-sm leading-relaxed text-slate-600">
                Nadciśnienie i cholesterol wpływają na ryzyko sercowo‑naczyniowe — poniżej możesz doprecyzować to, co znasz z
                ostatniej rozmowy z lekarzem lub z wyników badań.
              </p>
              {radioGroup('hypertension', 'Czy kiedykolwiek zdiagnozowano u Ciebie nadciśnienie tętnicze?', [
                { value: 'no', label: 'Nie' },
                { value: 'yes_controlled', label: 'Tak — leczę i jest pod kontrolą (leki, pomiary domowe)' },
                { value: 'yes_uncontrolled', label: 'Tak — bez stałego leczenia lub niepewna kontrola' },
              ])}
              {form.hypertension === 'yes_controlled' ? (
                <div className="space-y-3 rounded-card border border-wellysa-green/20 bg-wellysa-green/10 p-4">
                  <p className="text-sm font-medium text-charcoal">Ostatni pomiar ciśnienia (mmHg)</p>
                  <p className="text-xs text-slate-500">Wpisz liczby tak, jak na ciśnieniomierzu — pola są opcjonalne, jeśli nie pamiętasz.</p>
                  <div className="grid grid-cols-2 gap-3 sm:max-w-md">
                    <label className="text-sm">
                      <span className="mb-1 block text-slate-600">Skurczowe („większa”)</span>
                      <input
                        type="text"
                        inputMode="numeric"
                        autoComplete="off"
                        value={form.hypertensionBpSystolic}
                        onChange={(e) =>
                          update('hypertensionBpSystolic', e.target.value.replace(/\D/g, '').slice(0, 3))
                        }
                        placeholder="np. 128"
                        className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                      />
                    </label>
                    <label className="text-sm">
                      <span className="mb-1 block text-slate-600">Rozkurczowe („mniejsza”)</span>
                      <input
                        type="text"
                        inputMode="numeric"
                        autoComplete="off"
                        value={form.hypertensionBpDiastolic}
                        onChange={(e) =>
                          update('hypertensionBpDiastolic', e.target.value.replace(/\D/g, '').slice(0, 3))
                        }
                        placeholder="np. 82"
                        className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                      />
                    </label>
                  </div>
                  <label className="block text-sm">
                    <span className="mb-1 block text-slate-600">Leki / schemat dawkowania (opcjonalnie)</span>
                    <input
                      value={form.hypertensionTherapyNote}
                      onChange={(e) => update('hypertensionTherapyNote', e.target.value)}
                      placeholder="np. Enarenal 5 mg rano"
                      className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                    />
                  </label>
                </div>
              ) : null}
              {radioGroup(
                'cholesterolHistory',
                'Czy powiedziano Ci kiedyś o zbyt wysokim cholesterolu lub innych nieprawidłowych lipidach (np. LDL, trójglicerydy)?',
                [
                  { value: 'no', label: 'Nie / nie badano' },
                  { value: 'yes', label: 'Tak' },
                  { value: 'unknown', label: 'Nie wiem' },
                ],
              )}
              {form.cholesterolHistory === 'yes' ? (
                <div className="space-y-2 rounded-card border border-wellysa-green/20 bg-wellysa-green/10 p-4">
                  <p className="text-sm font-medium text-charcoal">Znasz ostatnie wyniki? (opcjonalnie)</p>
                  <label className="block text-sm">
                    <span className="mb-1 block text-xs text-slate-500">
                      Możesz wpisać liczby z laboratorium albo skrót od lekarza — jednym polem.
                    </span>
                    <input
                      value={form.cholesterolDetails}
                      onChange={(e) => update('cholesterolDetails', e.target.value)}
                      placeholder="np. cholesterol całkowity 240 mg/dl, LDL 3,8 mmol/l"
                      className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                    />
                  </label>
                </div>
              ) : null}
            </>
          ) : null}

          {step === 5 ? (
            <>
              {radioGroup(
                'familyOncology',
                'Czy w Twojej bliskiej rodzinie (rodzice, rodzeństwo, dziadkowie) zdiagnozowano nowotwór złośliwy?',
                [
                  { value: 'no', label: 'Nie / nie wiem' },
                  { value: 'yes', label: 'Tak' },
                ],
              )}
              {form.familyOncology === 'yes' ? (
                <div className="space-y-4">
                  <div className="rounded-xl border border-slate-200/80 bg-white px-4 py-3 text-sm leading-relaxed text-slate-600 shadow-sm">
                    <p>
                      <strong className="font-medium text-charcoal">Historia rodzinna</strong> pomaga dopasować profilaktykę — nie ocenia wartości „dobro–źle”.
                      Uzupełnij tyle, ile pamiętasz; pola są <strong className="font-medium text-charcoal">opcjonalne</strong>.
                    </p>
                  </div>
                  {form.familyOncologyRelatives.map((rel, relIdx) => (
                    <div
                      key={rel.id}
                      className="space-y-3 rounded-card border border-wellysa-green/20 bg-wellysa-green/10 p-4"
                    >
                      <div className="flex flex-wrap items-start justify-between gap-2 border-b border-wellysa-green/15 pb-3">
                        <p className="text-sm font-semibold text-charcoal">
                          Osoba {relIdx + 1}
                          {form.familyOncologyRelatives.length > 1 ? ` z ${form.familyOncologyRelatives.length}` : ''}
                        </p>
                        {form.familyOncologyRelatives.length > 1 ? (
                          <button
                            type="button"
                            onClick={() => removeRelative(rel.id)}
                            className="inline-flex items-center gap-1 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 transition hover:border-rose-200 hover:text-rose-700"
                          >
                            <Trash2 className="h-3.5 w-3.5" aria-hidden />
                            Usuń osobę
                          </button>
                        ) : null}
                      </div>
                      <label className="block text-sm">
                        <span className="mb-1 block text-slate-600">Pokrewieństwo</span>
                        <select
                          value={rel.kinship}
                          onChange={(e) => patchRelative(rel.id, { kinship: e.target.value })}
                          className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                        >
                          {FAMILY_MEMBER_OPTIONS.map((o) => (
                            <option key={o.value || '_k'} value={o.value}>
                              {o.label}
                            </option>
                          ))}
                        </select>
                      </label>
                      {rel.kinship === 'inne' ? (
                        <label className="block text-sm">
                          <span className="mb-1 block text-slate-600">Jakie pokrewieństwo? (wpisz)</span>
                          <input
                            value={rel.kinshipCustom}
                            onChange={(e) => patchRelative(rel.id, { kinshipCustom: e.target.value })}
                            placeholder="np. kuzynka po stronie ojca"
                            className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                          />
                        </label>
                      ) : null}
                      <div className="space-y-3">
                        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Nowotwory u tej osoby</p>
                        {rel.sites.map((siteRow, siteIdx) => (
                          <div
                            key={siteRow.id}
                            className="rounded-xl border border-slate-200/90 bg-white/90 p-3 shadow-sm sm:p-4"
                          >
                            <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
                              <span className="text-xs font-medium text-slate-500">
                                {rel.sites.length > 1 ? `Przypadek ${siteIdx + 1}` : 'Przypadek'}
                              </span>
                              {rel.sites.length > 1 ? (
                                <button
                                  type="button"
                                  onClick={() => removeSiteRow(rel.id, siteRow.id)}
                                  className="inline-flex items-center gap-1 text-xs font-medium text-slate-500 hover:text-rose-600"
                                >
                                  <Trash2 className="h-3 w-3" aria-hidden />
                                  Usuń
                                </button>
                              ) : null}
                            </div>
                            <div className="grid gap-3 sm:grid-cols-2">
                              <label className="text-sm sm:col-span-2">
                                <span className="mb-1 block text-slate-600">Narząd / typ</span>
                                <select
                                  value={siteRow.site}
                                  onChange={(e) => patchSite(rel.id, siteRow.id, { site: e.target.value })}
                                  className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                                >
                                  {ONCOLOGY_SITE_OPTIONS.map((o) => (
                                    <option key={o.value || '_s'} value={o.value}>
                                      {o.label}
                                    </option>
                                  ))}
                                </select>
                              </label>
                              {siteRow.site === 'inne' ? (
                                <label className="text-sm sm:col-span-2">
                                  <span className="mb-1 block text-slate-600">Opisz (wpisz)</span>
                                  <input
                                    value={siteRow.siteCustom}
                                    onChange={(e) => patchSite(rel.id, siteRow.id, { siteCustom: e.target.value })}
                                    placeholder="np. rak przełyku"
                                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                                  />
                                </label>
                              ) : null}
                              <label className="text-sm sm:max-w-[11rem]">
                                <span className="mb-1 block text-slate-600">Wiek w rozpoznaniu (lata)</span>
                                <input
                                  type="text"
                                  inputMode="numeric"
                                  value={siteRow.ageAtDiagnosis}
                                  onChange={(e) =>
                                    patchSite(rel.id, siteRow.id, {
                                      ageAtDiagnosis: e.target.value.replace(/\D/g, '').slice(0, 3),
                                    })
                                  }
                                  placeholder="np. 48"
                                  className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                                />
                              </label>
                            </div>
                          </div>
                        ))}
                        <button
                          type="button"
                          onClick={() => addSiteRow(rel.id)}
                          className="inline-flex w-full items-center justify-center gap-2 rounded-xl border border-dashed border-wellysa-green/40 bg-white/80 py-2.5 text-sm font-medium text-wellysa-green transition hover:bg-wellysa-green/5 sm:w-auto sm:px-4"
                        >
                          <Plus className="h-4 w-4" aria-hidden />
                          Dodaj kolejny nowotwór u tej osoby
                        </button>
                      </div>
                      <label className="block text-sm">
                        <span className="mb-1 block text-slate-600">Uwagi tylko do tej osoby (opcjonalnie)</span>
                        <textarea
                          value={rel.notes}
                          onChange={(e) => patchRelative(rel.id, { notes: e.target.value })}
                          rows={2}
                          placeholder="np. leczenie, rekurencja — jeśli chcesz doprecyzować"
                          className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                        />
                      </label>
                    </div>
                  ))}
                  <button
                    type="button"
                    onClick={addRelative}
                    className="inline-flex w-full items-center justify-center gap-2 rounded-xl border-2 border-wellysa-green/25 bg-white py-3 text-sm font-semibold text-charcoal transition hover:border-wellysa-green/50 hover:bg-wellysa-green/5"
                  >
                    <Plus className="h-4 w-4 text-wellysa-green" aria-hidden />
                    Dodaj kolejną osobę z nowotworem
                  </button>
                  <label className="block text-sm">
                    <span className="mb-1 block text-slate-600">Uwagi ogólne do całej historii rodzinnej (opcjonalnie)</span>
                    <textarea
                      value={form.familyOncologyDetails}
                      onChange={(e) => update('familyOncologyDetails', e.target.value)}
                      rows={2}
                      className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35"
                      placeholder="Dowolny wpis — np. wiele pokoleń, szczegóły, których nie ma z góry na liście"
                    />
                  </label>
                </div>
              ) : null}
            </>
          ) : null}

          {step === 6 ? (
            <>
              {radioGroup('chestPainRecent', 'W ostatnich tygodniach: ból w klatce lub duszności w wysiłku?', [
                { value: 'no', label: 'Nie' },
                { value: 'yes', label: 'Tak' },
              ])}
              {radioGroup('weightLossUnplanned', 'Nieplanowana utrata masy ciała w ostatnich miesiącach?', [
                { value: 'no', label: 'Nie' },
                { value: 'yes', label: 'Tak' },
              ])}
            </>
          ) : null}

          {step === 7 ? (
            <>
              <div className="rounded-card border border-slate-200 bg-section/90 p-4 sm:p-5">
                <p className="text-sm font-semibold text-charcoal">Podsumowanie odpowiedzi</p>
                <p className="mt-1 text-xs text-slate-500">Sprawdź dane przed wysłaniem — poniżej to, co zaznaczyłeś(aś) w ankiecie.</p>
                <dl className="mt-4 max-h-[min(42vh,320px)] space-y-2.5 overflow-y-auto text-sm">
                  {getSurveySummaryItems(form).map(({ label, value }, sumIdx) => (
                    <div
                      key={`${sumIdx}-${label}`}
                      className="grid gap-0.5 border-b border-slate-100 pb-2 last:border-0 last:pb-0 sm:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)] sm:gap-3"
                    >
                      <dt className="text-slate-500">{label}</dt>
                      <dd className="break-words font-medium text-charcoal">{value}</dd>
                    </div>
                  ))}
                </dl>
              </div>
              <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-slate-200 p-4">
                <input
                  type="checkbox"
                  checked={form.consentRodo}
                  onChange={(e) => update('consentRodo', e.target.checked)}
                  className="mt-1 h-4 w-4 rounded border-slate-300 text-wellysa-green"
                />
                <span className="text-sm text-slate-700">
                  Wyrażam zgodę na przetwarzanie danych osobowych w celu kontaktu i kwalifikacji do usług Wellysa oraz
                  przekazania zgłoszenia do panelu obsługi (RODO).
                </span>
              </label>
              <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-slate-200 p-4">
                <input
                  type="checkbox"
                  checked={form.consentMarketing}
                  onChange={(e) => update('consentMarketing', e.target.checked)}
                  className="mt-1 h-4 w-4 rounded border-slate-300 text-wellysa-green"
                />
                <span className="text-sm text-slate-700">Chcę otrzymywać informacje o profilaktyce i produktach Wellysa (opcjonalnie).</span>
              </label>
              <TurnstileField
                key={turnstileMountId}
                ref={turnstileRef}
                onToken={setTurnstileToken}
                className="flex justify-center py-1"
              />
              {isTurnstileDevTestKey() ? (
                <p className="text-center text-[11px] text-slate-500">
                  Lokalny podgląd: używany jest klucz testowy Cloudflare (wpisz własny Site Key w .env dla produkcji).
                </p>
              ) : null}
              {message ? (
                <p className={`rounded-card px-4 py-3 text-sm ${message.includes('Błąd') ? 'bg-rose-50 text-rose-800' : 'bg-wellysa-green/10 text-wellysa-darkGreen'}`}>
                  {message}
                </p>
              ) : null}
            </>
          ) : null}
        </motion.div>
      </AnimatePresence>

      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-4">
        <button
          type="button"
          disabled={step === 0}
          onClick={() => setStep((s) => Math.max(0, s - 1))}
          className="inline-flex items-center gap-1 rounded-full border border-slate-200 px-4 py-2.5 text-sm font-medium text-charcoal disabled:opacity-40"
        >
          <ChevronLeft className="h-4 w-4" />
          Wstecz
        </button>
        {message && !message.includes('Błąd') ? (
          <button
            type="button"
            onClick={onClose}
            className="rounded-full bg-charcoal px-6 py-2.5 text-sm font-bold text-white hover:opacity-90"
          >
            Zamknij
          </button>
        ) : step < 7 ? (
          <button
            type="button"
            onClick={() => setStep((s) => Math.min(7, s + 1))}
            className="inline-flex items-center gap-1 rounded-full bg-wellysa-green px-5 py-2.5 text-sm font-bold text-white hover:opacity-90"
          >
            Dalej
            <ChevronRight className="h-4 w-4" />
          </button>
        ) : (
          <button
            type="button"
            disabled={!canSubmit() || saving || !!message}
            onClick={handleSubmit}
            className="inline-flex items-center gap-2 rounded-full bg-wellysa-green px-6 py-2.5 text-sm font-bold text-white hover:opacity-90 disabled:opacity-40"
          >
            {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            Wyślij do Wellysa
          </button>
        )}
      </div>
    </div>
  )

  return (
    <ModalShell
      open={open}
      onClose={onClose}
      wide
      title="Ankieta profilaktyczna — wersja Wellysa"
      subtitle="Spokojny, przewidywalny flow — bez presji czasu. Dane trafiają do zespołu tak, żeby można było je sensownie wykorzystać w rozmowie o profilaktyce."
    >
      {body}
    </ModalShell>
  )
}
