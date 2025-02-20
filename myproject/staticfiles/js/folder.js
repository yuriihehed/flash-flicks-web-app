// static/js/folder.js

document.addEventListener("DOMContentLoaded", function () {
    var modal = document.getElementById("folderModal");
    var openModal = document.getElementById("openModal");
    var closeModal = document.querySelector(".close");

    // Open Modal
    if (openModal) {
        openModal.onclick = function () {
            modal.style.display = "block";
        };
    }

    // Close Modal
    if (closeModal) {
        closeModal.onclick = function () {
            modal.style.display = "none";
        };
    }

    // Close Modal When Clicking Outside the Modal
    window.onclick = function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };

    // Handle AJAX Form Submission
    document.getElementById("folderForm").addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent traditional form submission
        var formData = new FormData(this);

        fetch(folderCreateUrl, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById("responseMessage").innerHTML = "Folder created: " + data.folder_name;
                setTimeout(() => {
                    modal.style.display = "none"; // Close modal on success
                    document.getElementById("folderForm").reset(); // Reset form
                    document.getElementById("responseMessage").innerHTML = ""; // Clear message
                }, 2000);
            } else {
                document.getElementById("responseMessage").innerHTML = "Folder creation failed.";
            }
        });
    });
});
