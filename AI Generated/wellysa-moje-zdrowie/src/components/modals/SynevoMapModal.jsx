import { useEffect, useRef } from 'react'
import ModalShell from './ModalShell'
import { SYNEVO_POINTS } from '../../data/synevoPoints'

export default function SynevoMapModal({ open, onClose }) {
  const mapEl = useRef(null)
  const mapInstance = useRef(null)

  useEffect(() => {
    if (!open || !mapEl.current) return

    let cancelled = false

    const run = async () => {
      const L = (await import('leaflet')).default
      if (cancelled || !mapEl.current) return

      if (mapInstance.current) {
        mapInstance.current.remove()
        mapInstance.current = null
      }

      delete L.Icon.Default.prototype._getIconUrl
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
        iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
      })

      const map = L.map(mapEl.current, { scrollWheelZoom: true }).setView([52.1, 19.4], 6)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap',
        maxZoom: 19,
      }).addTo(map)

      SYNEVO_POINTS.forEach((p) => {
        L.marker([p.lat, p.lng])
          .addTo(map)
          .bindPopup(`<strong>${p.name}</strong><br/>${p.address}, ${p.city}`)
      })

      mapInstance.current = map
      setTimeout(() => map.invalidateSize(), 200)
    }

    run()

    return () => {
      cancelled = true
      if (mapInstance.current) {
        mapInstance.current.remove()
        mapInstance.current = null
      }
    }
  }, [open])

  return (
    <ModalShell
      open={open}
      onClose={onClose}
      wide
      title="Punkty partnerskie"
      subtitle="Lokalizacje punktów, z którymi współpracujemy, na mapie — listę w projekcie możesz zastąpić własnym zestawem adresów."
    >
      <div className="space-y-3">
        <p className="text-xs text-slate-500">
          Łącznie na mapie: <strong>{SYNEVO_POINTS.length}</strong> punktów (demo). Możesz przesłać CSV z adresami — dopiszemy import.
        </p>
        <div ref={mapEl} className="h-[min(60vh,420px)] w-full overflow-hidden rounded-2xl border border-slate-200 bg-slate-100" />
      </div>
    </ModalShell>
  )
}
