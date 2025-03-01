document.addEventListener("DOMContentLoaded", function() {
    // Handle Flash Messages Timeout
    setTimeout(() => {
        let messages = document.querySelectorAll('.flash-messages div');
        messages.forEach(msg => msg.style.display = "none");
    }, 3000);

    // File Upload Preview
    const fileInput = document.getElementById("fileUpload");
    if (fileInput) {
        fileInput.addEventListener("change", function() {
            let fileName = this.files[0] ? this.files[0].name : "No file chosen";
            document.getElementById("fileLabel").innerText = fileName;
        });
    }

    // Handle Credit Request
    const requestCreditBtn = document.getElementById("requestCredits");
    if (requestCreditBtn) {
        requestCreditBtn.addEventListener("click", function() {
            alert("Credits requested! Admin will review your request.");
        });
    }
});

