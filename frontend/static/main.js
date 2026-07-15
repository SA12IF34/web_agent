const startButton = document.getElementById('start-btn');
const statusPanel = document.getElementById('status-panel');
const statusText = document.getElementById('status-text');
const statusMessage = document.getElementById('status-message');
const languageSelect = document.getElementById('language-select');
const modeSelect = document.getElementById('mode-select');
const voiceWave = document.getElementById('voice-wave');
const appShell = document.getElementById('app-shell');
const agentCard = document.getElementById('agent-card');
const customerSupportMode = document.getElementById('customer-support');
const collapseToggle = document.getElementById('collapse-toggle');
const supportTabsContainer = document.getElementById('support-tabs');
const supportTabButtons = Array.from(document.querySelectorAll('.support-tab'));
const supportContent = document.getElementById('support-content');
const accountSelect = document.getElementById('account-select');

let started = false;
let activeSupportTab = 'products';
let selectedAccountId = '';

let websocket;

let audioQueue = [];
let sampleRate = 16000;
let playbackRate = 1;

let audioOutputContext;
let nextPlayTime = 0;
let isPlaying = false;


let audioContext;
let mediaStream;
let processor;
let microphone;

function floatToInt16(float32) {
    const out = new Int16Array(float32.length);
    for (let i = 0; i < float32.length; i++) {
        const s = Math.max(-1, Math.min(1, float32[i]));
        out[i] = s < 0 ? Math.round(s * 32768) : Math.round(s * 32767);
    }
    return out;
}

// Linear interpolation resampler to 16 kHz for streaming chunks
function resampleFloatToInt16_16k(input, inSampleRate) {
    const target = sampleRate;
    if (!inSampleRate || inSampleRate === target) return floatToInt16(input);
    const ratio = inSampleRate / target;
    const newLen = Math.max(1, Math.round(input.length / ratio));
    const out = new Int16Array(newLen);
    for (let i = 0; i < newLen; i++) {
        const idx = i * ratio;
        const i0 = Math.floor(idx);
        const i1 = Math.min(i0 + 1, input.length - 1);
        const frac = idx - i0;
        const sample = input[i0] + (input[i1] - input[i0]) * frac;
        const s = Math.max(-1, Math.min(1, sample));
        out[i] = s < 0 ? Math.round(s * 32768) : Math.round(s * 32767);
    }
    return out;
}

async function requestMicrophonePermission() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach(track => track.stop()); // Stop the stream as we don't need it yet
        return true;
    } catch (err) {
        console.error('Error accessing microphone:', err);
        return false;
    }
}

async function startAudioCapture() {
    try {
        
                
        // Step 1: Request microphone permission with minimal constraints first
        console.log('Requesting microphone permission...');
        let stream;
        try {
            // First try with just basic audio permission
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            console.log('Basic microphone permission granted');
        } catch (permissionErr) {
            console.error('Error getting microphone permission:', permissionErr);
            alert('Microphone permission denied: ' + permissionErr.message);
            return false;
        }
        
        // Step 2: Now that we have permission, try with our desired constraints
        try {
            // Configure audio constraints
            const audioConstraints = {
                // Use minimal constraints for better compatibility
                echoCancellation: true,
                noiseSuppression: true,
                channelCount: 1,
                sampleRate: { ideal: sampleRate }
            };
            
            // Get the audio stream with our desired constraints
            mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: audioConstraints
            });
            
            console.log('MediaStream obtained successfully with constraints');
            try {
                const t = mediaStream.getAudioTracks && mediaStream.getAudioTracks()[0];
                const settings = t && t.getSettings ? t.getSettings() : null;
                console.log('Microphone track settings:', settings);
            } catch(_) {}
            
            // We successfully obtained a new constrained stream; stop the initial permission stream
            try { stream.getTracks().forEach(track => track.stop()); } catch(_) {}
        } catch (constraintErr) {
            console.error('Error with audio constraints, falling back to basic stream:', constraintErr);
            // If constraints fail, use the original stream
            mediaStream = stream; // keep original stream active (not stopped)
        }
        
        // Step 3: Create audio context and processing pipeline
        try {
            // Create audio context with low-latency preference
            audioContext = new (window.AudioContext || window.webkitAudioContext)({ latencyHint: 'interactive' });
            // Ensure the context is running
            if (audioContext.state === 'suspended') {
                try { await audioContext.resume(); } catch (_) {}
            }
            console.log('AudioContext created with input sample rate:', audioContext.sampleRate);
            
            // Create microphone source
            microphone = audioContext.createMediaStreamSource(mediaStream);
            console.log('Microphone source created');
            
            // Create script processor node for audio processing
            // Note: ScriptProcessorNode is deprecated but has better browser support than AudioWorklet
            const bufferSize = 1024;
            processor = audioContext.createScriptProcessor(bufferSize, 1, 1);
            console.log('Processor created with buffer size:', bufferSize);
            
            // Connect the nodes
            microphone.connect(processor);
            // Route to a zero-gain sink to avoid audible mic playback while keeping processor active
            const zeroGainNode = audioContext.createGain();
            zeroGainNode.gain.value = 0.0;
            processor.connect(zeroGainNode);
            zeroGainNode.connect(audioContext.destination);
            
            // Process audio data
            processor.onaudioprocess = function(e) {
                
                // Get input mono channel
                const inputData = e.inputBuffer.getChannelData(0);
                const inRate = audioContext.sampleRate;
                
                // Resample to 16 kHz and convert to Int16 for server-side compatibility
                let pcm16;
                if (inRate !== sampleRate) {
                    pcm16 = resampleFloatToInt16_16k(inputData, inRate);
                } else {
                    pcm16 = floatToInt16(inputData);
                }
                
                // Send the audio data to the server
                if (websocket) {
                    websocket.send(pcm16.buffer);
                }
            };
            
            console.log('Audio capture setup complete');
            return true;
        } catch (audioErr) {
            console.error('Error setting up audio processing:', audioErr);
            // Clean up the stream if audio processing setup fails
            if (mediaStream) {
                mediaStream.getTracks().forEach(track => track.stop());
            }
            alert('Error setting up audio processing: ' + audioErr.message);
            return false;
        }
    } catch (err) {
        console.error('Unexpected error in startAudioCapture:', err);
        alert('Unexpected error starting audio capture: ' + err.message);
        return false;
    }
}

