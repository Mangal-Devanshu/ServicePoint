from app import app
from flask import render_template,request,redirect,url_for,flash,session
from models import User,db,ServiceProfessional,Category,Service,ServiceRequest,Transaction,Review
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import random

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
def show_index():
    print("Home page requested")
    category=Category.query.all()
    return render_template("index.html",category=category)

@app.route('/home')
@login_required
@user_required
def show_home():
    print("Home page requested")
    category=Category.query.all()
    user=User.query.filter_by(username=session['user']).first()
    service=Service.query.all()
    return render_template("home.html",user=user,category=category)

@app.route('/ViewProfessional/<int:id>')
@login_required
@user_required
def show_book_professional(id):
    print("Book page requested")
    service=Service.query.get(id)
    professional=ServiceProfessional.query.get(service.service_professional_id)
    print(service.id)
    reviews=Review.query.filter_by(service_id=id).all()
    print(reviews)
    return render_template("book_professional.html",service=service,professional=professional,reviews=reviews)

@app.route('/book/<int:id>')
@login_required
@user_required
def show_book(id):
    print("Book page requested")
    service=Service.query.get(id)
    professional=ServiceProfessional.query.get(service.service_professional_id)
    return render_template("book.html",service=service,professional=professional)

@app.route('/book/<int:id>',methods=['POST'])
@login_required
@user_required
def handle_book(id):
    print("Book form submitted")
    service=Service.query.get(id)
    professional=ServiceProfessional.query.get(service.service_professional_id)
    time=request.form.get('time')
    date=request.form.get('date')
    appointment=datetime.strptime(date+" "+time, '%Y-%m-%d %H:%M')
    address = request.form.get('address')
    user_id=User.query.filter_by(username=session['user']).first().id
    price=service.price
    otp=random.randint(100000,999999)
    
    if appointment=="" :
        flash("Please enter appointment date and time")
        return redirect(url_for('show_book',id=id))

    service_request=ServiceRequest(user_id=user_id,service_professional_id=professional.id,service_id=service.id,appointment=appointment,address=address,otp=otp)
    db.session.add(service_request)
    db.session.commit()

    service_request_id=ServiceRequest.query.filter_by(user_id=session['user'],service_professional_id=professional.id,service_id=service.id,appointment=appointment,address=address).first()
    transaction=Transaction(user_id=user_id,service_professional_id=professional.id,service_request_id=service_request.id,price=price,date=datetime.now())
    db.session.add(transaction)
    db.session.commit()
    flash("Service booked successfully")
    return redirect(url_for('show_payment',id=transaction.id,service_request_id=service_request.id))


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
        return redirect(url_for('show_home'))
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
    user=User.query.filter_by(username=session['user']).first()
    service_requests=ServiceRequest.query.filter_by(user_id=user.id).all()
    transaction=Transaction.query.filter_by(user_id=user.id).all()
    return render_template("dashboard/user.html",user=user,service_requests=service_requests,transactions=transaction)
    
@app.route('/dashboard/professional')
@login_required
@professional_required
def show_dashboard_professional():
    print("Professional dashboard requested")
    professional=ServiceProfessional.query.filter_by(username=session['user']).first()  
    service=Service.query.filter_by(service_professional_id=professional.id).first()    
    service_requests=ServiceRequest.query.filter_by(service_professional_id=professional.id).all()
    transaction=Transaction.query.filter_by(service_professional_id=professional.id).all()
    return render_template("dashboard/professional.html",professional=professional,service=service,service_requests=service_requests,transactions=transaction)

@app.route('/dashboard/professional/service_request/<int:id>',methods=['POST'])
@login_required
@professional_required
def handle_dashboard_professional(id):
    print("Professional dashboard form submitted")
    transaction=Transaction.query.filter_by(service_request_id=id).first()
    service_request=ServiceRequest.query.get(id)
    updated_status=request.form.get('status')
    otp=request.form.get('OTP')
    if updated_status==service_request.status:
        flash("No changes made")
        return redirect(url_for('show_dashboard_professional'))
    if updated_status=="approved" and service_request.status=="pending":
        service_request.status=updated_status
        db.session.commit()
        flash("Service request approved")
        return redirect(url_for('show_dashboard_professional'))
    if updated_status=="completed" and service_request.status=="approved":
        if str(otp).strip()==str(service_request.otp).strip():
            service_request.status=updated_status
            transaction.status="completed"
            service_request.payment_status="released"
            db.session.commit()
            flash("Service request completed")
            return redirect(url_for('show_dashboard_professional'))
        flash("Invalid OTP")
        return redirect(url_for('show_dashboard_professional'))
    if updated_status=="canceled" and service_request.status=="pending":
        service_request.status=updated_status
        transaction.status="failed"
        service_request.payment_status="refunded"
        db.session.commit()
        flash("Service request canceled")
    if updated_status=="canceled" and service_request.status=="approved":
        service_request.status=updated_status
        transaction.status="refunded"
        service_request.payment_status="refunded"
        db.session.commit()
        flash("Service request canceled")
        return redirect(url_for('show_dashboard_professional'))
    flash("Invalid status change")
    return redirect(url_for('show_dashboard_professional'))

    

