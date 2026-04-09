import { useState } from 'react'
import { Menu, X } from 'lucide-react'

export default function Header() {
  const [open, setOpen] = useState(false)

  const navLinks = [
    { href: '#panel-uslug', label: 'Panel usług' },
    { href: '#system-vs-rzeczywistosc', label: 'Dlaczego Wellysa' },
    { href: '#jak-dziala', label: 'Jak to działa' },
    { href: '#pobierz', label: 'Pobierz' },
  ]

  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-slate-200/50 bg-white/85 backdrop-blur-xl">
      <nav className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between gap-4">
        <a
          href="https://wellysa.com/"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center shrink-0 py-0.5 hover:opacity-85 focus:outline-none focus-visible:ring-2 focus-visible:ring-wellysa-green focus-visible:ring-offset-2 rounded-sm transition-opacity"
          aria-label="Wellysa — strona główna"
        >
          <img
            src="/images/wellysa-logo.png"
            width={240}
            height={70}
            alt=""
            className="h-8 w-auto md:h-9"
            decoding="async"
          />
        </a>

        <ul className="hidden lg:flex items-center gap-8 text-sm">
          {navLinks.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="text-charcoal hover:text-wellysa-green transition-colors font-medium whitespace-nowrap"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        <a
          href="#pobierz"
          className="hidden md:inline-flex px-6 py-2.5 rounded-card bg-wellysa-green text-white text-sm font-semibold hover:opacity-90 transition-opacity shrink-0"
        >
          Pobierz aplikację
        </a>

        <button
          type="button"
          className="lg:hidden p-2"
          onClick={() => setOpen(!open)}
          aria-label="Menu"
        >
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </nav>

      {open && (
        <div className="lg:hidden border-t border-slate-100 bg-white/98 px-6 py-4">
          <ul className="flex flex-col gap-3">
            {navLinks.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  className="block text-charcoal hover:text-wellysa-green font-medium py-1"
                  onClick={() => setOpen(false)}
                >
                  {link.label}
                </a>
              </li>
            ))}
            <li>
              <a
                href="#pobierz"
                className="block px-6 py-3 rounded-card bg-wellysa-green text-white font-semibold text-center mt-2"
                onClick={() => setOpen(false)}
              >
                Pobierz aplikację
              </a>
            </li>
          </ul>
        </div>
      )}
    </header>
  )
}
