from flask import Flask, request, redirect, url_for, render_template, flash, session
from flask_mysqldb import MySQL

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'your-unique-secret-key-here'

# Database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Use your MySQL username
app.config['MYSQL_PASSWORD'] = 'root'  # Use your MySQL password
app.config['MYSQL_DB'] = 'student_portal'

# Initialize MySQL
mysql = MySQL(app)

# Route for login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']  # Get the username from the form
        password = request.form['password']  # Get the password from the form
        
        # Check if user exists in the database using the username and password
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()  # Fetch the first user that matches the query
        
        if user:
            session['user_id'] = user[0]  # Store the user's ID in the session
            session['username'] = user[1]
            flash('Login successful!', 'success')
            return redirect(url_for('index'))  # Redirect to the index page
        else:
            flash('Invalid credentials. Please try again.', 'error')
            return redirect(url_for('login'))  # Redirect back to login page if invalid

    return render_template('login.html')  # Render login page if GET request

# Route for index page after successful login
@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login page if not logged in
    
    user_id = session['user_id']
    
    # Fetch user details from the 'details' table
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT full_name, email, phone_number,course,date_of_birth, address, 
               attendance_discrete_maths, attendance_oop, attendance_ui_design, 
               attendance_linear_algebra, attendance_networking_hardware
        FROM details WHERE user_id = %s
    """, (user_id,))
    
    # Get the user's details
    user_details = cur.fetchone()
    
    if user_details:
        # Pass the details to the template
        return render_template('index.html', user_details=user_details)
    else:
        flash('No details found for this user.', 'error')
        return redirect(url_for('login'))  # Redirect back to login page if no details found
    

@app.route('/od', methods=['GET', 'POST'])
def od_details():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect('/login')  # Redirect to login page if not logged in

    if request.method == 'POST':
        user_id = session['user_id']  # Logged-in user's ID
        full_name = request.form.get('name')  # Get Full Name from the form
        rollno = request.form.get('rollno')  # (Optional, can be used for validation/logging)
        od_date = request.form.get('dat')  # Get OD Date from the form
        club = request.form.get('complainttype')  # Get Selected Club from the form

        # Insert data into the on_duty table (or update if user_id already exists)
        cur = mysql.connection.cursor()
        try:
            cur.execute(
                """
                INSERT INTO on_duty (user_id, full_name, od_date, club)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    full_name = VALUES(full_name),
                    od_date = VALUES(od_date),
                    club = VALUES(club)
                """,
                (user_id, full_name, od_date, club)
            )


            cur.execute("""
                        INSERT INTO on_duty (user_id, full_name, od_date, club)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, full_name, od_date, club))
            mysql.connection.commit()

            mysql.connection.commit()
            flash('OD Details saved successfully!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        finally:
            cur.close()

        return redirect('/index')  # Redirect back to the index page after saving

    return render_template('od.html')  # Render the OD form page for GET requests

@app.route('/logout')
def logout():
    # Clear session data
    session.clear()
    # Redirect to a route serving the coverpage.html
    return render_template('coverpage.html')


@app.route('/coverpage')
def coverpage():
    session.clear()
    return render_template('coverpage.html')


@app.route('/academic')
def academic():
    # Fetch data from the 'academic_calendar' table
    cur = mysql.connection.cursor()
    cur.execute("SELECT DATE_FORMAT(date, '%d-%b') AS formatted_date, day, holiday FROM academic_calendar")
    rows = cur.fetchall()  # Fetch all rows from the table
    cur.close()
    
    # Pass the data to the template
    return render_template('academic.html', academic_data=rows)


@app.route('/exam')
def exam():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login page if not logged in
    
    user_id = session['user_id']
    
    # Fetch user course from the 'details' table
    cur = mysql.connection.cursor()
    cur.execute("SELECT course FROM details WHERE user_id = %s", (user_id,))
    user_course = cur.fetchone()    
    
    if user_course:
        # Get the course name
        course_name = user_course[0]
        
        # Fetch exam schedule based on the user's course
     

        cur.execute("""
        SELECT es.id, es.course_code, es.subject_name, es.exam_date, es.exam_time, es.room_no
        FROM exam_schedule es
        JOIN departments d ON es.department_id = d.department_id
        WHERE d.department_name = %s;
        """,(course_name,))
        
        exams = cur.fetchall()  # Get all exams for the user's course
        
        return render_template('exam.html', exams=exams)
    else:
        flash('Course not found.', 'error')
        return redirect(url_for('login'))  # Redirect back to login page if no course found



@app.route('/complaints', methods=['GET', 'POST'])
def complaints():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure the user is logged in

    if request.method == 'POST':
        # Get form data using `get()` to avoid KeyError if a field is missing
        full_name = request.form.get('full_name', '')
        roll_number = request.form.get('roll_number', '')
        complaint_type = request.form.get('complainttype', '')
        comments = request.form.get('comments', '')

        # Insert complaint into the database
        cur = mysql.connection.cursor()
        cur.execute(""" 
            INSERT INTO complaints (user_id, username, rollno, complainttype, comments)
            VALUES (%s, %s, %s, %s, %s)
        """, (session['user_id'], session['username'], roll_number, complaint_type, comments))
        mysql.connection.commit()  # Commit the transaction

        flash('Your complaint has been submitted successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('complaints.html')


@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect('/login')  # Redirect to login page if not logged in

    if request.method == 'POST':
        # Get form inputs
        new_password = request.form['password']
        repeat_password = request.form['repeatPassword']

        # Check if new passwords match
        if new_password != repeat_password:
            flash('New password and confirm password do not match.', 'danger')
            return render_template('password.html')  # Reload the password page

        # Update the password in the database without validation
        cur = mysql.connection.cursor()
        user_id = session['user_id']
        cur.execute("UPDATE users SET password = %s WHERE user_id = %s", (new_password, user_id))
        mysql.connection.commit()
        cur.close()

        flash('Password updated successfully!', 'success')
        return redirect('/index')  # Redirect to the dashboard

    return render_template('password.html')  # Render password page for GET request

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # Get form data
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        username = request.form['userName']
        password = request.form['password']
        address = request.form['address']
        course = request.form['course']
        date_of_birth = request.form['date_of_birth']
        email = request.form['email']

        cur = mysql.connection.cursor()
        try:
            # Insert into `users` table
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            mysql.connection.commit()

            # Get the generated user_id
            user_id = cur.lastrowid

            # Insert into `details` table
            full_name = f"{first_name} {last_name}"
            cur.execute("""
                INSERT INTO details 
                (user_id, full_name, email, address, date_of_birth, course,
                 attendance_discrete_maths, attendance_oop, attendance_ui_design, 
                 attendance_linear_algebra, attendance_networking_hardware) 
                VALUES (%s, %s, %s, %s, %s, %s, 0, 0, 0, 0, 0)
            """, (user_id, full_name, email, address, date_of_birth, course))
            mysql.connection.commit()

            flash('Account created successfully!', 'success')
            return redirect(url_for('index'))  # Redirect to /index on success

        except Exception as e:
            mysql.connection.rollback()
            flash(f"An error occurred: {e}", 'danger')
            return render_template('signup.html')  # Stay on the sign-up page on error

        finally:
            cur.close()

    return render_template('signup.html')
# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
