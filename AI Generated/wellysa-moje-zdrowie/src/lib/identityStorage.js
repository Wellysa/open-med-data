const KEY = 'wellysa_landing_identity'

export function saveLandingIdentity(identity) {
  try {
    localStorage.setItem(KEY, JSON.stringify(identity))
  } catch {
    /* ignore */
  }
}

export function loadLandingIdentity() {
  try {
    const raw = localStorage.getItem(KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}
