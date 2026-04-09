import { motion } from 'framer-motion'
import { ClipboardList, LineChart, ListOrdered } from 'lucide-react'

const systemVsCards = [
  {
    icon: ListOrdered,
    title: 'Kolejka do kolejki',
    text: 'NFZ obiecuje badania — my pomagamy z terminem i kolejnymi krokami. Zamiast miesięcy „w kolejce do kolejki”, idziesz przejrzyście dalej.',
  },
  {
    icon: ClipboardList,
    title: 'Ankieta‑gigant',
    text: 'W IKP poziom szczegółu bywa przytłaczający. Skracamy formalności do minimum — bez gubienia tego, co ważne dla bilansu i profilaktyki.',
  },
  {
    icon: LineChart,
    title: 'Wyniki bez odpowiedzi',
    text: 'W systemie często widzisz tylko liczby. W Wellysa dostajesz kontekst: co to znaczy i co warto zrobić dalej — wspólnie z lekarzem.',
  },
]

const comparisonRows = [
  {
    feature: 'Rezerwacja terminu',
    nfz: 'Może się uda',
    wellysa: 'Wspieramy realne terminy i kolejne kroki',
  },
  {
    feature: 'Interpretacja',
    nfz: 'Suche cyfry',
    wellysa: 'Wyjaśnienie i osobisty plan działania',
  },
  {
    feature: 'Doświadczenie',
    nfz: 'Urząd',
    wellysa: 'Aplikacja i wsparcie w jednym miejscu',
  },
]

export default function WhyAndHowSection() {
  return (
    <div className="border-t border-slate-100">
      <section id="system-vs-rzeczywistosc" className="scroll-mt-24 bg-section py-14 md:py-20">
        <div className="mx-auto max-w-6xl px-6 md:px-8">
          <h2 className="text-center text-3xl font-bold tracking-tight text-charcoal md:text-4xl">
            System vs. rzeczywistość
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-center text-slate-600 md:text-lg">
            Darmowe ścieżki z NFZ i IKP masz z urzędu — spokój i przejrzystość w obsłudze to Twój wybór.
          </p>

          <div className="mt-12 grid gap-6 md:grid-cols-3 md:gap-8">
            {systemVsCards.map((item, i) => {
              const Icon = item.icon
              return (
                <motion.article
                  key={item.title}
                  initial={{ opacity: 0, y: 14 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.35, delay: i * 0.06 }}
                  className="rounded-card border border-slate-200/80 bg-white p-8 shadow-sm"
                >
                  <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-charcoal">
                    <Icon className="h-6 w-6" strokeWidth={1.5} />
                  </div>
                  <h3 className="text-lg font-bold text-charcoal">{item.title}</h3>
                  <p className="mt-3 text-slate-600 leading-relaxed">{item.text}</p>
                </motion.article>
              )
            })}
          </div>
        </div>
      </section>

      <section id="jak-dziala" className="scroll-mt-24 border-t border-slate-100 bg-white py-14 md:py-20">
        <div className="mx-auto max-w-4xl px-6 md:px-8">
          <h2 className="text-center text-3xl font-bold tracking-tight text-charcoal md:text-4xl">
            Wellysa vs. stary system
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-center text-slate-600">
            Krótkie porównanie — w praktyce różnica to czas, kontekst i wygoda.
          </p>

          <div className="mt-10 overflow-hidden rounded-card border border-slate-200 shadow-sm">
            <table className="w-full text-left text-sm md:text-base">
              <thead>
                <tr className="border-b border-slate-200 bg-section/80">
                  <th className="px-4 py-4 font-bold text-charcoal md:px-6 md:py-5">Funkcja</th>
                  <th className="px-4 py-4 font-semibold text-slate-500 md:px-6 md:py-5">NFZ / IKP</th>
                  <th className="px-4 py-4 font-bold text-wellysa-green md:px-6 md:py-5">Wellysa</th>
                </tr>
              </thead>
              <tbody>
                {comparisonRows.map((row, i) => (
                  <tr
                    key={row.feature}
                    className={`border-b border-slate-100 last:border-0 ${
                      i % 2 === 0 ? 'bg-white' : 'bg-section/40'
                    }`}
                  >
                    <td className="px-4 py-4 font-semibold text-charcoal md:px-6 md:py-5">{row.feature}</td>
                    <td className="px-4 py-4 text-slate-500 md:px-6 md:py-5">{row.nfz}</td>
                    <td className="px-4 py-4 font-semibold text-wellysa-green md:px-6 md:py-5">{row.wellysa}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  )
}
