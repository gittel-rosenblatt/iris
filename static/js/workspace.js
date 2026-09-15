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

document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.question-card');
    const jumpSelect = document.getElementById('question-jump-select');
    const progress = document.getElementById('progressFill');
    const progressPercent = document.getElementById('progressPercent'); 
    const
    let currentIndex = 0;

    function showCard(index) {
        cards.forEach(card => card.classList.remove('active'));
        
        if (cards[index]) {
        cards[index].classList.add('active');

        currentIndex = index;

        const percentage = (currentIndex + 1) / cards.length * 100;
        progress.style.width = `${percentage}%`;
        progressPercent.textContent = `${Math.round(percentage)}%`;
        }
    }

    document.querySelectorAll('.next-btn').forEach(button => {
        button.addEventListener('click', () => {
        if (currentIndex < cards.length - 1) {
            currentIndex++;
            showCard(currentIndex);
        }

        if (currentIndex == cards.length - 1) {
            
        }
        });
    });

    document.querySelectorAll('.prev-btn').forEach(button => {
        button.addEventListener('click', () => {
            if (currentIndex > 0) {
                currentIndex--;
                showCard(currentIndex);
            }
        });
    });

    if (jumpSelect) {
        jumpSelect.addEventListener('change', (e) => {
            const selectedIndex = parseInt(e.target.value, 10);
            showCard(selectedIndex);
        });
    }
});