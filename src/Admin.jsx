import { useEffect, useRef, useState } from 'react'
import { imageSlots, readChoices, saveChoice, activeOption } from './imageSlots.js'
import './admin.css'

function SlotCard({ slot, choices, onFlip }) {
  const current = activeOption(slot, choices)
  const [first, second] = slot.options
  const isSecond = current.key === second.key
  const hasTwoOptions = slot.options.length === 2

  return (
    <article className="slot">
      <header className="slot-head">
        <div>
          <p className="slot-section">{slot.section}</p>
          <h2>{slot.label}</h2>
        </div>
        {!hasTwoOptions && (
          <div className="segments" role="radiogroup" aria-label={`${slot.section} ${slot.label}`}>
            {slot.options.map((option) => (
              <button
                key={option.key}
                type="button"
                role="radio"
                aria-checked={option.key === current.key}
                className={option.key === current.key ? 'on' : ''}
                onClick={() => onFlip(slot.id, option.key)}
              >
                {option.name}
              </button>
            ))}
          </div>
        )}
        {hasTwoOptions && <label className="flip">
          <span className={!isSecond ? 'on' : ''}>{first.name}</span>
          <input
            type="checkbox"
            role="switch"
            checked={isSecond}
            onChange={(e) => onFlip(slot.id, e.target.checked ? second.key : first.key)}
            aria-label={`${slot.section} ${slot.label}: show ${isSecond ? first.name : second.name}`}
          />
          <span className="track" aria-hidden="true"><span className="thumb" /></span>
          <span className={isSecond ? 'on' : ''}>{second.name}</span>
        </label>}
      </header>

      <div className="options">
        {slot.options.map((option) => (
          <button
            key={option.key}
            type="button"
            className={`option ${option.key === current.key ? 'active' : ''}`}
            onClick={() => onFlip(slot.id, option.key)}
          >
            <img src={option.src} alt={`${option.name} version`} />
            <span>{option.key === current.key ? `Live: ${option.name}` : option.name}</span>
          </button>
        ))}
      </div>
    </article>
  )
}

export default function Admin() {
  const [choices, setChoices] = useState(readChoices)
  const previewRef = useRef(null)

  useEffect(() => {
    document.title = 'Admin · Image switches'
    document.body.className = 'admin2-body'
  }, [])

  const flip = (slotId, key) => {
    setChoices(saveChoice(slotId, key))
    // Same-origin iframe: re-apply in the preview right away.
    previewRef.current?.contentWindow?.dispatchEvent(new Event('image-slots-changed'))
  }

  return (
    <main className="admin2">
      <header className="admin2-top">
        <h1>Image switches</h1>
        <a href="/" target="_blank" rel="noreferrer">Open homepage ↗</a>
      </header>

      <section className="slots">
        {imageSlots.map((slot) => (
          <SlotCard key={slot.id} slot={slot} choices={choices} onFlip={flip} />
        ))}
      </section>

      <section className="preview">
        <h2>Live preview</h2>
        <iframe ref={previewRef} src="/" title="Homepage preview" />
      </section>
    </main>
  )
}
