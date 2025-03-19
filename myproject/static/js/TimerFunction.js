
document.addEventListener("DOMContentLoaded", function () {
    // If there's a global timer running, stop it
    if (window.globalTimer) {
        clearInterval(window.globalTimer);
        console.log("Stopped global timer.");
    }

    // Check if the timer should be displayed
    checkIfOnTimerPage();

    // Initialize flipping functionality
    document.querySelectorAll('.flashcard').forEach(card => {
        card.addEventListener("click", function (e) {
            if (!e.target.classList.contains("star-btn") && !e.target.classList.contains("edit-btn") && !card.classList.contains("editing")) {
                this.classList.toggle("flipped");
            }
        });
    });

    updateCards();
});

function checkIfOnTimerPage() {
    const heroTimer = document.getElementById("heroTimerWidget");
    const timerEnabled = localStorage.getItem("study_timer_active");

    if (timerEnabled === "true") {
        heroTimer.style.display = "block";
        startTimer();
    }
}

function startTimer() {
    let timerDisplay = document.getElementById("timerDisplay");
    let seconds = 0;
    let minutes = 0;

    window.globalTimer = setInterval(() => {
        seconds++;
        if (seconds === 60) {
            seconds = 0;
            minutes++;
        }
        timerDisplay.innerText = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }, 1000);
}

const cards = document.querySelectorAll('.flashcard');
let currentIndex = 0;

function updateCards() {
    cards.forEach((card, index) => {
        card.style.display = index === currentIndex ? 'block' : 'none';
    });
    document.getElementById('cardCounter').innerText = `${currentIndex + 1} / ${cards.length}`;
}

document.getElementById('prevBtn').addEventListener('click', () => {
    currentIndex = Math.max(0, currentIndex - 1);
    updateCards();
});

document.getElementById('nextBtn').addEventListener('click', () => {
    currentIndex = Math.min(cards.length - 1, currentIndex + 1);
    updateCards();
});

function toggleFavorite(element) {
    const card = element.closest('.flashcard');
    card.classList.toggle('flash');
    setTimeout(() => card.classList.remove('flash'), 500);
}

function toggleEdit(button, event) {
    event.stopPropagation();

    const card = button.closest('.flashcard');
    const fields = card.querySelectorAll('.card-title, .card-term, .card-back-title, .card-back-content');

    const isEditing = card.classList.contains('editing');

    if (isEditing) {
        fields.forEach(el => {
            el.contentEditable = "false";
            el.classList.remove('editable');
        });
        card.classList.remove('editing');
        button.textContent = "Edit";
    } else {
        fields.forEach(el => {
            el.contentEditable = "true";
            el.classList.add('editable');
        });
        card.classList.add('editing');
        button.textContent = "Save";
    }
}

updateCards();