from app import app
from flask import render_template,request,redirect,url_for,flash,session
from models import User,db,ServiceProfessional,Category,Service,ServiceRequest
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'logged_in' in session:
            return func(*args, **kwargs)
        else:
            flash("You are not authorized to view this page, please login")
            return redirect(url_for('show_login'))
    return inner

def admin_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'logged_in' in session and session['user_type']=="admin":
            return func(*args, **kwargs)
        else:
            flash("You are not authorized to view this page")
            return redirect(url_for('show_login'))
    return inner

def professional_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'logged_in' in session and session['user_type']=="service professional":
            return func(*args, **kwargs)
        else:
            flash("You are not authorized to view this page")
            return redirect(url_for('show_login'))
    return inner

def user_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'logged_in' in session and session['user_type']=="user":
            return func(*args, **kwargs)
        else:
            flash("You are not authorized to view this page")
            return redirect(url_for('show_login'))
    return inner

@app.route('/')
def show_home():
    print("Home page requested")
    return render_template("index.html")

@app.route('/logout')
def show_logout():
    print("Logout requested")
    session.clear()
    flash("Logged out successfully")
    return redirect(url_for('show_home'))

@app.route('/login')
def show_login():
    print("Login page requested")
    if 'logged_in' in session:
        flash("You are already logged in logout to login again")
        if session['user_type']=="user":
            return redirect(url_for('show_dashboard_user'))
        elif session['user_type']=="service professional":
            return redirect(url_for('show_dashboard_professional'))
        else:
            return redirect(url_for('show_admin'))
    else:
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
    
    user = User.query.filter_by(username=username).first()

    if username=="admin" and check_password_hash(user.passhash, password):
        session['user'] = username
        session['user_type']="admin"
        session['logged_in']= True
        user = User.query.filter_by(username=username).first()
        return redirect(url_for('show_admin'))
    elif ServiceProfessional.query.filter_by(username=username).first():
        role="service professional"
        user = ServiceProfessional.query.filter_by(username=username).first()
    elif User.query.filter_by(username=username).first():
        role="user"
        user = User.query.filter_by(username=username).first()
    else: 
        user=None
    

    if user is None or not check_password_hash(user.passhash, password):
        flash("Invalid username or password")
        return redirect(url_for('show_login'))
    elif role=="user":
        session['logged_in']= True
        session['user_type']="user"
        session['user'] = username
        return redirect(url_for('show_dashboard_user'))
    elif role=="service professional":
        user = ServiceProfessional.query.filter_by(username=username).first()
        session['logged_in']= True
        session['user_type']="service professional"
        session['user'] = username
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
    service_name = request.form.get('service_name')
    service_description = request.form.get('service_description')
    service_price = request.form.get('service_price')
    service_duration = request.form.get('service_duration')
    if username=="" or password=="" or name=="" or email=="" or confirm_password==""  or description=="" or experience=="" or service_name=="" or service_description=="" or service_price=="" or service_duration=="" :    
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
    service=Service(name=service_name,description=service_description,price=service_price,time=service_duration,category_id=category,service_professional_id=professional.id)
    db.session.add(service)
    db.session.commit()
    flash("Professional registered successfully")
    return redirect(url_for('show_login'))

@app.route("/profile")
def show_profile():
    print("profile page requested")
    if 'logged_in' in session:
        if session['user_type']=="service professional":
            user = ServiceProfessional.query.filter_by(username=session['user']).first()
            categories=Category.query.all()
            service=Service.query.filter_by(service_professional_id=user.id).first()
            return render_template("profile.html",user=user,categories=categories,service=service)
        else:
            user = User.query.filter_by(username=session['user']).first()
            return render_template("profile.html",user=user)
    else:
        flash("You are not authorized to view this page, please login")
        return render_template("login.html")

