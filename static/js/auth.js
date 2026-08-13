const loginInput = document.querySelector('#password');
const loginToggle = document.querySelector('#toggle-login-pass');

loginToggle?.addEventListener('click', () => {
    if (loginInput.type === 'password') {
        loginInput.type = 'text';
        loginToggle.textContent = 'Hide'; 
    } else {
        loginInput.type = 'password';
        loginToggle.textContent = 'Show';
    }
});

const signupInput = document.querySelector('#choose-password');
const signupToggle = document.querySelector('#toggle-signup-pass');

signupToggle?.addEventListener('click', () => {
    if (signupInput.type === 'password') {
        signupInput.type = 'text';
        signupToggle.textContent = 'Hide'; 
    } else {
        signupInput.type = 'password';
        signupToggle.textContent = 'Show';
    }
});

const confirmInput = document.querySelector('#confirm-password');
const confirmToggle = document.querySelector('#toggle-confirm-pass');

confirmToggle?.addEventListener('click', () => {
    if (confirmInput.type === 'password') {
        confirmInput.type = 'text';
        confirmToggle.textContent = 'Hide'; 
    } else {
        confirmInput.type = 'password';
        confirmToggle.textContent = 'Show';
    }
});

const resetInput = document.querySelector('#reset-password');
const resetToggle = document.querySelector('#toggle-reset-pass');

resetToggle?.addEventListener('click', () => {
    if (resetInput.type === 'password') {
        resetInput.type = 'text';
        resetToggle.textContent = 'Hide'; 
    } else {
        resetInput.type = 'password';
        resetToggle.textContent = 'Show';
    }
});

const confirmResetInput = document.querySelector('#confirm-reset-password');
const confirmResetToggle = document.querySelector('#toggle-confirm-reset-pass');

confirmResetToggle?.addEventListener('click', () => {
    if (confirmResetInput.type === 'password') {
        confirmResetInput.type = 'text';
        confirmResetToggle.textContent = 'Hide'; 
    } else {
        confirmResetInput.type = 'password';
        confirmResetToggle.textContent = 'Show';
    }
});