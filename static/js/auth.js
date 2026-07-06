const passwordInput = document.querySelector('#password');
const toggleButton = document.querySelector('#toggle-password');

toggleButton.addEventListener('click', () => {
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleButton.textContent = 'Hide'; 
    } else {
        passwordInput.type = 'password';
        toggleButton.textContent = 'Show';
    }
});