@app.route("/profile", methods=['POST'])
@login_required
def handle_profile():
    print("profile form submitted")
    if session['user_type']=="user" or session['user_type']=="admin":
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        current_password = request.form.get('current_password')
        if name=="" or username=="" or email=="" or current_password=="":
            flash("Please enter all the fields")
            return redirect(url_for('show_profile'))
        if new_password!="" and new_password!=confirm_password:
            flash("Passwords do not match")
            return redirect(url_for('show_profile'))
        user = User.query.filter_by(username=session['user']).first()
        if not check_password_hash(user.passhash, current_password):
            flash("Invalid password")
            return redirect(url_for('show_profile'))
        if username=="admin" and user.username!=username:
            flash("Username cannot be changed")
            return redirect(url_for('show_profile'))
        if user.username!=username:
            username_exists=User.query.filter_by(username=username).first()
            if username_exists or ServiceProfessional.query.filter_by(username=username).first():
                flash("Username already exists")
                return redirect(url_for('show_profile'))
        new_passhash=generate_password_hash(new_password)
        user.name=name
        if user.username!=username and user.username!="admin":
            user.username=username
        if new_password!="":
            user.passhash=new_passhash  
        db.session.commit()
        flash("Profile updated successfully")
        return redirect(url_for('show_profile'))
    if session['user_type']=="service professional":
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        category = request.form.get('category')
        confirm_password = request.form.get('confirm_password')
        current_password = request.form.get('current_password')
        description = request.form.get('description')
        experience = request.form.get('experience')
        service_name = request.form.get('service_name')
        service_description = request.form.get('service_description')
        service_price = request.form.get('service_price')
        service_duration = request.form.get('service_duration')
        if name=="" or username==""  or current_password=="" or description=="" or experience=="":
            flash("Please enter all the fields")
            return redirect(url_for('show_profile'))
        if new_password!="" and new_password!=confirm_password:
            flash("Passwords do not match")
            return redirect(url_for('show_profile'))
        user = ServiceProfessional.query.filter_by(username=session['user']).first()
        if not check_password_hash(user.passhash, current_password):
            flash("Invalid password")
            return redirect(url_for('show_profile'))
        if user.username!=username:
            username_exists=User.query.filter_by(username=username).first()
            if username_exists or ServiceProfessional.query.filter_by(username=username).first():
                flash("Username already exists")
                return redirect(url_for('show_profile'))
        service=Service.query.filter_by(service_professional_id=user.id).first()
        if service_name=="" or service_description=="" or service_price=="" or service_duration=="":
            flash("Please enter all the fields also for service")
            return redirect(url_for('show_profile'))
        if service_name!=service.name:
            service.name=service_name
        if service_description!=service.description:
            service.description=service_description
        if service_price!=service.price:
            service.price=service_price
        if service_duration!=service.time:
            service.time=service_duration
        
        new_passhash=generate_password_hash(new_password)
        if user.name!=name:
            user.name=name
        if user.username!=username:
            user.username=username
        if user.description!=description:
            user.description=description
        if user.experience!=experience:
            user.experience=experience
        if new_password!="":
            user.passhash=new_passhash  
        if user.category!=category:
            user.category=category
        db.session.commit()
        flash("Profile updated successfully")
        return redirect(url_for('show_profile'))


@app.route('/dashboard/user')
@login_required
@user_required
def show_dashboard_user():
    print("User dashboard requested")
    return render_template("dashboard/user.html")
    
@app.route('/dashboard/professional')
@login_required
@professional_required
def show_dashboard_professional():
    print("Professional dashboard requested")
    return render_template("dashboard/professional.html")

@app.route('/dashboard/admin')
@login_required
@admin_required
def show_admin():
    print("Admin page requested")
    categories=Category.query.all()
    professionals=ServiceProfessional.query.all()
    return render_template("dashboard/admin.html",categories=categories,professionals=professionals)

@app.route('/category/add')
@login_required
@admin_required
def show_add_category():
    print("Add category page requested")
    return render_template("category/add.html")

@app.route('/category/add', methods=['POST'])
@login_required
@admin_required
def handle_add_category():
    print("Add category form submitted")
    name = request.form.get('name')
    if name=="":
        flash("Please enter category name")
        return redirect(url_for('show_add_category'))
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    flash("Category added successfully")
    return redirect(url_for('show_admin'))

    
@app.route('/category/<int:id>')
@login_required
@admin_required
def show_category(id):
    print("Category page requested")
    category=Category.query.get(id)
    services=Service.query.filter_by(category_id=id).all()
    professionals=ServiceProfessional.query.filter_by(category=id).all()
    return render_template("category.html",category=category,services=services,professionals=professionals)

@app.route('/category/<int:id>/edit')
@login_required
@admin_required
def show_edit_category(id):
    print("Edit category page requested")
    category=Category.query.get(id)
    return render_template("category/edit.html",category=category)

@app.route('/category/<int:id>/edit', methods=['POST'])
@login_required
@admin_required
def handle_edit_category(id):
    print("Edit category form submitted")
    name = request.form.get('name')
    if name=="":
        flash("Please enter category name")
        return redirect(url_for('show_edit_category',id=id))
    category = Category.query.get(id)
    if category.name==name:
        flash("No changes made")
    if category.name!=name:
       category.name=name
    db.session.commit()
    flash("Category updated successfully")
    return redirect(url_for('show_admin'))

@app.route('/category/<int:id>/delete')
@login_required
@admin_required
def delete_category(id):
    print("Delete category requested")
    category = Category.query.get(id)
    db.session.delete(category)
    db.session.commit()
    flash("Category deleted successfully")
    return redirect(url_for('show_admin'))

@app.route('/professional/<int:id>')
@login_required
@admin_required
def show_professional(id):
    print("Professional page requested")
    professional=ServiceProfessional.query.get(id)
    services=Service.query.filter_by(service_professional_id=id).first()
    print(services)
    return render_template("view_professional.html",professional=professional,services=services)

@app.route('/professional/<int:id>/delete')
@login_required
@admin_required
def delete_professional(id):
    print("Delete professional requested")
    professional = ServiceProfessional.query.get(id)
    db.session.delete(professional)
    db.session.commit()
    flash("Professional deleted successfully")
    return redirect(url_for('show_admin'))






