// ===== DOM Ready =====
document.addEventListener('DOMContentLoaded', () => {
    if (window.lucide) lucide.createIcons();

    // Initialize Music Page if present
    if (document.querySelector('.music-layout')) {
        const urlParams = new URLSearchParams(window.location.search);
        const emotion = urlParams.get('emotion') || 'Happy';

        // Highlight correct button
        const btn = document.querySelector(`[data-emotion="${emotion}"]`);
        if (btn) btn.click(); // This will call renderPlaylist(emotion)
        else renderPlaylist(emotion);
    }
});


// ===== Tab Logic =====
function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    document.getElementById(`${tabId}-tab`).classList.add('active');
}


// ===== Text Analysis — calls backend API =====
function analyzeEmotion() {
    const loading = document.getElementById('analysis-loading');
    const result = document.getElementById('analysis-result');

    // Determine which tab is active
    const activeTab = document.querySelector('.tab-content.active');
    if (!activeTab) return;

    const tabId = activeTab.id;

    if (tabId === 'text-tab') {
        const text = document.getElementById('text-input').value.trim();
        if (!text) {
            alert('Please enter some text to analyze.');
            return;
        }
        if (loading) loading.style.display = 'block';
        if (result) result.style.display = 'none';

        fetch('/api/analyze/text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        })
            .then(res => res.json())
            .then(data => {
                if (loading) loading.style.display = 'none';
                if (data.error) {
                    alert(data.error);
                    if (data.redirect) window.location.href = data.redirect;
                    return;
                }
                displayResults(data);
            })
            .catch(err => {
                if (loading) loading.style.display = 'none';
                console.error('Analysis error:', err);
                alert('Error analyzing text. Please try again.');
            });

    } else if (tabId === 'image-tab') {
        const fileInput = document.getElementById('image-input');
        if (!fileInput.files[0]) {
            alert('Please upload an image first.');
            return;
        }

        if (loading) loading.style.display = 'block';
        if (result) result.style.display = 'none';

        const formData = new FormData();
        formData.append('image', fileInput.files[0]);

        fetch('/api/analyze/image', {
            method: 'POST',
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                if (loading) loading.style.display = 'none';
                if (data.error) {
                    alert(data.error);
                    if (data.redirect) window.location.href = data.redirect;
                    return;
                }
                displayResults(data);
            })
            .catch(err => {
                if (loading) loading.style.display = 'none';
                console.error('Image analysis error:', err);
                alert('Error analyzing image. Please try again.');
            });
    }
}


function displayResults(data) {
    const result = document.getElementById('analysis-result');
    if (!result) return;

    const emojis = {
        Happy: "😊", Sad: "😟", Angry: "😤",
        Neutral: "😐", Fearful: "😨", Surprised: "😲"
    };

    const emotion = data.emotion || 'Neutral';
    const stress = data.stress_level || 'Low';

    document.getElementById('result-emotion').textContent = emotion;
    document.getElementById('result-emoji').textContent = emojis[emotion] || '😐';
    document.getElementById('result-stress').textContent = stress;
    document.getElementById('result-stress-icon').textContent =
        stress === "Low" ? "🟢" : stress === "Medium" ? "🟡" : "🔴";

    result.style.display = 'block';

    // Re-render Lucide icons inside the result
    if (window.lucide) lucide.createIcons();

    // Show message if face not detected
    if (data.message) {
        let msgEl = document.getElementById('result-message');
        if (!msgEl) {
            msgEl = document.createElement('p');
            msgEl.id = 'result-message';
            msgEl.style.cssText = 'text-align: center; color: var(--muted-foreground); font-size: 0.875rem; margin-top: 1rem;';
            result.querySelector('.results-grid').after(msgEl);
        }
        msgEl.textContent = data.message;
        msgEl.style.display = 'block';
    } else {
        const msgEl = document.getElementById('result-message');
        if (msgEl) msgEl.style.display = 'none';
    }
}


// ===== Voice Input — Web Speech API =====
let isRecording = false;
let recognition = null;

function toggleRecording() {
    const btn = document.getElementById('record-btn');
    const status = document.getElementById('record-status');

    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('Speech recognition is not supported in your browser. Please use Google Chrome.');
        return;
    }

    isRecording = !isRecording;

    if (isRecording) {
        // Start recording with Web Speech API
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            btn.classList.add('recording');
            status.textContent = "🔴 Listening... Speak now";
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            status.textContent = `Recognized: "${transcript}"`;

            // Send recognized text to backend for analysis
            const loading = document.getElementById('analysis-loading');
            const result = document.getElementById('analysis-result');
            if (loading) loading.style.display = 'block';
            if (result) result.style.display = 'none';

            fetch('/api/analyze/text', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: transcript })
            })
                .then(res => res.json())
                .then(data => {
                    if (loading) loading.style.display = 'none';
                    if (data.error) {
                        alert(data.error);
                        if (data.redirect) window.location.href = data.redirect;
                        return;
                    }
                    displayResults(data);
                })
                .catch(err => {
                    if (loading) loading.style.display = 'none';
                    console.error('Voice analysis error:', err);
                    alert('Error analyzing voice input.');
                });
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            status.textContent = `Error: ${event.error}. Click to try again.`;
            btn.classList.remove('recording');
            isRecording = false;
        };

        recognition.onend = () => {
            btn.classList.remove('recording');
            isRecording = false;
        };

        recognition.start();

    } else {
        // Stop recording
        if (recognition) {
            recognition.stop();
        }
        btn.classList.remove('recording');
        status.textContent = "Click to start recording";
    }
}