function stopAudioCapture() {
    if (processor) {
        processor.disconnect();
        processor = null;
    }
    
    if (microphone) {
        microphone.disconnect();
        microphone = null;
    }
    
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
    }
    
    if (audioContext && audioContext.state !== 'closed') {
        audioContext.close();
        audioContext = null;
    }

}

function playAudio() {
    if (isPlaying) return;
    voiceWave?.classList.add('active');
    statusPanel?.classList.add('is-speaking');
    statusText.textContent = 'Agent is speaking';
    isPlaying = true;

    while (audioQueue.length > 0) {
        const audio = audioQueue.shift();

        if (!audioOutputContext) {
            audioOutputContext = new (window.AudioContext || window.webkitAudioContext)();
        }

        const pcm16 = new Int16Array(audio);
        const floatData = new Float32Array(pcm16.length);
        
        for (let i=0; i < pcm16.length; i++) {
            floatData[i] = pcm16[i] / 32768.0;
        }

        const audioBuffer = audioOutputContext.createBuffer(
            1,
            floatData.length,
            sampleRate
        );
        audioBuffer.getChannelData(0).set(floatData);

        const source = audioOutputContext.createBufferSource();
        source.buffer = audioBuffer;
        source.playbackRate.value = playbackRate;

        const gainNode = audioOutputContext.createGain();
        gainNode.gain.value = 1.0; // Full volume
        
        // Connect the nodes
        source.connect(gainNode);
        gainNode.connect(audioOutputContext.destination);
        
        // Calculate when this chunk should start playing
        const currentTime = audioOutputContext.currentTime;
        const bufferDuration = audioBuffer.duration;
        const effectiveDuration = bufferDuration / playbackRate;
        
        // If nextPlayTime is in the past or too close to current time, move it slightly ahead
        if (nextPlayTime <= currentTime + 0.03) {
            nextPlayTime = currentTime + 0.03; // Small buffer to prevent glitches
        }
        
        // Schedule the audio to start at the calculated time
        source.start(nextPlayTime);
        
        // Update nextPlayTime for the next chunk
        nextPlayTime += effectiveDuration;
    }

    isPlaying = false;
}

