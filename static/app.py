from flask import Flask, render_template, redirect, url_for, flash, request, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'mysecretkey123'

# MySQL Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="project"
)
proctor = 0
@app.route('/') 
def login_page():
    return render_template('index.html')

@app.route('/student_login', methods=['POST'])
def student_login():
    roll_number = request.form['roll_number']
    password = request.form['password']
    
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students_login WHERE roll_number=%s AND password=%s", (roll_number, password))
    student = cursor.fetchone()
    cursor.close()
    
    if student:
        session['roll_number'] = roll_number  
        flash('Login successful! Redirecting to Student Dashboard...', 'success')
        return redirect(url_for('student_dashboard'))
    else:
        flash('Invalid credentials. Please try again.', 'danger')
        return redirect(url_for('login_page'))

@app.route('/faculty_login', methods=['POST'])
def faculty_login():
    faculty_id = request.form['faculty_id']
    password = request.form['password']
    
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM faculty_login_info WHERE faculty_id=%s AND password=%s", (faculty_id, password))
    faculty = cursor.fetchone()
    cursor.close()
    
    if faculty:
        session['faculty_id'] = faculty_id
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT Proctor FROM faculty_info Where Faculty_id = %s",(faculty_id,))
        global proctor 
        proctor = cursor.fetchone()
        proctor = int(proctor["Proctor"])
        cursor.close()
        flash('Login successful! Redirecting to Faculty Dashboard...', 'success')
        return redirect(url_for('faculty_dashboard'))
    else:
        flash('Invalid credentials. Please try again.', 'danger')
        return redirect(url_for('login_page'))
    

@app.route('/student_dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')

@app.route('/faculty_dashboard')
def faculty_dashboard():
    return render_template('faculty_dashboard.html')

@app.route('/faculty_details')
def faculty_details():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT faculty_id, name, department, email, phone FROM faculty")
    faculties = cursor.fetchall()
    cursor.close()
    return render_template('faculty_details.html', faculties=faculties)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login_page'))

@app.route('/student_details')
def student_details():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT Roll_Number, Student_id , Name, Department, Semester, Email FROM student_info WHERE Semester = %s ",(proctor,))
    students = cursor.fetchall()
    for student in students:
        print(student)
    cursor.close()
    return render_template('student_details.html', students=students)

@app.route('/add_student_result', methods=['GET', 'POST'])  
def add_student_result():
    if request.method == 'POST':
        roll_number = request.form['roll_number']
        python_marks = request.form['python_marks']
        web_dev_marks = request.form['web_dev_marks']
        chm_marks = request.form['chm_marks']
        english_marks = request.form['english_marks']
        iot_marks = request.form['iot_marks']
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT Roll_Number FROM student_info WHERE Semester = %s ",(proctor,))
        rollnumbers = cursor.fetchall()
        rollnumber_list = []
        for rollnumber in rollnumbers:
            rollnumber_list.append(rollnumber['Roll_Number'])
        
        for rollnumber in rollnumber_list:
            print(rollnumber)

        try:
            cursor = db.cursor()
            query = """
            INSERT INTO Result_Sem5 (Roll_Number, PP_marks, WD_marks, CHM_marks, ENG_marks, IOT_marks)
            VALUES (%s, %s, %s, %s, %s, %s) 
            """
            cursor.execute(query, (roll_number, python_marks, web_dev_marks, chm_marks, english_marks, iot_marks))
            db.commit()

            flash('Student result added successfully!', 'success')
            return redirect(url_for('faculty_dashboard'))
          
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", 'danger')
            db.rollback()  
            
        finally:
            cursor.close()
        

        
    return render_template('add_student_result.html')

@app.route('/check_student_results')
def check_student_results():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT roll_number, python_marks, web_dev_marks, chm_marks, english_marks, iot_marks FROM student_results")
    marks = cursor.fetchall()
    cursor.close()
    return render_template('student_result.html', marks=marks)

@app.route('/individual_student_result')
def individual_student_result():
    if 'roll_number' not in session:
        flash('You must be logged in to view this page.', 'danger')
        return redirect(url_for('login_page'))

    roll_number = session['roll_number']  

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT roll_number, python_marks, web_dev_marks, chm_marks, english_marks, iot_marks FROM student_results WHERE roll_number = %s", (roll_number,))
    marks = cursor.fetchall()
    cursor.close()
    
    return render_template('individual_student_result.html', marks=marks)

@app.route('/modify_student_result', methods=['GET', 'POST'])
def modify_student_result():
    if request.method == 'POST':
        roll_number = request.form['roll_number']
        python_marks = request.form['python_marks']
        web_dev_marks = request.form['web_dev_marks']
        chm_marks = request.form['chm_marks']
        english_marks = request.form['english_marks']
        iot_marks = request.form['iot_marks']

        try:
            cursor = db.cursor()
            query = """
            UPDATE student_results
            SET python_marks = %s,
                web_dev_marks = %s,
                chm_marks = %s,
                english_marks = %s,
                iot_marks = %s
            WHERE roll_number = %s
            """
            cursor.execute(query, (python_marks, web_dev_marks, chm_marks, english_marks, iot_marks, roll_number))
            db.commit()  

            flash('Student result modified successfully!', 'success')
            return redirect(url_for('faculty_dashboard'))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", 'danger')
            db.rollback()  
        finally:
            cursor.close()  

    return render_template('modify_student_result.html')


@app.route('/delete_student_result', methods=['POST'])
def delete_student_result():
    roll_number = request.form['roll_number']

    # Establish the database connection and execute the delete query
    try:
        cursor = db.cursor()
        query = "DELETE FROM student_results WHERE roll_number = %s"
        cursor.execute(query, (roll_number,))
        db.commit()  # Commit the transaction

        flash('Student result deleted successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'danger')
        db.rollback()  # Rollback in case of an error
    finally:
        cursor.close()  # Ensure cursor is closed

    return redirect(url_for('faculty_dashboard'))


if __name__ == '__main__':
    app.run(debug=True)