// ===== Image Input =====
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


// ===== Language Selection Modal =====
function showLanguageModal() {
    const modal = document.getElementById('language-modal');
    if (modal) {
        modal.style.display = 'flex';
        // Reset check boxes
        document.querySelectorAll('input[name="language"]').forEach(cb => {
            cb.checked = false;
            cb.disabled = false;
        });
    }
}

function closeLanguageModal() {
    const modal = document.getElementById('language-modal');
    if (modal) modal.style.display = 'none';
}

function handleLangSelection(checkbox) {
    const checked = document.querySelectorAll('input[name="language"]:checked');
    if (checked.length >= 2) {
        document.querySelectorAll('input[name="language"]:not(:checked)').forEach(cb => {
            cb.disabled = true;
        });
    } else {
        document.querySelectorAll('input[name="language"]').forEach(cb => {
            cb.disabled = false;
        });
    }
}

function submitLanguages() {
    const checked = document.querySelectorAll('input[name="language"]:checked');
    const languages = Array.from(checked).map(cb => cb.value);

    // Get selected playback format
    const format = document.querySelector('input[name="playback-format"]:checked')?.value || 'both';

    // Get current emotion from result
    const emotion = document.getElementById('result-emotion').textContent || 'Neutral';

    // Build query params
    const params = new URLSearchParams();
    params.append('emotion', emotion);
    params.append('format', format);
    if (languages.length > 0) {
        params.append('languages', languages.join(','));
    }

    // Redirect
    window.location.href = `/music?${params.toString()}`;
}


// ===== Music Logic =====
// ===== Music Logic =====
// Playlists are now fetched from the YouTube API backend
let currentVideos = [];
let currentIndex = 0;
let player = null;

function onYouTubeIframeAPIReady() {
    // This function is called automatically by YouTube API script
    console.log("YouTube API Ready");
}

