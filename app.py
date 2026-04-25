from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# =========================
# DATABASE INIT
# =========================
def init_db():
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            course TEXT,
            marks INTEGER DEFAULT 0,
            cgpa REAL DEFAULT 0.0,
            attendance INTEGER DEFAULT 0,
            fee TEXT DEFAULT 'Unpaid',
            result_status TEXT DEFAULT 'Not Published'
        )
    """)

    conn.commit()
    conn.close()

init_db()


# =========================
# DB CONNECT
# =========================
def get_db():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# HOME
# =========================
@app.route('/')
def home():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM students ORDER BY id ASC")
    students = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM students")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM students WHERE fee='Paid'")
    paid = cur.fetchone()[0]

    cur.execute("SELECT AVG(cgpa) FROM students")
    avg_cgpa = cur.fetchone()[0] or 0

    cur.execute("SELECT MAX(cgpa) FROM students")
    max_cgpa = cur.fetchone()[0] or 0

    conn.close()

    return render_template(
        'index.html',
        students=students,
        total=total,
        paid=paid,
        avg_cgpa=round(avg_cgpa, 2),
        max_cgpa=max_cgpa
    )


# =========================
# ADD STUDENT
# =========================
@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name', '').strip()
    age = request.form.get('age', '').strip()
    course = request.form.get('course', '').strip()
    marks = request.form.get('marks', '0').strip()

    if not name or not age or not course:
        return redirect('/')

    marks = int(marks)
    cgpa = round((marks / 100) * 4, 2)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO students (name, age, course, marks, cgpa, attendance, fee, result_status)
        VALUES (?, ?, ?, ?, ?, 0, 'Unpaid', 'Not Published')
    """, (name, age, course, marks, cgpa))

    conn.commit()
    conn.close()

    return redirect('/')


# =========================
# EDIT STUDENT (FIXED)
# =========================
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        course = request.form['course']
        marks = int(request.form['marks'])

        cgpa = round((marks / 100) * 4, 2)

        cur.execute("""
            UPDATE students
            SET name=?, age=?, course=?, marks=?, cgpa=?
            WHERE id=?
        """, (name, age, course, marks, cgpa, id))

        conn.commit()
        conn.close()
        return redirect('/')

    cur.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cur.fetchone()
    conn.close()

    return render_template('edit.html', student=student)


# =========================
# MOVE COURSE (FIXED)
# =========================
@app.route('/course/<int:id>/<string:new_course>')
def move_course(id, new_course):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE students
        SET course=?
        WHERE id=?
    """, (new_course, id))

    conn.commit()
    conn.close()

    return redirect('/')


# =========================
# PUBLISH RESULT
# =========================
@app.route('/publish/<int:id>')
def publish(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE students
        SET result_status='Published'
        WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect('/')


# =========================
# ATTENDANCE +1
# =========================
@app.route('/attendance/<int:id>')
def attendance(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE students
        SET attendance = attendance + 1
        WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect('/')


# =========================
# PAY FEE
# =========================
@app.route('/pay/<int:id>')
def pay(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE students
        SET fee='Paid'
        WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect('/')


# =========================
# DELETE
# =========================
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/')


# =========================
# SEARCH (BONUS FIX)
# =========================
@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM students
        WHERE name LIKE ? OR course LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%"))

    students = cur.fetchall()
    conn.close()

    return render_template('index.html', students=students, total=0, paid=0, avg_cgpa=0, max_cgpa=0)


# =========================
# RUN
# =========================
if __name__ == '__main__':
    app.run(debug=True)