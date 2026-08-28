const trigger = document.querySelector('#profileTrigger');
const menu = document.querySelector('#dropdownMenu');

trigger.addEventListener('click', (event) => {
    event.stopPropagation(); 
    menu.classList.toggle('show');
});

document.addEventListener('click', (event) => {
    if (!trigger.contains(event.target) && !menu.contains(event.target)) {
        menu.classList.remove('show');
    }
});

const closeBannerBtn = document.querySelector('#bannerClose');
const autofillBanner = document.querySelector('.autofill-banner');

closeBannerBtn?.addEventListener('click', () => {
    autofillBanner.classList.add('close');
});

const passwordModal = document.querySelector('#passwordModal');
const openModalBtn = document.querySelector('#changePassword');
const closeModalBtn = document.querySelector('#closePasswordModal');
const cancelModalBtn = document.querySelector('#cancelPasswordModal');

openModalBtn?.addEventListener('click', () => {
    passwordModal.classList.add('is-open');
    passwordModal.setAttribute('aria-hidden', 'false');
});

const closeModal = () => {
    passwordModal.classList.remove('is-open');
    passwordModal.setAttribute('aria-hidden', 'true');
};

closeModalBtn.addEventListener('click', closeModal);
cancelModalBtn.addEventListener('click', closeModal);

window.addEventListener('click', (e) => {
    if (e.target === passwordModal) {
        closeModal();
    }
});

const currentInput = document.querySelector('#current-password');
const currentToggle = document.querySelector('#toggle-current-password');

currentToggle?.addEventListener('click', () => {
    if (currentInput.type === 'password') {
        currentInput.type = 'text';
        currentToggle.textContent = 'Hide'; 
    } else {
        currentInput.type = 'password';
        currentToggle.textContent = 'Show';
    }
});

const newInput = document.querySelector('#new-password');
const newToggle = document.querySelector('#toggle-new-password');

newToggle?.addEventListener('click', () => {
    if (newInput.type === 'password') {
        newInput.type = 'text';
        newToggle.textContent = 'Hide'; 
    } else {
        newInput.type = 'password';
        newToggle.textContent = 'Show';
    }
});

const confirmInput = document.querySelector('#confirm-password');
const confirmToggle = document.querySelector('#toggle-confirm-password');

confirmToggle?.addEventListener('click', () => {
    if (confirmInput.type === 'password') {
        confirmInput.type = 'text';
        confirmToggle.textContent = 'Hide'; 
    } else {
        confirmInput.type = 'password';
        confirmToggle.textContent = 'Show';
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.get('modal') === 'password') {
        const passwordModal = document.querySelector('#passwordModal');
        passwordModal?.classList.add('is-open');
        passwordModal?.setAttribute('aria-hidden', 'false');
    }
});