from app import app
from flask import render_template

@app.route('/')
def show_home():
    print("Home page requested")
    return render_template("index.html", name="Raju")

@app.route('/login')
def show_login():
    print("Login page requested")
    return render_template("login.html")

@app.route('/register')
def show_register():
    print("Register page requested")
    return render_template("register.html")

@app.route("/services")
def service():
    print("Services page requested")
    return render_template("services.html")

@app.route('/register/professional')
def show_register_professional():
    print("Professional register page requested")
    return render_template("register_professional.html")

@app.route('/dashboard/user')
def show_dashboard_user():
    print("User dashboard requested")
    return render_template("dashboard_user.html")

@app.route('/dashboard/professional')
def show_dashboard_professional():
    print("Professional dashboard requested")
    return render_template("dashboard_professional.html")

@app.route('/dashboard/admin')
def show_admin():
    print("Admin page requested")
    return render_template("dashboard_admin.html")

