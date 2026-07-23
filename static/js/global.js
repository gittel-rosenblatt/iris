document.addEventListener('DOMContentLoaded', () => {
    const inputs = document.querySelectorAll('input[type="text"], input[type="tel"], input[type="email"], textarea');

    inputs.forEach(input => {
        // Prevent adding multiple mic buttons if script runs twice
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
});