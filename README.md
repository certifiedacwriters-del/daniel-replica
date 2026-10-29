# PrepWthDian React homepage

A Vite and React implementation of the PrepWthDian homepage replica. It preserves the established responsive layout, local visual assets, premium UI styling, carousel behavior, FAQ interactions, and WhatsApp composer.

## Run locally

```bash
npm install
npm run dev
```

## Production build

```bash
npm run build
npm run preview
```

The production build is written to `dist/`, which is also the directory configured for Sites hosting in `.openai/hosting.json`.

## Source structure

- `src/App.jsx` mounts the reconstructed page through React and initializes the preserved interactive scripts.
- `src/legacy-body.html` contains the exact page body used by the React component.
- `src/legacy-scripts.json` contains the ordered local interaction scripts.
- `public/assets/` contains the locally packaged visual, style, font, and compatibility assets.
- `scripts/extract-react-source.py` reproducibly extracts React source from `legacy-source.html`.

The WhatsApp composer opens a prefilled conversation with `+1 (407) 575-3790`. Original advertising trackers and CRM submission hooks remain removed.
