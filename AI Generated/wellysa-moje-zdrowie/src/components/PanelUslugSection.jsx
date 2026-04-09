import { useState } from 'react'
import { motion } from 'framer-motion'
import { Sparkles } from 'lucide-react'
import MojeZdrowieSurveyModal from './modals/MojeZdrowieSurveyModal'
import SynevoMapModal from './modals/SynevoMapModal'
import ResultsUploadModal from './modals/ResultsUploadModal'
import ServicesHubModal from './modals/ServicesHubModal'

export default function PanelUslugSection() {
  const [hubOpen, setHubOpen] = useState(false)
  const [tool, setTool] = useState(null)

  const openTool = (key) => {
    setHubOpen(false)
    setTool(key)
  }

  return (
    <section
      id="panel-uslug"
      className="scroll-mt-24 border-t border-slate-100 bg-gradient-to-b from-section/90 to-white py-16 md:py-24"
      aria-labelledby="panel-uslug-title"
    >
      <div className="mx-auto max-w-4xl px-6 md:px-8">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.35 }}
          className="rounded-[28px] border border-slate-200/90 bg-white px-6 py-8 shadow-[0_4px_40px_rgba(15,23,42,0.06)] md:px-10 md:py-10"
        >
          <p className="flex items-center justify-center gap-2 text-xs font-semibold uppercase tracking-wider text-wellysa-green md:justify-start">
            <Sparkles className="h-3.5 w-3.5" />
            Panel usług Wellysa
          </p>
          <h2
            id="panel-uslug-title"
            className="mt-3 text-center text-2xl font-semibold tracking-tight text-charcoal md:text-left md:text-3xl"
          >
            Zacznij w domu — dokończysz z nami lub w gabinecie
          </h2>
          <p className="mx-auto mt-3 max-w-2xl text-center text-sm leading-relaxed text-slate-600 md:mx-0 md:text-left md:text-base">
            Dane wprowadzasz Ty (wygodnie), decyzje i interpretacja — po naszej stronie. Otwórz panel, żeby przejść do ankiety, mapy
            punktów partnerskich lub wysyłki wyników do zespołu Wellysa.
          </p>
          <div className="mt-8 flex flex-col items-stretch justify-center gap-3 sm:flex-row sm:flex-wrap md:justify-start">
            <button
              type="button"
              onClick={() => setHubOpen(true)}
              className="inline-flex min-h-[44px] items-center justify-center rounded-full bg-wellysa-green px-8 py-3 text-sm font-bold text-white shadow-sm transition hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-wellysa-green focus-visible:ring-offset-2"
            >
              Otwórz panel usług
            </button>
            <a
              href="#pobierz"
              className="inline-flex min-h-[44px] items-center justify-center rounded-full border border-slate-200 bg-white px-8 py-3 text-sm font-semibold text-charcoal transition hover:border-wellysa-green hover:text-wellysa-green"
            >
              Pobierz aplikację
            </a>
          </div>
        </motion.div>
      </div>

      <ServicesHubModal open={hubOpen} onClose={() => setHubOpen(false)} onPickTool={openTool} />
      <MojeZdrowieSurveyModal open={tool === 'survey'} onClose={() => setTool(null)} />
      <SynevoMapModal open={tool === 'map'} onClose={() => setTool(null)} />
      <ResultsUploadModal open={tool === 'upload'} onClose={() => setTool(null)} />
    </section>
  )
}