function playSong(title, artist, videoId, shouldAutoplay = true) {
    document.getElementById('player-title').textContent = title;
    document.getElementById('player-artist').textContent = artist;

    if (videoId) {
        // Update current index based on videoId
        const index = currentVideos.findIndex(v => v.videoId === videoId);
        if (index !== -1) currentIndex = index;

        // Check format preference from URL
        const urlParams = new URLSearchParams(window.location.search);
        const format = urlParams.get('format') || 'both';

        // Embed YouTube video
        const wrapper = document.getElementById('youtube-embed-wrapper');
        const defaultArt = document.getElementById('default-art');
        const playIcon = document.getElementById('play-icon');

        if (format === 'audio') {
            // Audio Only mode: Hide video wrapper, show default art
            defaultArt.style.display = 'flex';
            defaultArt.style.background = 'var(--gradient-primary)';
            wrapper.style.display = 'none';
        } else {
            // Video + Audio mode: Show video, hide default art
            defaultArt.style.display = 'none';
            wrapper.style.display = 'block';
        }

        // If player exists, load new video
        if (player && typeof player.loadVideoById === 'function') {
            if (shouldAutoplay) {
                player.loadVideoById(videoId);
            } else {
                player.cueVideoById(videoId);
            }
        } else {
            // Create new player
            wrapper.innerHTML = '<div id="youtube-player"></div>';
            player = new YT.Player('youtube-player', {
                height: '100%',
                width: '100%',
                videoId: videoId,
                playerVars: {
                    'autoplay': shouldAutoplay ? 1 : 0,
                    'playsinline': 1
                },
                events: {
                    'onStateChange': onPlayerStateChange,
                    'onError': onPlayerError
                }
            });
        }

        // Update play button to pause icon
        if (playIcon) {
            playIcon.setAttribute('data-lucide', shouldAutoplay ? 'pause' : 'play');
            if (window.lucide) lucide.createIcons();
        }
    }
}

function onPlayerStateChange(event) {
    const playIcon = document.getElementById('play-icon');
    if (event.data == YT.PlayerState.PLAYING) {
        if (playIcon) playIcon.setAttribute('data-lucide', 'pause');
    } else {
        if (playIcon) playIcon.setAttribute('data-lucide', 'play');
    }
    if (window.lucide) lucide.createIcons();
}

function onPlayerError(event) {
    console.warn("YouTube Player Error:", event.data);
    // Error codes: 150/101 = restricted playback, 100 = video not found
    // Auto-skip to next video
    playNext();
}

function togglePlay() {
    if (player && typeof player.getPlayerState === 'function') {
        const state = player.getPlayerState();
        if (state === YT.PlayerState.PLAYING) {
            player.pauseVideo();
        } else {
            player.playVideo();
        }
    }
}

function playNext() {
    if (currentVideos.length > 0) {
        currentIndex = (currentIndex + 1) % currentVideos.length;
        const video = currentVideos[currentIndex];
        playSong(video.title, video.channelTitle, video.videoId);
    }
}

function playPrevious() {
    if (currentVideos.length > 0) {
        currentIndex = (currentIndex - 1 + currentVideos.length) % currentVideos.length;
        const video = currentVideos[currentIndex];
        playSong(video.title, video.channelTitle, video.videoId);
    }
}



function selectEmotion(emotion) {
    document.querySelectorAll('.emotion-btn[data-emotion]').forEach(btn => {
        if (btn.dataset.emotion === emotion) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    renderPlaylist(emotion);
}

function renderPlaylist(emotion) {
    document.getElementById('playlist-title').textContent = `${emotion} Recommendations`;
    document.getElementById('current-emotion-badge').textContent = `Emotion: ${emotion}`;

    const list = document.getElementById('playlist-tracks');
    list.innerHTML = '<p style="padding: 1rem; color: var(--muted-foreground);">Loading recommendations...</p>';

    // Check for languages in URL
    const urlParams = new URLSearchParams(window.location.search);
    const langParam = urlParams.get('languages');
    const languages = langParam ? langParam.split(',') : [];

    fetch('/api/music/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            emotion: emotion,
            languages: languages
        })
    })
        .then(res => res.json())
        .then(data => {
            list.innerHTML = '';
            if (!data.videos || data.videos.length === 0) {
                list.innerHTML = '<p style="padding: 1rem;">No recommendations found. Please try again.</p>';
                return;
            }

            // Store videos globally
            currentVideos = data.videos;
            currentIndex = 0;

            // Show first 10 tracks (Strictly)
            const initialTracks = currentVideos.slice(0, 10);
            list.innerHTML = '';

            initialTracks.forEach((video, index) => {
                const div = createTrackElement(video, index);
                div.onclick = () => playSong(video.title, video.channelTitle, video.videoId);
                list.appendChild(div);
            });

            // Handle "Show More" visibility (if more than 10)
            const showMoreContainer = document.getElementById('show-more-container');
            if (currentVideos.length > 10) {
                showMoreContainer.style.display = 'block';
            } else {
                showMoreContainer.style.display = 'none';
            }

            // Auto-load the first track
            if (currentVideos.length > 0) {
                const first = currentVideos[0];
                playSong(first.title, first.channelTitle, first.videoId, false);
            }

            if (window.lucide) lucide.createIcons();
        })
        .catch(err => {
            console.error('Music fetch error:', err);
            list.innerHTML = '<p style="padding: 1rem; color: red;">Error loading music. Check API key.</p>';
        });
}

