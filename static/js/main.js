/* 
 * DOM Content Loaded Event Listener
 * Initializes the application, icons, and page-specific logic.
 */
document.addEventListener('DOMContentLoaded', () => {
    console.info("[APP] Initializing Mood Music Hub...");
    if (window.lucide) lucide.createIcons();

    // Initialize Music Page if present
    if (document.querySelector('.music-layout')) {
        console.debug("[APP] Music layout detected, initializing localized settings.");
        const urlParams = new URLSearchParams(window.location.search);
        const emotion = urlParams.get('emotion') || 'Happy';
        const languages = urlParams.get('languages');

        // Sync local dropdown if present
        const langSelect = document.getElementById('music-lang-select');
        if (langSelect && languages) {
            langSelect.value = languages.split(',')[0];
        }

        // Highlight correct button AND filter visibility
        const btn = document.querySelector(`[data-emotion="${emotion}"]`);
        if (btn) {
            console.info(`[APP] Auto-selecting emotion: ${emotion}`);
            btn.click(); 
        } else {
            selectEmotion(emotion);
        }
    }
});


/* 
 * Tab Switching Logic
 * Handles visibility of content sections and camera cleanup.
 */
function switchTab(tabId) {
    console.info(`[APP] Switching to tab: ${tabId}`);
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    document.getElementById(`${tabId}-tab`).classList.add('active');

    // Stop camera if leaving image tab to save resources
    if (tabId !== 'image') {
        stopCamera();
    }
}


/* 
 * Main Emotion Analysis Wrapper
 * Dispatches to text or image analysis based on active tab.
 */
