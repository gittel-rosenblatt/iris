document.addEventListener('DOMContentLoaded', () => {
// Voice-to-Text 

    const inputs = document.querySelectorAll('input[type="text"], input[type="tel"], input[type="email"], textarea');

    inputs.forEach(input => {
        if (input.parentNode.classList.contains('input-with-vtt')) return;

        const wrapper = document.createElement('div');
        wrapper.className = 'input-with-vtt';

        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'vtt-icon-btn';
        btn.innerHTML = '🎤';
        btn.setAttribute('data-tooltip', 'Click to speak');
        btn.setAttribute('aria-label', 'Click to speak');

        wrapper.appendChild(btn);

        let recognition = null;
        let isListening = false;

        btn.addEventListener('click', () => {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) return alert("Browser doesn't support Web Speech API");

            if (isListening && recognition) {
                recognition.stop();
                return;
            }

            recognition = new SpeechRecognition();
            isListening = true;
            btn.textContent = '🔴';
            btn.setAttribute('data-tooltip', 'Click to stop listening');

            recognition.onresult = (e) => {
                input.value = e.results[0][0].transcript;
            };

            recognition.onend = () => {
                isListening = false;
                btn.textContent = '🎤';
                btn.setAttribute('data-tooltip', 'Click to speak');
            };

            recognition.onerror = () => {
                isListening = false;
                btn.textContent = '🎤';
                btn.setAttribute('data-tooltip', 'Click to speak');
            };

            recognition.start();
        });
    });

// Text-to-Speech 
    const ttsButtons = document.querySelectorAll('.btn-tts');
    let isClicked = false;

    ttsButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();

            isClicked = !isClicked;

            if (isClicked) {
                btn.innerHTML = 'Stop <span aria-hidden="true">⏹️</span>';
                document.body.classList.add('active');
            } else {
                btn.innerHTML = 'Listen <span aria-hidden="true">🔊</span>';
                document.body.classList.remove('active');
                window.speechSynthesis.cancel()
            }
        });
    });
            
    document.addEventListener('click', (e) => {
        if (!isClicked) {
            return;
        } else if (e.target.closest('[aria-hidden="true"]')) {
            return; 
        } else {
            e.preventDefault();
            const clone = e.target.cloneNode(true);
            clone.querySelectorAll('[aria-hidden="true"]').forEach(el => el.remove());
            const text = clone.innerText;
            const readText = new SpeechSynthesisUtterance(text);
            window.speechSynthesis.cancel()
            window.speechSynthesis.speak(readText);

            if (!('speechSynthesis' in window)) {
            console.warn('Text-to-Speech is not supported in this browser.');
        }
    }});
});