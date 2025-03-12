window.onload = function () {
    const progressElement = document.querySelector(".study-progress p");
    const cards = document.querySelectorAll(".flashcard");
    let currentIndex = 0;
    const totalCards = cards.length;
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const cardCounter = document.getElementById("cardCounter");
    const learnedBtn = document.getElementById("learned-btn");
    const notLearnedBtn = document.getElementById("not-learned-btn");

    // 1. Initialize Chart.js
    const ctx = document.getElementById('myProgressChart').getContext('2d');
    const myChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Learned', 'Not Learned'],
            datasets: [{
                label: 'Study Progress',
                data: [0, 0], // We'll fill this dynamically
                backgroundColor: [
                    'rgba(75, 192, 192, 0.6)',  // Teal for "Learned"
                    'rgba(255, 99, 132, 0.6)'   // Red for "Not Learned"
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: 'Flashcard Study Progress'
                }
            }
        }
    });
    // 2. Function to count Learned vs Not Learned from the DOM
    function countLearnedStatus() {
        let learnedCount = 0;
        let notLearnedCount = 0;
        const statusSpans = document.querySelectorAll('.learned-status span');
        statusSpans.forEach((span) => {
            const text = span.innerText.trim();
            if (text === "Learned ✅") {
                learnedCount++;
            } else if (text === "Not Learned ❌") {
                notLearnedCount++;
            }
        });
        return [learnedCount, notLearnedCount];
    }
    // 3. Function to update the chart data
    function updateChart() {
        const [learnedCount, notLearnedCount] = countLearnedStatus();
        myChart.data.datasets[0].data[0] = learnedCount;
        myChart.data.datasets[0].data[1] = notLearnedCount;
        myChart.update();
        // After updating the chart, update the percentage text
        updateProgress(learnedCount, notLearnedCount);
    }
    // 4. Display the percentage in the "Progress: X%" paragraph
    function updateProgress(learnedCount, notLearnedCount) {
        const total = learnedCount + notLearnedCount;
        let percentage = 0;
        if (total > 0) {
            percentage = Math.round((learnedCount / total) * 100);
        }
        // Update the DOM text
        progressElement.innerText = `Progress: ${percentage}%`;
    }

    function updateCards() {
        cards.forEach((card, index) => {
            card.style.display = index === currentIndex ? "block" : "none";
        });
        cardCounter.innerText = `${currentIndex + 1} / ${totalCards}`;
    }

    prevBtn.addEventListener("click", () => {
        currentIndex = Math.max(0, currentIndex - 1);
        updateCards();
    });

    nextBtn.addEventListener("click", () => {
        currentIndex = Math.min(totalCards - 1, currentIndex + 1);
        updateCards();
    });

    learnedBtn.addEventListener("click", () => markLearned(true));
    notLearnedBtn.addEventListener("click", () => markLearned(false));


    cards.forEach(card => {
        card.addEventListener("click", function (e) {
            if (
                !e.target.classList.contains("star-btn") &&
                !card.classList.contains("editing")
            ) {
                this.classList.toggle("flipped");
            }
        });
    });

    updateCards();


    function markLearned(learned) {
        const flashcardId = cards[currentIndex].id.replace("card", "");

        fetch(`/update_flashcard_status/${flashcardId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ learned: learned }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log(
                        `✅ Flashcard ${flashcardId} marked as ${learned ? "Learned" : "Not Learned"
                        }`
                    );

                    const termBox = document.querySelector(
                        `.term-box[data-flashcard-id='${flashcardId}']`
                    );
                    if (termBox) {
                        const statusSpan = termBox.querySelector(".learned-status span");
                        if (statusSpan) {
                            if (learned) {
                                statusSpan.innerText = "Learned ✅";
                                statusSpan.classList.remove("text-danger");
                                statusSpan.classList.add("text-success");
                            } else {
                                statusSpan.innerText = "Not Learned ❌";
                                statusSpan.classList.remove("text-success");
                                statusSpan.classList.add("text-danger");
                            }
                        }
                    }
                    // Update the chart whenever a flashcard's status changes
                    updateChart();
                } else {
                    console.error("❌ Error updating status:", data.error);
                }
            })
            .catch(error => console.error("❌ API Error:", error));
    }
    // 5. Initial chart update based on the current DOM state
    updateChart();
};


function toggleStar(button, event) {
    event.stopPropagation();
    flashEffect(button);

    const card = button.closest('.flashcard');
    const flashcardId = card.id.replace("card", "");

    const isCurrentlyStarred = button.classList.contains("active-star");
    const newStarredState = !isCurrentlyStarred;

    if (newStarredState) {
        button.classList.add("active-star");
    } else {
        button.classList.remove("active-star");
    }

    fetch(`/update_star_status/${flashcardId}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({ starred: newStarredState }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log(`Flashcard ${flashcardId} star set to ${newStarredState}`);

                const termBox = document.querySelector(
                    `.term-box[data-flashcard-id='${flashcardId}']`
                );
                if (termBox) {

                    let cornerStarSpan = termBox.querySelector(".corner-star");

                    if (!cornerStarSpan) {
                        cornerStarSpan = document.createElement("span");
                        cornerStarSpan.classList.add("corner-star");
                        cornerStarSpan.innerText = "★";

                        const heading = termBox.querySelector("h3");
                        heading.appendChild(cornerStarSpan);
                    }


                    if (newStarredState) {
                        cornerStarSpan.style.display = "inline";
                    } else {
                        cornerStarSpan.style.display = "none";
                    }
                }
            } else {
                console.error("Error toggling star:", data.error);
            }
        })
        .catch(err => console.error(err));
}


function flashEffect(element) {
    const card = element.closest('.flashcard');
    card.classList.add('flash');
    setTimeout(() => card.classList.remove('flash'), 500);
}


function toggleEdit(button, event) {
    event.stopPropagation();

    const card = button.closest('.flashcard');

    const fields = card.querySelectorAll('.card-title, .card-term');
    const isEditing = card.classList.contains('editing');

    if (isEditing) {

        fields.forEach(el => {
            el.contentEditable = "false";
            el.classList.remove('editable');
        });
        card.classList.remove('editing');
        button.textContent = "Edit";


        const flashcardId = card.id.replace("card", "");
        const newTerm = card.querySelector('.card-title').innerText;
        const newDefinition = card.querySelector('.card-term').innerText;


        fetch(`/update_flashcard_text/${flashcardId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ term: newTerm, definition: newDefinition }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log(`✅ Updated text for flashcard ${flashcardId}`);

                    const termBox = document.querySelector(
                        `.term-box[data-flashcard-id='${flashcardId}']`
                    );
                    if (termBox) {
                        const termHeading = termBox.querySelector('h3');
                        const definitionParagraph = termBox.querySelector('p');
                        if (termHeading && definitionParagraph) {
                            termHeading.innerText = newTerm;
                            definitionParagraph.innerText = newDefinition;
                        }
                    }
                } else {
                    console.error("❌ Error updating text:", data.error);
                }
            })
            .catch(error => console.error("❌ API Error:", error));

    } else {
        // --- EDIT MODE ---
        fields.forEach(el => {
            el.contentEditable = "true";
            el.classList.add('editable');
        });
        card.classList.add('editing');
        button.textContent = "Save";
    }
}

function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value;
}