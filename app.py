from flask import Flask, send_file
from flask import render_template,request,redirect,session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import io

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://farm_test_user:KcAMdxzOVawCoypFuvWwLpiKntHD1v9B@dpg-crf8snbgbbvc73c0nvk0-a.oregon-postgres.render.com/farm_test"

db = SQLAlchemy(app)

class Farmers(db.Model):
    farmer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(5), nullable=False)
    mobile_number = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    gstno = db.Column(db.String(20), unique=True, nullable=True)
    password = db.Column(db.String, nullable=False)
    address = db.Column(db.String(200), nullable=False)  # Increased length for address
    products = db.relationship('Products', backref='farmer', lazy=True)
    contracts = db.relationship('Contracts', foreign_keys='Contracts.farmer_id', backref='farmer', lazy=True)

    def __repr__(self):
        return f'<Farmer {self.name}>'

class Buyers(db.Model):
    buyer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(5), nullable=False)
    mobile_number = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    gstno = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    address = db.Column(db.String(200), nullable=False)  # Increased length for address
    contracts = db.relationship('Contracts', foreign_keys='Contracts.buyer_id', backref='buyer', lazy=True)

    def __repr__(self):
        return f'<Buyer {self.name}>'

class Products(db.Model):
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.farmer_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(100), nullable=False)
    product_img = db.Column(db.LargeBinary, nullable=False)
    def __repr__(self):
        return f'<Product {self.name}>'

@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        farmer_id = request.form['farmer_id']
        name = request.form['name']
        quantity = request.form['quantity']
        product_img = request.files['product_img'].read()  # Read the image data
        
        # Create and save the product instance
        new_product = Products(
            farmer_id=int(farmer_id),
            name=name,
            quantity=quantity,
            product_img=product_img
        )
        db.session.add(new_product)
        db.session.commit()
        
        return render_template('add_product.html')

    return render_template('add_product.html')


@app.route('/add-farmer', methods=['GET', 'POST'])
def add_farmer():
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        mobile_number = request.form['mobile_number']
        email = request.form.get('email')  # email is optional
        gstno = request.form.get('gstno')  # gstno is optional
        password = request.form['password']
        address = request.form['address']
        
        # Create and save the farmer instance
        new_farmer = Farmers(
            name=name,
            gender=gender,
            mobile_number=mobile_number,
            email=email,
            gstno=gstno,
            password=password,
            address=address
        )
        db.session.add(new_farmer)
        db.session.commit()
        
        return render_template('add_farmer.html')

    return render_template('add_farmer.html')

class Contracts(db.Model):
    contract_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Added contract_id as primary key
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.buyer_id'), nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.farmer_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<Contract Buyer: {self.buyer_id}, Farmer: {self.farmer_id}, Product: {self.product_id}>'

# Create the database and tables
with app.app_context():
    db.create_all()


@app.route("/")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/save", methods=['POST'])
def save():
    username = request.form['username']
    password = request.form['password']

    data = Credentials(
        name=username,
        password=password
    )

    db.session.add(data)
    db.session.commit()

    return render_template("login.html")

@app.route("/check", methods=['POST'])
def check_credentials():
    username = request.form['username']
    password = request.form['password']

    user = Credentials.query.filter_by(name=username).first()
    if user and user.password == password:
        return render_template("success.html")
    else:
        return render_template("failure.html")

@app.route('/dashboard')
def datas():
    all_datas = Products.query.all()
    products_with_farmer_names = []

    for record in all_datas:
        farmer = Farmers.query.get(record.farmer_id)
        farmer_name = farmer.name if farmer else 'Unknown'
        product_details = {
            'product': record,
            'farmer_name': farmer_name
        }
        products_with_farmer_names.append(product_details)

    return render_template('dashboard.html', datas=products_with_farmer_names)

@app.route('/farmers')
def list_farmers():
    farmers = Farmers.query.all()  # Query to get all farmers
    return render_template('farmers.html', farmers=farmers)

@app.route('/product_image/<int:product_id>')
def product_image(product_id):
    product = Products.query.get_or_404(product_id)
    image = io.BytesIO(product.product_img)
    return send_file(image, mimetype='image/jpeg')  # Adjust mimetype based on your image format




