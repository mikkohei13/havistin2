`/nappi` is a login-protected Flask page served by `app/routes/nappi.py` (nappi_root) and rendered with `app/templates/nappi.html`.

Frontend logic in `app/static/app/nappi.js` handles the flow: Aloita starts geolocation.watchPosition, Havainto starts MediaRecorder, recording auto-stops at 20s, then audio + lat/lng are posted as multipart to `/nappi/api/transcribe`.

Backend `nappi_transcribe` in `app/routes/nappi.py` validates auth/input, transcribes Finnish speech via OpenAI Audio API (client.audio.transcriptions.create), then extracts structured JSON (species, count, notes) with GPT (chat.completions JSON mode), normalizes output, and returns {species,count,notes,raw_transcript,warnings}.

All persistence is browser-side IndexedDB (`nappi_db / observations`) in `nappi.js`; no server DB. Observations are listed from IndexedDB, and row click opens a modal with details + Leaflet map marker.

Styles are in `app/static/app/nappi.css`. OpenAI key is read from env via `app/app_secrets.py` (`openai_api_key`).