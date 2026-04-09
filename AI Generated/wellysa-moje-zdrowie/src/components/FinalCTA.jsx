export default function FinalCTA() {
  return (
    <section
      id="pobierz"
      className="py-20 md:py-28 px-6 md:px-12 bg-gradient-to-b from-section/90 to-white border-t border-slate-100"
    >
      <div className="max-w-3xl mx-auto text-center">
        <h2 className="text-3xl md:text-4xl lg:text-[2.75rem] font-bold tracking-tight text-charcoal leading-tight">
          Nie bądź zakładnikiem systemu. Przejmij kontrolę.
        </h2>
        <p className="text-lg text-slate-600 mt-6 max-w-2xl mx-auto leading-relaxed">
          Badania z programów publicznych to Twoje prawo — spokój ducha i przejrzysta obsługa to kwestia narzędzia.
          Pobierz Wellysa i zrób profilaktykę na własnych zasadach, z aplikacją i panelem w przeglądarce.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center mt-12">
          <a
            href="https://apps.apple.com/pl/app/wellysa-asystent/id6751268147"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-card bg-wellysa-green text-white font-bold hover:opacity-90 transition-opacity"
            aria-label="Pobierz z App Store"
          >
            <svg className="w-8 h-8" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
              <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z" />
            </svg>
            Pobierz z App Store
          </a>
          <a
            href="https://play.google.com/store/apps/details?id=com.wellysa.onkoradar_dev&hl=pl"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-card border-2 border-charcoal text-charcoal font-bold hover:bg-charcoal hover:text-white transition-colors"
            aria-label="Pobierz z Google Play"
          >
            <svg className="w-8 h-8" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
              <path d="M3.609 1.814L13.792 12 3.61 22.186a.996.996 0 0 1-.61-.92V2.734a1 1 0 0 1 .609-.92zm10.89 10.893l2.302 2.302-10.937 6.333 8.635-8.635zm3.199-3.198l2.807 1.626a1 1 0 0 1 0 1.73l-2.808 1.626L15.206 12l2.492-2.491zM5.864 2.658L16.802 8.99l-2.302 2.302-8.636-8.634z" />
            </svg>
            Pobierz z Google Play
          </a>
        </div>
        <p className="mt-12 text-sm text-slate-500">
          <a
            href="https://wellysa.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-wellysa-green font-semibold hover:underline"
          >
            Wellysa.com
          </a>
          <span className="text-slate-400"> · </span>
          <span className="text-slate-600">System prewencji nowej generacji</span>
        </p>
      </div>
    </section>
  )
}
