let countdownIntervals = []; // Store multiple interval IDs

// --- Clear Existing Intervals ---
function clearAllIntervals() {
    countdownIntervals.forEach(intervalId => clearInterval(intervalId));
    countdownIntervals = [];
}

// --- Update Countdown Function (Generalized) ---
// Takes the target date and the container element for the specific timer
function updateCountdown(targetDate, containerElement, isPreview) { // Added isPreview flag
    if (!targetDate || !containerElement) {
        return; // Exit if essential info is missing
    }

    let daysEl, hoursEl, minutesEl, secondsEl;

    // Select elements based on whether it's a preview or the main display page
    if (isPreview) {
        daysEl = containerElement.querySelector('.preview-days');
        hoursEl = containerElement.querySelector('.preview-hours');
        minutesEl = containerElement.querySelector('.preview-minutes');
        secondsEl = containerElement.querySelector('.preview-seconds');
    } else {
        // Use IDs for the main display page (assuming containerElement is #countdown)
        daysEl = document.getElementById('days'); // Use getElementById directly
        hoursEl = document.getElementById('hours');
        minutesEl = document.getElementById('minutes');
        secondsEl = document.getElementById('seconds');
    }


    const now = new Date().getTime();
    const distance = targetDate - now;

    // Time calculations
    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    // Display the result - Check if elements exist before updating
    if (distance >= 0) {
        if (daysEl) daysEl.textContent = String(days).padStart(2, '0');
        if (hoursEl) hoursEl.textContent = String(hours).padStart(2, '0');
        if (minutesEl) minutesEl.textContent = String(minutes).padStart(2, '0');
        if (secondsEl) secondsEl.textContent = String(seconds).padStart(2, '0');
    } else {
        // Countdown finished - display 00 or a message
        if (daysEl) daysEl.textContent = "00";
        if (hoursEl) hoursEl.textContent = "00";
        if (minutesEl) minutesEl.textContent = "00";
        if (secondsEl) secondsEl.textContent = "00";

        // Stop the specific interval for *this* timer
        // Find the interval associated with this container (more complex, needs mapping)
        // For now, we rely on the fact that finished timers just show 00.
        // A better approach would involve passing the intervalId to clear it here.

        // Optionally add a finished message (only on main display page)
        if (!isPreview) {
             const wrapper = document.querySelector('.countdown-wrapper');
             // Check if message already exists to avoid duplicates
             if(wrapper && !wrapper.querySelector('.finished-message')) {
                 const finishedMessage = document.createElement('p');
                 finishedMessage.textContent = "Countdown Finished!";
                 finishedMessage.className = 'finished-message'; // Add class for styling/checking
                 finishedMessage.style.color = 'var(--accent-red, red)';
                 finishedMessage.style.fontSize = '1.5em';
                 wrapper.appendChild(finishedMessage);
             }
        }
    }
}

// --- Initialize Timers ---
function initializeTimers() {
    clearAllIntervals(); // Clear any previous intervals

    // --- Logic for Timer Display Page ---
    const mainCountdownElement = document.getElementById('countdown');
    if (mainCountdownElement) {
        const targetDateStr = mainCountdownElement.getAttribute('data-target-date');
        if (targetDateStr) {
            const targetDate = Date.parse(targetDateStr.replace(' ', 'T'));
            if (!isNaN(targetDate)) {
                // Initial call - pass false for isPreview
                updateCountdown(targetDate, mainCountdownElement, false);
                // Start interval for the main timer
                const intervalId = setInterval(() => updateCountdown(targetDate, mainCountdownElement, false), 1000);
                countdownIntervals.push(intervalId); // Store interval ID
            } else {
                console.error("Invalid date format for main timer:", targetDateStr);
                mainCountdownElement.innerHTML = "Error: Invalid date format.";
            }
        } else {
            console.error("Missing data-target-date for main timer.");
            mainCountdownElement.innerHTML = "Error: Target date not specified.";
        }
    }

    // --- Logic for Landing Page Previews ---
    const previewBoxes = document.querySelectorAll('.timer-box-preview');
    if (previewBoxes.length > 0) {
        previewBoxes.forEach(box => {
            const targetDateStr = box.getAttribute('data-target-date');
            const previewContainer = box.querySelector('.preview-countdown'); // The container for preview spans

            if (targetDateStr && previewContainer) {
                const targetDate = Date.parse(targetDateStr.replace(' ', 'T'));
                if (!isNaN(targetDate)) {
                    // Initial call for this preview box - pass true for isPreview
                    updateCountdown(targetDate, previewContainer, true);
                    // Start interval for *this* preview box
                    const intervalId = setInterval(() => updateCountdown(targetDate, previewContainer, true), 1000);
                    countdownIntervals.push(intervalId); // Store interval ID
                } else {
                    console.error("Invalid date format for preview timer:", targetDateStr, box);
                    if (previewContainer) previewContainer.textContent = "Invalid Date";
                }
            } else {
                 console.error("Missing data-target-date or preview container for box:", box);
                 if (previewContainer) previewContainer.textContent = "Error";
            }
        });
    }

    if (!mainCountdownElement && previewBoxes.length === 0) {
        console.log("No countdown elements found to initialize.");
    }
}


// --- Event Listener for DOM Ready ---
document.addEventListener('DOMContentLoaded', initializeTimers);