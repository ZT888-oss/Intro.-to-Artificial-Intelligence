const poviForm = document.getElementById("povi-form");
const studentMessage = document.getElementById("student-message");
const poviResponse = document.getElementById("povi-response");
const signOutButton = document.getElementById("sign-out-button");
const languageSelect = document.getElementById("language-select");

// mood-check modal
const modal = document.getElementById("welcome-modal");
const closeButton = document.getElementById("close-modal");
const continueButton = document.getElementById("continue-button");

// Mood selection
const moodOptions = document.querySelectorAll(".mood-option");
const moodError = document.getElementById("mood-error");
let selectedMoodLevel = null;

//recommendation 
const recommendationPanel = document.getElementById("wellbeing-recommendation");
const recommendationTitle = document.getElementById("recommendation-title");
const recommendationMessage = document.getElementById("recommendation-message");
const talkToPoviButton = document.getElementById("talk-to-povi-button");
const universitySupportLink = document.getElementById("university-support-link");
const bookSupportLink = document.getElementById("book-support-link");
const urgentSupportLink = document.getElementById("urgent-support-link");


async function loadWellbeingIndex() {
    const scoreElement = document.getElementById("wellbeing-score");
    const statusElement = document.getElementById("wellbeing-status");
    const progressBar = document.getElementById(
        "wellbeing-progress-bar"
    );
    const descriptionElement = document.getElementById(
        "wellbeing-description"
    );

    try {
        const response = await fetch("/api/wellbeing-index", {
            credentials: "include"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.message || "Unable to load well-being index."
            );
        }

        if (data.index === null) {
            scoreElement.textContent = "--";
            statusElement.textContent = "No data";
            progressBar.style.width = "0%";

            descriptionElement.textContent =
                "Complete your first mood check-in to generate an index.";

            return;
        }

        scoreElement.textContent = data.index;
        statusElement.textContent = data.status;
        progressBar.style.width = `${data.index}%`;


        const recommendation = data.recommendation;

        if (recommendation && recommendationPanel) {
            recommendationPanel.hidden = false;
            recommendationPanel.dataset.level = recommendation.level;

            recommendationTitle.textContent =
                recommendation.title;

            recommendationMessage.textContent =
                recommendation.message;

            talkToPoviButton.hidden =
                recommendation.primaryAction !== "talk-to-povi";

            universitySupportLink.hidden =
                recommendation.secondaryAction !==
                "view-university-support";

            bookSupportLink.hidden =
                recommendation.primaryAction !== "book-support";

            urgentSupportLink.hidden =
                recommendation.secondaryAction !==
                "view-urgent-resources";
        }

        if (talkToPoviButton) {
            talkToPoviButton.addEventListener("click", function () {
                studentMessage.focus();

                poviForm.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });
            });
        }

    } catch (error) {
        console.error(error);

        statusElement.textContent = "Unavailable";
        descriptionElement.textContent = error.message;
    }
}


async function showMoodModalWhenNeeded() {
    try {
        const response = await fetch("/api/mood-checkins", {
            credentials: "include"
        });

        const contentType =
            response.headers.get("content-type");

        if (
            !contentType ||
            !contentType.includes("application/json")
        ) {
            const text = await response.text();

            throw new Error(
                `Expected JSON but received: ${text.slice(0, 80)}`
            );
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.message ||
                "Unable to check today's mood status."
            );
        }

        if (!data.checkedInToday && modal) {
            modal.classList.add("show");
        } else if (modal) {
            modal.classList.remove("show");
        }
    } catch (error) {
        console.error(
            "Check daily mood status error:",
            error
        );
    }
}


document.addEventListener("DOMContentLoaded", function () {

    // Sign out
    if (signOutButton) {
        signOutButton.addEventListener("click", async function () {
            signOutButton.disabled = true;
            try {
                const response = await fetch("/api/logout", { method: "POST", credentials: "include" });
                if (!response.ok) throw new Error("Unable to sign out. Please try again.");
                localStorage.removeItem("loggedIn");
                window.location.href = "login.html";
            } catch (error) {
                document.getElementById("povi-error").textContent = error.message;
                signOutButton.disabled = false;
            }
        });
    }
    //decide if show pop out check-in window
    showMoodModalWhenNeeded();

    // const shouldShowPopup =
    //     sessionStorage.getItem("showLoginPopup") === "true";

    // if (modal && shouldShowPopup) {
    //     modal.classList.add("show");
    //     sessionStorage.removeItem("showLoginPopup");
    // }

    function closeModal() {
        if (modal) {
            modal.classList.remove("show");
        }
    }

    if (closeButton) {
        closeButton.addEventListener("click", closeModal);
    }

    if (modal) {
        modal.addEventListener("click", function (event) {
            if (event.target === modal) {
                closeModal();
            }
        });
    }


    continueButton.addEventListener("click", async function () {
        if (selectedMoodLevel === null) {
            moodError.textContent = "Please select your current mood.";
            return;
        }


        //sned the mood to backend to evaluate well-being Index
        try {
            const response = await fetch("/api/mood-checkins", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },

                credentials: "include",

                body: JSON.stringify({
                    moodLevel: selectedMoodLevel
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || "Unable to save mood.");
            }

            console.log("Mood saved:", data);

            closeModal();

            // Refresh the dashboard card
            await loadWellbeingIndex();
        } catch (error) {
            moodError.textContent = error.message;
            console.error(error);
        }
    });


    //mood check-in
    moodOptions.forEach(function (option) {
        option.addEventListener("click", function () {
            moodOptions.forEach(function (mood) {
                mood.classList.remove("selected");
            });

            option.classList.add("selected");

            selectedMoodLevel = Number(option.dataset.level);

            moodError.textContent = "";

            console.log("Selected mood level:", selectedMoodLevel);
        });
    });

    //load mood index
    loadWellbeingIndex();


    //========================
    // Language selection
    //==========================

    const translations = {
        en: {
            title: "Share How You're Feeling",
            description: "Tell Povi what is on your mind.",
            button: "Send",
            wellbeingTitle: "Well-being Index",
            recentCheckins: "Your recent mood check-ins"
        },

        fr: {
            title: "Partagez ce que vous ressentez",
            description: "Dites à Povi ce qui vous préoccupe.",
            button: "Envoyer",
            wellbeingTitle: "Indice de bien-être",
            recentCheckins: "Vos récents bilans d'humeur"
        }
    };

    function applyLanguage(language) {
        const t = translations[language];

        if (!t) {
            return;
        }

        document.getElementById("title").textContent =
            t.title;

        document.getElementById("description").textContent =
            t.description;

        document.getElementById("submit-button").textContent =
            t.button;

        document.getElementById("wellbeing-title").textContent =
            t.wellbeingTitle;

        document.getElementById("recent-checkins-text").textContent =
            t.recentCheckins;
    }

    //when user select language preference, save preference to database
    if (languageSelect) {
    languageSelect.addEventListener("change", async function () {
        const language = this.value;

        applyLanguage(language);

        try {
            const response = await fetch("/api/profile/language", {
                method: "PUT",//update existing message
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "include", //use for identifing which logged-in user is changing their language
                body: JSON.stringify({
                    language
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.message || //print server error mesaage
                    "Unable to save language preference."
                );
            }

            console.log("Language saved:", data);

        } catch (error) {
            console.error(
                "Language update error:",
                error
            );
        }
    });
}

});