function analyzeEmotion() {
    const loading = document.getElementById('analysis-loading');
    const result = document.getElementById('analysis-result');

    // Determine which tab is active
    const activeTab = document.querySelector('.tab-content.active');
    if (!activeTab) {
        console.error("[APP] No active tab found for analysis.");
        return;
    }

    const tabId = activeTab.id;
    console.info(`[APP] Starting analysis on tab: ${tabId}`);

    if (tabId === 'text-tab') {
        const text = document.getElementById('text-input').value.trim();
        if (!text) {
            alert('Please enter some text to analyze.');
            return;
        }
        
        if (loading) loading.style.display = 'block';
        if (result) result.style.display = 'none';

        // Perform Text Analysis Request
        fetch('/api/analyze/text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        })
            .then(res => {
                if (!res.ok) {
                    return res.json().then(errData => {
                        throw new Error(errData.error || `Server responded with ${res.status}`);
                    }).catch(() => {
                        throw new Error(`Server error: ${res.status}`);
                    });
                }
                return res.json();
            })
            .then(data => {
                if (loading) loading.style.display = 'none';
                if (data.error) {
                    console.warn(`[APP] Text Analysis API returned error: ${data.error}`);
                    alert(data.error);
                    if (data.redirect) window.location.href = data.redirect;
                    return;
                }
                console.info(`[APP] Text Analysis Success: ${data.emotion}`);
                displayResults(data);
            })
            .catch(err => {
                if (loading) loading.style.display = 'none';
                console.error('[APP] Detailed Analysis Error:', err);
                const errorMsg = err.message || 'Error analyzing text.';
                alert(`${errorMsg} Please try again.`);
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

        // Perform Image Analysis Request
        fetch('/api/analyze/image', {
            method: 'POST',
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                if (loading) loading.style.display = 'none';
                if (data.error) {
                    console.warn(`[APP] Image Analysis API returned error: ${data.error}`);
                    alert(data.error);
                    if (data.redirect) window.location.href = data.redirect;
                    return;
                }
                console.info(`[APP] Image Analysis Success: ${data.emotion}`);
                displayResults(data);
            })
            .catch(err => {
                if (loading) loading.style.display = 'none';
                console.error('[APP] Image analysis error:', err);
                alert('Error analyzing image. Please try again.');
            });
    }
}


/* 
 * UI Update: Display Analysis Results
 * Updates the emoji, emotion text, and stress level on the page.
 */
function displayResults(data) {
    const result = document.getElementById('analysis-result');
    if (!result) return;
    
    console.debug("[APP] Rendering analysis results to UI.");
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


/* 
 * Voice Input Management
 * Handles Web Speech API recording and transmission of transcript.
 */
let isRecording = false;
let recognition = null;

function toggleRecording() {
    const btn = document.getElementById('record-btn');
    const status = document.getElementById('record-status');

    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.warn("[APP] Speech Recognition not supported in this browser.");
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


/* 
 * Camera & Image Mode Selection
 * Toggles between file upload and live camera interface.
 */
function setCameraMode(isCamera) {
    isCameraMode = isCamera;
    console.info(`[APP] Setting camera mode: ${isCamera}`);
    const uploadContainer = document.getElementById('upload-container');
    const cameraContainer = document.getElementById('camera-container');
    const analyzeBtnContainer = document.getElementById('analyze-btn-container');
    const uploadBtn = document.getElementById('mode-upload-btn');
    const cameraBtn = document.getElementById('mode-camera-btn');

    if (isCamera) {
        uploadContainer.style.display = 'none';
        cameraContainer.style.display = 'block';
        analyzeBtnContainer.style.display = 'none';
        uploadBtn.classList.remove('active');
        cameraBtn.classList.add('active');
    } else {
        uploadContainer.style.display = 'block';
        cameraContainer.style.display = 'none';
        analyzeBtnContainer.style.display = 'block';
        uploadBtn.classList.add('active');
        cameraBtn.classList.remove('active');
        stopCamera();
    }
}

/* 
 * Start Live Camera Stream
 * Requests media permissions and hooks stream to video element.
 */
async function startCamera() {
    console.info("[APP] Requesting camera access...");
    const video = document.getElementById('camera-feed');
    const startBtn = document.getElementById('start-camera-btn');
    const captureBtn = document.getElementById('capture-btn');

    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: "user" 
            } 
        });
        video.srcObject = stream;
        console.info("[APP] Camera stream active.");
        startBtn.innerHTML = '<i data-lucide="video-off" style="width: 16px; margin-right: 0.5rem;"></i> Stop Camera';
        startBtn.onclick = stopCamera;
        captureBtn.disabled = false;
        if (window.lucide) lucide.createIcons();
    } catch (err) {
        console.error("[APP] Camera access error:", err);
        alert("Could not access camera. Please ensure you have granted permissions.");
    }
}

function stopCamera() {
    const video = document.getElementById('camera-feed');
    const startBtn = document.getElementById('start-camera-btn');
    const captureBtn = document.getElementById('capture-btn');

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    
    if (video) video.srcObject = null;
    if (startBtn) {
        startBtn.innerHTML = '<i data-lucide="camera" style="width: 16px; margin-right: 0.5rem;"></i> Start Camera';
        startBtn.onclick = startCamera;
    }
    if (captureBtn) captureBtn.disabled = true;
    if (window.lucide) lucide.createIcons();
}

/* 
 * Capture Frame & Analyze
 * Grabs a frame from the video feed, converts to Base64, and sends to 'String Backend' API.
 */
function captureAndAnalyze() {
    const video = document.getElementById('camera-feed');
    const canvas = document.getElementById('camera-canvas');
    const loading = document.getElementById('analysis-loading');
    const result = document.getElementById('analysis-result');

    if (!video || !canvas) {
        console.error("[APP] Camera elements missing, cannot capture frame.");
        return;
    }

    // Set canvas dimensions to match video stream
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw frame to canvas for processing
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    if (loading) loading.style.display = 'block';
    if (result) result.style.display = 'none';

    // Get Base64 from canvas - high quality JPEG
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    console.info("[APP] Captured frame, sending to String Backend...");

    fetch('/api/analyze/image_string', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: imageData })
    })
        .then(res => res.json())
        .then(data => {
            if (loading) loading.style.display = 'none';
            if (data.error) {
                console.error(`[APP] String Backend Error: ${data.error}`);
                alert(data.error);
                return;
            }
            console.info(`[APP] Capture Analysis Success: ${data.emotion}`);
            displayResults(data);
        })
        .catch(err => {
            if (loading) loading.style.display = 'none';
            console.error('[APP] Camera string analysis error:', err);
            alert('Error analyzing camera frame.');
        });
}

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

