const loginForm = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const loginButton = document.querySelector(".sign-in-button");
const errorMessage = document.getElementById("login-error");
const togglePassword = document.getElementById("toggle-password");
const indicators = document.querySelectorAll(".indicator");

const illustration = document.querySelector(".login-illustration");
const introductionTitle = document.querySelector(".introduction-text h2");
const introductionParagraph = document.querySelector(".introduction-text p");




const slides = [
    {
        image: "Login/mental-health.jpg",
        title: "Breathe easy here",
        description: "It’s okay to not be okay."
    },
    {
        image: "Login/second.jpg",
        title: "You are not alone",
        description: "Healing takes time, and asking for help is a courageous step."
    },
    {
        image: "Login/mental.jpg",
        title: "Every day is a new beginning",
        description: "Progress isn't always visible, but every effort counts."
    },
    {
        image: "Login/heal.jpg",
        title: "Strength comes from reaching out",
        description: "It's not weak to ask for help. It's brave."
    }
];

let currentSlide = 0;

function showSlide(index) {
    currentSlide = index;

    illustration.src = slides[index].image;
    illustration.alt = slides[index].title;

    introductionTitle.textContent = slides[index].title;
    introductionParagraph.textContent = slides[index].description;

    indicators.forEach((indicator, indicatorIndex) => {
        indicator.classList.toggle(
            "active",
            indicatorIndex === index
        );

        indicator.setAttribute(
            "aria-current",
            indicatorIndex === index ? "true" : "false"
        );
    });
}

function showNextSlide() {
    const nextSlide =
        (currentSlide + 1) % slides.length;

    showSlide(nextSlide);
}

//Run showNextSlide every 4000 milliseconds
let slideTimer = setInterval(showNextSlide, 4000);

indicators.forEach((indicator, index) => {
    indicator.addEventListener("click", function () {
        showSlide(index);

        clearInterval(slideTimer);
        slideTimer = setInterval(showNextSlide, 4000);
    });
});

showSlide(0);


togglePassword.addEventListener("click", () => {
    console.log("clicked");
    console.log(passwordInput);

    if (passwordInput.type === "password") {

        passwordInput.type = "text";
        togglePassword.textContent = "Hide";

    } else {

        passwordInput.type = "password";
        togglePassword.textContent = "Show";
    }

});


// =========================================
// Highlight Active Input
// =========================================

const inputs = document.querySelectorAll("input");

inputs.forEach(input => {

    input.addEventListener("focus", () => {

        input.style.borderBottom = "2px solid #4CAF50";

    });

    input.addEventListener("blur", () => {

        input.style.borderBottom = "2px solid #ddd";

    });

});



// Form Validation
function validateLogin() {

    const username = emailInput.value.trim();
    const password = passwordInput.value.trim();

    if (username === "") {

        showError("Please enter your username or email.");
        return false;
    }

    if (password === "") {

        showError("Please enter your password.");
        return false;
    }

    const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>/?]).{6,}$/;

    if (password.length < 6) {

    showError("Password must be at least 6 characters.");

    return false;
    }


    hideError();

        return true;

    }


// Show Error
function showError(message) {

    errorMessage.hidden = false;
    errorMessage.textContent = message;

}


// Hide Error
function hideError() {

    errorMessage.hidden = true;
    errorMessage.textContent = "";

}



// Login Button Animation

function startLoading() {

    loginButton.disabled = true;
    loginButton.textContent = "Signing In...";

}

function stopLoading() {

    loginButton.disabled = false;
    loginButton.textContent = "Sign In";

}


//connect with backend
async function login(username, password) {
    const response = await fetch("/api/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username,
            password
        })
    });

    const data = await response.json();

    if(response.ok){
        sessionStorage.setItem("showLoginPopup", "true");
    }
    else if (!response.ok) {
        throw new Error(data.message || "Login failed.");
    }

    return data;
}




// Handle Login
loginForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    if(!validateLogin()){
        return;
    }
    
    const username = emailInput.value.trim();
    const password = passwordInput.value;

    startLoading();

    setTimeout(function() {
       stopLoading();
    },900);
        


    try {
        const result = await login(username, password);

        localStorage.setItem("loggedIn", "true");
        localStorage.setItem(
            "preferredLanguage",
            result.user.preferredLanguage
        );

        setTimeout(function() {
            window.location.href = "dashboard.html";
        }, 1000);


    } catch (error) {
        showError(error.message);
    }
});


// =========================================
// Google Button
// =========================================

const googleButton = document.querySelector(".google-sign-in-button");

googleButton.addEventListener("click", () => {

    alert("Google Login Coming Soon!");

});



function validateRegister() {

    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    if (username === "") {
        showError("Please enter a username.");
        return false;
    }

    if (email === "") {
        showError("Please enter your email.");
        return false;
    }

    // Password must:
    // - be at least 6 characters
    // - contain uppercase
    // - contain lowercase
    // - contain number
    // - contain special character
    const passwordPattern =
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*<>/?]).{6,}$/;

    if (!passwordPattern.test(password)) {

        showError(
            "Password must be at least 6 characters and include an uppercase letter, lowercase letter, number, and special character."
        );

        return false;
    }

    if (password !== confirmPassword) {

        showError("Passwords do not match.");

        return false;
    }

    hideError();

    return true;
}


// Press Escape to Clear Errors
document.addEventListener("keydown", (event) => {

    if (event.key === "Escape") {

        hideError();

    }

});


// =========================================
// Welcome Animation
// =========================================

window.addEventListener("load", () => {

    document.querySelector(".login-container").animate(

        [
            {
                opacity: 0,
                transform: "translateY(40px)"
            },
            {
                opacity: 1,
                transform: "translateY(0px)"
            }
        ],

        {
            duration: 700,
            easing: "ease-out"
        }

    );

});