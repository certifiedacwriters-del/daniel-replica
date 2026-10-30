import { useEffect, useLayoutEffect } from 'react'
import legacyMarkup from './legacy-body.html?raw'
import scriptManifest from './legacy-scripts.json'
import './trusted-logos.css'
import { applyChoices, STORAGE_KEY } from './imageSlots.js'

const bodyClassName = 'home wp-singular page-template-default page page-id-2622 wp-custom-logo wp-embed-responsive wp-theme-hello-elementor hello-elementor-default elementor-default elementor-kit-7 elementor-page elementor-page-2622'

function appendScript(definition) {
  return new Promise((resolve) => {
    const script = document.createElement('script')
    for (const [name, value] of Object.entries(definition.attributes)) {
      if (name !== 'src') script.setAttribute(name, value)
    }

    if (definition.src) {
      script.src = definition.src
      script.onload = resolve
      script.onerror = resolve
    } else {
      script.textContent = definition.content
    }

    document.body.appendChild(script)
    if (!definition.src) resolve()
  })
}

export default function App() {
  useLayoutEffect(() => {
    document.body.className = bodyClassName
    document.documentElement.classList.add('react-replica')
    applyChoices()

    // Re-apply when the choice changes in /admin2 (another tab or the preview iframe).
    const onStorage = (event) => { if (event.key === STORAGE_KEY) applyChoices() }
    const onLocalChange = () => applyChoices()
    window.addEventListener('storage', onStorage)
    window.addEventListener('image-slots-changed', onLocalChange)
    return () => {
      window.removeEventListener('storage', onStorage)
      window.removeEventListener('image-slots-changed', onLocalChange)
    }
  }, [])

  useEffect(() => {
    const loadedScripts = []
    let cancelled = false

    const initializeLegacyPage = async () => {
      for (const definition of scriptManifest) {
        if (cancelled) return
        const before = Array.from(document.body.children)
        await appendScript(definition)
        const appended = Array.from(document.body.children).filter(
          (node) => node.tagName === 'SCRIPT' && !before.includes(node),
        )
        loadedScripts.push(...appended)
      }
      window.dispatchEvent(new Event('load'))
    }

    initializeLegacyPage()
    return () => {
      cancelled = true
      loadedScripts.forEach((script) => script.remove())
    }
  }, [])

  return <div className="legacy-react-page" dangerouslySetInnerHTML={{ __html: legacyMarkup }} />
}
