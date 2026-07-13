/* ==========================================================
   Daily Report
   Show / Hide "Other" Activity Textbox
========================================================== */

document.addEventListener("DOMContentLoaded", function () {

    function setupOtherActivity(checkboxClass, otherBoxId) {

        const checkboxes = document.querySelectorAll("." + checkboxClass);

        const otherBox = document.getElementById(otherBoxId);

        if (!otherBox) return;

        function updateVisibility() {

            let isOtherChecked = false;

            checkboxes.forEach(function (checkbox) {

                if (
                    checkbox.value === "इतर" &&
                    checkbox.checked
                ) {

                    isOtherChecked = true;

                }

            });

            if (isOtherChecked) {

                otherBox.style.display = "block";

            } else {

                otherBox.style.display = "none";

                const input = otherBox.querySelector("input");

                if (input) {

                    input.value = "";

                }

            }

        }

        checkboxes.forEach(function (checkbox) {

            checkbox.addEventListener("change", updateVisibility);

        });

        updateVisibility();

    }

    setupOtherActivity(
        "study-checkbox",
        "study-other-box"
    );

    setupOtherActivity(
        "special-checkbox",
        "special-other-box"
    );

});