function stopAudioOutput() {
    // Reset timing
    nextPlayTime = 0;
    
    // Close the audio context to release resources
    if (audioOutputContext && audioOutputContext.state !== 'closed') {
        audioOutputContext.close();
        audioOutputContext = null;
    }
    
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function renderSupportPlaceholder(message) {
    supportContent.innerHTML = `<p class="support-placeholder">${escapeHtml(message)}</p>`;
}

function renderSupportList(items, renderItem) {
    if (!items || items.length === 0) {
        renderSupportPlaceholder('No records found for this account.');
        return;
    }

    const cards = items.map((item) => `<article class="support-item">${renderItem(item)}</article>`).join('');
    supportContent.innerHTML = `<div class="support-list">${cards}</div>`;
}

function renderProducts(products) {
    renderSupportList(products, (product) => `
        <div class="support-item-title">${escapeHtml(product.name || 'Product')}</div>
        <div class="support-item-meta">Price: ${escapeHtml(product.price ?? 'n/a')} • Stock: ${escapeHtml(product.stock ?? 'n/a')}</div>
        <p>${escapeHtml(product.description || 'No description available.')}</p>
    `);
}

function renderOrders(orders) {
    renderSupportList(orders, (order) => `
        <div class="support-item-title">${escapeHtml(order.id || 'Order')}</div>
        <div class="support-item-meta">Created: ${escapeHtml(order.created_at || 'n/a')} • Total: ${escapeHtml(order.total_price ?? 'n/a')}</div>
        <p>Status: ${escapeHtml(order.status || 'Unknown')} • Products: ${escapeHtml((order.products || []).join(', ') || 'None')}</p>
    `);
}

function renderPayments(payments) {
    renderSupportList(payments, (payment) => `
        <div class="support-item-title">${escapeHtml(payment.id || 'Payment')}</div>
        <div class="support-item-meta">Order: ${escapeHtml(payment.order || 'n/a')} • Created: ${escapeHtml(payment.created_at || 'n/a')}</div>
        <p>Status: ${escapeHtml(payment.status || 'Unknown')}</p>
    `);
}

function renderSupportRequests(items, typeLabel) {
    renderSupportList(items, (item) => `
        <div class="support-item-title">${escapeHtml(item.id || typeLabel)}</div>
        <div class="support-item-meta">Created: ${escapeHtml(item.created_at || 'n/a')}</div>
        <p>${escapeHtml(item.description || 'No description available.')}</p>
    `);
}

async function fetchSupportData(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
    }
    return response.json();
}

async function loadSupportTab(tabName, accountId) {
    if (!accountId) {
        supportTabsContainer?.classList.remove('is-ready');
        renderSupportPlaceholder('Choose an account to start exploring support data.');
        return;
    }

    supportTabsContainer?.classList.add('is-ready');
    renderSupportPlaceholder('Loading data...');

    try {
        let data;
        switch (tabName) {
            case 'products':
                data = await fetchSupportData('/products');
                renderProducts(data);
                break;
            case 'orders':
                data = await fetchSupportData(`/orders/${accountId}`);
                renderOrders(data);
                break;
            case 'payments':
                data = await fetchSupportData(`/payments/${accountId}`);
                renderPayments(data);
                break;
            case 'requests':
                data = await fetchSupportData(`/requests/${accountId}`);
                renderSupportRequests(data, 'Request');
                break;
            case 'complaints':
                data = await fetchSupportData(`/complaints/${accountId}`);
                renderSupportRequests(data, 'Complaint');
                break;
            default:
                renderSupportPlaceholder('Select a tab to view support data.');
        }
    } catch (error) {
        console.error(error);
        renderSupportPlaceholder('Unable to load support data right now.');
    }
}

function setActiveSupportTab(tabName) {
    activeSupportTab = tabName;
    supportTabButtons.forEach((button) => {
        button.classList.toggle('active', button.dataset.tab === tabName);
    });
}

function handleSupportAccountChange(event) {
    selectedAccountId = event.target.value;

    if (!selectedAccountId) {
        supportTabsContainer?.classList.remove('is-ready');
        renderSupportPlaceholder('Choose an account to start exploring support data.');
        return;
    }

    setActiveSupportTab(activeSupportTab);
    loadSupportTab(activeSupportTab, selectedAccountId);
}

function setAgentCardCollapsed(isCollapsed) {
    agentCard?.classList.toggle('collapse', isCollapsed);
    appShell?.classList.toggle('support-mode', isCollapsed);
    collapseToggle?.setAttribute('aria-expanded', String(!isCollapsed));
    if (collapseToggle) {
        collapseToggle.textContent = isCollapsed ? 'Expand Card' : 'Collapse Card';
    }
}

function handleStartCustomerSupportMode() {
    setAgentCardCollapsed(true);
    customerSupportMode?.classList.add('show');
}

function handleExitCustomerSupportMode() {
    setAgentCardCollapsed(false);
    customerSupportMode?.classList.remove('show');
}