/* 
 * Submit Language Selection
 * Finalizes music preferences and redirects to the player.
 */
function submitLanguages() {
    console.info("[APP] Submitting language and playback preferences.");
    const checked = document.querySelectorAll('input[name="language"]:checked');
    const languages = Array.from(checked).map(cb => cb.value);

    // Get selected playback format
    const format = document.querySelector('input[name="playback-format"]:checked')?.value || 'both';

    // Get current emotion from result display
    const emotion = document.getElementById('result-emotion').textContent || 'Neutral';

    // Build query params for redirection
    const params = new URLSearchParams();
    params.append('emotion', emotion);
    params.append('format', format);
    if (languages.length > 0) {
        params.append('languages', languages.join(','));
    }

    const redirectUrl = `/music?${params.toString()}`;
    console.info(`[APP] Redirecting to music page: ${redirectUrl}`);
    window.location.href = redirectUrl;
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
            // Audio Only mode: Show default art, but keep player active at 1px height
            // Using display:none often breaks YouTube API events like Error and Ended
            defaultArt.style.display = 'flex';
            defaultArt.style.background = 'var(--gradient-primary)';
            wrapper.style.display = 'block';
            wrapper.style.height = '1px';
            wrapper.style.opacity = '0.01'; 
            wrapper.style.pointerEvents = 'none'; // Don't let user click it
            wrapper.style.marginBottom = '0';
        } else {
            // Video + Audio mode: Show video, hide default art
            defaultArt.style.display = 'none';
            wrapper.style.display = 'block';
            wrapper.style.height = 'auto';
            wrapper.style.opacity = '1';
            wrapper.style.pointerEvents = 'auto';
            wrapper.style.marginBottom = '1rem';
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
                    'playsinline': 1,
                    'origin': window.location.origin
                },
                events: {
                    'onStateChange': onPlayerStateChange,
                    'onError': onPlayerError,
                    'onReady': (event) => {
                        if (shouldAutoplay) event.target.playVideo();
                    }
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
    } else if (event.data == YT.PlayerState.ENDED) {
        // Automatically play the next song when current one ends
        console.log("Track ended, playing next...");
        playNext();
    } else {
        if (playIcon) playIcon.setAttribute('data-lucide', 'play');
    }
    if (window.lucide) lucide.createIcons();
}

