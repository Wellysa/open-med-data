import { motion } from 'framer-motion'
import { ClipboardList, MapPin, Microscope } from 'lucide-react'
import ModalShell from './ModalShell'

const TILES = [
  {
    key: 'survey',
    title: 'Ankieta profilaktyczna',
    desc: 'Odpowiednikiem ankiety z „Moje Zdrowie” w IKP — czytelniej, z zapisem do zespołu i Twoimi danymi (imię, nazwisko, PESEL, e-mail).',
    icon: ClipboardList,
    cta: 'Otwórz ankietę',
  },
  {
    key: 'map',
    title: 'Punkty partnerskie',
    desc: 'Dostępne lokalizacje punktów, z którymi współpracujemy — wybierz wygodne miejsce na interaktywnej mapie.',
    icon: MapPin,
    cta: 'Otwórz mapę',
  },
  {
    key: 'upload',
    title: 'Wyślij wyniki PDF',
    desc: 'Wgraj wyniki — API zakłada zlecenie analizy. Płatność i interpretacja są w panelu Wellysa (auto lub po konsultacji, zależnie od trybu).',
    icon: Microscope,
    cta: 'Wgraj plik',
  },
]

export default function ServicesHubModal({ open, onClose, onPickTool }) {
  return (
    <ModalShell
      open={open}
      onClose={onClose}
      wide
      title="Panel usług Wellysa"
      subtitle="Wybierz usługę — każda opcja otwiera narzędzie w osobnym oknie."
    >
      <div className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {TILES.map(({ key, title, desc, icon: Icon, cta }, i) => (
            <motion.button
              key={key}
              type="button"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04 }}
              onClick={() => onPickTool(key)}
              className="flex flex-col rounded-2xl border border-slate-100 bg-white p-6 text-left shadow-sm transition-all hover:border-wellysa-green/40 hover:shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-wellysa-green focus-visible:ring-offset-2"
            >
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 text-wellysa-green">
                <Icon className="h-6 w-6" strokeWidth={1.5} aria-hidden />
              </div>
              <h3 className="text-lg font-semibold text-charcoal">{title}</h3>
              <p className="mt-2 flex-1 text-sm leading-relaxed text-slate-600">{desc}</p>
              <span className="mt-5 inline-flex w-fit rounded-full bg-wellysa-green px-4 py-2 text-sm font-bold text-white">{cta}</span>
            </motion.button>
          ))}
        </div>
        <p className="border-t border-slate-100 pt-4 text-center text-xs text-slate-500">
          Backend: ustaw{' '}
          <code className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[11px]">VITE_ADMIN_API_BASE_URL</code> w{' '}
          <code className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[11px]">.env</code> — szczegóły w{' '}
          <code className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[11px]">.env.example</code> i{' '}
          <code className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[11px]">src/lib/adminApi.js</code>.
        </p>
      </div>
    </ModalShell>
  )
}
