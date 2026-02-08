"""
Al Muslim Engineers - Solar Solutions Web Application
A comprehensive Flask-based ecommerce platform for solar products and services
Serving Rawalpindi, Pakistan
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import random
import json

# Initialize Flask App
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__,
            template_folder=os.path.join(basedir, 'templates'),
            static_folder=os.path.join(basedir, 'static'))
app.config['SECRET_KEY'] = 'al-muslim-engineers-solar-solutions-2024-rawalpindi'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///solar_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Database
db = SQLAlchemy(app)

# Create upload folder if not exists
os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), exist_ok=True)

# ==================== HELPER FUNCTION FOR JSON PARSING ====================

def parse_json(value):
    """Convert JSON string to Python object"""
    if value is None:
        return None
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return None

# ==================== DATABASE MODELS ====================

class User(db.Model):
    """User model for both admin and clients"""
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(20), default='client')  # 'admin' or 'client'
    address = db.Column(db.String(200))
    city = db.Column(db.String(50), default='Rawalpindi')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    applications = db.relationship('MeteringApplication', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    maintenance_requests = db.relationship('MaintenanceRequest', backref='user', lazy=True)
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)

class Product(db.Model):
    """Solar products model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # panel, inverter, battery, controller, mounting, cables
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    image = db.Column(db.String(200))
    specifications = db.Column(db.Text)  # JSON string
    wattage = db.Column(db.Integer)  # For panels
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

class MeteringApplication(db.Model):
    """Net, Gross Metering & Simple Solar Setup Applications"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    application_type = db.Column(db.String(20), nullable=False)  # 'net', 'gross', or 'simple_solar'
    system_capacity = db.Column(db.Float, nullable=False)  # in kW
    consumption_units = db.Column(db.Integer)  # monthly units consumed
    property_type = db.Column(db.String(50))  # residential, commercial, industrial
    property_address = db.Column(db.String(200), nullable=False)
    ownership_type = db.Column(db.String(20), default='owner')  # 'owner' or 'tenant'
    reference_number = db.Column(db.String(20), unique=True)
    status = db.Column(db.String(20), default='pending')  # pending, under_review, approved, rejected, completed
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    documents = db.Column(db.Text)  # JSON string of document paths
    noc_message = db.Column(db.Text)  # NOC message for tenants
    admin_notes = db.Column(db.Text)
    estimated_cost = db.Column(db.Float)
    
    def generate_reference(self):
        """Generate unique reference number"""
        prefixes = {'net': 'NET', 'gross': 'GROSS', 'simple_solar': 'SOL'}
        prefix = prefixes.get(self.application_type, 'APP')
        timestamp = datetime.now().strftime('%Y%m%d')
        random_num = random.randint(1000, 9999)
        return f"{prefix}-{timestamp}-{random_num}"

class Order(db.Model):
    """Product orders model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_number = db.Column(db.String(20), unique=True)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, shipped, delivered, cancelled
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed
    shipping_address = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    """Order items model"""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)

class MaintenanceRequest(db.Model):
    """Maintenance service requests"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    request_type = db.Column(db.String(50), nullable=False)  # cleaning, repair, inspection, upgrade
    system_capacity = db.Column(db.Float)
    installation_date = db.Column(db.Date)
    issue_description = db.Column(db.Text, nullable=False)
    preferred_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending, scheduled, in_progress, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_notes = db.Column(db.Text)

class Feedback(db.Model):
    """Customer feedback model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text, nullable=False)
    service_type = db.Column(db.String(50))  # installation, product, maintenance, general
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GalleryProject(db.Model):
    """Gallery projects model"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    system_capacity = db.Column(db.Float)  # in kW
    completion_date = db.Column(db.Date)
    images = db.Column(db.Text)  # JSON string of image paths
    category = db.Column(db.String(50))  # residential, commercial, industrial
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Cart(db.Model):
    """Shopping cart model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== AI SOLAR RECOMMENDATION SYSTEM ====================

