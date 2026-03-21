(() => {
    const DB_NAME = "havis_db";
    const STORE_NAME = "observations";
    const SESSIONS_STORE = "sessions";
    const DB_VERSION = 3;
    const LS_ACTIVE_SESSION_KEY = "havis_active_session";
    const MAX_RECORDING_MS = 20000;
    const API_URL = "/havis/api/transcribe";

    function normalizeUserId(value) {
        if (value === null || value === undefined) {
            return "";
        }
        return String(value);
    }

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
    let sessionStatusTimer = null;
    let modalScrollLockY = 0;
    let modalBodyScrollLocked = false;
    let modalObservation = null;
    let modalEditLocked = false;
    let recordingMode = null;

    const currentUserId = normalizeUserId(
        typeof window.HAVIS_USER_ID !== "undefined" ? window.HAVIS_USER_ID : ""
    );

    const startBtn = document.getElementById("start-btn");
    const sessionActiveEl = document.getElementById("session-active");
    const recordBtn = document.getElementById("record-btn");
    const endSessionBtn = document.getElementById("end-session-btn");
    const submitBtn = document.getElementById("submit-btn");
    const cancelBtn = document.getElementById("cancel-btn");
    const recordingActions = document.getElementById("recording-actions");
    const gpsStatusEl = document.getElementById("gps_status");
    const sessionStatusEl = document.getElementById("session_status");
    const uiStatusEl = document.getElementById("ui_status");
    const observationsList = document.getElementById("observations-list");
    const modal = document.getElementById("detail-modal");
    const modalClose = document.getElementById("modal-close");
    const modalBody = document.getElementById("modal-body");
    const modalMap = document.getElementById("modal-map");
    const modalEditBtn = document.getElementById("modal-edit-btn");
    const modalRecordingActions = document.getElementById("modal-recording-actions");
    const modalSubmitBtn = document.getElementById("modal-submit-btn");
    const modalCancelBtn = document.getElementById("modal-cancel-btn");
    const modalProcessStatusEl = document.getElementById("modal-process-status");

    function setGpsStatus(text) {
        gpsStatusEl.textContent = text;
    }

    function setUiStatus(text) {
        uiStatusEl.textContent = text;
    }

    function setModalEditStatus(text) {
        if (!modalProcessStatusEl) {
            return;
        }
        if (text) {
            modalProcessStatusEl.textContent = text;
            modalProcessStatusEl.classList.remove("hidden");
        } else {
            modalProcessStatusEl.textContent = "";
            modalProcessStatusEl.classList.add("hidden");
        }
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

    function pad2(n) {
        return String(n).padStart(2, "0");
    }

    function formatSessionStartStampFi(isoString) {
        const date = new Date(isoString);
        if (Number.isNaN(date.getTime())) {
            return "";
        }
        const d = date.getDate();
        const m = date.getMonth() + 1;
        const yyyy = date.getFullYear();
        return `${d}.${m}.${yyyy} klo ${pad2(date.getHours())}.${pad2(date.getMinutes())}`;
    }

    function formatMinutesAgoPartFi(isoString) {
        const start = new Date(isoString).getTime();
        if (Number.isNaN(start)) {
            return "";
        }
        const mins = Math.floor((Date.now() - start) / 60000);
        if (mins <= 0) {
            return "0 minuuttia";
        }
        if (mins === 1) {
            return "1 minuutti";
        }
        return `${mins} minuuttia`;
    }

    function buildSessionOngoingStatusLine(isoString) {
        const stamp = formatSessionStartStampFi(isoString);
        const ago = formatMinutesAgoPartFi(isoString);
        if (!stamp || !ago) {
            return "Havaintoerä käynnissä.";
        }
        return `Havaintoerä aloitettu ${ago} sitten (${stamp})`;
    }

    function updateSessionStatusText() {
        if (!sessionStatusEl || !currentSessionStartIso) {
            return;
        }
        sessionStatusEl.textContent = buildSessionOngoingStatusLine(currentSessionStartIso);
    }

    function stopSessionStatusTicker() {
        if (sessionStatusTimer !== null) {
            clearInterval(sessionStatusTimer);
            sessionStatusTimer = null;
        }
    }

    function startSessionStatusTicker() {
        stopSessionStatusTicker();
        sessionStatusTimer = window.setInterval(() => {
            if (currentSessionStartIso) {
                updateSessionStatusText();
            }
        }, 30000);
    }

    function syncSessionStatusLine() {
        if (!sessionStatusEl) {
            return;
        }
        if (currentSessionId && currentSessionStartIso) {
            sessionStatusEl.classList.remove("hidden");
            updateSessionStatusText();
            startSessionStatusTicker();
        } else {
            sessionStatusEl.classList.add("hidden");
            sessionStatusEl.textContent = "";
            stopSessionStatusTicker();
        }
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
            req.onupgradeneeded = () => {
                const nextDb = req.result;
                if (!nextDb.objectStoreNames.contains(STORE_NAME)) {
                    nextDb.createObjectStore(STORE_NAME, { keyPath: "id" });
                }
                if (!nextDb.objectStoreNames.contains(SESSIONS_STORE)) {
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

    function getAllSessions() {
        return new Promise((resolve, reject) => {
            const tx = db.transaction(SESSIONS_STORE, "readonly");
            const store = tx.objectStore(SESSIONS_STORE);
            const req = store.getAll();
            req.onsuccess = () => resolve(req.result || []);
            req.onerror = () => reject(req.error);
        });
    }

    function isSessionOpen(s) {
        return s && (s.endedAt === null || s.endedAt === undefined || s.endedAt === "");
    }

    function sessionHasUserId(s) {
        return typeof s.userId === "string" && s.userId.length > 0;
    }

    function reconcileActiveSessionPointer() {
        try {
            const raw = localStorage.getItem(LS_ACTIVE_SESSION_KEY);
            if (!raw) {
                return;
            }
            const p = JSON.parse(raw);
            if (normalizeUserId(p.userId) !== currentUserId) {
                localStorage.removeItem(LS_ACTIVE_SESSION_KEY);
            }
        } catch (_) {
            localStorage.removeItem(LS_ACTIVE_SESSION_KEY);
        }
    }

    function persistActiveSessionPointer() {
        if (!currentUserId || !currentSessionId || !currentSessionStartIso) {
            return;
        }
        try {
            localStorage.setItem(
                LS_ACTIVE_SESSION_KEY,
                JSON.stringify({
                    userId: currentUserId,
                    sessionId: currentSessionId,
                    sessionStartedAt: currentSessionStartIso,
                })
            );
        } catch (_) {
            /* quota or private mode */
        }
    }

    function clearActiveSessionPointer() {
        try {
            localStorage.removeItem(LS_ACTIVE_SESSION_KEY);
        } catch (_) {
            /* ignore */
        }
    }

    async function resumeOpenSession() {
        if (!db || !currentUserId) {
            return false;
        }
        const all = await getAllSessions();
        const openForUser = all.filter(
            (s) => sessionHasUserId(s) && s.userId === currentUserId && isSessionOpen(s)
        );
        if (openForUser.length === 0) {
            clearActiveSessionPointer();
            return false;
        }

        openForUser.sort((a, b) => String(b.startedAt).localeCompare(String(a.startedAt)));
        const chosen = openForUser[0];
        if (openForUser.length > 1) {
            const now = new Date().toISOString();
            for (let i = 1; i < openForUser.length; i++) {
                const s = openForUser[i];
                s.endedAt = now;
                await putSession(s);
            }
        }

        const stored = await getSession(chosen.id);
        if (!stored || !isSessionOpen(stored)) {
            clearActiveSessionPointer();
            return false;
        }

        currentSessionId = stored.id;
        currentSessionStartIso = stored.startedAt;
        persistActiveSessionPointer();
        setControlsSessionReady();
        await startGps();
        syncSessionStatusLine();
        return true;
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

    function sessionGroupKey(observation) {
        const sid = observation.sessionId;
        if (sid !== undefined && sid !== null && String(sid).trim() !== "") {
            return `id:${sid}`;
        }
        const started = observation.sessionStartedAt;
        if (started !== undefined && started !== null && String(started).trim() !== "") {
            return `at:${started}`;
        }
        return "legacy";
    }

    function groupObservationsBySession(observations) {
        const buckets = new Map();
        for (const obs of observations) {
            const key = sessionGroupKey(obs);
            if (!buckets.has(key)) {
                buckets.set(key, []);
            }
            buckets.get(key).push(obs);
        }
        const entries = Array.from(buckets.entries());
        for (const [, items] of entries) {
            items.sort((a, b) => String(b.timestamp).localeCompare(String(a.timestamp)));
        }
        entries.sort((a, b) => {
            const maxIn = (items) => {
                let max = 0;
                for (const o of items) {
                    const t = new Date(o.timestamp).getTime();
                    if (!Number.isNaN(t) && t > max) {
                        max = t;
                    }
                }
                return max;
            };
            return maxIn(b[1]) - maxIn(a[1]);
        });
        return entries;
    }

    function sessionStartedIsoForGroup(key, items) {
        if (key === "legacy") {
            return "";
        }
        if (key.startsWith("at:")) {
            return key.slice(3);
        }
        if (key.startsWith("id:")) {
            for (const o of items) {
                const s = o.sessionStartedAt;
                if (s !== undefined && s !== null && String(s).trim() !== "") {
                    return s;
                }
            }
        }
        return "";
    }

    function observationGroupHeaderHtml(key, items) {
        if (key === "legacy") {
            return '<div class="observation-group-header">Ei tallennettua havaintoerää</div>';
        }
        const iso = sessionStartedIsoForGroup(key, items);
        const stamp = iso ? formatSessionStartStampFi(iso) : "";
        const label = stamp
            ? `Havaintoerä ${stamp}`
            : "Havaintoerä";
        return `<div class="observation-group-header">${label}</div>`;
    }

    function observationGroupsHtml(groupEntries) {
        return groupEntries
            .map(
                ([key, items]) =>
                    `<div class="observation-group">${observationGroupHeaderHtml(key, items)}${items
                        .map(rowHtml)
                        .join("")}</div>`
            )
            .join("");
    }

    async function renderList() {
        const all = await getAllObservations();
        if (all.length === 0) {
            observationsList.innerHTML = '<p class="empty-text">Ei vielä havaintoja.</p>';
            return;
        }
        const groupEntries = groupObservationsBySession(all);
        const flatOrdered = groupEntries.flatMap(([, items]) => items);
        observationsList.innerHTML = observationGroupsHtml(groupEntries);
        observationsList.querySelectorAll(".observation-row").forEach((row) => {
            row.addEventListener("click", () => {
                if (modalEditLocked) {
                    return;
                }
                const id = row.dataset.id;
                const observation = flatOrdered.find((item) => item.id === id);
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

    function observationDetailHtml(observation) {
        return `
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
    }

    function setModalFooterIdle() {
        modalEditBtn.classList.remove("hidden");
        modalRecordingActions.classList.add("hidden");
        modalSubmitBtn.disabled = false;
        modalCancelBtn.disabled = false;
        modalEditBtn.disabled = false;
    }

    function setModalFooterRecording() {
        modalEditBtn.classList.add("hidden");
        modalRecordingActions.classList.remove("hidden");
        modalSubmitBtn.disabled = false;
        modalCancelBtn.disabled = false;
    }

    function lockBodyScrollForModal() {
        if (modalBodyScrollLocked) {
            return;
        }
        modalScrollLockY = window.scrollY;
        document.body.style.position = "fixed";
        document.body.style.top = `-${modalScrollLockY}px`;
        document.body.style.width = "100%";
        modalBodyScrollLocked = true;
    }

    function unlockBodyScrollForModal() {
        if (!modalBodyScrollLocked) {
            return;
        }
        document.body.style.position = "";
        document.body.style.top = "";
        document.body.style.width = "";
        window.scrollTo(0, modalScrollLockY);
        modalBodyScrollLocked = false;
    }

    function openModal(observation) {
        modalObservation = { ...observation };
        modalBody.innerHTML = observationDetailHtml(modalObservation);
        setModalFooterIdle();
        setModalEditStatus("");
        modalEditLocked = false;
        modalClose.disabled = false;

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

        lockBodyScrollForModal();
        modal.classList.remove("hidden");
        if (map) {
            requestAnimationFrame(() => {
                map.invalidateSize();
            });
        }
    }

    function closeModal() {
        if (modalEditLocked) {
            return;
        }
        modal.classList.add("hidden");
        modalObservation = null;
        setModalEditStatus("");
        stopMap();
        unlockBodyScrollForModal();
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

    async function saveErrorObservationEdit(message, baseline) {
        const observation = {
            ...baseline,
            species: "",
            count: "",
            notes: "",
            raw_transcript: "",
            has_error: true,
            error_message: message,
            species_unrecognized: true,
        };
        await putObservation(observation);
        modalObservation = observation;
        modalBody.innerHTML = observationDetailHtml(observation);
    }

    async function beginAudioRecording(mode) {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            setUiStatus("Tällä selaimella ei voi äänittää.");
            if (mode === "session") {
                recordBtn.disabled = false;
                setControlsSessionReady();
            } else {
                modalEditLocked = false;
                modalClose.disabled = false;
                recordBtn.disabled = false;
                setModalFooterIdle();
                setModalEditStatus("Tällä selaimella ei voi äänittää.");
            }
            return;
        }

        if (mode === "session") {
            recordBtn.disabled = true;
        } else {
            recordBtn.disabled = true;
        }

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
            recordingMode = mode;
            if (mode === "session") {
                setControlsRecording();
            } else {
                setModalEditStatus("");
                setModalFooterRecording();
            }

            recorder.addEventListener("dataavailable", (event) => {
                if (event.data && event.data.size > 0) {
                    recorderChunks.push(event.data);
                }
            });

            recorder.addEventListener("stop", async () => {
                const recMode = recordingMode;
                recordingMode = null;
                const action = recordingAction;

                if (recMode === "session") {
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
                    return;
                }

                if (recMode === "modal-edit") {
                    if (action !== "submit") {
                        setUiStatus("Muokkaus peruutettu.");
                        setModalEditStatus("Muokkaus peruutettu.");
                        setModalFooterIdle();
                        modalEditLocked = false;
                        modalClose.disabled = false;
                        recordBtn.disabled = false;
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
                    setModalEditStatus("Analysoidaan havaintoa...");

                    try {
                        const payload = await sendAudio(blob, { lat: "", lng: "" }, blobMimeType);
                        const base = modalObservation;
                        const updated = {
                            ...base,
                            species: payload.species || "",
                            count: payload.count === undefined || payload.count === null ? "" : payload.count,
                            notes: payload.notes || "",
                            raw_transcript: payload.raw_transcript || "",
                            has_error: false,
                            error_message: "",
                            species_unrecognized: (payload.species || "").trim() === "",
                        };
                        await putObservation(updated);
                        modalObservation = updated;
                        modalBody.innerHTML = observationDetailHtml(updated);
                        setUiStatus("Havainto päivitetty.");
                        setModalEditStatus("Havainto päivitetty.");
                    } catch (error) {
                        await saveErrorObservationEdit(
                            error.message || "Tuntematon virhe.",
                            modalObservation
                        );
                        setUiStatus("Yritä uudelleen.");
                        setModalEditStatus("Yritä uudelleen.");
                    } finally {
                        await renderList();
                        isRecording = false;
                        setModalFooterIdle();
                        modalEditLocked = false;
                        modalClose.disabled = false;
                        recordBtn.disabled = false;
                        clearAutoStopTimer();
                        stopRecorderStream();
                        recordingMimeType = "";
                        recorderChunks = [];
                        recordingAction = "";
                    }
                }
            });

            recorder.start();
            setUiStatus("Äänitys käynnissä..");
            if (mode === "modal-edit") {
                setModalEditStatus("Äänitys käynnissä..");
            }
            autoStopTimer = setTimeout(() => {
                if (recorder && recorder.state === "recording") {
                    setUiStatus("20 sekuntia täynnä, lopetetaan äänitys...");
                    if (mode === "modal-edit") {
                        setModalEditStatus("20 sekuntia täynnä, lopetetaan äänitys...");
                    }
                    stopRecording("submit");
                }
            }, MAX_RECORDING_MS);
        } catch (_) {
            setUiStatus("Mikrofonin käynnistys epäonnistui.");
            clearAutoStopTimer();
            stopRecorderStream();
            isRecording = false;
            recordingMode = null;
            if (mode === "session") {
                setControlsSessionReady();
            } else {
                modalEditLocked = false;
                modalClose.disabled = false;
                recordBtn.disabled = false;
                setModalFooterIdle();
                setModalEditStatus("Mikrofonin käynnistys epäonnistui.");
            }
        }
    }

    async function startRecording() {
        if (modalEditLocked || isRecording) {
            return;
        }
        await beginAudioRecording("session");
    }

    async function startModalEditRecording() {
        if (!db || !modalObservation || modalEditLocked || isRecording) {
            return;
        }
        modalEditLocked = true;
        modalClose.disabled = true;
        recordBtn.disabled = true;
        modalEditBtn.disabled = true;
        await beginAudioRecording("modal-edit");
    }

    function stopRecording(action) {
        if (recorder && recorder.state === "recording") {
            recordingAction = action;
            if (recordingMode === "session") {
                submitBtn.disabled = true;
                cancelBtn.disabled = true;
            } else if (recordingMode === "modal-edit") {
                modalSubmitBtn.disabled = true;
                modalCancelBtn.disabled = true;
            }
            recorder.stop();
        }
    }

    async function init() {
        try {
            db = await openDb();
            reconcileActiveSessionPointer();
            setGpsStatus("");
            const resumed = await resumeOpenSession();
            if (!resumed) {
                setControlsIdle();
            }
            await renderList();
            syncSessionStatusLine();
            if (resumed) {
                setUiStatus("");
            } else {
                setUiStatus(
                    currentUserId
                        ? "Aloita havaintoerä Aloita-painikkeella."
                        : "Käyttäjätunnistus puuttuu. Päivitä sivu."
                );
            }
        } catch (_) {
            setGpsStatus("");
            setUiStatus("Tallennustilan alustus epäonnistui.");
        }

        startBtn.addEventListener("click", async () => {
            if (!db) {
                return;
            }
            if (!currentUserId) {
                setUiStatus("Käyttäjätunnistus puuttuu. Päivitä sivu.");
                return;
            }
            try {
                const startedAt = new Date().toISOString();
                const session = {
                    id: buildId(),
                    startedAt,
                    endedAt: null,
                    userId: currentUserId,
                };
                await putSession(session);
                currentSessionId = session.id;
                currentSessionStartIso = startedAt;
                persistActiveSessionPointer();
                await startGps();
                syncSessionStatusLine();
                setUiStatus("");
            } catch (_) {
                setUiStatus("Havaintoerän aloitus epäonnistui.");
            }
        });

        endSessionBtn.addEventListener("click", async () => {
            if (!db || isRecording || modalEditLocked || !currentSessionId) {
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
                clearActiveSessionPointer();
                setControlsIdle();
                syncSessionStatusLine();
                setUiStatus("Havaintoerä päättyi. Voit aloittaa uuden havaintoerän.");
            } catch (_) {
                setUiStatus("Havaintoerän päättäminen epäonnistui.");
            }
        });

        recordBtn.addEventListener("click", async () => {
            await startRecording();
        });
        submitBtn.addEventListener("click", () => {
            if (!isRecording || recordingMode !== "session") {
                return;
            }
            setUiStatus("Analysoidaan havaintoa...");
            stopRecording("submit");
        });
        cancelBtn.addEventListener("click", () => {
            if (!isRecording || recordingMode !== "session") {
                return;
            }
            setUiStatus("Peruutetaan havaintoa...");
            stopRecording("cancel");
        });

        modalEditBtn.addEventListener("click", async () => {
            await startModalEditRecording();
        });
        modalSubmitBtn.addEventListener("click", () => {
            if (!isRecording || recordingMode !== "modal-edit") {
                return;
            }
            setUiStatus("Analysoidaan havaintoa...");
            setModalEditStatus("Analysoidaan havaintoa...");
            stopRecording("submit");
        });
        modalCancelBtn.addEventListener("click", () => {
            if (!isRecording || recordingMode !== "modal-edit") {
                return;
            }
            setUiStatus("Peruutetaan havaintoa...");
            setModalEditStatus("Peruutetaan havaintoa...");
            stopRecording("cancel");
        });

        modalClose.addEventListener("click", closeModal);
        modal.addEventListener("click", (event) => {
            if (event.target === modal && !modalEditLocked) {
                closeModal();
            }
        });
    }

    init();
})();
