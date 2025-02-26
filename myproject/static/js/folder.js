// // static/js/folder.js

// document.addEventListener("DOMContentLoaded", function () {
//     var modal = document.getElementById("folderModal");
//     var openModal = document.getElementById("openModal");
//     var closeModal = document.querySelector(".close");

//     // Open Modal
//     if (openModal) {
//         openModal.onclick = function () {
//             modal.style.display = "block";
//         };
//     }

//     // Close Modal
//     if (closeModal) {
//         closeModal.onclick = function () {
//             modal.style.display = "none";
//         };
//     }

//     // Close Modal When Clicking Outside the Modal
//     window.onclick = function (event) {
//         if (event.target === modal) {
//             modal.style.display = "none";
//         }
//     };

//     // Handle AJAX Form Submission
//     document.getElementById("folderForm").addEventListener("submit", function (event) {
//         event.preventDefault(); // Prevent traditional form submission
//         var formData = new FormData(this);

//         fetch(folderCreateUrl, {
//             method: "POST",
//             body: formData,
//             headers: {
//                 "X-CSRFToken": csrfToken
//             }
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.success) {
//                 document.getElementById("responseMessage").innerHTML = "Folder created: " + data.folder_name;
// //                 setTimeout(() => {
// //                     modal.style.display = "none"; // Close modal on success
// //                     document.getElementById("folderForm").reset(); // Reset form
// //                     document.getElementById("responseMessage").innerHTML = ""; // Clear message
// //                     location.reload(); // Reload the page to show the new folder
// //                 }, 2000);
// //             } else {
// //                 document.getElementById("responseMessage").innerHTML = "Folder creation failed.";
// //             }
// //         });
// //     });
// // });


// document.addEventListener("DOMContentLoaded", function() {
//     // Get both modal buttons
//     const openModalBtn = document.getElementById("openModal");
//     const openModalMainBtn = document.getElementById("openModalMain");
//     const modal = document.getElementById("folderModal");
//     const closeBtn = document.querySelector(".close");
//     const folderForm = document.getElementById("folderForm");
//     const responseMessage = document.getElementById("responseMessage");

//     // Function to open modal
//     function openModal() {
//         modal.style.display = "block";
//     }

//     // Function to close modal
//     function closeModal() {
//         modal.style.display = "none";
//     }

//     // Add event listeners to both buttons
//     if (openModalBtn) {
//         openModalBtn.addEventListener("click", openModal);
//     }
    
//     if (openModalMainBtn) {
//         openModalMainBtn.addEventListener("click", openModal);
//     }

//     // Close button event
//     closeBtn.addEventListener("click", closeModal);

//     // Close when clicking outside
//     window.addEventListener("click", function(event) {
//         if (event.target == modal) {
//             closeModal();
//         }
//     });

//     // Form submission
//     folderForm.addEventListener("submit", function(e) {
//         e.preventDefault();
        
//         const formData = new FormData(folderForm);
        
//         fetch(folderCreateUrl, {
//             method: "POST",
//             headers: {
//                 "X-CSRFToken": csrfToken,
//             },
//             body: formData
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.success) {
//                 responseMessage.innerHTML = "Folder created successfully!";
//                 responseMessage.style.color = "green";
//                 // Refresh the page after a short delay
//                 setTimeout(() => {
//                     window.location.reload();
//                 }, 1000);
//             } else {
//                 responseMessage.innerHTML = data.error || "An error occurred.";
//                 responseMessage.style.color = "red";
//             }
//         })
//         .catch(error => {
//             responseMessage.innerHTML = "An error occurred.";
//             responseMessage.style.color = "red";
//             console.error("Error:", error);
//         });
//     });
// });


document.addEventListener("DOMContentLoaded", function() {
    // Get modal elements
    const modal = document.getElementById("folderModal");
    const openModalBtn = document.getElementById("openModal");
    const openModalMainBtn = document.getElementById("openModalMain");
    const closeBtn = document.querySelector(".close");
    const folderForm = document.getElementById("folderForm");
    const responseMessage = document.getElementById("responseMessage");

    // Function to open modal
    function openModal() {
        modal.style.display = "block";
    }

    // Function to close modal
    function closeModal() {
        modal.style.display = "none";
    }

    // Add event listeners to both buttons
    if (openModalBtn) {
        openModalBtn.addEventListener("click", function() {
            openModal();
        });
    }
    
    if (openModalMainBtn) {
        openModalMainBtn.addEventListener("click", function() {
            openModal();
        });
    }

    // Close button event
    if (closeBtn) {
        closeBtn.addEventListener("click", function() {
            closeModal();
        });
    }

    // Close when clicking outside
    window.addEventListener("click", function(event) {
        if (event.target == modal) {
            closeModal();
        }
    });

    // Form submission
    if (folderForm) {
        folderForm.addEventListener("submit", function(e) {
            e.preventDefault();
            
            const formData = new FormData(folderForm);
            
            fetch(folderCreateUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    responseMessage.innerHTML = "Folder created successfully!";
                    responseMessage.style.color = "green";
                    // Refresh the page after a short delay
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    responseMessage.innerHTML = data.error || "An error occurred.";
                    responseMessage.style.color = "red";
                }
            })
            .catch(error => {
                responseMessage.innerHTML = "An error occurred.";
                responseMessage.style.color = "red";
                console.error("Error:", error);
            });
        });
    }

    // Add console logs to debug
    console.log("Modal buttons found:", {
        openModalBtn: !!openModalBtn,
        openModalMainBtn: !!openModalMainBtn,
        modal: !!modal,
        closeBtn: !!closeBtn,
        folderForm: !!folderForm
    });
});