def get_solar_recommendation(monthly_bill, roof_area, property_type):
    """
    AI-based solar system recommendation
    Returns recommended system capacity, estimated savings, and payback period
    """
    # Average electricity rate in Rawalpindi (approximate)
    electricity_rate = 25  # PKR per unit
    
    # Calculate monthly consumption
    monthly_units = monthly_bill / electricity_rate
    
    # Solar panel efficiency factors
    peak_sun_hours = 5.5  # Average for Rawalpindi
    system_loss_factor = 0.8
    
    # Calculate required system capacity
    daily_units = monthly_units / 30
    required_capacity = daily_units / (peak_sun_hours * system_loss_factor)
    
    # Round to nearest standard capacity (1kW to 50kW)
    standard_capacities = [1, 2, 3, 5, 7, 10, 15, 20, 25, 30, 40, 50]
    recommended_capacity = min([c for c in standard_capacities if c >= required_capacity], default=50)
    
    # Check roof area constraint (approx 100 sq ft per kW)
    required_area = recommended_capacity * 100
    if required_area > roof_area:
        recommended_capacity = int(roof_area / 100)
        recommended_capacity = max(1, recommended_capacity)
    
    # Cost estimation (approximate rates in PKR)
    cost_per_kw = 80000  # Average installed cost per kW
    total_cost = recommended_capacity * cost_per_kw
    
    # Savings calculation
    monthly_generation = recommended_capacity * peak_sun_hours * 30 * system_loss_factor
    monthly_savings = monthly_generation * electricity_rate
    annual_savings = monthly_savings * 12
    
    # Payback period
    payback_years = total_cost / annual_savings if annual_savings > 0 else 0
    
    # Carbon offset (approx 1.5 lbs CO2 per kWh, converted to kg)
    annual_carbon_offset = (monthly_generation * 12 * 0.453592) / 1000  # in tonnes
    
    # Eligibility for net metering (> 5kW)
    net_metering_eligible = recommended_capacity >= 5
    
    return {
        'recommended_capacity': recommended_capacity,
        'monthly_consumption': round(monthly_units, 2),
        'estimated_cost': total_cost,
        'monthly_savings': round(monthly_savings, 2),
        'annual_savings': round(annual_savings, 2),
        'payback_period': round(payback_years, 1),
        'carbon_offset': round(annual_carbon_offset, 2),
        'net_metering_eligible': net_metering_eligible,
        'required_area': required_area,
        'monthly_generation': round(monthly_generation, 2)
    }

# ==================== HELPER FUNCTIONS ====================

