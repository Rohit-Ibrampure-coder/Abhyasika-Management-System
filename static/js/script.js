/* ==========================================
   Abhyasika Management System
   Professional UI Script
========================================== */

document.addEventListener("DOMContentLoaded", function () {

    /* ==========================================
       LIGHT / DARK MODE
    ========================================== */

    const html = document.documentElement;

    const themeToggle = document.getElementById("theme-toggle");

    const themeIcon = document.getElementById("theme-icon");

    let savedTheme = localStorage.getItem("theme") || "light";

    html.setAttribute("data-bs-theme", savedTheme);

    updateThemeIcon();

    if (themeToggle) {

        themeToggle.addEventListener("click", function () {

            let currentTheme = html.getAttribute("data-bs-theme");

            let newTheme = currentTheme === "light" ? "dark" : "light";

            html.setAttribute("data-bs-theme", newTheme);

            localStorage.setItem("theme", newTheme);

            updateThemeIcon();

        });

    }

    function updateThemeIcon() {

        if (!themeIcon) return;

        if (html.getAttribute("data-bs-theme") === "dark") {

            themeIcon.className = "bi bi-sun-fill";

        } else {

            themeIcon.className = "bi bi-moon-stars-fill";

        }

    }

    /* ==========================================
       SIDEBAR TOGGLE
    ========================================== */

    const sidebar = document.getElementById("sidebar");

    const sidebarToggle = document.getElementById("sidebarToggle");

    if (sidebar && sidebarToggle) {

        if (localStorage.getItem("sidebar") === "collapsed") {

            sidebar.classList.add("collapsed");

        }

        sidebarToggle.addEventListener("click", function () {

            sidebar.classList.toggle("collapsed");

            if (sidebar.classList.contains("collapsed")) {

                localStorage.setItem("sidebar", "collapsed");

            } else {

                localStorage.setItem("sidebar", "expanded");

            }

        });

    }

    /* ==========================================
       AUTO CLOSE ALERTS
    ========================================== */

    document.querySelectorAll(".alert").forEach(function (alert) {

        setTimeout(function () {

            bootstrap.Alert.getOrCreateInstance(alert).close();

        }, 5000);

    });

    /* ==========================================
       ACTIVE SIDEBAR MENU
    ========================================== */

    const currentURL = window.location.pathname;

    document.querySelectorAll(".sidebar .nav-link").forEach(function (link) {

        if (link.getAttribute("href") === currentURL) {

            link.classList.add("active");

        }

    });

    /* ==========================================
       BUTTON LOADING
    ========================================== */

    document.querySelectorAll("form").forEach(function (form) {

        form.addEventListener("submit", function () {

            const button = form.querySelector("button[type='submit']");

            if (button) {

                button.disabled = true;

                button.innerHTML =
                    '<span class="spinner-border spinner-border-sm me-2"></span>Please Wait...';

            }

        });

    });

    /* ==========================================
       DASHBOARD WELCOME
    ========================================== */

    const welcomeGreeting = document.getElementById("welcomeGreeting");

    const currentDate = document.getElementById("currentDate");

    if (welcomeGreeting && currentDate) {

        const now = new Date();

        const hour = now.getHours();

        let greeting = "";

        if (hour < 12) {

            greeting = "🌅 Good Morning";

        }

        else if (hour < 17) {

            greeting = "☀️ Good Afternoon";

        }

        else {

            greeting = "🌙 Good Evening";

        }

        welcomeGreeting.innerHTML = greeting;

        currentDate.innerHTML = now.toLocaleDateString(

            "en-IN",

            {

                weekday: "long",

                day: "numeric",

                month: "long",

                year: "numeric"

            }

        );

    }

});