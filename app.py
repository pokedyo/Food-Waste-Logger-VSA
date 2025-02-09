from flask import Flask, render_template, request, redirect, send_from_directory
import sqlite3

app = Flask(__name__)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename, mimetype='application/json' if filename.endswith('.json') else None)


# Initialize the database
def init_db():
    connection = sqlite3.connect("food_wastage.db")
    connection.execute(
        """CREATE TABLE IF NOT EXISTS food_wastage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            group_name TEXT,
            amount REAL
        )"""
    )
    connection.close()

init_db()

def connect_db():
    connection = sqlite3.connect('food_wastage.db')
    return connection


# Routes
@app.route("/")
def index():
    connection = sqlite3.connect("food_wastage.db")
    food_wastage = connection.execute(
        "SELECT date, group_name, SUM(amount) as total FROM food_wastage GROUP BY date, group_name"
    ).fetchall()
    connection.close()
    return render_template("index.html", food_wastage=food_wastage)

@app.route("/log", methods=["POST"])
def log_wastage():
    date = request.form["date"]
    group_name = request.form["group_name"]
    amount = request.form["amount"]
    connection = sqlite3.connect("food_wastage.db")
    connection.execute("INSERT INTO food_wastage (date, group_name, amount) VALUES (?, ?, ?)", (date, group_name, amount))
    connection.commit()
    connection.close()
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete_record():
    record_id = request.form["record_id"]
    connection = sqlite3.connect("food_wastage.db")
    connection.execute("DELETE FROM food_wastage WHERE id = ?", (record_id,))
    connection.commit()
    connection.close()
    return redirect("/")

# Route to display the summary page
@app.route('/summary')
def summary():
    connection = sqlite3.connect("food_wastage.db")
    db = connection.cursor()
    
    # Query to get total wastage per day for each grade group
    db.execute("""
        SELECT date, 
               SUM(CASE WHEN group_name = '1st-3rd' THEN amount ELSE 0 END) AS group_1,
               SUM(CASE WHEN group_name = '4th-5th' THEN amount ELSE 0 END) AS group_2,
               SUM(CASE WHEN group_name = '6th-7th' THEN amount ELSE 0 END) AS group_3,
               SUM(CASE WHEN group_name = '8th-12th' THEN amount ELSE 0 END) AS group_4,
               SUM(amount) AS total_wastage
        FROM food_wastage
        GROUP BY date
        ORDER BY date DESC
    """)
    
    summary_data = db.fetchall()
    connection.close()
    
    return render_template('summary.html', summary_data=summary_data)

@app.route('/reset', methods=['POST'])
def reset():
    connection = connect_db()
    db = connection.cursor()

    # Delete all records from the 'wastage' table
    db.execute("DELETE FROM food_wastage")

    # Commit the changes and close the connection
    connection.commit()
    connection.close()

    # Redirect to the summary page after reset
    return render_template('summary.html', summary_data=[])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) 
