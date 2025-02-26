// static/js/folder.js
document.addEventListener("DOMContentLoaded", function () {
    // Modal elements
    const modal = document.getElementById("folderModal");
    const openModalButtons = document.querySelectorAll("[id^='openModal']");
    const closeModal = document.querySelector(".close");
    
    // Open modal from any button with ID starting with "openModal"
    openModalButtons.forEach(button => {
        button.addEventListener("click", function() {
            modal.style.display = "block";
        });
    });
    
    // Close modal with X button
    if (closeModal) {
        closeModal.addEventListener("click", function() {
            modal.style.display = "none";
        });
    }
    
    // Close modal when clicking outside
    window.addEventListener("click", function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
    
    // Form submission
    const folderForm = document.getElementById("folderForm");
    if (folderForm) {
        folderForm.addEventListener("submit", function(event) {
            event.preventDefault();
            const formData = new FormData(this);
            const responseMessage = document.getElementById("responseMessage");
            
            // Show loading message
            responseMessage.innerHTML = "Creating folder...";
            
            fetch(folderCreateUrl, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Server response:", data);
                if (data.success) {
                    responseMessage.innerHTML = "Folder created successfully! Refreshing...";
                    // Refresh the page after successful creation
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                } else {
                    responseMessage.innerHTML = "Error: " + (data.error || "Unknown error");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                responseMessage.innerHTML = "Error: " + error.message;
            });
        });
    }
    
    // Sidebar toggle
    const sidebar = document.getElementById("sidebar");
    const toggleBtn = document.getElementById("sidebarToggle");
    
    if (sidebar && toggleBtn) {
        toggleBtn.addEventListener("click", function() {
            sidebar.classList.toggle("sidebar-collapsed");
            sidebar.classList.toggle("sidebar-expanded");
            
            if (sidebar.classList.contains("sidebar-collapsed")) {
                toggleBtn.innerHTML = "➜";
            } else {
                toggleBtn.innerHTML = "➡";
            }
        });
    }
});