def login_required(f):
    """Decorator to check if user is logged in"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to check if user is admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.user_type != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def generate_order_number():
    """Generate unique order number"""
    prefix = 'AME'
    timestamp = datetime.now().strftime('%Y%m%d')
    random_num = random.randint(10000, 99999)
    return f"{prefix}-{timestamp}-{random_num}"

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Landing page"""
    featured_products = Product.query.filter_by(is_active=True).limit(6).all()
    gallery_projects = GalleryProject.query.limit(4).all()
    approved_feedbacks = Feedback.query.filter_by(is_approved=True).limit(6).all()
    
    # Parse JSON images for gallery projects
    for project in gallery_projects:
        project.images_list = parse_json(project.images) or []
    
    # Get stats for display
    total_installations = GalleryProject.query.count()
    total_clients = User.query.filter_by(user_type='client').count()
    total_capacity = db.session.query(db.func.sum(GalleryProject.system_capacity)).scalar() or 0
    
    return render_template('index.html', 
                         featured_products=featured_products,
                         gallery_projects=gallery_projects,
                         feedbacks=approved_feedbacks,
                         stats={
                             'installations': total_installations,
                             'clients': total_clients,
                             'capacity': round(total_capacity, 2)
                         })

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        address = request.form.get('address')
        
        # Validation
        if not all([full_name, email, phone, password]):
            flash('All required fields must be filled', 'danger')
            return redirect(url_for('signup'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('signup'))
        
        # Create user
        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            password_hash=generate_password_hash(password),
            address=address,
            city='Rawalpindi',
            user_type='client'
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_type'] = user.user_type
            session['user_name'] = user.full_name
            
            flash(f'Welcome back, {user.full_name}!', 'success')
            
            if user.user_type == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('client_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# ==================== CLIENT DASHBOARD ROUTES ====================

@app.route('/dashboard')
@login_required
def client_dashboard():
    """Client dashboard"""
    user = User.query.get(session['user_id'])
    
    # Get user's applications
    applications = MeteringApplication.query.filter_by(user_id=user.id).order_by(MeteringApplication.submitted_at.desc()).all()
    
    # Get user's orders
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    
    # Get user's maintenance requests
    maintenance = MaintenanceRequest.query.filter_by(user_id=user.id).order_by(MaintenanceRequest.created_at.desc()).all()
    
    # Calculate savings (mock calculation based on applications)
    total_savings = 0
    for app in applications:
        if app.status == 'completed':
            total_savings += app.system_capacity * 5000  # Approximate annual savings
    
    return render_template('client_dashboard.html',
                         user=user,
                         applications=applications,
                         orders=orders,
                         maintenance=maintenance,
                         total_savings=total_savings)

@app.route('/apply-metering', methods=['GET', 'POST'])
@login_required
def apply_metering():
    """Apply for Net or Gross Metering"""
    if request.method == 'POST':
        application_type = request.form.get('application_type')
        system_capacity = float(request.form.get('system_capacity'))
        consumption_units = int(request.form.get('consumption_units', 0))
        property_type = request.form.get('property_type')
        property_address = request.form.get('property_address')
        ownership_type = request.form.get('ownership_type', 'owner')
        noc_message = request.form.get('noc_message', '')
        
        # Validation
        if not all([application_type, system_capacity, property_address]):
            flash('All required fields must be filled', 'danger')
            return redirect(url_for('apply_metering'))
        
        # Check capacity range (1kW to 50kW)
        if system_capacity < 1 or system_capacity > 50:
            flash('System capacity must be between 1kW and 50kW', 'danger')
            return redirect(url_for('apply_metering'))
        
        # Net metering eligibility check (> 5kW)
        if application_type == 'net' and system_capacity < 5:
            flash('Net metering requires system capacity of 5kW or greater', 'danger')
            return redirect(url_for('apply_metering'))
        
        # Handle document uploads
        uploaded_docs = {}
        doc_fields = ['electricity_bill', 'cnic_front', 'cnic_back']
        
        # Owner needs land ownership doc, tenant needs NOC (stamp paper or message)
        if ownership_type == 'owner':
            doc_fields.append('land_ownership')
        else:
            doc_fields.append('noc_document')
        
        for field in doc_fields:
            if field in request.files:
                file = request.files[field]
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    rand = random.randint(1000, 9999)
                    filename = f"{field}_{timestamp}_{rand}_{filename}"
                    filepath = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    uploaded_docs[field] = f"uploads/{filename}"
        
        # Validate required documents
        required_docs = ['electricity_bill', 'cnic_front', 'cnic_back']
        if ownership_type == 'owner':
            required_docs.append('land_ownership')
        # Tenant can provide NOC document OR noc_message
        elif ownership_type == 'tenant' and 'noc_document' not in uploaded_docs and not noc_message.strip():
            flash('Tenants must provide either a NOC document (stamp paper) or a NOC message', 'danger')
            return redirect(url_for('apply_metering'))
        
        missing = [d.replace('_', ' ').title() for d in required_docs if d not in uploaded_docs]
        if missing:
            flash(f'Please upload required documents: {", ".join(missing)}', 'danger')
            return redirect(url_for('apply_metering'))
        
        # Create application
        application = MeteringApplication(
            user_id=session['user_id'],
            application_type=application_type,
            system_capacity=system_capacity,
            consumption_units=consumption_units,
            property_type=property_type,
            property_address=property_address,
            ownership_type=ownership_type,
            documents=json.dumps(uploaded_docs),
            noc_message=noc_message if ownership_type == 'tenant' else None,
            estimated_cost=system_capacity * 80000  # Approximate cost
        )
        
        application.reference_number = application.generate_reference()
        
        db.session.add(application)
        db.session.commit()
        
        flash(f'Application submitted successfully! Reference: {application.reference_number}', 'success')
        return redirect(url_for('client_dashboard'))
    
    return render_template('apply_metering.html')

@app.route('/application-status/<int:app_id>')
@login_required
def application_status(app_id):
    """View application status"""
    application = MeteringApplication.query.get_or_404(app_id)
    
    # Ensure user owns this application
    if application.user_id != session['user_id'] and session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('client_dashboard'))
    
    # Parse JSON documents
    application.docs_dict = parse_json(application.documents) or {}
    
    return render_template('application_status.html', application=application)

# ==================== SIMPLE SOLAR SETUP ROUTE ====================

@app.route('/apply-solar-setup', methods=['GET', 'POST'])
@login_required
def apply_solar_setup():
    """Apply for Simple Solar Setup - requires only CNIC and electricity bill"""
    if request.method == 'POST':
        system_capacity = float(request.form.get('system_capacity', 0))
        property_address = request.form.get('property_address', '')
        property_type = request.form.get('property_type', 'residential')
        consumption_units = int(request.form.get('consumption_units', 0))
        
        # Validation
        if not all([system_capacity, property_address]):
            flash('All required fields must be filled', 'danger')
            return redirect(url_for('apply_solar_setup'))
        
        if system_capacity < 1 or system_capacity > 50:
            flash('System capacity must be between 1kW and 50kW', 'danger')
            return redirect(url_for('apply_solar_setup'))
        
        # Handle document uploads (only CNIC and electricity bill)
        uploaded_docs = {}
        for field in ['electricity_bill', 'cnic_front', 'cnic_back']:
            if field in request.files:
                file = request.files[field]
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    rand = random.randint(1000, 9999)
                    filename = f"{field}_{timestamp}_{rand}_{filename}"
                    filepath = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    uploaded_docs[field] = f"uploads/{filename}"
        
        # Validate required documents
        missing = [d.replace('_', ' ').title() for d in ['electricity_bill', 'cnic_front', 'cnic_back'] if d not in uploaded_docs]
        if missing:
            flash(f'Please upload required documents: {", ".join(missing)}', 'danger')
            return redirect(url_for('apply_solar_setup'))
        
        # Create application
        application = MeteringApplication(
            user_id=session['user_id'],
            application_type='simple_solar',
            system_capacity=system_capacity,
            consumption_units=consumption_units,
            property_type=property_type,
            property_address=property_address,
            ownership_type='owner',
            documents=json.dumps(uploaded_docs),
            estimated_cost=system_capacity * 80000
        )
        
        application.reference_number = application.generate_reference()
        
        db.session.add(application)
        db.session.commit()
        
        flash(f'Solar setup application submitted! Reference: {application.reference_number}', 'success')
        return redirect(url_for('client_dashboard'))
    
    return render_template('apply_solar_setup.html')

# ==================== ECOMMERCE ROUTES ====================

@app.route('/products')
def products():
    """Product catalog"""
    category = request.args.get('category', 'all')
    
    if category == 'all':
        products = Product.query.filter_by(is_active=True).all()
    else:
        products = Product.query.filter_by(category=category, is_active=True).all()
    
    return render_template('products.html', products=products, category=category)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    product = Product.query.get_or_404(product_id)
    related_products = Product.query.filter_by(category=product.category).filter(Product.id != product_id).limit(4).all()
    
    # Parse JSON specifications
    product.specs_dict = parse_json(product.specifications) or {}
    
    return render_template('product_detail.html', product=product, related_products=related_products)

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """Add product to cart"""
    quantity = int(request.form.get('quantity', 1))
    
    # Check if already in cart
    cart_item = Cart.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(user_id=session['user_id'], product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    flash('Product added to cart', 'success')
    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    """Shopping cart"""
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    
    total = 0
    for item in cart_items:
        total += item.product.price * item.quantity
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update-cart/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    """Update cart quantity"""
    quantity = int(request.form.get('quantity', 1))
    cart_item = Cart.query.get_or_404(cart_id)
    
    if cart_item.user_id != session['user_id']:
        flash('Access denied', 'danger')
        return redirect(url_for('cart'))
    
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity
    
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/remove-from-cart/<int:cart_id>')
@login_required
def remove_from_cart(cart_id):
    """Remove item from cart"""
    cart_item = Cart.query.get_or_404(cart_id)
    
    if cart_item.user_id != session['user_id']:
        flash('Access denied', 'danger')
        return redirect(url_for('cart'))
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart', 'info')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout process"""
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    
    if not cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('products'))
    
    # Calculate total
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        shipping_address = request.form.get('shipping_address')
        
        if not shipping_address:
            flash('Please provide shipping address', 'danger')
            return redirect(url_for('checkout'))
        
        # Create order
        order = Order(
            user_id=session['user_id'],
            order_number=generate_order_number(),
            total_amount=total,
            shipping_address=shipping_address
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price
            )
            db.session.add(order_item)
            
            # Update stock
            cart_item.product.stock_quantity -= cart_item.quantity
            
            # Remove from cart
            db.session.delete(cart_item)
        
        db.session.commit()
        
        flash(f'Order placed successfully! Order number: {order.order_number}', 'success')
        return redirect(url_for('order_confirmation', order_id=order.id))
    
    user = User.query.get(session['user_id'])
    return render_template('checkout.html', cart_items=cart_items, total=total, user=user)

@app.route('/order-confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    """Order confirmation page"""
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != session['user_id']:
        flash('Access denied', 'danger')
        return redirect(url_for('client_dashboard'))
    
    return render_template('order_confirmation.html', order=order)

# ==================== MAINTENANCE ROUTES ====================

@app.route('/maintenance', methods=['GET', 'POST'])
@login_required
def maintenance():
    """Maintenance service request"""
    if request.method == 'POST':
        request_type = request.form.get('request_type')
        system_capacity = request.form.get('system_capacity')
        installation_date = request.form.get('installation_date')
        issue_description = request.form.get('issue_description')
        preferred_date = request.form.get('preferred_date')
        
        if not all([request_type, issue_description]):
            flash('Please fill all required fields', 'danger')
            return redirect(url_for('maintenance'))
        
        maintenance_request = MaintenanceRequest(
            user_id=session['user_id'],
            request_type=request_type,
            system_capacity=float(system_capacity) if system_capacity else None,
            installation_date=datetime.strptime(installation_date, '%Y-%m-%d').date() if installation_date else None,
            issue_description=issue_description,
            preferred_date=datetime.strptime(preferred_date, '%Y-%m-%d').date() if preferred_date else None
        )
        
        db.session.add(maintenance_request)
        db.session.commit()
        
        flash('Maintenance request submitted successfully!', 'success')
        return redirect(url_for('client_dashboard'))
    
    return render_template('maintenance.html')

# ==================== FEEDBACK ROUTES ====================

@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    """Submit feedback"""
    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        comment = request.form.get('comment')
        service_type = request.form.get('service_type')
        
        if not all([rating, comment]):
            flash('Please provide rating and comment', 'danger')
            return redirect(url_for('feedback'))
        
        feedback_item = Feedback(
            user_id=session['user_id'],
            rating=rating,
            comment=comment,
            service_type=service_type
        )
        
        db.session.add(feedback_item)
        db.session.commit()
        
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('index'))
    
    return render_template('feedback.html')

# ==================== GALLERY ROUTES ====================

@app.route('/gallery')
def gallery():
    """Project gallery"""
    category = request.args.get('category', 'all')
    
    if category == 'all':
        projects = GalleryProject.query.order_by(GalleryProject.completion_date.desc()).all()
    else:
        projects = GalleryProject.query.filter_by(category=category).order_by(GalleryProject.completion_date.desc()).all()
    
    # Parse JSON images for projects
    for project in projects:
        project.images_list = parse_json(project.images) or []
    
    return render_template('gallery.html', projects=projects, category=category)

@app.route('/gallery/project/<int:project_id>')
def gallery_project_detail(project_id):
    """Gallery project detail"""
    project = GalleryProject.query.get_or_404(project_id)
    # Parse JSON images
    project.images_list = parse_json(project.images) or []
    return render_template('project_detail.html', project=project)

# ==================== AI SOLAR CALCULATOR ROUTE ====================

@app.route('/solar-calculator', methods=['GET', 'POST'])
def solar_calculator():
    """AI Solar Calculator"""
    recommendation = None
    
    if request.method == 'POST':
        monthly_bill = float(request.form.get('monthly_bill', 0))
        roof_area = float(request.form.get('roof_area', 0))
        property_type = request.form.get('property_type', 'residential')
        
        if monthly_bill > 0 and roof_area > 0:
            recommendation = get_solar_recommendation(monthly_bill, roof_area, property_type)
    
    return render_template('solar_calculator.html', recommendation=recommendation)

# ==================== ADMIN DASHBOARD ROUTES ====================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    # Statistics
    total_users = User.query.filter_by(user_type='client').count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    pending_applications = MeteringApplication.query.filter_by(status='pending').count()
    pending_maintenance = MaintenanceRequest.query.filter_by(status='pending').count()
    
    # Recent data
    recent_applications = MeteringApplication.query.order_by(MeteringApplication.submitted_at.desc()).limit(5).all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html',
                         stats={
                             'users': total_users,
                             'products': total_products,
                             'orders': total_orders,
                             'pending_applications': pending_applications,
                             'pending_maintenance': pending_maintenance
                         },
                         recent_applications=recent_applications,
                         recent_orders=recent_orders)

