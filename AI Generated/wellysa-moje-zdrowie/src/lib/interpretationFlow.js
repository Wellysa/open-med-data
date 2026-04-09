/**
 * Panel pacjenta Wellysa — płatność i wyświetlanie interpretacji po uploadzie wyników z landingu.
 * Zobacz .env.example: odpowiedź JSON z POST /api/landing/results-upload może zawierać
 * panelCheckoutUrl lub orderId do zbudowania linku.
 */

export function getWellysaPanelBaseUrl() {
  const u = import.meta.env.VITE_WELLYSA_PANEL_URL
  return typeof u === 'string' ? u.replace(/\/$/, '') : ''
}

/** Ścieżka względna z placeholderem {orderId} lub pełny URL szablonowy. */
export function getPanelOrderPathTemplate() {
  const t = import.meta.env.VITE_WELLYSA_PANEL_ORDER_PATH_TEMPLATE
  return typeof t === 'string' && t.trim().length > 0 ? t.trim() : '/zamowienie/{orderId}'
}

export function buildPanelOrderUrl(orderId) {
  const base = getWellysaPanelBaseUrl()
  if (!orderId || !String(orderId).trim()) return base || ''
  const id = String(orderId).trim()
  if (!base) return ''
  const tpl = getPanelOrderPathTemplate()
  const path = tpl.replace(/\{orderId\}/g, encodeURIComponent(id))
  if (/^https?:\/\//i.test(path)) return path
  const normalized = path.startsWith('/') ? path : `/${path}`
  return `${base}${normalized}`
}

/**
 * Preferuj absolutny URL z API; w przeciwnym razie złóż z panelu + szablonu; na końcu sam base.
 * @param {{ orderId?: string | null, panelCheckoutUrl?: string | null }} meta
 */
export function resolvePanelUrlAfterUpload(meta) {
  const raw = meta?.panelCheckoutUrl
  if (typeof raw === 'string' && /^https?:\/\//i.test(raw.trim())) return raw.trim()
  const oid = meta?.orderId
  if (oid) {
    const built = buildPanelOrderUrl(oid)
    if (built) return built
  }
  return getWellysaPanelBaseUrl()
}

export function panelFlowButtonLabel() {
  const l = import.meta.env.VITE_WELLYSA_PANEL_CTA_LABEL
  return typeof l === 'string' && l.trim().length > 0 ? l.trim() : 'Otwórz panel — płatność i interpretacja'
}
