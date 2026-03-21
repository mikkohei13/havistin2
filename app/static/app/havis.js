(() => {
    const DB_NAME = "havis_db";
    const STORE_NAME = "observations";
    const SESSIONS_STORE = "sessions";
    const DB_VERSION = 2;
    const MAX_RECORDING_MS = 20000;
    const API_URL = "/havis/api/transcribe";

    let db = null;
    let watchId = null;
    let latestCoords = null;
    let recorder = null;
    let recorderStream = null;
    let recorderChunks = [];
    let autoStopTimer = null;
    let isRecording = false;
    let recordingMimeType = "";
    let recordingAction = "";
    let map = null;
    let mapMarker = null;
    let currentSessionId = null;
    let currentSessionStartIso = null;

    const startBtn = document.getElementById("start-btn");
    const sessionActiveEl = document.getElementById("session-active");
    const recordBtn = document.getElementById("record-btn");
    const endSessionBtn = document.getElementById("end-session-btn");
    const submitBtn = document.getElementById("submit-btn");
    const cancelBtn = document.getElementById("cancel-btn");
    const recordingActions = document.getElementById("recording-actions");
    const gpsStatusEl = document.getElementById("gps_status");
    const uiStatusEl = document.getElementById("ui_status");
    const observationsList = document.getElementById("observations-list");
    const modal = document.getElementById("detail-modal");
    const modalClose = document.getElementById("modal-close");
    const modalBody = document.getElementById("modal-body");
    const modalMap = document.getElementById("modal-map");

    function setGpsStatus(text) {
        gpsStatusEl.textContent = text;
    }

    function setUiStatus(text) {
        uiStatusEl.textContent = text;
    }

    function setControlsIdle() {
        startBtn.classList.remove("hidden");
        sessionActiveEl.classList.add("hidden");
        recordBtn.disabled = false;
        recordingActions.classList.add("hidden");
    }

    function setControlsSessionReady() {
        startBtn.classList.add("hidden");
        sessionActiveEl.classList.remove("hidden");
        recordBtn.classList.remove("hidden");
        endSessionBtn.classList.remove("hidden");
        recordBtn.disabled = false;
        endSessionBtn.disabled = false;
        recordingActions.classList.add("hidden");
    }

    function setControlsRecording() {
        recordBtn.classList.add("hidden");
        endSessionBtn.classList.add("hidden");
        recordingActions.classList.remove("hidden");
        submitBtn.disabled = false;
        cancelBtn.disabled = false;
    }

    function formatAccuracy(value) {
        if (!Number.isFinite(value)) {
            return "";
        }
        return `${Math.round(value)} m`;
    }

    function gpsErrorLabel(errorCode) {
        if (errorCode === 1) {
            return "Paikannus on estetty";
        }
        if (errorCode === 2) {
            return "Sijaintia ei saatu";
        }
        if (errorCode === 3) {
            return "Paikannus aikakatkaistiin";
        }
        return "Tuntematon virhe";
    }

    function toDisplayTime(isoString) {
        const date = new Date(isoString);
        if (Number.isNaN(date.getTime())) {
            return isoString;
        }
        return date.toLocaleString("fi-FI");
    }

    function toNumOrNull(value) {
        if (value === "" || value === null || value === undefined) {
            return null;
        }
        const num = Number(value);
        return Number.isFinite(num) ? num : null;
    }

    function openDb() {
        return new Promise((resolve, reject) => {
            const req = indexedDB.open(DB_NAME, DB_VERSION);
            req.onupgradeneeded = (event) => {
                const nextDb = req.result;
                const oldVersion = event.oldVersion;
                if (!nextDb.objectStoreNames.contains(STORE_NAME)) {
                    nextDb.createObjectStore(STORE_NAME, { keyPath: "id" });
                }
                if (oldVersion < 2 && !nextDb.objectStoreNames.contains(SESSIONS_STORE)) {
                    nextDb.createObjectStore(SESSIONS_STORE, { keyPath: "id" });
                }
            };
            req.onsuccess = () => resolve(req.result);
            req.onerror = () => reject(req.error);
        });
    }

    function putSession(session) {
        return new Promise((resolve, reject) => {
            const tx = db.transaction(SESSIONS_STORE, "readwrite");
            const store = tx.objectStore(SESSIONS_STORE);
            store.put(session);
            tx.oncomplete = () => resolve();
            tx.onerror = () => reject(tx.error);
        });
    }

    function getSession(id) {
        return new Promise((resolve, reject) => {
            const tx = db.transaction(SESSIONS_STORE, "readonly");
            const store = tx.objectStore(SESSIONS_STORE);
            const req = store.get(id);
            req.onsuccess = () => resolve(req.result);
            req.onerror = () => reject(req.error);
        });
    }

    function putObservation(observation) {
        return new Promise((resolve, reject) => {
            const tx = db.transaction(STORE_NAME, "readwrite");
            const store = tx.objectStore(STORE_NAME);
            store.put(observation);
            tx.oncomplete = () => resolve();
            tx.onerror = () => reject(tx.error);
        });
    }

    function getAllObservations() {
        return new Promise((resolve, reject) => {
            const tx = db.transaction(STORE_NAME, "readonly");
            const store = tx.objectStore(STORE_NAME);
            const req = store.getAll();
            req.onsuccess = () => resolve(req.result || []);
            req.onerror = () => reject(req.error);
        });
    }

    function rowHtml(observation) {
        const species = observation.species || "Tunnistamaton laji";
        const count = observation.count === "" ? "-" : String(observation.count);
        const notes = observation.notes || "";
        const badges = [];

        if (observation.has_error) {
            badges.push('<span class="badge badge-error">Virhe</span>');
        }
        if (observation.species_unrecognized) {
            badges.push('<span class="badge badge-warn">Ei lajia</span>');
        }
        if (observation.lat === "" || observation.lng === "") {
            badges.push('<span class="badge badge-warn">Ei GPS</span>');
        }

        return `
            <button class="observation-row" data-id="${observation.id}" type="button">
                <div class="observation-main">
                    <strong>${species}</strong>
                    <span>x ${count}</span>
                </div>
                <div class="observation-meta">${toDisplayTime(observation.timestamp)}</div>
                <div class="observation-notes">${notes}</div>
                <div class="observation-badges">${badges.join("")}</div>
            </button>
        `;
    }

    async function renderList() {
        const all = await getAllObservations();
        all.sort((a, b) => String(b.timestamp).localeCompare(String(a.timestamp)));
        if (all.length === 0) {
            observationsList.innerHTML = '<p class="empty-text">Ei vielä havaintoja.</p>';
            return;
        }
        observationsList.innerHTML = all.map(rowHtml).join("");
        observationsList.querySelectorAll(".observation-row").forEach((row) => {
            row.addEventListener("click", () => {
                const id = row.dataset.id;
                const observation = all.find((item) => item.id === id);
                if (observation) {
                    openModal(observation);
                }
            });
        });
    }

    function stopMap() {
        if (map) {
            map.remove();
            map = null;
            mapMarker = null;
        }
        modalMap.style.display = "none";
    }

    function openModal(observation) {
        modalBody.innerHTML = `
            <p><strong>Laji:</strong> ${observation.species || "Tunnistamaton laji"}</p>
            <p><strong>Maara:</strong> ${observation.count === "" ? "-" : observation.count}</p>
            <p><strong>Aika:</strong> ${toDisplayTime(observation.timestamp)}</p>
            ${
                observation.sessionStartedAt
                    ? `<p><strong>Havaintoerä (aloitettu):</strong> ${toDisplayTime(observation.sessionStartedAt)}</p>`
                    : ""
            }
            <p><strong>Muistiinpanot:</strong> ${observation.notes || "-"}</p>
            <p><strong>Litterointi:</strong> ${observation.raw_transcript || "-"}</p>
            <p><strong>Sijainti:</strong> ${observation.lat || "-"}, ${observation.lng || "-"}</p>
            ${observation.error_message ? `<p><strong>Virhe:</strong> ${observation.error_message}</p>` : ""}
        `;

        stopMap();
        const lat = toNumOrNull(observation.lat);
        const lng = toNumOrNull(observation.lng);
        if (lat !== null && lng !== null) {
            modalMap.style.display = "block";
            map = L.map("modal-map");
            L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                attribution: "&copy; OpenStreetMap",
            }).addTo(map);
            map.setView([lat, lng], 14);
            mapMarker = L.marker([lat, lng]).addTo(map);
        }

        modal.classList.remove("hidden");
    }

    function closeModal() {
        modal.classList.add("hidden");
        stopMap();
    }

    function stopRecorderStream() {
        if (!recorderStream) {
            return;
        }
        recorderStream.getTracks().forEach((track) => track.stop());
        recorderStream = null;
    }

    function clearAutoStopTimer() {
        if (autoStopTimer !== null) {
            clearTimeout(autoStopTimer);
            autoStopTimer = null;
        }
    }

    async function startGps() {
        if (!("geolocation" in navigator)) {
            setGpsStatus("GPS ei ole saatavilla. Et voi kirjata havaintoja.");
            setControlsSessionReady();
            return;
        }
        if (watchId !== null) {
            setControlsSessionReady();
            return;
        }

        setGpsStatus("Kaynnistetään GPS...");
        watchId = navigator.geolocation.watchPosition(
            (position) => {
                latestCoords = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                };
                const accuracy = formatAccuracy(position.coords.accuracy);
                setGpsStatus(
                    accuracy
                        ? `GPS:n tarkkuus ${accuracy}.`
                        : "GPS:n tarkkuus tuntematon."
                );
            },
            (error) => {
                setGpsStatus(
                    `GPS ei ole saatavilla (${gpsErrorLabel(error.code)}). Et voi kirjata havaintoja.`
                );
            },
            { enableHighAccuracy: true, maximumAge: 5000, timeout: 10000 }
        );
        setControlsSessionReady();
    }

    function buildId() {
        if (window.crypto && window.crypto.randomUUID) {
            return window.crypto.randomUUID();
        }
        return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    }

    function extensionFromMimeType(mimeType) {
        const normalized = String(mimeType || "").toLowerCase();
        if (normalized.includes("webm")) {
            return "webm";
        }
        if (normalized.includes("mp4") || normalized.includes("m4a")) {
            return "m4a";
        }
        if (normalized.includes("wav")) {
            return "wav";
        }
        if (normalized.includes("mpeg") || normalized.includes("mp3")) {
            return "mp3";
        }
        if (normalized.includes("ogg")) {
            return "ogg";
        }
        return "webm";
    }

    async function sendAudio(blob, coordsSnapshot, mimeType) {
        const formData = new FormData();
        const ext = extensionFromMimeType(mimeType);
        formData.append("audio", blob, `recording.${ext}`);
        if (coordsSnapshot.lat !== "") {
            formData.append("lat", String(coordsSnapshot.lat));
        }
        if (coordsSnapshot.lng !== "") {
            formData.append("lng", String(coordsSnapshot.lng));
        }

        const response = await fetch(API_URL, {
            method: "POST",
            body: formData,
        });

        const payload = await response.json().catch(() => ({}));
        if (!response.ok) {
            const message = payload.message || "Palvelinvirhe.";
            throw new Error(message);
        }
        return payload;
    }

    async function saveErrorObservation(message, coordsSnapshot) {
        const observation = {
            id: buildId(),
            timestamp: new Date().toISOString(),
            sessionId: currentSessionId || "",
            sessionStartedAt: currentSessionStartIso || "",
            lat: coordsSnapshot.lat === "" ? "" : String(coordsSnapshot.lat),
            lng: coordsSnapshot.lng === "" ? "" : String(coordsSnapshot.lng),
            species: "",
            count: "",
            notes: "",
            raw_transcript: "",
            has_error: true,
            error_message: message,
            species_unrecognized: true,
        };
        await putObservation(observation);
    }

    async function startRecording() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            setUiStatus("Tällä selaimella ei voi äänittää.");
            return;
        }

        recordBtn.disabled = true;

        try {
            recorderStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const candidateMimeTypes = [
                "audio/webm;codecs=opus",
                "audio/webm",
                "audio/mp4",
                "audio/ogg;codecs=opus",
                "audio/ogg",
            ];
            let options = {};
            for (const candidate of candidateMimeTypes) {
                if (window.MediaRecorder.isTypeSupported(candidate)) {
                    options = { mimeType: candidate };
                    break;
                }
            }
            recorder = Object.keys(options).length > 0
                ? new MediaRecorder(recorderStream, options)
                : new MediaRecorder(recorderStream);
            recordingMimeType = recorder.mimeType || "";
            recorderChunks = [];
            isRecording = true;
            recordingAction = "";
            setControlsRecording();

            recorder.addEventListener("dataavailable", (event) => {
                if (event.data && event.data.size > 0) {
                    recorderChunks.push(event.data);
                }
            });

            recorder.addEventListener("stop", async () => {
                const action = recordingAction;
                const coordsSnapshot = {
                    lat: latestCoords ? latestCoords.lat : "",
                    lng: latestCoords ? latestCoords.lng : "",
                };
                if (action !== "submit") {
                    setUiStatus("Havainto peruutettu. Voit aloittaa uuden havainnon.");
                    setControlsSessionReady();
                    isRecording = false;
                    clearAutoStopTimer();
                    stopRecorderStream();
                    recordingMimeType = "";
                    recorderChunks = [];
                    recordingAction = "";
                    return;
                }

                const blobMimeType = recordingMimeType || "audio/webm";
                const blob = new Blob(recorderChunks, { type: blobMimeType });
                setUiStatus("Analysoidaan havaintoa...");

                try {
                    const payload = await sendAudio(blob, coordsSnapshot, blobMimeType);
                    const observation = {
                        id: buildId(),
                        timestamp: new Date().toISOString(),
                        sessionId: currentSessionId || "",
                        sessionStartedAt: currentSessionStartIso || "",
                        lat: coordsSnapshot.lat === "" ? "" : String(coordsSnapshot.lat),
                        lng: coordsSnapshot.lng === "" ? "" : String(coordsSnapshot.lng),
                        species: payload.species || "",
                        count: payload.count === undefined || payload.count === null ? "" : payload.count,
                        notes: payload.notes || "",
                        raw_transcript: payload.raw_transcript || "",
                        has_error: false,
                        error_message: "",
                        species_unrecognized: (payload.species || "").trim() === "",
                    };
                    await putObservation(observation);
                    setUiStatus("Havainto tallennettu.");
                } catch (error) {
                    await saveErrorObservation(error.message || "Tuntematon virhe.", coordsSnapshot);
                    setUiStatus("Yritä uudelleen.");
                } finally {
                    await renderList();
                    isRecording = false;
                    setControlsSessionReady();
                    clearAutoStopTimer();
                    stopRecorderStream();
                    recordingMimeType = "";
                    recorderChunks = [];
                    recordingAction = "";
                }
            });

            recorder.start();
            setUiStatus("Äänitys käynnissä..");
            autoStopTimer = setTimeout(() => {
                if (recorder && recorder.state === "recording") {
                    setUiStatus("20 sekuntia täynnä, lopetetaan äänitys...");
                    stopRecording("submit");
                }
            }, MAX_RECORDING_MS);
        } catch (_) {
            setUiStatus("Mikrofonin käynnistys epäonnistui.");
            clearAutoStopTimer();
            stopRecorderStream();
            isRecording = false;
            setControlsSessionReady();
        }
    }

    function stopRecording(action) {
        if (recorder && recorder.state === "recording") {
            recordingAction = action;
            submitBtn.disabled = true;
            cancelBtn.disabled = true;
            recorder.stop();
        }
    }

    async function init() {
        try {
            db = await openDb();
            await renderList();
            setGpsStatus("");
            setUiStatus("Aloita havaintoerä Aloita-painikkeella.");
        } catch (_) {
            setGpsStatus("");
            setUiStatus("Tallennustilan alustus epäonnistui.");
        }

        startBtn.addEventListener("click", async () => {
            if (!db) {
                return;
            }
            try {
                const startedAt = new Date().toISOString();
                const session = { id: buildId(), startedAt, endedAt: null };
                await putSession(session);
                currentSessionId = session.id;
                currentSessionStartIso = startedAt;
                await startGps();
                setUiStatus(`Havaintoerä käynnissä (aloitettu ${toDisplayTime(startedAt)}).`);
            } catch (_) {
                setUiStatus("Havaintoerän aloitus epäonnistui.");
            }
        });

        endSessionBtn.addEventListener("click", async () => {
            if (!db || isRecording || !currentSessionId) {
                return;
            }
            if (
                !window.confirm(
                    "Lopetetaanko havaintoerä? Voit aloittaa uuden erän myöhemmin Aloita-painikkeella."
                )
            ) {
                return;
            }
            try {
                const session = await getSession(currentSessionId);
                if (session) {
                    session.endedAt = new Date().toISOString();
                    await putSession(session);
                }
                currentSessionId = null;
                currentSessionStartIso = null;
                setControlsIdle();
                setUiStatus("Havaintoerä päättyi. Voit aloittaa uuden havaintoerän.");
            } catch (_) {
                setUiStatus("Havaintoerän päättäminen epäonnistui.");
            }
        });

        recordBtn.addEventListener("click", async () => {
            await startRecording();
        });
        submitBtn.addEventListener("click", () => {
            if (!isRecording) {
                return;
            }
            setUiStatus("Analysoidaan havaintoa...");
            stopRecording("submit");
        });
        cancelBtn.addEventListener("click", () => {
            if (!isRecording) {
                return;
            }
            setUiStatus("Peruutetaan havaintoa...");
            stopRecording("cancel");
        });

        modalClose.addEventListener("click", closeModal);
        modal.addEventListener("click", (event) => {
            if (event.target === modal) {
                closeModal();
            }
        });
    }

    init();
})();
