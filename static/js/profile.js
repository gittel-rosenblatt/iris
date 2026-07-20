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

closeBannerBtn.addEventListener('click', () => {
    autofillBanner.classList.add('close');
});

const passwordModal = document.querySelector('#passwordModal');
const openModalBtn = document.querySelector('#changePassword');
const closeModalBtn = document.querySelector('#closePasswordModal');
const cancelModalBtn = document.querySelector('#cancelPasswordModal');

openModalBtn.addEventListener('click', () => {
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