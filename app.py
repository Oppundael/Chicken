from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "hemlig_nyckel"  # Krävs för sessionshantering

# Skapa databas om den inte finns
def init_db():
    conn = sqlite3.connect("votes.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS votes (id INTEGER PRIMARY KEY, name TEXT, chicken INTEGER)''')
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        chicken = request.form["chicken"]

        conn = sqlite3.connect("votes.db")
        c = conn.cursor()
        c.execute("INSERT INTO votes (name, chicken) VALUES (?, ?)", (name, chicken))
        conn.commit()
        conn.close()

        return redirect("/thanks")

    return render_template("index.html")

@app.route("/thanks")
def thanks():
    return "<h1>Tack för din röst!</h1><a href='/'>Tillbaka</a>"

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password")
        if password == "1972":
            session["admin"] = True
        else:
            return "<h1>Åtkomst nekad</h1><a href='/admin'>Försök igen</a>"
    
    if not session.get("admin"):
        return '''
            <form method="POST">
                <label for="password">Lösenord:</label>
                <input type="password" name="password" required>
                <button type="submit">Logga in</button>
            </form>
        '''
    
    conn = sqlite3.connect("votes.db")
    c = conn.cursor()
    c.execute("SELECT name, chicken FROM votes")
    votes = c.fetchall()
    conn.close()
    
    result_text = "<h1>Admin Panel</h1><ul>"
    for name, chicken in votes:
        result_text += f"<li>{name} röstade på Kyckling {chicken}</li>"
    result_text += "</ul><form action='/reset' method='POST' onsubmit='return confirm(\"Är du säker på att du vill rensa alla röster?\")'>"
    result_text += "<button type='submit'>Rensa röstning</button></form>"
    result_text += "<a href='/'>Tillbaka</a>"
    
    return result_text

@app.route("/reset", methods=["POST"])
def reset_votes():
    if not session.get("admin"):
        return "<h1>Åtkomst nekad</h1><a href='/'>Tillbaka</a>"
    
    conn = sqlite3.connect("votes.db")
    c = conn.cursor()
    c.execute("DELETE FROM votes")
    conn.commit()
    conn.close()
    
    return "<h1>Röstningen har rensats!</h1><a href='/admin'>Tillbaka</a>"

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
