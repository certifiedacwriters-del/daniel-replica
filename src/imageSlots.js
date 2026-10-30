// Images on the homepage that can be flipped between two versions from /admin2.
// To make another section swappable:
//   1. add data-swap-slot="<id>" to its <img> in legacy-body.html
//   2. add an entry below with the same id and its two image paths
export const imageSlots = [
  {
    id: 'hero-headline',
    section: 'Hero',
    label: 'Headline image',
    options: [
      { key: 'a', name: 'Original', src: '/assets/c452827f192f4b4e.png' },
      { key: 'b', name: 'New', src: '/assets/hero-headline.png' },
      { key: 'c', name: 'Tutor (red)', src: '/assets/hero-headline-tutor.png' },
    ],
    defaultKey: 'c',
  },
  {
    id: 'hero-photo',
    section: 'Hero',
    label: 'Photo',
    options: [
      { key: 'a', name: 'Original', src: '/assets/6ff928485faf7ffe.png' },
      { key: 'b', name: 'Nurse (blue)', src: '/assets/hero-photo-nurse.png' },
      { key: 'c', name: 'Nurse (crimson)', src: '/assets/hero-photo-nurse-crimson.png' },
    ],
    defaultKey: 'c',
  },
]

const STORAGE_KEY = 'image-slot-choices'

export function readChoices() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}
  } catch {
    return {}
  }
}

export function saveChoice(slotId, key) {
  const choices = { ...readChoices(), [slotId]: key }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(choices))
  return choices
}

export function activeOption(slot, choices = readChoices()) {
  const key = choices[slot.id] || slot.defaultKey
  return slot.options.find((option) => option.key === key) || slot.options[0]
}

// Point every tagged <img> on the page at its chosen image.
export function applyChoices(root = document) {
  const choices = readChoices()
  for (const slot of imageSlots) {
    const { src } = activeOption(slot, choices)
    root.querySelectorAll(`img[data-swap-slot="${slot.id}"]`).forEach((img) => {
      if (img.getAttribute('src') !== src) {
        img.removeAttribute('srcset')
        img.setAttribute('src', src)
      }
    })
  }
}

export { STORAGE_KEY }
