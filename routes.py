from app import app
from flask import render_template,request,redirect,url_for,flash,session
from models import User,db,ServiceProfessional,Category,Service,ServiceRequest
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def show_home():
    print("Home page requested")
    return render_template("index.html")

@app.route('/login')
def show_login():
    print("Login page requested")
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def handle_login():
    print("Login form submitted")
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    if  username=="" or  password=="":
        flash("Please enter both username and password")
        return redirect(url_for('show_login')) 
    role="none"
    if username=="admin" and password=="admin":
        session['admin'] = username
        return redirect(url_for('show_admin'))
    elif ServiceProfessional.query.filter_by(username=username).first():
        user=ServiceProfessional.query.filter_by(username=username).first()
        role="service professional"
    elif User.query.filter_by(username=username).first():
        user=User.query.filter_by(username=username).first()
        role="user"
    else: 
        user=None
    
    if user is None or not check_password_hash(user.passhash, password):
        flash("Invalid username or password")
        return redirect(url_for('show_login'))
    elif role=="user":
        session['user'] = username
        return redirect(url_for('show_dashboard_user'))
    elif role=="service professional":
        session['service professional'] = username
        return redirect(url_for('show_dashboard_professional'))


@app.route('/register')
def show_register():
    print("Register page requested")
    return render_template("register.html")

@app.route('/register', methods=['POST'])
def handle_register():
    print("Register form submitted")

    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    name = request.form.get('name')
    confirm_password = request.form.get('confirmPassword')
    if username=="" or password=="" or name=="" or email=="" or confirm_password=="":
        flash("Please enter all the fields")
        return redirect(url_for('show_register'))
    db_username=User.query.filter_by(username=username).first()
    db_email=User.query.filter_by(email=email).first()
    if password!=confirm_password:
        flash("Passwords do not match")
        return redirect(url_for('show_register'))   
    if db_username or ServiceProfessional.query.filter_by(username=username).first() or username=="admin":
        flash("Username already exists")
        return redirect(url_for('show_register'))   
    if  db_email or ServiceProfessional.query.filter_by(email=email).first():
        flash("Email already exists")
        return redirect(url_for('show_register')) 
    passhash=generate_password_hash(password)
    user = User(username=username, passhash=passhash, name=name, email=email)
    db.session.add(user)
    db.session.commit()
    flash("User registered successfully")
    return redirect(url_for('show_login'))

@app.route("/services")
def service():
    print("Services page requested")
    return render_template("services.html")

@app.route('/register/professional')
def show_register_professional():
    print("Professional register page requested")
    categories=Category.query.all()
    return render_template("register_professional.html",categories=categories)

@app.route('/register/professional', methods=['POST'])
def handle_register_professional():
    print("Professional register form submitted")
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    name = request.form.get('name')
    category = request.form.get('category')
    description = request.form.get('description')
    experience = request.form.get('experience')
    confirm_password = request.form.get('confirmPassword')
    if username=="" or password=="" or name=="" or email=="" or confirm_password==""  or description=="" or experience=="":
        flash("Please enter all the fields")
        return redirect(url_for('show_register_professional'))
    db_username=User.query.filter_by(username=username).first()
    db_email=User.query.filter_by(email=email).first()  
    if password!=confirm_password:
        flash("Passwords do not match")
        return redirect(url_for('show_register_professional'))   
    if db_username or ServiceProfessional.query.filter_by(username=username).first() or username=="admin":
        flash("Username already exists")
        return redirect(url_for('show_register_professional'))   
    if  db_email or ServiceProfessional.query.filter_by(email=email).first():
        flash("Email already exists")
        return redirect(url_for('show_register_professional')) 
    passhash=generate_password_hash(password)
    professional = ServiceProfessional(username=username, passhash=passhash, name=name, email=email, category=category, description=description, experience=experience)
    db.session.add(professional)
    db.session.commit()
    flash("Professional registered successfully")
    return redirect(url_for('show_login'))

@app.route('/dashboard/user')
def show_dashboard_user():
    print("User dashboard requested")
    if 'user' in session:
        return render_template("dashboard_user.html")
    else:
        flash("You are not authorized to view this page")
        return render_template("login.html")

@app.route('/dashboard/professional')
def show_dashboard_professional():
    print("Professional dashboard requested")
    if 'service professional' in session:
        return render_template("dashboard_professional.html")
    else:
        flash("You are not authorized to view this page")
        return render_template("login.html")
    

@app.route('/dashboard/admin')
def show_admin():
    print("Admin page requested")
    if 'admin' in session:
        return render_template("dashboard_admin.html")
    else:
        flash("You are not authorized to view this page")
        return render_template("login.html")