# ==================== ADMIN PRODUCT MANAGEMENT ====================

@app.route('/admin/products')
@admin_required
def admin_products():
    """Admin product management"""
    products = Product.query.all()
    return render_template('admin_products.html', products=products)

@app.route('/admin/product/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    """Add new product"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        price = float(request.form.get('price'))
        stock_quantity = int(request.form.get('stock_quantity'))
        wattage = request.form.get('wattage')
        specifications = request.form.get('specifications')
        
        # Handle image upload
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"{timestamp}_{filename}"
                file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
                image = f"uploads/{filename}"
        
        product = Product(
            name=name,
            description=description,
            category=category,
            price=price,
            stock_quantity=stock_quantity,
            wattage=wattage,
            specifications=specifications,
            image=image
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin_add_product.html')

@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    """Edit product"""
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.category = request.form.get('category')
        product.price = float(request.form.get('price'))
        product.stock_quantity = int(request.form.get('stock_quantity'))
        product.wattage = request.form.get('wattage')
        product.specifications = request.form.get('specifications')
        product.is_active = bool(request.form.get('is_active'))
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"{timestamp}_{filename}"
                file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
                product.image = f"uploads/{filename}"
        
        db.session.commit()
        flash('Product updated successfully', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin_edit_product.html', product=product)

@app.route('/admin/product/delete/<int:product_id>')
@admin_required
def admin_delete_product(product_id):
    """Delete product"""
    product = Product.query.get_or_404(product_id)
    product.is_active = False
    db.session.commit()
    flash('Product deleted successfully', 'success')
    return redirect(url_for('admin_products'))

# ==================== ADMIN APPLICATION MANAGEMENT ====================

@app.route('/admin/applications')
@admin_required
def admin_applications():
    """Manage metering applications"""
    status = request.args.get('status', 'all')
    
    if status == 'all':
        applications = MeteringApplication.query.order_by(MeteringApplication.submitted_at.desc()).all()
    else:
        applications = MeteringApplication.query.filter_by(status=status).order_by(MeteringApplication.submitted_at.desc()).all()
    
    return render_template('admin_applications.html', applications=applications, status=status)

@app.route('/admin/application/<int:app_id>', methods=['GET', 'POST'])
@admin_required
def admin_application_detail(app_id):
    """View and update application"""
    application = MeteringApplication.query.get_or_404(app_id)
    
    if request.method == 'POST':
        application.status = request.form.get('status')
        application.admin_notes = request.form.get('admin_notes')
        application.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Application updated successfully', 'success')
        return redirect(url_for('admin_applications'))
    
    # Parse JSON documents
    application.docs_dict = parse_json(application.documents) or {}
    
    return render_template('admin_application_detail.html', application=application)

# ==================== ADMIN ORDER MANAGEMENT ====================

@app.route('/admin/orders')
@admin_required
def admin_orders():
    """Manage orders"""
    status = request.args.get('status', 'all')
    
    if status == 'all':
        orders = Order.query.order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.filter_by(status=status).order_by(Order.created_at.desc()).all()
    
    return render_template('admin_orders.html', orders=orders, status=status)

@app.route('/admin/order/<int:order_id>', methods=['GET', 'POST'])
@admin_required
def admin_order_detail(order_id):
    """View and update order"""
    order = Order.query.get_or_404(order_id)
    
    if request.method == 'POST':
        order.status = request.form.get('status')
        order.payment_status = request.form.get('payment_status')
        
        db.session.commit()
        flash('Order updated successfully', 'success')
        return redirect(url_for('admin_orders'))
    
    return render_template('admin_order_detail.html', order=order)

# ==================== ADMIN MAINTENANCE MANAGEMENT ====================

@app.route('/admin/maintenance')
@admin_required
def admin_maintenance():
    """Manage maintenance requests"""
    status = request.args.get('status', 'all')
    
    if status == 'all':
        requests = MaintenanceRequest.query.order_by(MaintenanceRequest.created_at.desc()).all()
    else:
        requests = MaintenanceRequest.query.filter_by(status=status).order_by(MaintenanceRequest.created_at.desc()).all()
    
    return render_template('admin_maintenance.html', requests=requests, status=status)

@app.route('/admin/maintenance/<int:req_id>', methods=['GET', 'POST'])
@admin_required
def admin_maintenance_detail(req_id):
    """View and update maintenance request"""
    maintenance_req = MaintenanceRequest.query.get_or_404(req_id)
    
    if request.method == 'POST':
        maintenance_req.status = request.form.get('status')
        maintenance_req.admin_notes = request.form.get('admin_notes')
        
        db.session.commit()
        flash('Maintenance request updated successfully', 'success')
        return redirect(url_for('admin_maintenance'))
    
    return render_template('admin_maintenance_detail.html', request=maintenance_req)

# ==================== ADMIN GALLERY MANAGEMENT ====================

@app.route('/admin/gallery')
@admin_required
def admin_gallery():
    """Manage gallery projects"""
    projects = GalleryProject.query.order_by(GalleryProject.created_at.desc()).all()
    # Parse JSON images for projects
    for project in projects:
        project.images_list = parse_json(project.images) or []
    return render_template('admin_gallery.html', projects=projects)

@app.route('/admin/gallery/add', methods=['GET', 'POST'])
@admin_required
def admin_add_gallery():
    """Add gallery project"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location')
        system_capacity = float(request.form.get('system_capacity'))
        completion_date = request.form.get('completion_date')
        category = request.form.get('category')
        
        # Handle multiple images
        images = []
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file.filename:
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    filename = f"{timestamp}_{random.randint(1000,9999)}_{filename}"
                    file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
                    images.append(f"uploads/{filename}")
        
        project = GalleryProject(
            title=title,
            description=description,
            location=location,
            system_capacity=system_capacity,
            completion_date=datetime.strptime(completion_date, '%Y-%m-%d').date() if completion_date else None,
            category=category,
            images=json.dumps(images)
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash('Gallery project added successfully', 'success')
        return redirect(url_for('admin_gallery'))
    
    return render_template('admin_add_gallery.html')

@app.route('/admin/gallery/edit/<int:project_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_gallery(project_id):
    """Edit gallery project"""
    project = GalleryProject.query.get_or_404(project_id)
    
    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.location = request.form.get('location')
        project.system_capacity = float(request.form.get('system_capacity'))
        completion_date = request.form.get('completion_date')
        project.completion_date = datetime.strptime(completion_date, '%Y-%m-%d').date() if completion_date else None
        project.category = request.form.get('category')
        
        # Handle new images
        if 'images' in request.files:
            files = request.files.getlist('images')
            existing_images = json.loads(project.images) if project.images else []
            for file in files:
                if file.filename:
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    filename = f"{timestamp}_{random.randint(1000,9999)}_{filename}"
                    file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
                    existing_images.append(f"uploads/{filename}")
            project.images = json.dumps(existing_images)
        
        db.session.commit()
        flash('Gallery project updated successfully', 'success')
        return redirect(url_for('admin_gallery'))
    
    # Parse JSON images
    project.images_list = parse_json(project.images) or []
    
    return render_template('admin_edit_gallery.html', project=project)

@app.route('/admin/gallery/delete/<int:project_id>')
@admin_required
def admin_delete_gallery(project_id):
    """Delete gallery project"""
    project = GalleryProject.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Gallery project deleted successfully', 'success')
    return redirect(url_for('admin_gallery'))

# ==================== ADMIN FEEDBACK MANAGEMENT ====================

@app.route('/admin/feedback')
@admin_required
def admin_feedback():
    """Manage feedback"""
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template('admin_feedback.html', feedbacks=feedbacks)

@app.route('/admin/feedback/approve/<int:feedback_id>')
@admin_required
def admin_approve_feedback(feedback_id):
    """Approve feedback"""
    feedback = Feedback.query.get_or_404(feedback_id)
    feedback.is_approved = True
    db.session.commit()
    flash('Feedback approved', 'success')
    return redirect(url_for('admin_feedback'))

# ==================== API ROUTES ====================

@app.route('/api/application-status/<ref_number>')
def api_application_status(ref_number):
    """API to check application status"""
    application = MeteringApplication.query.filter_by(reference_number=ref_number).first()
    
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    return jsonify({
        'reference_number': application.reference_number,
        'type': application.application_type,
        'capacity': application.system_capacity,
        'status': application.status,
        'submitted_at': application.submitted_at.strftime('%Y-%m-%d'),
        'updated_at': application.updated_at.strftime('%Y-%m-%d')
    })

@app.route('/api/solar-calculator', methods=['POST'])
def api_solar_calculator():
    """API endpoint for solar calculator"""
    data = request.get_json()
    monthly_bill = float(data.get('monthly_bill', 0))
    roof_area = float(data.get('roof_area', 0))
    property_type = data.get('property_type', 'residential')
    
    recommendation = get_solar_recommendation(monthly_bill, roof_area, property_type)
    
    return jsonify(recommendation)

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    db.session.rollback()
    return render_template('500.html'), 500

# ==================== CONTEXT PROCESSORS ====================

@app.context_processor
def inject_globals():
    """Inject global variables to templates"""
    return {
        'current_year': datetime.now().year,
        'company_name': 'Al Muslim Engineers',
        'company_tagline': 'Powering Pakistan with Clean Energy'
    }

# ==================== INITIALIZE DATABASE ====================

def init_db():
    """Initialize database with default data"""
    with app.app_context():
        db.create_all()
        
        # Add new columns if they don't exist (migration for existing databases)
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            if 'metering_application' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('metering_application')]
                with db.engine.connect() as conn:
                    if 'ownership_type' not in columns:
                        conn.execute(text("ALTER TABLE metering_application ADD COLUMN ownership_type VARCHAR(20) DEFAULT 'owner'"))
                    if 'noc_message' not in columns:
                        conn.execute(text("ALTER TABLE metering_application ADD COLUMN noc_message TEXT"))
                    conn.commit()
        except Exception as e:
            print(f"Migration note: {e}")
        
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@almuslim.com').first()
        if not admin:
            admin = User(
                full_name='Administrator',
                email='admin@almuslim.com',
                phone='+92-300-1234567',
                password_hash=generate_password_hash('admin123'),
                user_type='admin',
                address='Main Office, Rawalpindi'
            )
            db.session.add(admin)
        
        # Add sample products if none exist
        if Product.query.count() == 0:
            sample_products = [
                Product(
                    name='550W Mono PERC Solar Panel',
                    description='High-efficiency monocrystalline solar panel with PERC technology. Ideal for residential and commercial installations.',
                    category='panel',
                    price=28500,
                    stock_quantity=100,
                    image='solar-panel-1.jpg',
                    wattage=550,
                    specifications='{"efficiency": "21.5%", "warranty": "25 years", "dimensions": "2279x1134x35mm"}'
                ),
                Product(
                    name='5kW Hybrid Solar Inverter',
                    description='Advanced hybrid inverter with MPPT charge controller. Supports grid-tie and off-grid operation.',
                    category='inverter',
                    price=185000,
                    stock_quantity=25,
                    image='inverter-1.jpg',
                    specifications='{"capacity": "5kW", "efficiency": "97.5%", "warranty": "5 years"}'
                ),
                Product(
                    name='10kWh Lithium Battery',
                    description='High-capacity lithium iron phosphate battery for solar energy storage. Long lifecycle and safe operation.',
                    category='battery',
                    price=450000,
                    stock_quantity=15,
                    image='battery-1.jpg',
                    specifications='{"capacity": "10kWh", "cycles": "6000+", "warranty": "10 years"}'
                ),
                Product(
                    name='60A MPPT Charge Controller',
                    description='Maximum Power Point Tracking charge controller for optimal solar panel performance.',
                    category='controller',
                    price=35000,
                    stock_quantity=40,
                    image='controller-1.jpg',
                    specifications='{"current": "60A", "voltage": "150V", "efficiency": "99.5%"}'
                ),
                Product(
                    name='Solar Mounting Structure',
                    description='Aluminum mounting structure for rooftop solar installations. Corrosion-resistant and durable.',
                    category='mounting',
                    price=8500,
                    stock_quantity=200,
                    image='mounting-1.jpg',
                    specifications='{"material": "Aluminum 6005-T5", "warranty": "10 years"}'
                ),
                Product(
                    name='Solar DC Cable Kit',
                    description='Professional grade DC cables and MC4 connectors for solar installations.',
                    category='cables',
                    price=4500,
                    stock_quantity=150,
                    image='cables-1.jpg',
                    specifications='{"gauge": "4mm²", "length": "50 meters", "rating": "1000V DC"}'
                )
            ]
            db.session.add_all(sample_products)
        
        # Add sample gallery projects if none exist
        if GalleryProject.query.count() == 0:
            sample_projects = [
                GalleryProject(
                    title='5kW Residential Installation',
                    description='Complete solar system installation for a 3-bedroom house in Bahria Town.',
                    location='Bahria Town, Rawalpindi',
                    system_capacity=5,
                    completion_date=datetime(2024, 1, 15).date(),
                    category='residential',
                    images=json.dumps(['project-1.jpg'])
                ),
                GalleryProject(
                    title='50kW Commercial Solar Farm',
                    description='Large-scale solar installation for industrial facility.',
                    location='Industrial Area, Rawalpindi',
                    system_capacity=50,
                    completion_date=datetime(2024, 2, 20).date(),
                    category='industrial',
                    images=json.dumps(['project-2.jpg'])
                ),
                GalleryProject(
                    title='10kW Modern Home System',
                    description='Premium solar installation with battery backup for modern residence.',
                    location='DHA Phase 2, Rawalpindi',
                    system_capacity=10,
                    completion_date=datetime(2024, 3, 10).date(),
                    category='residential',
                    images=json.dumps(['project-3.jpg'])
                )
            ]
            db.session.add_all(sample_projects)
        
        db.session.commit()
        print("Database initialized successfully!")

# Run initialization
init_db()

# ==================== MAIN ENTRY POINT ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
