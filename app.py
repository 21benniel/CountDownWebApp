import os
import uuid
import calendar
from datetime import datetime, timedelta, time
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort, session
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# **REQUIRED for sessions** - replace with a real secret key in production
app.secret_key = os.urandom(24) # Generates a random key each time server starts

# --- Create Upload Directory ---
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Helper Function ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Static Predefined Timer Data ---
static_trending_timers = {
    'christmas': { 'name': 'Christmas 2025', 'target_date': '2025-12-25 00:00:00', 'theme': 'theme-christmas' },
    'new-year': { 'name': 'New Year 2026', 'target_date': '2026-01-01 00:00:00', 'theme': 'theme-newyear' },
    'diwali': { 'name': 'Diwali 2025', 'target_date': '2025-10-21 00:00:00', 'theme': 'theme-diwali' },
    'halloween': { 'name': 'Halloween 2025', 'target_date': '2025-10-31 00:00:00', 'theme': 'theme-halloween' },
    'black-friday': { 'name': 'Black Friday 2025', 'target_date': '2025-11-28 00:00:00', 'theme': 'theme-blackfriday' },
    'valentines': { 'name': 'Valentine\'s Day 2026', 'target_date': '2026-02-14 00:00:00', 'theme': 'theme-valentines' },
    'easter': { 'name': 'Easter 2026', 'target_date': '2026-04-05 00:00:00', 'theme': 'theme-easter' },
    'mothers-day': { 'name': 'Mother\'s Day 2026 (US)', 'target_date': '2026-05-10 00:00:00', 'theme': 'theme-mothersday' },
    'fathers-day': { 'name': 'Father\'s Day 2026 (US)', 'target_date': '2026-06-21 00:00:00', 'theme': 'theme-fathersday' },
}

# --- Date Calculation Helpers ---
def get_next_weekday(start_date, weekday):
    days_ahead = weekday - start_date.weekday()
    if days_ahead <= 0: days_ahead += 7
    return start_date + timedelta(days=days_ahead)

def get_month_end(start_date):
    last_day = calendar.monthrange(start_date.year, start_date.month)[1]
    return start_date.replace(day=last_day)

# --- Routes ---

@app.route('/')
def landing_page():
    """Displays the landing page with custom form and timers."""
    now = datetime.now()
    today = now.date()
    date_format = "%Y-%m-%d %H:%M:%S"

    # Calculate dynamic dates
    next_monday_target = datetime.combine(get_next_weekday(today, 0), time(0, 0, 0))
    next_weekend_target = datetime.combine(get_next_weekday(today, 5), time(0, 0, 0))
    month_end_target = datetime.combine(get_month_end(today), time(23, 59, 59))

    dynamic_timers = {
        'next-monday': {'name': 'Next Monday 😭', 'target_date': next_monday_target.strftime(date_format), 'theme': 'theme-monday'},
        'next-weekend': {'name': 'Next Weekend', 'target_date': next_weekend_target.strftime(date_format), 'theme': 'theme-weekend'},
        'month-end': {'name': 'End of Month', 'target_date': month_end_target.strftime(date_format), 'theme': 'theme-monthend'},
    }

    all_trending_timers = {**static_trending_timers, **dynamic_timers}
    # Get custom timers from session
    custom_timers_list = session.get('custom_timers', [])

    return render_template(
        'landing_page.html',
        trending_timers=all_trending_timers,
        custom_timers=custom_timers_list # Pass custom timers to template
    )

@app.route('/timer/trending/<timer_id>') # Renamed route slightly for clarity
def show_trending_timer(timer_id):
    """Displays a predefined or calculated trending timer."""
    # Recalculate dynamic timers to ensure accuracy if accessed directly
    now = datetime.now()
    today = now.date()
    date_format = "%Y-%m-%d %H:%M:%S"
    next_monday_target = datetime.combine(get_next_weekday(today, 0), time(0, 0, 0))
    next_weekend_target = datetime.combine(get_next_weekday(today, 5), time(0, 0, 0))
    month_end_target = datetime.combine(get_month_end(today), time(23, 59, 59))
    dynamic_timers = {
        'next-monday': {'name': 'Next Monday 😭', 'target_date': next_monday_target.strftime(date_format), 'theme': 'theme-monday'},
        'next-weekend': {'name': 'Next Weekend', 'target_date': next_weekend_target.strftime(date_format), 'theme': 'theme-weekend'},
        'month-end': {'name': 'End of Month', 'target_date': month_end_target.strftime(date_format), 'theme': 'theme-monthend'},
    }
    all_trending_timers = {**static_trending_timers, **dynamic_timers}

    timer_data = all_trending_timers.get(timer_id)
    if not timer_data:
        abort(404)

    return render_template(
        'timer_display.html',
        timer_name=timer_data['name'],
        target_date_iso=timer_data['target_date'],
        background_style=timer_data['theme']
    )

@app.route('/timer/custom', methods=['POST'])
def handle_custom_timer():
    """Handles the submission of the custom timer form and saves to session."""
    if 'background' not in request.files:
        return "No background image part in form", 400
    file = request.files['background']
    timer_name = request.form.get('name', 'Custom Timer')
    target_time_str = request.form.get('time')

    if not target_time_str:
         return "No target time provided", 400

    try:
        target_dt = datetime.strptime(target_time_str, '%Y-%m-%dT%H:%M')
        target_date_iso = target_dt.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return "Invalid date/time format submitted", 400

    if file.filename == '':
        return "No selected file", 400

    if file and allowed_file(file.filename):
        original_ext = file.filename.rsplit('.', 1)[1].lower()
        # Generate unique ID for this timer
        timer_id = str(uuid.uuid4())
        unique_filename = timer_id + '.' + original_ext # Use timer ID in filename
        secure_name = secure_filename(unique_filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
        try:
            file.save(filepath)

            # Get existing custom timers from session or initialize empty list
            custom_timers_list = session.get('custom_timers', [])

            # Add new timer details to the list
            new_timer = {
                'id': timer_id,
                'name': timer_name,
                'target_date': target_date_iso,
                'bg_filename': secure_name
            }
            custom_timers_list.append(new_timer)

            # Save updated list back to session
            session['custom_timers'] = custom_timers_list
            session.modified = True # Mark session as modified

            # Redirect back to the landing page
            return redirect(url_for('landing_page'))

        except Exception as e:
            print(f"Error saving file or session: {e}")
            return "Error processing custom timer", 500
    else:
        return "File type not allowed", 400

# New route to display a specific custom timer from session
@app.route('/timer/custom/<custom_timer_id>')
def show_custom_timer(custom_timer_id):
    """Displays a specific custom timer stored in the session."""
    custom_timers_list = session.get('custom_timers', [])
    timer_data = None
    for timer in custom_timers_list:
        if timer.get('id') == custom_timer_id:
            timer_data = timer
            break

    if not timer_data:
        # Timer not found in session (maybe expired or invalid ID)
        # Redirect to landing page with a message? Or show 404?
        # For now, redirecting to landing page.
        # flash("Custom timer not found.") # Requires flash import and handling in template
        return redirect(url_for('landing_page'))

    # Construct the URL for the background image
    background_image_url = url_for('uploaded_file', filename=timer_data['bg_filename'])

    return render_template(
        'timer_display.html',
        timer_name=timer_data['name'],
        target_date_iso=timer_data['target_date'],
        background_style=background_image_url # Pass image URL
    )


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serves files uploaded by users."""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)