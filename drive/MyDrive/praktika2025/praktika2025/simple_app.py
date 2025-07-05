from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'simple-cafe-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///simple_cafe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Отношения
    menu_items = db.relationship('MenuItem', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<MenuItem {self.name}>'

class Table(db.Model):
    __tablename__ = 'tables'
    
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    is_occupied = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Table {self.number}>'

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('tables.id'), nullable=False)
    customer_name = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, preparing, ready, completed
    total_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    table = db.relationship('Table', backref='orders')
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.id}>'

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    menu_item = db.relationship('MenuItem', backref='order_items')
    
    @property
    def total_price(self):
        return self.quantity * self.price

@app.route('/')
def index():
    total_orders = Order.query.count()
    active_orders = Order.query.filter(Order.status.in_(['pending', 'preparing', 'ready'])).count()
    available_tables = Table.query.filter_by(is_occupied=False).count()
    
    today = date.today()
    today_orders = Order.query.filter(db.func.date(Order.created_at) == today).count()
    
    today_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(
        db.func.date(Order.created_at) == today,
        Order.status == 'completed'
    ).scalar() or 0
    
    # Последние заказы
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('simple/index.html',
                         total_orders=total_orders,
                         active_orders=active_orders,
                         available_tables=available_tables,
                         today_orders=today_orders,
                         today_revenue=today_revenue,
                         recent_orders=recent_orders)

@app.route('/menu')
def menu():
    categories = Category.query.all()
    menu_items = MenuItem.query.all()
    return render_template('simple/menu.html', categories=categories, menu_items=menu_items)

@app.route('/menu/add', methods=['GET', 'POST'])
def add_menu_item():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        category_id = int(request.form['category_id'])
        
        menu_item = MenuItem(
            name=name,
            description=description,
            price=price,
            category_id=category_id
        )
        
        db.session.add(menu_item)
        db.session.commit()
        
        flash('Блюдо успешно добавлено!', 'success')
        return redirect(url_for('menu'))
    
    categories = Category.query.all()
    return render_template('simple/add_menu_item.html', categories=categories)

