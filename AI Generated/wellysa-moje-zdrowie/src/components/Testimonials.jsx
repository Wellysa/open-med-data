import { useState } from 'react'
import { ChevronLeft, ChevronRight, Quote } from 'lucide-react'

const testimonials = [
  {
    quote: 'Ankieta w IKP to była katorga. Z Wellysa poszło w 3 minuty. Polecam!',
    author: 'Marek',
    age: 46,
  },
  {
    quote: 'Nareszcie rozumiem moje wyniki badań, a nie tylko patrzę na normy.',
    author: 'Anna',
    age: 41,
  },
  {
    quote: 'Wellysa znalazła mi termin na pakiet badań profilaktycznych w ciągu tygodnia. W mojej przychodni POZ czekali miesiąc.',
    author: 'Jacek',
    age: 50,
  },
]

export default function Testimonials() {
  const [active, setActive] = useState(0)

  const next = () => setActive((i) => (i + 1) % testimonials.length)
  const prev = () => setActive((i) => (i - 1 + testimonials.length) % testimonials.length)

  return (
    <section className="py-20 md:py-32 px-6 md:px-12 bg-section">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-charcoal text-center mb-20">
          Pacjenci, którzy zaufali Wellysa zamiast IKP.
        </h2>

        <div className="relative">
          <div className="bg-white rounded-card p-8 md:p-12 shadow-sm border border-slate-100 min-h-[240px]">
            <Quote className="w-10 h-10 text-wellysa-green/40 mb-6" />
            <blockquote className="text-xl md:text-2xl text-charcoal leading-relaxed mb-6">
              „{testimonials[active].quote}”
            </blockquote>
            <footer className="text-slate-600 font-medium">
              — {testimonials[active].author}, {testimonials[active].age} lat.
            </footer>
          </div>

          <div className="flex justify-center gap-4 mt-8">
            <button
              type="button"
              onClick={prev}
              className="w-12 h-12 rounded-full bg-white border border-slate-200 flex items-center justify-center text-charcoal hover:bg-section transition-colors"
              aria-label="Poprzedni"
            >
              <ChevronLeft size={24} />
            </button>
            <div className="flex gap-2 items-center">
              {testimonials.map((_, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setActive(i)}
                  className={`w-2.5 h-2.5 rounded-full transition-colors ${
                    i === active ? 'bg-wellysa-green' : 'bg-slate-300'
                  }`}
                  aria-label={`Świadectwo ${i + 1}`}
                />
              ))}
            </div>
            <button
              type="button"
              onClick={next}
              className="w-12 h-12 rounded-full bg-white border border-slate-200 flex items-center justify-center text-charcoal hover:bg-section transition-colors"
              aria-label="Następny"
            >
              <ChevronRight size={24} />
            </button>
          </div>
        </div>

        <div className="mt-12 grid sm:grid-cols-3 gap-4 hidden sm:grid">
          {testimonials.map((t, i) => (
            <article
              key={i}
              className={`rounded-card p-6 border transition-all cursor-pointer ${
                i === active
                  ? 'bg-white border-wellysa-green shadow-md'
                  : 'bg-white/60 border-slate-100 hover:border-slate-200'
              }`}
              onClick={() => setActive(i)}
            >
              <p className="text-slate-600 line-clamp-3">„{t.quote}”</p>
              <p className="text-sm font-medium text-charcoal mt-3">
                {t.author}, {t.age} lat
              </p>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
