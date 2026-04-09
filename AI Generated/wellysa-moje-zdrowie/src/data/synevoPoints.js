/**
 * Punkty pobrań Synevo — zestaw startowy do mapy (współrzędne przybliżone do centrów/oddziałów).
 * W produkcji podmień na listę z CSV (np. z eksportu synevo.pl/znajdz-punkt) lub API.
 * Format: { id, name, address, city, lat, lng }
 */
export const SYNEVO_POINTS = [
  { id: 'waw1', name: 'Synevo — Śródmieście', city: 'Warszawa', address: 'ul. Marszałkowska (rejon)', lat: 52.2302, lng: 21.0104 },
  { id: 'waw2', name: 'Synevo — Mokotów', city: 'Warszawa', address: 'Mokotów', lat: 52.1824, lng: 21.0201 },
  { id: 'waw3', name: 'Synevo — Bemowo', city: 'Warszawa', address: 'Bemowo', lat: 52.245, lng: 20.92 },
  { id: 'krk', name: 'Synevo — Kraków', city: 'Kraków', address: 'Centrum', lat: 50.0647, lng: 19.945 },
  { id: 'wro', name: 'Synevo — Wrocław', city: 'Wrocław', address: 'Centrum', lat: 51.1079, lng: 17.0385 },
  { id: 'poz', name: 'Synevo — Poznań', city: 'Poznań', address: 'Centrum', lat: 52.4064, lng: 16.9252 },
  { id: 'gdn', name: 'Synevo — Gdańsk', city: 'Gdańsk', address: 'Wrzeszcz', lat: 54.382, lng: 18.6 },
  { id: 'szz', name: 'Synevo — Szczecin', city: 'Szczecin', address: 'Centrum', lat: 53.4285, lng: 14.5528 },
  { id: 'lod', name: 'Synevo — Łódź', city: 'Łódź', address: 'Śródmieście', lat: 51.7592, lng: 19.456 },
  { id: 'kat', name: 'Synevo — Katowice', city: 'Katowice', address: 'Centrum', lat: 50.2649, lng: 19.0238 },
  { id: 'lub', name: 'Synevo — Lublin', city: 'Lublin', address: 'Centrum', lat: 51.2465, lng: 22.5684 },
  { id: 'bia', name: 'Synevo — Białystok', city: 'Białystok', address: 'Centrum', lat: 53.1325, lng: 23.1688 },
  { id: 'rze', name: 'Synevo — Rzeszów', city: 'Rzeszów', address: 'Centrum', lat: 50.0413, lng: 21.999 },
  { id: 'ols', name: 'Synevo — Olsztyn', city: 'Olsztyn', address: 'Centrum', lat: 53.7784, lng: 20.4801 },
  { id: 'tor', name: 'Synevo — Toruń', city: 'Toruń', address: 'Centrum', lat: 53.0138, lng: 18.5981 },
  { id: 'zak', name: 'Synevo — Zielona Góra', city: 'Zielona Góra', address: 'Centrum', lat: 51.9355, lng: 15.5064 },
  { id: 'opi', name: 'Synevo — Opole', city: 'Opole', address: 'Centrum', lat: 50.6751, lng: 17.9213 },
  { id: 'glc', name: 'Synevo — Gliwice', city: 'Gliwice', address: 'Centrum', lat: 50.2945, lng: 18.6714 },
  { id: 'byd', name: 'Synevo — Bydgoszcz', city: 'Bydgoszcz', address: 'Centrum', lat: 53.1235, lng: 18.0076 },
  { id: 'zgr', name: 'Synevo — Gorzów Wielkopolski', city: 'Gorzów Wlkp.', address: 'Centrum', lat: 52.7325, lng: 15.2389 },
]
