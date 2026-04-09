export default function Hero() {
  return (
    <section className="border-b border-slate-100 bg-white pt-28 md:pt-36 pb-16 md:pb-24 px-6 md:px-12">
      <div className="mx-auto max-w-3xl text-center">
        <h1 className="text-4xl font-bold leading-tight tracking-tight text-charcoal md:text-5xl lg:text-[3.25rem] lg:leading-[1.08] text-balance">
          Znudziło Ci się czekanie na NFZ? My też nie mamy na to czasu.
        </h1>
        <p className="mx-auto mt-8 max-w-2xl text-lg leading-relaxed text-slate-600 md:text-xl md:leading-relaxed text-pretty">
          Program „Moje Zdrowie” w IKP to dobry kierunek — ale bywa wolny i frustrujący. Zamiast walczyć z formularzami i
          szukać „placówek widmo”, zrób bilans z Wellysa: szybciej, zrozumiale i z interpretacją, która mówi,{' '}
          <strong className="font-semibold text-charcoal">co dalej</strong>.
        </p>
        <div className="mt-10 flex flex-col items-stretch justify-center gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:justify-center">
          <a
            href="#panel-uslug"
            className="inline-flex items-center justify-center gap-2 rounded-card bg-wellysa-green px-8 py-4 text-base font-bold text-white shadow-sm hover:opacity-90 transition-opacity"
            aria-label="Przejdź do panelu usług Wellysa"
          >
            Otwórz panel usług
          </a>
          <a
            href="#system-vs-rzeczywistosc"
            className="inline-flex items-center justify-center gap-2 rounded-card border-2 border-charcoal bg-white px-8 py-4 text-base font-semibold text-charcoal hover:bg-charcoal hover:text-white transition-colors"
            aria-label="Zobacz różnicę między systemem a Wellysa"
          >
            Sprawdź różnicę
          </a>
          <a
            href="#pobierz"
            className="inline-flex items-center justify-center gap-2 rounded-card border border-slate-200 px-8 py-4 text-base font-semibold text-charcoal hover:border-slate-300 hover:bg-section transition-colors"
            aria-label="Przejdź do pobrania aplikacji"
          >
            Pobierz aplikację
          </a>
        </div>
      </div>
    </section>
  )
}
