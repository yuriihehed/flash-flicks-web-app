/*
what does this do?
1. Selects all elements with the class .flashcard.
2. Uses a currentIndex variable and an updateCards() function to only display the card at that index (by toggling a .show class).
3. Sets up event listeners on the Prev/Next buttons to change the index and update the display.
4. Adds a click handler to each card that toggles the .flipped class (unless the click comes from a star or edit button or if the card is in editing mode).
5. Defines global functions for the star flash effect (flashEffect) and for toggling edit mode (toggleEdit).
6. Finally, initializes the display by calling updateCards().
*/
document.addEventListener('DOMContentLoaded', function() {
    // 1. Select all flashcards
    const cards = document.querySelectorAll('.flashcard');
    let currentIndex = 0;
  
    // 2. Function to show only the current card
    function updateCards() {
      cards.forEach((card, index) => {
        card.classList.remove('show');
        if (index === currentIndex) {
          card.classList.add('show');
        }
      });
      // Update the card counter
      const cardCounter = document.getElementById('cardCounter');
      if (cardCounter) {
        cardCounter.textContent = `${currentIndex + 1} / ${cards.length}`;
      }
    }
  
    // 3. Next/Prev Button Handlers
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
  
    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        if (currentIndex > 0) {
          currentIndex--;
        }
        updateCards();
      });
    }
  
    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        if (currentIndex < cards.length - 1) {
          currentIndex++;
        }
        updateCards();
      });
    }
  
    // 4. Flip on click (unless star/edit is clicked)
    cards.forEach(card => {
      card.addEventListener('click', function(e) {
        // If we didn't click a star/edit button and the card is not in "editing" mode
        if (!e.target.classList.contains('star-btn') && 
            !e.target.classList.contains('edit-btn') &&
            !card.classList.contains('editing')) {
          card.classList.toggle('flipped');
        }
      });
    });
  
    // 5. Star flash effect
    window.flashEffect = function(button) {
      const card = button.closest('.flashcard');
      card.classList.add('flash');
      setTimeout(() => card.classList.remove('flash'), 500);
    };
  
    // 6. Toggle Edit
    window.toggleEdit = function(button, event) {
      event.stopPropagation(); // avoid flipping when clicking edit button
      const card = button.closest('.flashcard');
      const fields = card.querySelectorAll('.card-title, .card-term, .card-back-title, .card-back-content');
      const isEditing = card.classList.contains('editing');
  
      if (isEditing) {
        // Save mode
        fields.forEach(el => {
          el.contentEditable = "false";
          el.classList.remove('editable');
        });
        card.classList.remove('editing');
        button.textContent = "Edit";
      } else {
        // Edit mode
        fields.forEach(el => {
          el.contentEditable = "true";
          el.classList.add('editable');
        });
        card.classList.add('editing');
        button.textContent = "Save";
      }
    };
  
    // 7. Initialize
    updateCards();
  });
  