function onPlayerError(event) {
    console.warn("YouTube Player Error Code:", event.data);
    
    // Error codes: 
    // 150/101 = restricted playback (domain or owner restriction)
    // 100 = video not found/removed
    // 2/5 = invalid parameters/browser issues
    
    const trackName = currentVideos[currentIndex]?.title || "Current Track";
    console.error(`Playback restricted for: "${trackName}". Skipping to next...`);
    
    // Optional: Show a small toast to the user if many tracks fail
    // showToast(`Skipping restricted track...`);

    // Auto-skip to next video to keep the music flowing
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

function changeLanguage() {
    const emotion = document.querySelector('.emotion-btn.active')?.dataset.emotion || 'Happy';
    renderPlaylist(emotion);
}



function selectEmotion(emotion) {
    document.querySelectorAll('.emotion-btn[data-emotion]').forEach(btn => {
        if (btn.dataset.emotion === emotion) {
            btn.classList.add('active');
            btn.style.display = 'inline-block'; // Show active
        } else {
            btn.classList.remove('active');
            btn.style.display = 'none'; // Hide others
        }
    });
    renderPlaylist(emotion);
}

/* 
 * Render Playlist
 * Fetches recommendations from the API and updates the UI list.
 */
function renderPlaylist(emotion) {
    console.info(`[APP] Fetching playlist recommendations for: ${emotion}`);
    document.getElementById('playlist-title').textContent = `${emotion} Recommendations`;
    document.getElementById('current-emotion-badge').textContent = `Emotion: ${emotion}`;

    const list = document.getElementById('playlist-tracks');
    list.innerHTML = '<p style="padding: 1rem; color: var(--muted-foreground);">Loading recommendations...</p>';

    // Priority 1: Check Local Dropdown
    const langSelect = document.getElementById('music-lang-select');
    let languages = [];
    if (langSelect) {
        languages = [langSelect.value];
    } else {
        // Priority 2: Check URL Params
        const urlParams = new URLSearchParams(window.location.search);
        const langParam = urlParams.get('languages');
        languages = langParam ? langParam.split(',') : [];
    }

    // API Call to suggest songs
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
                console.warn("[APP] No music recommendations returned from API.");
                list.innerHTML = '<p style="padding: 1rem;">No recommendations found. Please try again.</p>';
                return;
            }

            console.info(`[APP] Received ${data.videos.length} recommendations.`);
            // Store videos globally for sequential playback
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

            // Handle "Show More" visibility
            const showMoreContainer = document.getElementById('show-more-container');
            if (currentVideos.length > 10) {
                showMoreContainer.style.display = 'block';
            } else {
                showMoreContainer.style.display = 'none';
            }

            // Auto-load the first track without autoplaying immediately
            if (currentVideos.length > 0) {
                const first = currentVideos[0];
                playSong(first.title, first.channelTitle, first.videoId, false);
            }

            if (window.lucide) lucide.createIcons();
        })
        .catch(err => {
            console.error('[APP] Music fetch error:', err);
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
        btn.innerHTML = '<i data-lucide="play" style="width: 18px; margin-right: 0.5rem;"></i> Start Exercise';
        text.textContent = "Ready";
        circle.className = "breath-circle";
        // Reset indicators
        document.querySelectorAll('.phase-indicators span').forEach(s => s.classList.remove('active'));
        if (window.lucide) lucide.createIcons();
        return;
    }

    btn.innerHTML = '<i data-lucide="square" style="width: 18px; margin-right: 0.5rem;"></i> Stop';
    if (window.lucide) lucide.createIcons();
    
    runBreathCycle();
    breathInterval = setInterval(runBreathCycle, 12000); // 4 + 4 + 4 = 12s total
}

function runBreathCycle() {
    const circle = document.getElementById('breath-circle');
    const text = document.getElementById('breath-text');
    const inhaleLabel = document.getElementById('label-inhale');
    const holdLabel = document.getElementById('label-hold');
    const exhaleLabel = document.getElementById('label-exhale');

    if (!circle || !text) return;

    // Reset status
    const resetLabels = () => {
        if (inhaleLabel) inhaleLabel.classList.remove('active');
        if (holdLabel) holdLabel.classList.remove('active');
        if (exhaleLabel) exhaleLabel.classList.remove('active');
    };

    // 1. INHALE (4s)
    resetLabels();
    if (inhaleLabel) inhaleLabel.classList.add('active');
    text.textContent = "Inhale";
    circle.className = "breath-circle inhale";

    // 2. HOLD (4s)
    setTimeout(() => {
        if (!breathInterval) return;
        resetLabels();
        if (holdLabel) holdLabel.classList.add('active');
        text.textContent = "Hold";
        // Keep inhale class to maintain scale(1.4)
    }, 4000);

    // 3. EXHALE (4s)
    setTimeout(() => {
        if (!breathInterval) return;
        resetLabels();
        if (exhaleLabel) exhaleLabel.classList.add('active');
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
