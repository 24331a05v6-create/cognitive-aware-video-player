from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from google import genai
import mysql.connector
import bcrypt
import random
from flask_mail import Mail, Message

app = Flask(__name__)
CORS(app)

# ------------------ AI CONFIG ------------------
client = genai.Client(api_key="AIzaSyBBuJqMy84S0IodlSt6jf4LNPxI4-wOEeE")
MODEL_NAME = "gemini-2.5-flash"

def simple_ai_response(user_input):
    try:
        prompt = f"""
You are a helpful AI assistant.

Guidelines:
- Give clear and structured answers.
- Keep responses medium length.
- Use bullet points when helpful.

User question: {user_input}
"""
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"


# ------------------ DATABASE ------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Sai@1919",
    database="login_demo"
)
cursor = db.cursor()

otp_store = {}

# ------------------ EMAIL ------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'saisrinivasjagannadh@gmail.com'
app.config['MAIL_PASSWORD'] = 'klegxnjlcwumrooc'

mail = Mail(app)

# ------------------ PAGE ROUTES ------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/ai")
def ai_page():
    return render_template("ai.html")

@app.route("/signup")
def signup_page():
    return render_template("signup.html")

@app.route("/forget")
def forget_page():
    return render_template("forget.html")

# ------------------ AI CHAT API ------------------
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
    ai_output = simple_ai_response(user_message)
    return jsonify({"response": ai_output})

# ------------------ LOGIN API ------------------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
    result = cursor.fetchone()

    if result:
        stored_password = result[0].encode()
        if bcrypt.checkpw(password.encode(), stored_password):
            return jsonify({"message": "Login successful"})

    return jsonify({"message": "Invalid username or password"})

# ------------------ SEND OTP ------------------
@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    email = data.get('email')

    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp

    msg = Message(
        subject="Your OTP Code",
        sender=app.config['MAIL_USERNAME'],
        recipients=[email]
    )
    msg.body = f"Your OTP is: {otp}"

    mail.send(msg)
    return jsonify({"message": "OTP sent to email"})

# ------------------ SIGNUP ------------------
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    otp = data.get('otp')

    if otp_store.get(email) != otp:
        return jsonify({"message": "Invalid OTP"})

    if password != confirm_password:
        return jsonify({"message": "Passwords do not match"})

    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    if cursor.fetchone():
        return jsonify({"message": "Username already exists"})

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
        (username, email, hashed_password.decode())
    )
    db.commit()

    return jsonify({"message": "Signup successful"})

# ------------------ RESET OTP ------------------
@app.route('/api/send-reset-otp', methods=['POST'])
def send_reset_otp():
    data = request.json
    email = data.get('email')

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    if not cursor.fetchone():
        return jsonify({"message": "Email not found"})

    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp

    msg = Message(
        subject="Password Reset OTP",
        sender=app.config['MAIL_USERNAME'],
        recipients=[email]
    )
    msg.body = f"Your password reset OTP is: {otp}"

    mail.send(msg)
    return jsonify({"message": "Reset OTP sent"})

# ------------------ RESET PASSWORD ------------------
@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')

    if otp_store.get(email) != otp:
        return jsonify({"message": "Invalid OTP"})

    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())

    cursor.execute(
        "UPDATE users SET password=%s WHERE email=%s",
        (hashed_password.decode(), email)
    )
    db.commit()

    return jsonify({"message": "Password reset successful"})


if __name__ == "__main__":
    app.run(debug=True)
