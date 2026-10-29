import { useEffect, useLayoutEffect } from 'react'
import legacyMarkup from './legacy-body.html?raw'
import scriptManifest from './legacy-scripts.json'

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