function createTrackElement(video, index = 0) {
    const div = document.createElement('button');
    div.className = 'track-item track-item-animate';
    div.style.animationDelay = `${index * 0.05}s`;
    div.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <img src="${video.thumbnail}" alt="Thumbnail" style="width: 40px; height: 40px; border-radius: 4px; object-fit: cover;">
            <div style="text-align: left;">
                <div style="font-weight: 600; font-size: 0.9rem; line-height: 1.2;">${video.title}</div>
                <div style="font-size: 0.8rem; color: var(--muted-foreground);">${video.channelTitle}</div>
            </div>
        </div>
        <i data-lucide="external-link" style="width: 16px; color: var(--primary);"></i>
    `;
    return div;
}

function showMoreTracks() {
    const list = document.getElementById('playlist-tracks');
    // Show remaining tracks (starting from 10, up to 18 total)
    const remainingTracks = currentVideos.slice(10);

    remainingTracks.forEach((video, index) => {
        const div = createTrackElement(video, index);
        div.onclick = () => playSong(video.title, video.channelTitle, video.videoId);
        list.appendChild(div);
    });

    document.getElementById('show-more-container').style.display = 'none';
    if (window.lucide) lucide.createIcons();
}



// ===== Relaxation - Breathing Exercise =====
let breathInterval;

function toggleBreathing() {
    const btn = document.getElementById('breath-btn');
    const circle = document.getElementById('breath-circle');
    const text = document.getElementById('breath-text');

    if (breathInterval) {
        clearInterval(breathInterval);
        breathInterval = null;
        btn.textContent = "Start Breathing";
        text.textContent = "Ready";
        circle.className = "breath-circle";
        return;
    }

    btn.textContent = "Stop";
    runBreathCycle();
    breathInterval = setInterval(runBreathCycle, 12000);
}

function runBreathCycle() {
    const circle = document.getElementById('breath-circle');
    const text = document.getElementById('breath-text');

    // Inhale
    text.textContent = "Inhale";
    circle.className = "breath-circle inhale";

    setTimeout(() => {
        text.textContent = "Hold";
        circle.className = "breath-circle inhale";
    }, 4000);

    setTimeout(() => {
        text.textContent = "Exhale";
        circle.className = "breath-circle exhale";
    }, 8000);
}


// ===== Contact Form =====
function handleContactSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const inputs = form.querySelectorAll('input, textarea');
    const data = {};

    inputs.forEach(input => {
        if (input.type === 'text') data.name = input.value;
        if (input.type === 'email') data.email = input.value;
        if (input.tagName === 'TEXTAREA') data.message = input.value;
    });

    fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
        .then(res => res.json())
        .then(response => {
            document.getElementById('contact-form-wrapper').style.display = 'none';
            document.getElementById('contact-success').style.display = 'block';
            if (window.lucide) lucide.createIcons();
        })
        .catch(err => {
            console.error('Contact error:', err);
            // Still show success for demo
            document.getElementById('contact-form-wrapper').style.display = 'none';
            document.getElementById('contact-success').style.display = 'block';
            if (window.lucide) lucide.createIcons();
        });
}

function resetContactForm() {
    document.getElementById('contact-form').reset();
    document.getElementById('contact-form-wrapper').style.display = 'block';
    document.getElementById('contact-success').style.display = 'none';
}
