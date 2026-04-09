import { useCallback, useEffect, useRef, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { ExternalLink, FileUp, Loader2 } from 'lucide-react'
import ModalShell from './ModalShell'
import TurnstileField from '../TurnstileField'
import { submitResultsPdf, isDemo } from '../../lib/adminApi'
import { isTurnstileConfigured, isTurnstileDevTestKey } from '../../lib/turnstileConfig'
import {
  getWellysaPanelBaseUrl,
  panelFlowButtonLabel,
  resolvePanelUrlAfterUpload,
} from '../../lib/interpretationFlow'
import { loadLandingIdentity, saveLandingIdentity } from '../../lib/identityStorage'

export default function ResultsUploadModal({ open, onClose }) {
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [pesel, setPesel] = useState('')
  const [email, setEmail] = useState('')
  const [notes, setNotes] = useState('')
  const [file, setFile] = useState(null)
  const [saving, setSaving] = useState(false)
  const [errorMessage, setErrorMessage] = useState(null)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [uploadResult, setUploadResult] = useState(null)
  const [turnstileToken, setTurnstileToken] = useState('')
  const [turnstileMountId, setTurnstileMountId] = useState(0)
  const turnstileRef = useRef(null)

  useEffect(() => {
    if (!open) return
    setErrorMessage(null)
    setUploadSuccess(false)
    setUploadResult(null)
    setFile(null)
    setTurnstileToken('')
    setTurnstileMountId((k) => k + 1)
    const id = loadLandingIdentity()
    if (id) {
      setFirstName(id.firstName || '')
      setLastName(id.lastName || '')
      setPesel(id.pesel || '')
      setEmail(id.email || '')
    }
  }, [open])

  const onDrop = useCallback((accepted) => {
    const f = accepted[0]
    if (f) setFile(f)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'], 'image/jpeg': [], 'image/png': [] },
    maxFiles: 1,
    multiple: false,
  })

  const handleSubmit = async () => {
    const p = pesel.replace(/\D/g, '')
    if (!firstName.trim() || !lastName.trim() || p.length !== 11 || !email.includes('@') || !file) {
      setErrorMessage('Uzupełnij imię, nazwisko, PESEL, e-mail i wybierz plik PDF.')
      return
    }
    if (isTurnstileConfigured() && !turnstileToken) {
      setErrorMessage('Potwierdź, że nie jesteś robotem (pole powyżej).')
      return
    }
    setSaving(true)
    setErrorMessage(null)
    saveLandingIdentity({ firstName: firstName.trim(), lastName: lastName.trim(), pesel: p, email: email.trim() })

    const fd = new FormData()
    fd.append('firstName', firstName.trim())
    fd.append('lastName', lastName.trim())
    fd.append('pesel', p)
    fd.append('email', email.trim())
    if (notes.trim()) fd.append('notes', notes.trim())
    fd.append('file', file)
    fd.append('source', 'wellysa-landing')
    fd.append('submittedAt', new Date().toISOString())

    try {
      const result = await submitResultsPdf(fd, isTurnstileConfigured() ? turnstileToken : undefined)
      setUploadResult(result)
      setUploadSuccess(true)
    } catch (e) {
      turnstileRef.current?.reset()
      setTurnstileToken('')
      setErrorMessage(e.message || 'Błąd wysyłki.')
    } finally {
      setSaving(false)
    }
  }

  const demoNotice = isDemo() && uploadSuccess
  const panelHref = uploadSuccess
    ? resolvePanelUrlAfterUpload({
        orderId: uploadResult?.orderId,
        panelCheckoutUrl: uploadResult?.panelCheckoutUrl,
      })
    : ''
  const hasPanelLink = Boolean(panelHref)
  const panelBaseConfigured = Boolean(getWellysaPanelBaseUrl())

  return (
    <ModalShell
      open={open}
      onClose={onClose}
      wide
      title="Wyniki z IKP lub laboratorium"
      subtitle="Plik trafia do API — zakładane jest zlecenie analizy. Płatność i gotowa interpretacja są w panelu pacjenta Wellysa."
    >
      <div className="space-y-5">
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="text-sm">
            <span className="mb-1 block text-slate-600">Imię</span>
            <input
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              disabled={uploadSuccess}
              className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35 disabled:bg-slate-50"
            />
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-slate-600">Nazwisko</span>
            <input
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              disabled={uploadSuccess}
              className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35 disabled:bg-slate-50"
            />
          </label>
        </div>
        <label className="block text-sm">
          <span className="mb-1 block text-slate-600">PESEL</span>
          <input
            inputMode="numeric"
            maxLength={11}
            value={pesel}
            onChange={(e) => setPesel(e.target.value.replace(/\D/g, '').slice(0, 11))}
            disabled={uploadSuccess}
            className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35 disabled:bg-slate-50"
          />
        </label>
        <label className="block text-sm">
          <span className="mb-1 block text-slate-600">E-mail</span>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={uploadSuccess}
            className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35 disabled:bg-slate-50"
          />
        </label>
        <label className="block text-sm">
          <span className="mb-1 block text-slate-600">Uwagi dla zespołu (opcjonalnie)</span>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            disabled={uploadSuccess}
            rows={2}
            className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none focus:ring-2 focus:ring-wellysa-green/35 disabled:bg-slate-50"
            placeholder="Np. które badania, data pobrania…"
          />
        </label>

        <div
          {...getRootProps()}
          className={`flex min-h-[140px] flex-col items-center justify-center rounded-2xl border-2 border-dashed px-4 py-8 transition-colors ${
            uploadSuccess
              ? 'cursor-not-allowed border-slate-100 bg-slate-50 opacity-60'
              : isDragActive
                ? 'cursor-pointer border-wellysa-green bg-emerald-50/50'
                : 'cursor-pointer border-slate-200 bg-slate-50/80 hover:border-slate-300'
          }`}
        >
          <input {...getInputProps()} disabled={uploadSuccess} />
          <FileUp className="mb-2 h-9 w-9 text-slate-400" />
          <p className="text-center text-sm font-medium text-charcoal">
            {file ? file.name : 'Upuść PDF / JPG lub kliknij'}
          </p>
        </div>

        {!uploadSuccess && isTurnstileConfigured() ? (
          <div className="space-y-1">
            <TurnstileField
              key={turnstileMountId}
              ref={turnstileRef}
              onToken={setTurnstileToken}
              className="flex justify-center py-1"
            />
            {isTurnstileDevTestKey() ? (
              <p className="text-center text-[11px] text-slate-500">
                Lokalny podgląd: klucz testowy Cloudflare — na produkcji ustaw VITE_CLOUDFLARE_TURNSTILE_SITE_KEY przed buildem.
              </p>
            ) : null}
          </div>
        ) : null}

        {errorMessage ? (
          <p className="rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-800">{errorMessage}</p>
        ) : null}

        {uploadSuccess ? (
          <div className="space-y-3 rounded-2xl border border-amber-200/90 bg-amber-50/90 px-4 py-4 text-sm text-charcoal">
            <p className="font-semibold text-charcoal">Plik przyjęty — dziękujemy</p>
            {demoNotice ? (
              <p className="rounded-lg bg-white/80 px-3 py-2 text-xs text-amber-900/90">
                Tryb demo — żądanie nie trafiło na serwer. Po ustawieniu{' '}
                <code className="rounded bg-amber-100/80 px-1 font-mono text-[11px]">VITE_ADMIN_API_BASE_URL</code>{' '}
                backend zapisze plik i zwróci np. <code className="font-mono text-[11px]">orderId</code> pod link do
                panelu.
              </p>
            ) : null}
            {uploadResult?.orderId ? (
              <p className="text-xs text-slate-600">
                Numer zgłoszenia (przydatny w kontakcie i w panelu):{' '}
                <code className="rounded bg-white/90 px-1.5 py-0.5 font-mono text-[13px] text-charcoal">
                  {uploadResult.orderId}
                </code>
              </p>
            ) : null}
            <ol className="list-decimal space-y-2 pl-5 text-slate-800">
              <li>
                <strong>API</strong> zapisuje dokument i uruchamia zlecenie analizy / interpretacji (asynchronicznie po
                stronie serwera).
              </li>
              <li>
                <strong>Płatność</strong> realizujesz wyłącznie w{' '}
                <strong className="text-charcoal">panelu pacjenta Wellysa</strong> — nie na zewnętrznym sklepie.
              </li>
              <li>
                Po zakończeniu płatności <strong>interpretacja i opis wyników</strong> będą dostępne w tym samym panelu.
                Mogą pojawić się <strong>automatycznie</strong>, gdy API zakończy opracowanie, albo{' '}
                <strong>po uzgodnieniu z lekarzem</strong> — zależnie od trybu zlecenia. W obu przypadkach pacjent widzi
                treść w jednym miejscu w aplikacji.
              </li>
            </ol>
            {hasPanelLink ? (
              <div className="pt-1">
                <a
                  href={panelHref}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 rounded-full bg-charcoal px-5 py-2.5 text-sm font-bold text-white transition hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-charcoal focus-visible:ring-offset-2"
                >
                  <ExternalLink className="h-4 w-4 shrink-0" aria-hidden />
                  {panelFlowButtonLabel()}
                </a>
                <p className="mt-2 text-xs text-slate-600">
                  Loguj się tym samym kontem co w aplikacji Wellysa. Po opłaceniu wróć do szczegółów zgłoszenia — tam
                  pojawi się interpretacja, gdy będzie gotowa.
                </p>
              </div>
            ) : (
              <p className="text-slate-700">
                Otwórz <strong>aplikację lub panel Wellysa</strong> (to samo konto / e-mail co w formularzu) — tam
                dokończysz płatność i zobaczysz interpretację, gdy będzie gotowa.
                {!panelBaseConfigured ? (
                  <>
                    {' '}
                    Bezpośredni link na stronie pojawi się po ustawieniu{' '}
                    <code className="rounded bg-white/80 px-1 font-mono text-[11px]">VITE_WELLYSA_PANEL_URL</code> przy
                    wdrożeniu.
                  </>
                ) : null}
              </p>
            )}
          </div>
        ) : null}

        <div className="flex flex-wrap justify-end gap-3">
          <button type="button" onClick={onClose} className="rounded-full border border-slate-200 px-5 py-2.5 text-sm font-medium text-charcoal hover:bg-slate-50">
            Zamknij
          </button>
          <button
            type="button"
            disabled={saving || uploadSuccess || (isTurnstileConfigured() && !turnstileToken)}
            onClick={handleSubmit}
            className="inline-flex items-center gap-2 rounded-full bg-wellysa-green px-6 py-2.5 text-sm font-bold text-white hover:opacity-90 disabled:opacity-40"
          >
            {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            Wyślij do panelu
          </button>
        </div>
      </div>
    </ModalShell>
  )
}