function handleUpdateAccount(field) {
    const updateForm = document.getElementById('update-form');
    const fieldEle = updateForm.querySelector(`input#${field}`);
    updateForm.classList.add('active');
    fieldEle.classList.add('active');

    updateForm.querySelector('button').onclick = (e) => {
        
        
        const response = fetch(`/account-update/${selectedAccountId}`, {
            method: 'POST',
            body: JSON.stringify({
                field: field,
                value: fieldEle.value        
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(response => {
            if (response.ok) {
                if (websocket instanceof WebSocket) {
                    websocket.send(
                        JSON.stringify({
                            status: "UserAccountUpdated",
                            account: selectedAccountId
                        })
                    )
                }

                updateForm.classList.remove('active');
                fieldEle.classList.remove('active');
            }
        })
            
    }
}

function handlePayment(paymentId) {
    const form = document.getElementById('payment-form');
    form.classList.add('active');

    form.querySelector('button').onclick = (e) => {
        fetch(`/pay/${paymentId}/${selectedAccountId}`, {
            method: 'POST',
            body: JSON.stringify({
                complete: true
            }),
            headers: {
                'Content-type': 'application/json'
            }
        }).then(response => {
            if (response.ok) {
                if (websocket instanceof WebSocket) {
                    websocket.send(
                        JSON.stringify({
                            status: 'PaymentCompleteDone',
                            account: selectedAccountId,
                            payment: paymentId
                        })
                    )
                }
                form.classList.remove('active')
            }
        })
    }
}

const handleConnect = async () => {
    if (websocket) {
        websocket.close();
        stopAudioCapture()
        startButton.innerText = 'Start Conversation';
        voiceWave?.classList.remove('active');
        statusPanel?.classList.remove('is-speaking');
        statusText.textContent = 'Idle';
        statusMessage.textContent = 'Ready when you are.'
        websocket = null;
        started = false;
        return;
    }

    const hasPermission = await requestMicrophonePermission();
    if (!hasPermission) {
        alert('Microphone permission is required for the voice agent to work.');
        return;
    }

    const captureStarted = await startAudioCapture();
    if (!captureStarted) {
        alert('Failed to start audio capture. Please check your microphone settings and browser permissions.');
        return;
    }

    const language = languageSelect?.value || 'en';
    const mode = modeSelect?.value || 'general';

    if (language === 'ar') {
        sampleRate = 24000;
        playbackRate = 1.05;
    } else {
        sampleRate = 16000;
        playbackRate = 1;
    }

    websocket = new WebSocket(`/agent/${mode}/${language}`);
    
    websocket.onopen = (e) => {
        console.log('connected!')
        started = true;
    }
    
    websocket.onmessage = async (e) => {
        let data = e.data;
        if (data instanceof Blob) {
            if (!data || data.size === 0) {
                console.error("The provided Blob is empty.");
                return;
            }
            const buffer = await data.arrayBuffer()
            audioQueue.push(buffer);
            playAudio();

        } else if (data instanceof ArrayBuffer) {
            audioQueue.push(data);
            playAudio();
            
        } else {
            data = JSON.parse(data);
            console.log(data)
            try {
                if (data.status) {
                    
                    if (data.status === 'AgentAudioDone') {
                        
                        voiceWave?.classList.remove('active');
                        statusText.textContent = 'Listening';
                        statusMessage.textContent = 'Waiting for your next command...';
                        
                    } 
                    if (data.status === 'UserStartedSpeaking') {
                        stopAudioOutput()
                    }
                    if (data.status === 'UpdateUserAccount') {
                        handleUpdateAccount(data.field);
                    }
                    if (data.status === 'PaymentComplete') {
                        handlePayment(data.payment)
                    }
                }
            } catch (error) {
                console.log('Error: ', error)
            }
        }
    }

    websocket.onclose = (e) => {
        stopAudioCapture()
        startButton.innerText = 'Start Conversation';
        voiceWave?.classList.remove('active');
        statusPanel?.classList.remove('is-speaking');
        statusText.textContent = 'Idle';
        statusMessage.textContent = 'Ready when you are.'
        websocket = null;
        started = false;
    }
    startButton.innerText = 'End Conversation';
};

if (startButton) {
    startButton.addEventListener('click', handleConnect)

    languageSelect.addEventListener('change', () => {
        if (websocket) {
            websocket.close();
            stopAudioCapture()
            websocket = null;
        }
        if (started) handleConnect();
    });

    modeSelect.addEventListener('change', (e) => {
        if (websocket) {
            websocket.close();
            stopAudioCapture()

            websocket = null;
        }

        if (e.target.value === 'support') {
            handleStartCustomerSupportMode();
        } else {
            handleExitCustomerSupportMode();
        }

        if (started) handleConnect();
    })

    collapseToggle?.addEventListener('click', () => {
        const isCollapsed = !agentCard?.classList.contains('collapse');
        setAgentCardCollapsed(isCollapsed);
    });

    supportTabButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            if (!tabName || !selectedAccountId) return;
            setActiveSupportTab(tabName);
            loadSupportTab(tabName, selectedAccountId);
        });
    });

    accountSelect?.addEventListener('change', handleSupportAccountChange);

    if (accountSelect) {
        accountSelect.value = 'ACC-100001';
        handleSupportAccountChange({ target: accountSelect });
    }
}
