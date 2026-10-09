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

document.querySelectorAll('.local-time').forEach(el => {
    const utcStr = el.getAttribute('data-utc');
    if (utcStr) {
        const date = new Date(utcStr);
        if (!isNaN(date.getTime())) {
            const datePart = date.toLocaleDateString(undefined, {
                month: 'short',
                day: '2-digit',
                year: 'numeric'
            });
            const timePart = date.toLocaleTimeString(undefined, {
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
            });
            el.innerHTML = `${datePart}<br>${timePart}`;
        }
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const submitBtn = document.getElementById('submitBtn');

    submitBtn.addEventListener('click', function() {
        // Disables the button immediately upon clicking
        this.disabled = true;
        
        // Optional: change button text so the user knows it worked
        this.innerText = 'Processing...';
        
        // If the button is inside a form, manually submit it
        this.form.submit();
    });
});

const form = document.querySelector('form');

form.addEventListener('submit', (e) => {
    const fileInput = document.getElementById('pdfFile');
    
    if (fileInput && fileInput.files.length === 0) {
        e.preventDefault();
        alert('Please choose a PDF file before uploading!');
        return;
    }

    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.innerText = 'Uploading...';
});