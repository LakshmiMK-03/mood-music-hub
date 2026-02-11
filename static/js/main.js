// DOM Elements and Global Variables
document.addEventListener('DOMContentLoaded', () => {
    // Lucide icons are auto-initialized by the script tag in base.html logic
    // but in case we add content dynamically, we call it again
    if (window.lucide) lucide.createIcons();

    // Initialize Music Page if present
    if (document.querySelector('.music-layout')) {
        renderPlaylist('Happy'); // Default
    }
});

// --- Tab Logic ---
function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    document.getElementById(`${tabId}-tab`).classList.add('active');
}

// --- Analysis Logic ---
function analyzeEmotion() {
    const loading = document.getElementById('analysis-loading');
    const result = document.getElementById('analysis-result');
    const imageAnalyzeBtn = document.getElementById('image-analyze-btn');

    if (imageAnalyzeBtn) imageAnalyzeBtn.disabled = true;

    if (loading) loading.style.display = 'block';
    if (result) result.style.display = 'none';

    // Simulate API call
    setTimeout(() => {
        if (loading) loading.style.display = 'none';
        if (result) result.style.display = 'block';
        if (imageAnalyzeBtn) imageAnalyzeBtn.disabled = false;

        // Random results
        const emotions = ["Happy", "Sad", "Angry", "Neutral", "Fearful", "Surprised"];
        const stressLevels = ["Low", "Medium", "High"];
        const emojis = { Happy: "😊", Sad: "😟", Angry: "😤", Neutral: "😐", Fearful: "😨", Surprised: "😲" };

        const emotion = emotions[Math.floor(Math.random() * emotions.length)];
        const stress = stressLevels[Math.floor(Math.random() * stressLevels.length)];
        const confidence = Math.floor(Math.random() * 20) + 78;

        document.getElementById('result-emotion').textContent = emotion;
        document.getElementById('result-emoji').textContent = emojis[emotion];
        document.getElementById('result-stress').textContent = stress;
        document.getElementById('result-stress-icon').textContent = stress === "Low" ? "🟢" : stress === "Medium" ? "🟡" : "🔴";
        document.getElementById('result-confidence').textContent = confidence + "%";

    }, 2000);
}

// --- Voice Input Logic ---
let isRecording = false;
function toggleRecording() {
    const btn = document.getElementById('record-btn');
    const status = document.getElementById('record-status');

    isRecording = !isRecording;

    if (isRecording) {
        btn.classList.add('recording');
        status.textContent = "🔴 Recording... Click to stop";
        // Auto analyze after 3 seconds for demo
        setTimeout(() => {
            if (isRecording) {
                toggleRecording();
                analyzeEmotion();
            }
        }, 3000);
    } else {
        btn.classList.remove('recording');
        status.textContent = "Click to start recording";
    }
}

// --- Image Input Logic ---
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const preview = document.getElementById('image-preview');
            const img = document.getElementById('preview-img');
            img.src = e.target.result;
            preview.style.display = 'block';
            document.getElementById('image-analyze-btn').disabled = false;
        };
        reader.readAsDataURL(file);
    }
}

// --- Music Logic ---
const playlists = {
    Happy: { name: "Energetic Vibes", songs: [{ t: "Happy", a: "Pharrell" }, { t: "Uptown Funk", a: "Bruno Mars" }, { t: "Good Vibrations", a: "Beach Boys" }] },
    Sad: { name: "Calm & Peaceful", songs: [{ t: "Weightless", a: "Marconi Union" }, { t: "Clair de Lune", a: "Debussy" }, { t: "River Flows in You", a: "Yiruma" }] },
    Angry: { name: "Soothing Instrumentals", songs: [{ t: "Adagio for Strings", a: "Barber" }, { t: "Moonlight Sonata", a: "Beethoven" }] },
    Neutral: { name: "Lo-fi Focus", songs: [{ t: "Snowman", a: "WYS" }, { t: "Coffee", a: "beabadoobee" }] },
    Fearful: { name: "Grounding Sounds", songs: [{ t: "Nature Sounds", a: "Unknown" }, { t: "Ambient Flow", a: "Artist" }] }
};

function selectEmotion(emotion) {
    document.querySelectorAll('.emotion-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[data-emotion="${emotion}"]`).classList.add('active');
    renderPlaylist(emotion);
}

function renderPlaylist(emotion) {
    const data = playlists[emotion] || playlists['Happy'];
    document.getElementById('playlist-title').textContent = data.name;
    document.getElementById('current-emotion-badge').textContent = `Emotion: ${emotion}`;

    const list = document.getElementById('playlist-tracks');
    list.innerHTML = '';

    data.songs.forEach((song, index) => {
        const div = document.createElement('button');
        div.className = 'track-item';
        div.innerHTML = `
            <div>
                <div style="font-weight: 600;">${song.t}</div>
                <div style="font-size: 0.875rem; color: var(--muted-foreground);">${song.a}</div>
            </div>
            <i data-lucide="play-circle" style="width: 20px; color: var(--primary);"></i>
        `;
        div.onclick = () => playSong(song.t, song.a);
        list.appendChild(div);
    });
    lucide.createIcons();
}

function playSong(title, artist) {
    document.getElementById('player-title').textContent = title;
    document.getElementById('player-artist').textContent = artist;
}

// --- Relaxation Logic ---
let breathInterval;
let breathState = 0; // 0: ready, 1: inhale, 2: hold, 3: exhale

function toggleBreathing() {
    const btn = document.getElementById('breath-btn');
    const circle = document.getElementById('breath-circle');
    const text = document.getElementById('breath-text');

    if (breathInterval) {
        // Stop
        clearInterval(breathInterval);
        breathInterval = null;
        btn.textContent = "Start Breathing";
        text.textContent = "Ready";
        circle.className = "breath-circle";
        return;
    }

    btn.textContent = "Stop";
    runBreathCycle();
    breathInterval = setInterval(runBreathCycle, 12000); // 4+4+4 = 12s
}

function runBreathCycle() {
    const circle = document.getElementById('breath-circle');
    const text = document.getElementById('breath-text');

    // Inhale
    text.textContent = "Inhale";
    circle.className = "breath-circle inhale";

    setTimeout(() => {
        // Hold
        text.textContent = "Hold";
        circle.className = "breath-circle inhale"; // Keep expanded
    }, 4000);

    setTimeout(() => {
        // Exhale
        text.textContent = "Exhale";
        circle.className = "breath-circle exhale";
    }, 8000);
}
