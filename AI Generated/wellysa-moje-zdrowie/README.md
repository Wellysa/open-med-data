# Wellysa „Moje Zdrowie” – Landing Page

Landing page dla aplikacji mobilnej Wellysa. Kierowany do polskich użytkowników programu Profilaktyka 40 Plus (IKP / Moje Zdrowie).

## Tech stack

- React + Vite
- Tailwind CSS
- Lucide React (ikony)
- Czcionka Inter (Google Fonts)

## Uruchomienie

```bash
npm install
npm run dev
```

## Budowanie

```bash
npm run build
```

Wynik w folderze `dist/`.

## Cloudflare Pages – deployment

### Opcja A: Git (dashboard)

1. Połącz repozytorium z Cloudflare Pages (Cloudflare Dashboard → Pages → Create project → Connect to Git)
2. **Root directory:** `AI Generated/wellysa-moje-zdrowie`
3. **Build command:** `npm run build`
4. **Build output directory:** `dist`
5. **Node.js version:** 18 lub 20 (ustaw w Settings → Environment variables: `NODE_VERSION=20`)

### Opcja B: Wrangler CLI

```bash
npm install
npm run build
npx wrangler pages deploy dist --project-name=wellysa-moje-zdrowie
```

Przy pierwszym deployu utworzysz projekt: `npx wrangler pages project create wellysa-moje-zdrowie`

### Opcja C: Static (bez Node – wersja standalone)

Jeśli nie chcesz budować projektu, możesz wgrać plik `index-standalone.html`:
1. Zmień nazwę na `index.html`
2. Utwórz folder z tym plikiem
3. Deploy: `npx wrangler pages deploy ./folder-z-index-html --project-name=wellysa-moje-zdrowie`
