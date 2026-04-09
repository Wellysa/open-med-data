/**
 * Integracja z panelem admina Wellysa.
 * Skonfiguruj VITE_ADMIN_API_BASE_URL w .env — patrz .env.example
 */

function baseUrl() {
  const b = import.meta.env.VITE_ADMIN_API_BASE_URL
  return typeof b === 'string' ? b.replace(/\/$/, '') : ''
}

function isDemo() {
  return !baseUrl()
}

/**
 * @param {object} payload
 * @param {{ firstName: string, lastName: string, pesel: string, email: string, phone?: string }} payload.identity
 * @param {object} payload.survey — płaskie odpowiedzi ankiety (Moje Zdrowie / Profilaktyka 40+ style)
 */
/**
 * @param {string | null | undefined} turnstileToken — token z Cloudflare Turnstile (pole `cfTurnstileResponse` w JSON)
 */
export async function submitLandingSurvey(payload, turnstileToken) {
  const base = baseUrl()
  if (!base) {
    console.info('[Wellysa landing] DEMO — brak VITE_ADMIN_API_BASE_URL, pomijam POST:', payload)
    return { ok: true, demo: true }
  }
  const body = {
    source: 'wellysa-landing',
    submittedAt: new Date().toISOString(),
    ...payload,
  }
  if (turnstileToken) body.cfTurnstileResponse = turnstileToken
  const res = await fetch(`${base}/api/landing/survey`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const t = await res.text().catch(() => res.statusText)
    throw new Error(t || `HTTP ${res.status}`)
  }
  return { ok: true, demo: false }
}

/**
 * @typedef {object} ResultsUploadResult
 * @property {boolean} ok
 * @property {boolean} demo
 * @property {string | null} orderId — do linkowania w panelu (np. resultsOrderId z API)
 * @property {string | null} panelCheckoutUrl — opcjonalny pełny URL z odpowiedzi API
 * @property {string | null} interpretationStatus — np. pending_payment (podgląd z API)
 */

/**
 * POST multipart: firstName, lastName, pesel, email, notes?, file, source, submittedAt
 *
 * Oczekiwana odpowiedź JSON (zalecana): { orderId?, resultsOrderId?, panelCheckoutUrl?, interpretationStatus? }
 * Przy pustym body lub non-JSON — traktujemy jako sukces bez metadanych.
 *
 * @param {FormData} formData
 * @param {string | null | undefined} turnstileToken — pole multipart `cf-turnstile-response` (konwencja Cloudflare)
 * @returns {Promise<ResultsUploadResult>}
 */
export async function submitResultsPdf(formData, turnstileToken) {
  const base = baseUrl()
  if (!base) {
    console.info('[Wellysa landing] DEMO — brak VITE_ADMIN_API_BASE_URL, pomijam upload PDF')
    return {
      ok: true,
      demo: true,
      orderId: null,
      panelCheckoutUrl: null,
      interpretationStatus: null,
    }
  }
  if (turnstileToken) formData.append('cf-turnstile-response', turnstileToken)
  const res = await fetch(`${base}/api/landing/results-upload`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) {
    const t = await res.text().catch(() => res.statusText)
    throw new Error(t || `HTTP ${res.status}`)
  }
  const ct = res.headers.get('content-type') || ''
  if (!ct.includes('application/json')) {
    return {
      ok: true,
      demo: false,
      orderId: null,
      panelCheckoutUrl: null,
      interpretationStatus: null,
    }
  }
  try {
    const body = await res.json()
    const orderId = body.orderId ?? body.resultsOrderId ?? null
    const panelCheckoutUrl = typeof body.panelCheckoutUrl === 'string' ? body.panelCheckoutUrl : null
    const interpretationStatus =
      typeof body.interpretationStatus === 'string' ? body.interpretationStatus : null
    return {
      ok: true,
      demo: false,
      orderId: orderId != null ? String(orderId) : null,
      panelCheckoutUrl,
      interpretationStatus,
    }
  } catch {
    return {
      ok: true,
      demo: false,
      orderId: null,
      panelCheckoutUrl: null,
      interpretationStatus: null,
    }
  }
}

/**
 * Opcjonalny endpoint pod **panel / aplikację** (nie musi być wywoływany z landingu).
 * Zwraca status płatności i interpretacji po przetworzeniu przez API.
 *
 * Przykład odpowiedzi:
 * {
 *   orderId, paymentStatus: 'pending'|'paid'|...,
 *   interpretationStatus: 'pending_payment'|'processing'|'ready'|'awaiting_clinician'|'failed',
 *   interpretation?: { markdown?, summary? },
 *   messageForPatient?: string
 * }
 *
 * @param {string} orderId
 * @returns {Promise<object | null>}
 */
export async function fetchResultsInterpretation(orderId) {
  const base = baseUrl()
  if (!base || !orderId) return null
  const res = await fetch(`${base}/api/landing/results-interpretation/${encodeURIComponent(orderId)}`, {
    headers: { Accept: 'application/json' },
  })
  if (res.status === 404) return null
  if (!res.ok) {
    const t = await res.text().catch(() => res.statusText)
    throw new Error(t || `HTTP ${res.status}`)
  }
  return res.json()
}

export { isDemo }
