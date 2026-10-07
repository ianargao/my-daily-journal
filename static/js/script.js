function togglePassword(id) {
    const input = document.getElementById(id);

    if (input) {
        input.type = input.type === "password" ? "text" : "password";
    }
}


/* ==========================================
   FLASH MESSAGE AUTO HIDE
========================================== */

setTimeout(() => {
    document.querySelectorAll(".flash").forEach(el => {

        el.style.opacity = "0";

        setTimeout(() => {
            el.remove();
        }, 350);

    });
}, 3500);


/* ==========================================
   SEPARATE DARK / LIGHT MODE
========================================== */

document.addEventListener("DOMContentLoaded", function () {

    const themeToggle = document.getElementById("themeToggle");

    if (!themeToggle) {
        return;
    }


    /* ======================================
       DETECT CURRENT PAGE
    ====================================== */

    const isDashboard =
        document.body.classList.contains("dashboard-page") ||
        document.querySelector(".app-shell") !== null;


    /* ======================================
       USE SEPARATE STORAGE
    ====================================== */

    const storageKey = isDashboard
        ? "dashboardTheme"
        : "authTheme";


    /* ======================================
       LOAD SAVED THEME
    ====================================== */

    const savedTheme = localStorage.getItem(storageKey);


    if (savedTheme === "dark") {

        document.body.classList.add("dark-mode");

    } else {

        document.body.classList.remove("dark-mode");

    }


    updateThemeButton();


    /* ======================================
       THEME TOGGLE
    ====================================== */

    themeToggle.addEventListener("click", function () {

        document.body.classList.toggle("dark-mode");


        if (document.body.classList.contains("dark-mode")) {

            localStorage.setItem(storageKey, "dark");

        } else {

            localStorage.setItem(storageKey, "light");

        }


        updateThemeButton();

    });


    /* ======================================
       UPDATE BUTTON
    ====================================== */

    function updateThemeButton() {

        const icon = themeToggle.querySelector(".theme-icon");
        const text = themeToggle.querySelector(".theme-text");


        if (!icon || !text) {
            return;
        }


        if (document.body.classList.contains("dark-mode")) {

            icon.textContent = "☀";
            text.textContent = "Light";

        } else {

            icon.textContent = "☾";
            text.textContent = "Dark";

        }

    }

});