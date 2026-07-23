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