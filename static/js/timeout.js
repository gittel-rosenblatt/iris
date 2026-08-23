const LOGOUT_AFTER_MS = 21600000; // 6 hours
const WARN_AFTER_MS = 21000000;   // 5 hours and 50 minutes

let warnTimer = setTimeout(showAccessibleWarning, WARN_AFTER_MS);
let logoutTimer = setTimeout(forceLogout, LOGOUT_AFTER_MS);
let countdownTimer;
let warningModal;

function forceLogout() {
    window.location.href = "/logout";
}

function showAccessibleWarning() {
    warningModal.show();

    let secondsLeft = 600; // 10 minutes in seconds

    countdownTimer = setInterval(() => {
        secondsLeft--; 

        let numOfMinutes = Math.floor(secondsLeft / 60); 
        let numOfSeconds = secondsLeft % 60; 
        
        const countdownText = document.getElementById("countdown");
        countdownText.textContent = `in ${numOfMinutes} minutes and ${numOfSeconds} seconds`;

        if (secondsLeft % 60 === 0) {
            const srText = document.getElementById("accessible-countdown");
            srText.textContent = `Your session expires in ${numOfMinutes} minutes.`;
        }

        if (secondsLeft == 0) {
            clearInterval(countdownTimer);
            forceLogout();
        }
    }, 1000);
}

const modalElement = document.getElementById('logoutWarningModal');
warningModal = new bootstrap.Modal(modalElement);

modalElement.addEventListener('shown.bs.modal', () => {
    document.getElementById("button").focus();
});

const button = document.getElementById("button");
button.addEventListener("click", function() {
    clearInterval(countdownTimer);
    clearTimeout(warnTimer);
    clearTimeout(logoutTimer);
    
    warnTimer = setTimeout(showAccessibleWarning, WARN_AFTER_MS);
    logoutTimer = setTimeout(forceLogout, LOGOUT_AFTER_MS);
    
    fetch('/keep-alive', { method: 'POST' })
        .then(response => response.json())
        .then(data => console.log(data.status))
        .catch(error => console.error('Error keeping session alive:', error));
        
    warningModal.hide();
});

modalElement.addEventListener('hide.bs.modal', () => {
    document.activeElement.blur(); // Instantly drops focus before the modal hides
});


modalElement.addEventListener('hidden.bs.modal', () => {
    document.getElementById("focus").focus();
});
