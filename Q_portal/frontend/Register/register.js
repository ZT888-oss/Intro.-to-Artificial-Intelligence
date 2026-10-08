const registerForm = document.getElementById("register-form");

const fullName = document.getElementById("full-name");
const email = document.getElementById("email");
const password = document.getElementById("password");
const confirmPassword = document.getElementById("confirm-password");

const registerButton = document.querySelector(".register-button");

const message = document.getElementById("register-message");

const togglePassword = document.getElementById("toggle-password");

const toggleConfirmPassword = document.getElementById("toggle-confirm-password");

const terms = document.getElementById("terms");
const termsLink = document.getElementById("open-terms");
const privacyLink = document.getElementById("open-privacy");

const termsModal = document.getElementById("terms-modal");
const privacyModal = document.getElementById("privacy-modal");

const closeModalButtons = document.querySelectorAll(".close-modal");


function openModal(modal) {
    modal.hidden = false;
    
    // ensure the background page cannot scroll
    document.body.style.overflow = "hidden";
}



// Show / Hide Password
togglePassword.addEventListener("click", () => {

    if(password.type === "password"){

        password.type = "text";
        togglePassword.textContent = "Hide";

    }
    else{

        password.type = "password";
        togglePassword.textContent = "Show";

    }

});

toggleConfirmPassword.addEventListener("click", () => {

    if(confirmPassword.type === "password"){

        confirmPassword.type = "text";
        toggleConfirmPassword.textContent = "Hide";

    }
    else{

        confirmPassword.type = "password";
        toggleConfirmPassword.textContent = "Show";

    }

});



//Error
function showError(text){

    message.hidden = false;
    message.style.color = "red";
    message.textContent = text;

}



// Show Success

function showSuccess(text){

    message.hidden = false;
    message.style.color = "green";
    message.textContent = text;

}



function hideMessage(){

    message.hidden = true;
    message.textContent = "";

}


//error
function showFieldError(errorId, message) {
    const errorElement = document.getElementById(errorId);

    if (errorElement) {
        errorElement.textContent = message;
    }
}

function clearFieldError(errorId) {
    const errorElement = document.getElementById(errorId);

    if (errorElement) {
        errorElement.textContent = "";
    }
}

function clearErrors() {
    const errorMessages = document.querySelectorAll(".error-message");

    errorMessages.forEach((error) => {
        error.textContent = "";
    });
}

function validateRegister() {
    clearErrors();

    let isValid = true;

    // Full name
    if (fullName.value.trim() === "") {
        showFieldError("name-error", "Full name is required.");
        isValid = false;
    }

    // Email required
    if (email.value.trim() === "") {
        showFieldError("email-error", "Email address is required.");
        isValid = false;
    } else {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailPattern.test(email.value.trim())) {
            showFieldError("email-error", "Please enter a valid email address.");
            isValid = false;
        }
    }

    // Password required and strength
    if (password.value === "") {
        showFieldError("password-error", "Password is required.");
        isValid = false;
    } else {
        const passwordPattern =
            /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*<>/?]).{6,}$/;

        if (!passwordPattern.test(password.value)) {
            showFieldError(
                "password-error",
                "Use at least 6 characters with uppercase, lowercase, number, and special character."
            );

            isValid = false;
        }
    }

    // Confirm password
    if (confirmPassword.value === "") {
        showFieldError(
            "confirm-password-error",
            "Please confirm your password."
        );

        isValid = false;
    } else if (password.value !== confirmPassword.value) {
        showFieldError(
            "confirm-password-error",
            "Passwords do not match."
        );

        isValid = false;
    }

    // Terms
    if (!terms.checked) {
        showFieldError(
            "terms-error",
            "Please accept the Terms of Service."
        );

        isValid = false;
    }

    return isValid;
}


// Loading Animation
function startLoading(){

    registerButton.disabled = true;
    registerButton.textContent = "Creating Account...";

}

function stopLoading(){

    registerButton.disabled = false;
    registerButton.textContent = "Create Account";

}

/*''''''''''''''''''''
    register info
'''''''''''''''''''''''*/
async function registerUser(
    username,
    email,
    password,
    preferredLanguage
) {
    const response = await fetch("/api/register", {//Send the request and wait until the backend responds. Then store the response in response
        method: "POST",
        //connect to app.use(express.json());
        headers: {
            "Content-Type": "application/json" //tell backend data i am sending is in json
        },
        body: JSON.stringify({
            username,
            email,
            password,
            preferredLanguage
        })
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.message || "Registration failed.");
    }

    return data;
}


//term of use section
function closeModal(modal) {
    modal.hidden = true;
    document.body.style.overflow = "";
}

termsLink.addEventListener("click", function (event) {
    event.preventDefault();
    openModal(termsModal);
});

privacyLink.addEventListener("click", function (event) {
    event.preventDefault();
    openModal(privacyModal);
});

//go through every close button, one at a time 
closeModalButtons.forEach((button) => {
    button.addEventListener("click", function () {
        //search upward through the parent of current button clicked, until fin its closest .model-overlay
        const modal = button.closest(".modal-overlay");
        closeModal(modal);
    }); 
});



// =======================================
// Submit Form
// =======================================
registerForm.addEventListener("submit", async function (event) {
    
    event.preventDefault();
    clearErrors();

    const formIsValid = validateRegister();

    if (!formIsValid) {
        console.log("Frontend validation failed.");
        return;
    }

    

    const username = document.getElementById("full-name").value.trim();

    const email = document
        .getElementById("email")
        .value
        .trim();

    const password = document
        .getElementById("password")
        .value;

    const preferredLanguage =
        document.getElementById("language-select")?.value || "English";

    try {
        const result = await registerUser(
            username,
            email,
            password,
            preferredLanguage
        );

        console.log(result);
        window.location.href = "login.html";

    } catch (error) {
        showError(error.message);
    }
});


// =======================================
// Focus Effect
// =======================================

const inputs =
    document.querySelectorAll("input");

inputs.forEach(input=>{

    input.addEventListener("focus",()=>{

        input.style.borderColor="#2ea043";

    });

    input.addEventListener("blur",()=>{

        input.style.borderColor="#ccc";

    });

});



// Welcome Animation
window.addEventListener("load",()=>{

    document.querySelector(".register-container")
        .animate(

            [
                {
                    opacity:0,
                    transform:"translateY(40px)"
                },
                {
                    opacity:1,
                    transform:"translateY(0px)"
                }
            ],

            {

                duration:700,
                easing:"ease-out"

            }

        );

});