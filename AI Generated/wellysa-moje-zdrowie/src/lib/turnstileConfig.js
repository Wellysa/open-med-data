/**
 * Cloudflare Turnstile — klucz witryny tylko po stronie klienta.
 * @see https://developers.cloudflare.com/turnstile/troubleshooting/testing/
 */
const TURNSTILE_PASSING_TEST_SITE_KEY = '1x00000000000000000000AA'

export function getTurnstileSiteKey() {
  const k = import.meta.env.VITE_CLOUDFLARE_TURNSTILE_SITE_KEY
  const trimmed = typeof k === 'string' ? k.trim() : ''
  if (trimmed) return trimmed

  const devFallbackOff = import.meta.env.VITE_CLOUDFLARE_TURNSTILE_DISABLE_DEV === 'true'
  if (import.meta.env.DEV && !devFallbackOff) return TURNSTILE_PASSING_TEST_SITE_KEY

  return ''
}

/**
 * Czy wymagamy tokena przed wysłaniem (ankieta / PDF).
 * W produkcji: tylko przy ustawionym VITE_CLOUDFLARE_TURNSTILE_SITE_KEY.
 * W dev: także klucz testowy CF (chyba że VITE_CLOUDFLARE_TURNSTILE_DISABLE_DEV=true).
 */
export function isTurnstileConfigured() {
  return getTurnstileSiteKey().length > 0
}

/** True tylko w dev, gdy nie podano własnego klucza — do ewentualnych podpowiedzi w UI. */
export function isTurnstileDevTestKey() {
  const k = import.meta.env.VITE_CLOUDFLARE_TURNSTILE_SITE_KEY
  const trimmed = typeof k === 'string' ? k.trim() : ''
  return import.meta.env.DEV && !trimmed && import.meta.env.VITE_CLOUDFLARE_TURNSTILE_DISABLE_DEV !== 'true'
}
