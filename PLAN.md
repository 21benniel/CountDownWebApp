# Countdown Timer Application Plan

This plan outlines the steps to build a multi-page countdown timer application using Flask, based on user sketches and requirements.

**I. Project Setup & Configuration**

1.  **Directory Structure:** Ensure the Flask project structure is in place:
    *   `app.py` (Main Flask application)
    *   `templates/` (For HTML files)
    *   `static/` (For CSS, JS, and potentially predefined theme images)
    *   `uploads/` (Create this directory to store user-uploaded background images)
    *   `requirements.txt` (Listing Flask)
2.  **Flask Configuration (`app.py`):**
    *   Configure Flask to serve static files.
    *   Set up a configuration variable for the upload folder (`app.config['UPLOAD_FOLDER'] = 'uploads/'`).
    *   Define allowed extensions for image uploads (e.g., png, jpg, jpeg, gif).

**II. Backend Development (`app.py`)**

1.  **Data for Trending Timers:** Define a data structure (like a Python dictionary) to hold information about the predefined trending timers (e.g., `{'christmas': {'name': 'Christmas Timer', 'target_date': '2025-12-25 00:00:00', 'theme': 'christmas'}, ...}`). The `theme` key will correspond to a CSS class or predefined background.
2.  **Landing Page Route (`/`)**:
    *   Create a route `@app.route('/')`.
    *   This route will render a new `landing_page.html` template.
    *   Pass the `trending_timers` data to the template so it can generate the grid.
3.  **Trending Timer Display Route (`/timer/<timer_id>`)**:
    *   Create a route like `@app.route('/timer/<timer_id>')`.
    *   Look up the `timer_id` in the `trending_timers` data.
    *   If found, render the `timer_display.html` template, passing the specific timer's name, target date, and theme identifier.
    *   If not found, handle the error (e.g., show a 404 page).
4.  **Custom Timer Form Submission Route (`/timer/custom`, methods=['POST'])**:
    *   Create a route `@app.route('/timer/custom', methods=['POST'])`.
    *   Retrieve the 'name', 'time', and uploaded 'background' file from the form data (`request.form`, `request.files`).
    *   Validate the input (check if file exists, has allowed extension, time format is valid).
    *   Generate a secure, unique filename for the uploaded image (e.g., using `uuid` and `werkzeug.utils.secure_filename`).
    *   Save the image to the `uploads/` directory.
    *   Store the necessary custom timer details (name, target time, uploaded image filename) temporarily (e.g., in the Flask session or pass via query parameters).
    *   Redirect the user to a route that displays the custom timer (e.g., `/timer/display?name=...&time=...&bg=...`).
5.  **Custom Timer Display Route (`/timer/display`)**:
    *   Create a route `@app.route('/timer/display')`.
    *   Retrieve the custom timer details (name, time, background image filename) from the query parameters (`request.args`) or the session.
    *   Construct the full URL path to the uploaded background image (e.g., `/uploads/unique_filename.jpg`).
    *   Render the `timer_display.html` template, passing the custom name, target time, and the background image URL.
6.  **Uploaded File Serving Route (`/uploads/<filename>`)**:
    *   Create a route `@app.route('/uploads/<filename>')`.
    *   Use Flask's `send_from_directory` function to securely serve files from the `uploads/` directory.

**III. Frontend Development (`templates/`, `static/`)**

1.  **Landing Page Template (`templates/landing_page.html`)**:
    *   Create the HTML structure based on "Page #1" sketch.
    *   Left Sidebar: Form with fields for "Custom Name", "Time" (use `<input type="datetime-local">`), "Background Upload" (`<input type="file" name="background">`), and a "Start" button. Ensure the form has `method="POST"`, `action="{{ url_for('handle_custom_timer') }}"`, and `enctype="multipart/form-data"`.
    *   Main Area: Loop through the `trending_timers` data passed from Flask to generate a grid of boxes. Each box should be a link (`<a>`) pointing to the corresponding `/timer/<timer_id>` route.
2.  **Timer Display Template (`templates/timer_display.html`)**:
    *   Modify the existing countdown page structure based on "Page #2".
    *   Accept variables from Flask: `timer_name`, `target_date_iso`, `background_style`.
    *   Use JavaScript to read `target_date_iso`.
    *   Display `timer_name`.
    *   Apply the `background_style`:
        *   If it's a theme identifier (e.g., 'christmas'), add a class to the `<body>` or a wrapper div (e.g., `<body class="theme-christmas">`).
        *   If it's an image URL (for custom timers), apply it using inline style: `<body style="background-image: url('{{ background_style }}');">`. (Or apply to a wrapper div).
3.  **CSS (`static/style.css`)**:
    *   Add styles for the `landing_page.html` layout (sidebar, grid).
    *   Style the custom timer form elements.
    *   Style the trending timer grid boxes.
    *   Define the base styles for `timer_display.html` (countdown text, positioning).
    *   Create theme classes (e.g., `.theme-christmas`, `.theme-newyear`) with specific backgrounds (colors, gradients, predefined images like stars).
    *   Ensure styles handle background images applied via inline styles correctly (e.g., `background-size: cover; background-position: center;`).
    *   Include the snow animation CSS if desired for specific themes.
4.  **JavaScript (`static/script.js`)**:
    *   Modify the countdown logic:
        *   Read the target date from an HTML attribute (e.g., `<div id="countdown" data-target-date="{{ target_date_iso }}">`) set by Flask in `timer_display.html`.
        *   Parse this ISO date string into a JavaScript Date object.
        *   Update the display elements as before.

**IV. Diagram**

```mermaid
graph TD
    subgraph User Flow
        A[User visits /] --> B[Landing Page (landing_page.html)];
        B -- Clicks Trending 'Christmas' --> C[/timer/christmas];
        B -- Submits Custom Form w/ Image --> D[/timer/custom POST];
        D -- Saves Image & Redirects --> E[/timer/display?params...];
        C --> F[Timer Display Page (timer_display.html)];
        E --> F;
    end

    subgraph Backend (Flask - app.py)
        G[/] --> H[Renders landing_page.html w/ Trending Data];
        I[/timer/<timer_id>] --> J[Fetches Data for timer_id];
        J --> K[Renders timer_display.html w/ Theme];
        L[/timer/custom POST] --> M[Handles Form Data & Saves Image];
        M --> N[Redirects to /timer/display w/ Custom Params];
        O[/timer/display] --> P[Renders timer_display.html w/ Custom Data & BG URL];
        Q[/uploads/<filename>] --> R[Serves Image from /uploads];
    end

    subgraph Frontend
        S[landing_page.html] -->|Displays| B;
        S -->|Form POSTs to| L;
        S -->|Links to| I;
        T[timer_display.html] -->|Displays| F;
        T -->|Uses| U[style.css];
        T -->|Uses| V[script.js];
        U -->|Styles| S & T;
        V -->|Runs Countdown on| T;
        V -->|Reads Target Date from| T;
    end

    subgraph Data
        W{Trending Timer Data} --> H & J;
        X{/uploads Directory} --> M & R;
    end

    H --> S;
    K --> T;
    P --> T;
    R --> T;