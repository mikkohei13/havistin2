`/havis` is a login-protected Flask page served by `app/routes/havis.py` (havis_root) and rendered with `app/templates/havis.html`.

Frontend logic in `app/static/app/havis.js` handles the flow: Aloita starts geolocation.watchPosition, Havainto starts MediaRecorder, recording auto-stops at 20s, then audio + lat/lng are posted as multipart to `/havis/api/transcribe`.

Backend `havis_transcribe` in `app/routes/havis.py` validates auth/input, transcribes Finnish speech via OpenAI Audio API (client.audio.transcriptions.create), then extracts structured JSON (species, count, notes) with GPT (chat.completions JSON mode), normalizes output, and returns {species,count,notes,raw_transcript,warnings}.

All persistence is browser-side IndexedDB (`havis_db / observations`) in `havis.js`; no server DB. Observations are listed from IndexedDB, and row click opens a modal with details + Leaflet map marker.

Styles are in `app/static/app/havis.css`. Status text is split: `#gps_status` for geolocation messages and `#ui_status` for recording/transcription/IndexedDB and other process UI. OpenAI key is read from env via `app/app_secrets.py` (`openai_api_key`).