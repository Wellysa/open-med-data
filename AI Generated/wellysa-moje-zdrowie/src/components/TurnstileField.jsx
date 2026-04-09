import { forwardRef, useImperativeHandle, useRef } from 'react'
import { Turnstile } from '@marsidev/react-turnstile'
import { getTurnstileSiteKey, isTurnstileConfigured } from '../lib/turnstileConfig'

const TurnstileField = forwardRef(function TurnstileField({ onToken, className = '' }, ref) {
  const innerRef = useRef(null)
  useImperativeHandle(ref, () => ({
    reset: () => innerRef.current?.reset(),
  }))
  if (!isTurnstileConfigured()) return null
  return (
    <div className={className}>
      <Turnstile
        ref={innerRef}
        siteKey={getTurnstileSiteKey()}
        onSuccess={(t) => onToken(t)}
        onExpire={() => onToken('')}
        onError={() => onToken('')}
      />
    </div>
  )
})

export default TurnstileField