@app.route('/dashboard/admin')
@login_required
@admin_required
def show_admin():
    print("Admin page requested")
    categories=Category.query.all()
    professionals=ServiceProfessional.query.all()
    service_requests=ServiceRequest.query.all()
    return render_template("dashboard/admin.html",categories=categories,professionals=professionals,service_requests=service_requests)

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
    reviews=Review.query.filter_by(service_id=services.id).all()
    print(reviews)
    return render_template("view_professional.html",professional=professional,service=services,reviews=reviews)

@app.route('/professional/<int:id>/delete')
@login_required
@admin_required
def delete_professional(id):
    print("Delete professional requested")
    professional = ServiceProfessional.query.get(id)
    service=Service.query.filter_by(service_professional_id=id).first()
    db.session.delete(service)
    db.session.delete(professional)
    db.session.commit()
    flash("Professional deleted successfully")
  
    return redirect(url_for('show_admin'))

@app.route('/service_request/<int:id>')
@login_required
@admin_required
def show_service_request(id):
    print("Service request page requested")
    service_request=ServiceRequest.query.get(id)
    return render_template("service_request/show.html",service_request=service_request)

@app.route('/service_request/<int:id>/edit')
@login_required
@admin_required
def show_edit_service_request(id):
    print("Edit service request page requested")
    service_request=ServiceRequest.query.get(id)
    return render_template("service_request/edit.html",service_request=service_request)

@app.route('/service_request/<int:id>/edit', methods=['POST'])
@login_required
@admin_required
def handle_edit_service_request(id):
    print("Edit service request form submitted")
    status = request.form.get('status')
    service_request = ServiceRequest.query.get(id)
    if status=="":
        flash("Please enter status")
        return redirect(url_for('show_edit_service_request',id=id))
    if service_request.status==status:
        flash("No changes made")
    if service_request.status!=status:
       service_request.status=status
    db.session.commit()
    flash("Service request updated successfully")
    return redirect(url_for('show_admin'))

@app.route('/service_request/<int:id>/delete')
@login_required
@admin_required
def delete_service_request(id):
    print("Delete service request requested")
    service_request = ServiceRequest.query.get(id)
    db.session.delete(service_request)
    db.session.commit()
    flash("Service request deleted successfully")
    return redirect(url_for('show_admin'))

@app.route('/otp/<int:id>',methods=['POST'])
@login_required
@user_required
def show_otp(id):
    print("OTP page requested")
    service_request=ServiceRequest.query.get(id)
    user=User.query.filter_by(username=session['user']).first()
    password=request.form.get('password')
    otp=random.randint(100000,999999)
    service_request.otp=otp
    db.session.commit()
    if password and check_password_hash(user.passhash, password):
        flash("OTP is "+str(otp))
        return redirect(url_for('show_dashboard_user'))
    flash("Invalid password")
    return redirect(url_for('show_dashboard_user'))
        

@app.route('/payment/<int:id>/<int:service_request_id>')
@login_required
@user_required
def show_payment(id,service_request_id):
    print("Payment page requested")
    transaction=Transaction.query.get(id)
    print(transaction)
    return render_template("payment.html",transaction=transaction,service_request_id=service_request_id)

@app.route('/payment/<int:id>/<int:service_request_id>',methods=['POST'])
@login_required
@user_required
def handle_payment(id,service_request_id):
    print("Payment form submitted")
    transaction=Transaction.query.get(id)
    service_request=ServiceRequest.query.get(service_request_id)
    Amount=request.form.get('amount')
    if Amount=="":
        flash("Please enter amount")
        return redirect(url_for('show_payment',id=id,service_request_id=service_request_id))
    transaction_Amount=transaction.price
    if float(Amount)==transaction_Amount:
        transaction.status="pending"
        transaction.service_request.payment_status="held"
        db.session.commit()
        flash("Payment successful! your money is held with us")
        return redirect(url_for('show_dashboard_user'))
    else:
        flash("Amount entered is not the actual amount")
        flash("Payment failed")
        db.session.delete(transaction)
        db.session.delete(service_request)
        db.session.commit()
        return redirect(url_for('show_book',id=service_request.service_id)) 
    
@app.route('/review/<int:id>')
@login_required
@user_required
def add_review(id):
    print("Review page requested")
    service=Service.query.get(id)
    return render_template("review.html",service=service)

@app.route('/review/<int:id>',methods=['POST'])
@login_required
@user_required
def handle_review(id):
    print("Review form submitted")
    service=Service.query.get(id)
    description=request.form.get('review')
    rating=request.form.get('rating')
    print(description,rating)
    if description=="" or rating=="":
        flash("Please enter both description and rating")
        return redirect(url_for('add_review',id=service.id))
    review=Review(service_id=service.id,user_id=User.query.filter_by(username=session['user']).first().id,description=description,rating=rating)
    db.session.add(review)
    db.session.commit()
    flash("Review added successfully")
    return redirect(url_for('show_home'))



