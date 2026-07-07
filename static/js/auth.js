const loginInput = document.querySelector('#password');
const loginToggle = document.querySelector('#toggle-login-pass');

loginToggle.addEventListener('click', () => {
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

signupToggle.addEventListener('click', () => {
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

confirmToggle.addEventListener('click', () => {
    if (confirmInput.type === 'password') {
        confirmInput.type = 'text';
        confirmToggle.textContent = 'Hide'; 
    } else {
        confirmInput.type = 'password';
        confirmToggle.textContent = 'Show';
    }
});


const switchToSignup = document.getElementById('switch-to-signup');
const switchToLogin = document.getElementById('switch-to-login');
const body = document.body; 

switchToSignup.addEventListener('click', () => {
    body.classList.add('is-switched');
});

switchToLogin.addEventListener('click', () => {
    body.classList.remove('is-switched');
});