@app.route('/menu/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.price = float(request.form['price'])
        item.category_id = int(request.form['category_id'])
        item.is_available = 'is_available' in request.form
        
        db.session.commit()
        
        flash('Блюдо успешно обновлено!', 'success')
        return redirect(url_for('menu'))
    
    categories = Category.query.all()
    return render_template('simple/edit_menu_item.html', item=item, categories=categories)

@app.route('/categories')
def categories():
    categories = Category.query.all()
    return render_template('simple/categories.html', categories=categories)

@app.route('/categories/add', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        
        flash('Категория успешно добавлена!', 'success')
        return redirect(url_for('categories'))
    
    return render_template('simple/add_category.html')

@app.route('/tables')
def tables():
    tables = Table.query.order_by(Table.number).all()
    return render_template('simple/tables.html', tables=tables)

@app.route('/tables/add', methods=['GET', 'POST'])
def add_table():
    if request.method == 'POST':
        number = int(request.form['number'])
        capacity = int(request.form['capacity'])
        
        existing_table = Table.query.filter_by(number=number).first()
        if existing_table:
            flash('Стол с таким номером уже существует!', 'error')
            return redirect(url_for('add_table'))
        
        table = Table(number=number, capacity=capacity)
        db.session.add(table)
        db.session.commit()
        
        flash('Стол успешно добавлен!', 'success')
        return redirect(url_for('tables'))
    
    return render_template('simple/add_table.html')

@app.route('/orders')
def orders():
    status_filter = request.args.get('status', 'all')
    
    query = Order.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    orders = query.order_by(Order.created_at.desc()).all()
    return render_template('simple/orders.html', orders=orders, status_filter=status_filter)

@app.route('/orders/new', methods=['GET', 'POST'])
def new_order():
    if request.method == 'POST':
        table_id = int(request.form['table_id'])
        customer_name = request.form.get('customer_name', '')
        
        order = Order(table_id=table_id, customer_name=customer_name)
        db.session.add(order)
        db.session.flush()  # Получаем ID заказа
        
        total_amount = 0
        for key in request.form.keys():
            if key.startswith('quantity_'):
                menu_item_id = int(key.split('_')[1])
                quantity = int(request.form[key])
                
                if quantity > 0:
                    menu_item = MenuItem.query.get(menu_item_id)
                    order_item = OrderItem(
                        order_id=order.id,
                        menu_item_id=menu_item_id,
                        quantity=quantity,
                        price=menu_item.price
                    )
                    db.session.add(order_item)
                    total_amount += menu_item.price * quantity
        
        order.total_amount = total_amount
        
        table = Table.query.get(table_id)
        table.is_occupied = True
        
        db.session.commit()
        
        flash('Заказ успешно создан!', 'success')
        return redirect(url_for('order_details', order_id=order.id))
    
    available_tables = Table.query.filter_by(is_occupied=False).all()
    categories = Category.query.all()
    menu_items = MenuItem.query.filter_by(is_available=True).all()
    
    return render_template('simple/new_order.html',
                         available_tables=available_tables,
                         categories=categories,
                         menu_items=menu_items)

@app.route('/orders/<int:order_id>')
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('simple/order_details.html', order=order)

@app.route('/orders/<int:order_id>/update_status', methods=['POST'])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form['status']
    
    order.status = new_status
    
    if new_status == 'completed':
        order.table.is_occupied = False
    
    db.session.commit()
    
    flash('Статус заказа обновлен!', 'success')
    return redirect(url_for('order_details', order_id=order_id))

@app.route('/reports')
def reports():
    
    from datetime import timedelta
    
    week_ago = datetime.utcnow() - timedelta(days=7)
    week_sales = db.session.query(
        db.func.date(Order.created_at).label('date'),
        db.func.sum(Order.total_amount).label('total'),
        db.func.count(Order.id).label('orders_count')
    ).filter(
        Order.created_at >= week_ago,
        Order.status == 'completed'
    ).group_by(
        db.func.date(Order.created_at)
    ).order_by('date').all()
    
    popular_items = db.session.query(
        MenuItem.name,
        db.func.sum(OrderItem.quantity).label('total_ordered'),
        db.func.sum(OrderItem.quantity * OrderItem.price).label('total_revenue')
    ).join(OrderItem).join(Order).filter(
        Order.status == 'completed'
    ).group_by(MenuItem.id).order_by(
        db.func.sum(OrderItem.quantity).desc()
    ).limit(5).all()
    
    return render_template('simple/reports.html',
                         week_sales=week_sales,
                         popular_items=popular_items)

@app.route('/api/menu')
def api_menu():
    categories = Category.query.all()
    menu_data = []
    
    for category in categories:
        items = MenuItem.query.filter_by(category_id=category.id, is_available=True).all()
        menu_data.append({
            'category': {
                'id': category.id,
                'name': category.name,
                'description': category.description
            },
            'items': [{
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': item.price
            } for item in items]
        })
    
    return jsonify(menu_data)

@app.route('/api/tables/status')
def api_tables_status():
    tables = Table.query.all()
    return jsonify([{
        'id': table.id,
        'number': table.number,
        'capacity': table.capacity,
        'is_occupied': table.is_occupied
    } for table in tables])

def init_sample_data():
    if Category.query.count() > 0:
        return
    
    categories = [
        Category(name='Горячие блюда', description='Основные блюда'),
        Category(name='Супы', description='Первые блюда'),
        Category(name='Салаты', description='Свежие салаты'),
        Category(name='Напитки', description='Горячие и холодные напитки'),
        Category(name='Десерты', description='Сладкие блюда')
    ]
    
    for category in categories:
        db.session.add(category)
    
    db.session.commit()
    
    menu_items = [
        MenuItem(name='Борщ', price=150, category_id=2, description='Традиционный борщ'),
        MenuItem(name='Солянка', price=180, category_id=2, description='Мясная солянка'),
        MenuItem(name='Салат Цезарь', price=250, category_id=3, description='Салат с курицей'),
        MenuItem(name='Котлета', price=200, category_id=1, description='Мясная котлета'),
        MenuItem(name='Кофе', price=80, category_id=4, description='Черный кофе'),
        MenuItem(name='Чай', price=60, category_id=4, description='Черный чай'),
        MenuItem(name='Мороженое', price=120, category_id=5, description='Ванильное мороженое'),
    ]
    
    for item in menu_items:
        db.session.add(item)
    
    tables = [
        Table(number=1, capacity=2),
        Table(number=2, capacity=4),
        Table(number=3, capacity=6),
        Table(number=4, capacity=2),
        Table(number=5, capacity=4),
    ]
    
    for table in tables:
        db.session.add(table)
    
    db.session.commit()
    print("Тестовые данные созданы!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_sample_data()
    
    print("=" * 50)
    print("ПРОСТАЯ СИСТЕМА УПРАВЛЕНИЯ КАФЕ")
    print("Адрес: http://localhost:5000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
