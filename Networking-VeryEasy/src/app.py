from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# Whimsical login page HTML
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>The Iron Potato Login Portal</title>
    <style>
        body { font-family: 'Comic Sans MS', cursive, sans-serif; background-color: #f0f8ff; text-align: center; padding-top: 50px; }
        .container { background-color: #ffffff; margin: auto; padding: 30px; border-radius: 15px; box-shadow: 5px 5px 15px #aaaaaa; width: 300px; }
        h1 { color: #8b0000; }
        label { display: block; margin-bottom: 5px; color: #333; }
        input[type="text"], input[type="password"] { width: calc(100% - 20px); padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 5px; }
        input[type="submit"] { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        input[type="submit"]:hover { background-color: #45a049; }
        .error { color: red; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to The Iron Potato Login Portal!</h1>
        <p>Please enter your credentials. (Our security is top-notch, don't you worry!)</p>
        <form method="POST" action="/login">
            <label for="username">User of Destiny:</label>
            <input type="text" id="username" name="username" required><br>
            <label for="password">Password of Unspeakable Power:</label>
            <input type="password" id="password" name="password" required><br>
            <input type="submit" value="Log In and Conquer!">
        </form>
        {% if error %}
        <p class="error">{{ error }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

# Whimsical success banner HTML
SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Juche Jaguar Communications Hub</title>
    <style>
        body { font-family: 'Impact', fantasy; background-color: #ffe0b2; text-align: center; padding-top: 50px; }
        .banner { background-color: #ff5722; color: white; margin: auto; padding: 20px; border-radius: 20px; box-shadow: 8px 8px 20px #888888; width: 60%; max-width: 600px; border: 5px solid #d32f2f; }
        h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 3px 3px #d32f2f; }
        p { font-size: 1.2em; }
        .jaguar-emoji { font-size: 4em; display: block; margin-20px; }
    </style>
</head>
<body>
    <div class="banner">
        <span class="jaguar-emoji">&#128006;</span> <h1>GLORY TO JUCHE JAGUAR!</h1>
        <p>You have successfully infiltrated the glorious internal communications hub!</p>
        <p>Prepare for highly sensitive memos about avocado toast and the current status of "The Iron Potato."</p>
    </div>
</body>
</html>
"""

# Hardcoded credentials for the challenge
CORRECT_USERNAME = "ironpotatoadmin"
CORRECT_PASSWORD = "C1{maybe_TLS_would_be_nice}"

@app.route('/')
def index():
    return render_template_string(LOGIN_HTML)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
        return render_template_string(SUCCESS_HTML)
    else:
        return render_template_string(LOGIN_HTML, error="Login failed! Are you sure you're a true User of Destiny?")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)