import os
import zipfile

# Структура проекта — все файлы с содержимым
files = {}

# ============================================================
# config.py
# ============================================================
files['auto_salon_crm/config.py'] = '''import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'auto-salon-secret-key-2024'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'autosalon.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
'''

# ============================================================
# models.py
# ============================================================
files['auto_salon_crm/models.py'] = '''from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='client')
    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    orders = db.relationship('Order', backref='client', lazy=True, foreign_keys='Order.client_id')
    managed_orders = db.relationship('Order', backref='manager', lazy=True, foreign_keys='Order.manager_id')
    service_requests = db.relationship('ServiceRequest', backref='client', lazy=True, foreign_keys='ServiceRequest.client_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    ROLES = {
        'client': 'Клиент',
        'sales': 'Отдел продаж',
        'finance': 'Финансовый отдел',
        'logistics': 'Логистика и склад',
        'service': 'Сервис и тех. служба',
        'management': 'Руководство'
    }

    @property
    def role_display(self):
        return self.ROLES.get(self.role, self.role)


class Car(db.Model):
    __tablename__ = 'cars'
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(30), nullable=False)
    vin = db.Column(db.String(17), unique=True, nullable=False)
    engine_type = db.Column(db.String(30), nullable=False)
    engine_volume = db.Column(db.Float)
    horsepower = db.Column(db.Integer)
    transmission = db.Column(db.String(20), nullable=False)
    drive_type = db.Column(db.String(20))
    mileage = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)
    purchase_price = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='in_stock')
    description = db.Column(db.Text)
    image_url = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship('Order', backref='car', lazy=True)
    service_requests = db.relationship('ServiceRequest', backref='car', lazy=True)

    STATUS_CHOICES = {
        'in_stock': 'На складе',
        'reserved': 'Зарезервирован',
        'sold': 'Продан',
        'in_transit': 'В пути',
        'in_service': 'На обслуживании'
    }

    @property
    def status_display(self):
        return self.STATUS_CHOICES.get(self.status, self.status)

    @property
    def full_name(self):
        return f"{self.brand} {self.model} ({self.year})"


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    status = db.Column(db.String(30), default='new')
    total_price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0)
    final_price = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(30))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    payments = db.relationship('Payment', backref='order', lazy=True)

    STATUS_CHOICES = {
        'new': 'Новый',
        'processing': 'В обработке',
        'approved': 'Одобрен',
        'payment_pending': 'Ожидает оплаты',
        'paid': 'Оплачен',
        'completed': 'Завершён',
        'cancelled': 'Отменён'
    }

    @property
    def status_display(self):
        return self.STATUS_CHOICES.get(self.status, self.status)


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(20), default='pending')
    payment_date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    created_by = db.relationship('User', foreign_keys=[created_by_id])

    TYPE_CHOICES = {
        'cash': 'Наличные',
        'card': 'Банковская карта',
        'transfer': 'Банковский перевод',
        'credit': 'Кредит',
        'leasing': 'Лизинг'
    }

    STATUS_CHOICES = {
        'pending': 'Ожидает',
        'completed': 'Проведён',
        'cancelled': 'Отменён',
        'refunded': 'Возврат'
    }

    @property
    def type_display(self):
        return self.TYPE_CHOICES.get(self.payment_type, self.payment_type)

    @property
    def status_display(self):
        return self.STATUS_CHOICES.get(self.status, self.status)


class Delivery(db.Model):
    __tablename__ = 'deliveries'
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    supplier = db.Column(db.String(150), nullable=False)
    expected_date = db.Column(db.Date, nullable=False)
    actual_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='planned')
    tracking_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    car = db.relationship('Car', backref='deliveries')
    created_by = db.relationship('User', foreign_keys=[created_by_id])

    STATUS_CHOICES = {
        'planned': 'Запланирована',
        'in_transit': 'В пути',
        'delivered': 'Доставлена',
        'cancelled': 'Отменена'
    }

    @property
    def status_display(self):
        return self.STATUS_CHOICES.get(self.status, self.status)


class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=True)
    service_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='new')
    priority = db.Column(db.String(10), default='normal')
    estimated_cost = db.Column(db.Float)
    actual_cost = db.Column(db.Float)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    scheduled_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    car_vin = db.Column(db.String(17))

    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_services')

    SERVICE_TYPES = {
        'maintenance': 'Техническое обслуживание',
        'repair': 'Ремонт',
        'diagnostics': 'Диагностика',
        'bodywork': 'Кузовные работы',
        'tire': 'Шиномонтаж',
        'detailing': 'Детейлинг',
        'warranty': 'Гарантийный ремонт',
        'pre_sale': 'Предпродажная подготовка'
    }

    STATUS_CHOICES = {
        'new': 'Новая',
        'accepted': 'Принята',
        'in_progress': 'В работе',
        'waiting_parts': 'Ожидание запчастей',
        'completed': 'Выполнена',
        'cancelled': 'Отменена'
    }

    PRIORITY_CHOICES = {
        'low': 'Низкий',
        'normal': 'Обычный',
        'high': 'Высокий',
        'urgent': 'Срочный'
    }

    @property
    def service_type_display(self):
        return self.SERVICE_TYPES.get(self.service_type, self.service_type)

    @property
    def status_display(self):
        return self.STATUS_CHOICES.get(self.status, self.status)

    @property
    def priority_display(self):
        return self.PRIORITY_CHOICES.get(self.priority, self.priority)
'''

# ============================================================
# decorators.py
# ============================================================
files['auto_salon_crm/decorators.py'] = '''from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Пожалуйста, войдите в систему.', 'warning')
                return redirect(url_for('login'))
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
'''

# ============================================================
# init_db.py
# ============================================================
files['auto_salon_crm/init_db.py'] = '''from app import create_app
from models import db, User, Car


def init_database():
    app = create_app()
    with app.app_context():
        db.create_all()

        if User.query.first():
            print("База данных уже инициализирована.")
            return

        users = [
            User(username='admin', email='admin@autosalon.ru',
                 full_name='Иванов Иван Иванович', phone='+7(900)111-11-11', role='management'),
            User(username='sales1', email='sales@autosalon.ru',
                 full_name='Петров Пётр Петрович', phone='+7(900)222-22-22', role='sales'),
            User(username='finance1', email='finance@autosalon.ru',
                 full_name='Сидорова Анна Михайловна', phone='+7(900)333-33-33', role='finance'),
            User(username='logistics1', email='logistics@autosalon.ru',
                 full_name='Козлов Дмитрий Алексеевич', phone='+7(900)444-44-44', role='logistics'),
            User(username='service1', email='service@autosalon.ru',
                 full_name='Николаев Алексей Сергеевич', phone='+7(900)555-55-55', role='service'),
            User(username='client1', email='client@mail.ru',
                 full_name='Морозова Елена Владимировна', phone='+7(900)666-66-66', role='client'),
            User(username='client2', email='client2@mail.ru',
                 full_name='Волков Артём Игоревич', phone='+7(900)777-77-77', role='client'),
        ]

        for user in users:
            user.set_password('password123')
            db.session.add(user)

        cars = [
            Car(brand='Toyota', model='Camry', year=2024, color='Белый',
                vin='JTD00000000000001', engine_type='Бензин', engine_volume=2.5,
                horsepower=200, transmission='Автомат', drive_type='Передний',
                mileage=0, price=3200000, purchase_price=2800000, status='in_stock',
                description='Новый седан бизнес-класса с полным пакетом опций.'),
            Car(brand='BMW', model='X5', year=2024, color='Чёрный',
                vin='WBA00000000000002', engine_type='Дизель', engine_volume=3.0,
                horsepower=249, transmission='Автомат', drive_type='Полный',
                mileage=0, price=7500000, purchase_price=6500000, status='in_stock',
                description='Премиальный кроссовер с дизельным двигателем.'),
            Car(brand='Kia', model='K5', year=2024, color='Серый',
                vin='KNA00000000000003', engine_type='Бензин', engine_volume=2.5,
                horsepower=194, transmission='Автомат', drive_type='Передний',
                mileage=0, price=2700000, purchase_price=2300000, status='in_stock',
                description='Стильный седан D-класса с отличной комплектацией.'),
            Car(brand='Hyundai', model='Tucson', year=2024, color='Синий',
                vin='KMH00000000000004', engine_type='Бензин', engine_volume=2.0,
                horsepower=150, transmission='Автомат', drive_type='Полный',
                mileage=0, price=2900000, purchase_price=2500000, status='in_stock',
                description='Компактный кроссовер с полным приводом.'),
            Car(brand='Mercedes-Benz', model='E-Class', year=2023, color='Серебристый',
                vin='WDB00000000000005', engine_type='Бензин', engine_volume=2.0,
                horsepower=197, transmission='Автомат', drive_type='Задний',
                mileage=5000, price=6000000, purchase_price=5200000, status='in_stock',
                description='Демонстрационный автомобиль в идеальном состоянии.'),
            Car(brand='Volkswagen', model='Tiguan', year=2024, color='Белый',
                vin='WVW00000000000006', engine_type='Бензин', engine_volume=2.0,
                horsepower=180, transmission='Автомат', drive_type='Полный',
                mileage=0, price=3100000, purchase_price=2700000, status='in_stock',
                description='Популярный семейный кроссовер.'),
            Car(brand='Audi', model='A6', year=2024, color='Чёрный',
                vin='WAU00000000000007', engine_type='Бензин', engine_volume=2.0,
                horsepower=245, transmission='Автомат', drive_type='Полный',
                mileage=0, price=5800000, purchase_price=5000000, status='in_transit',
                description='Представительский седан нового поколения.'),
            Car(brand='Skoda', model='Octavia', year=2024, color='Красный',
                vin='TMB00000000000008', engine_type='Бензин', engine_volume=1.4,
                horsepower=150, transmission='Автомат', drive_type='Передний',
                mileage=0, price=2200000, purchase_price=1900000, status='in_stock',
                description='Надёжный и практичный лифтбек.'),
            Car(brand='Toyota', model='RAV4', year=2024, color='Зелёный',
                vin='JTD00000000000009', engine_type='Гибрид', engine_volume=2.5,
                horsepower=222, transmission='Вариатор', drive_type='Полный',
                mileage=0, price=3500000, purchase_price=3000000, status='in_stock',
                description='Гибридный кроссовер с экономичным расходом.'),
            Car(brand='Lexus', model='RX', year=2024, color='Бежевый',
                vin='JTJ00000000000010', engine_type='Гибрид', engine_volume=2.5,
                horsepower=308, transmission='Вариатор', drive_type='Полный',
                mileage=0, price=7200000, purchase_price=6300000, status='in_stock',
                description='Премиальный гибридный кроссовер.'),
        ]

        for car in cars:
            db.session.add(car)

        db.session.commit()
        print("База данных успешно инициализирована!")
        print("")
        print("=== Учётные записи для входа ===")
        print("Руководство:    admin / password123")
        print("Отдел продаж:   sales1 / password123")
        print("Финансы:        finance1 / password123")
        print("Логистика:      logistics1 / password123")
        print("Сервис:         service1 / password123")
        print("Клиент 1:       client1 / password123")
        print("Клиент 2:       client2 / password123")


if __name__ == '__main__':
    init_database()
'''

# ============================================================
# requirements.txt
# ============================================================
files['auto_salon_crm/requirements.txt'] = '''Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Werkzeug==3.0.1
'''

# ============================================================
# app.py
# ============================================================
files['auto_salon_crm/app.py'] = '''from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Car, Order, Payment, Delivery, ServiceRequest
from decorators import role_required
from config import Config
from datetime import datetime, date
from sqlalchemy import func


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Пожалуйста, войдите в систему.'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ==================== ОБЩИЕ МАРШРУТЫ ====================

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for(f'{current_user.role}_dashboard'))
        cars = Car.query.filter_by(status='in_stock').limit(6).all()
        return render_template('index.html', cars=cars)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                if not user.is_active:
                    flash('Ваш аккаунт деактивирован.', 'danger')
                    return redirect(url_for('login'))
                login_user(user)
                flash(f'Добро пожаловать, {user.full_name}!', 'success')
                return redirect(url_for('index'))
            flash('Неверное имя пользователя или пароль.', 'danger')
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            full_name = request.form.get('full_name')
            phone = request.form.get('phone')

            if User.query.filter_by(username=username).first():
                flash('Имя пользователя уже занято.', 'danger')
                return redirect(url_for('register'))
            if User.query.filter_by(email=email).first():
                flash('Email уже зарегистрирован.', 'danger')
                return redirect(url_for('register'))

            user = User(username=username, email=email, full_name=full_name,
                       phone=phone, role='client')
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Регистрация успешна! Войдите в систему.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Вы вышли из системы.', 'info')
        return redirect(url_for('index'))

    # ==================== КЛИЕНТ ====================

    @app.route('/client/dashboard')
    @login_required
    @role_required('client')
    def client_dashboard():
        orders = Order.query.filter_by(client_id=current_user.id).order_by(Order.created_at.desc()).limit(5).all()
        services = ServiceRequest.query.filter_by(client_id=current_user.id).order_by(ServiceRequest.created_at.desc()).limit(5).all()
        return render_template('client/dashboard.html', orders=orders, services=services)

    @app.route('/client/catalog')
    @login_required
    @role_required('client')
    def client_catalog():
        brand = request.args.get('brand', '')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)

        query = Car.query.filter_by(status='in_stock')
        if brand:
            query = query.filter(Car.brand.ilike(f'%{brand}%'))
        if min_price:
            query = query.filter(Car.price >= min_price)
        if max_price:
            query = query.filter(Car.price <= max_price)

        cars = query.order_by(Car.price).all()
        brands = db.session.query(Car.brand).distinct().order_by(Car.brand).all()
        return render_template('client/catalog.html', cars=cars,
                             brands=[b[0] for b in brands],
                             filters={'brand': brand, 'min_price': min_price, 'max_price': max_price})

    @app.route('/client/car/<int:car_id>')
    @login_required
    @role_required('client')
    def client_car_detail(car_id):
        car = Car.query.get_or_404(car_id)
        return render_template('client/car_detail.html', car=car)

    @app.route('/client/order/<int:car_id>', methods=['POST'])
    @login_required
    @role_required('client')
    def client_create_order(car_id):
        car = Car.query.get_or_404(car_id)
        if car.status != 'in_stock':
            flash('Этот автомобиль недоступен для заказа.', 'danger')
            return redirect(url_for('client_catalog'))

        order = Order(
            client_id=current_user.id,
            car_id=car.id,
            total_price=car.price,
            discount=0,
            final_price=car.price,
            payment_method=request.form.get('payment_method', 'cash'),
            notes=request.form.get('notes', ''),
            status='new'
        )
        car.status = 'reserved'
        db.session.add(order)
        db.session.commit()
        flash('Заказ успешно создан!', 'success')
        return redirect(url_for('client_my_orders'))

    @app.route('/client/orders')
    @login_required
    @role_required('client')
    def client_my_orders():
        orders = Order.query.filter_by(client_id=current_user.id).order_by(Order.created_at.desc()).all()
        return render_template('client/my_orders.html', orders=orders)

    @app.route('/client/services')
    @login_required
    @role_required('client')
    def client_my_services():
        services = ServiceRequest.query.filter_by(client_id=current_user.id).order_by(ServiceRequest.created_at.desc()).all()
        return render_template('client/my_services.html', services=services)

    @app.route('/client/service/new', methods=['GET', 'POST'])
    @login_required
    @role_required('client')
    def client_new_service():
        if request.method == 'POST':
            sr = ServiceRequest(
                client_id=current_user.id,
                service_type=request.form.get('service_type'),
                description=request.form.get('description'),
                car_vin=request.form.get('car_vin', ''),
                priority='normal',
                status='new'
            )
            db.session.add(sr)
            db.session.commit()
            flash('Заявка на сервис создана!', 'success')
            return redirect(url_for('client_my_services'))
        return render_template('client/my_services.html',
                             service_types=ServiceRequest.SERVICE_TYPES, new_form=True)

    @app.route('/client/profile', methods=['GET', 'POST'])
    @login_required
    @role_required('client')
    def client_profile():
        if request.method == 'POST':
            current_user.full_name = request.form.get('full_name')
            current_user.phone = request.form.get('phone')
            current_user.email = request.form.get('email')
            db.session.commit()
            flash('Профиль обновлён!', 'success')
        return render_template('client/profile.html')

    # ==================== ОТДЕЛ ПРОДАЖ ====================

    @app.route('/sales/dashboard')
    @login_required
    @role_required('sales')
    def sales_dashboard():
        new_orders = Order.query.filter_by(status='new').count()
        processing_orders = Order.query.filter_by(status='processing').count()
        total_this_month = Order.query.filter(
            Order.status == 'completed',
            Order.created_at >= date.today().replace(day=1)
        ).count()
        revenue_this_month = db.session.query(func.sum(Order.final_price)).filter(
            Order.status == 'completed',
            Order.created_at >= date.today().replace(day=1)
        ).scalar() or 0

        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
        return render_template('sales/dashboard.html',
                             new_orders=new_orders, processing_orders=processing_orders,
                             total_this_month=total_this_month, revenue_this_month=revenue_this_month,
                             recent_orders=recent_orders)

    @app.route('/sales/orders')
    @login_required
    @role_required('sales')
    def sales_orders():
        status = request.args.get('status', '')
        query = Order.query
        if status:
            query = query.filter_by(status=status)
        orders = query.order_by(Order.created_at.desc()).all()
        return render_template('sales/orders.html', orders=orders,
                             statuses=Order.STATUS_CHOICES, current_status=status)

    @app.route('/sales/order/<int:order_id>', methods=['GET', 'POST'])
    @login_required
    @role_required('sales')
    def sales_order_detail(order_id):
        order = Order.query.get_or_404(order_id)
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'update_status':
                new_status = request.form.get('status')
                order.status = new_status
                if new_status == 'processing' and not order.manager_id:
                    order.manager_id = current_user.id
                if new_status == 'completed':
                    order.car.status = 'sold'
                elif new_status == 'cancelled':
                    order.car.status = 'in_stock'
            elif action == 'update_discount':
                discount = float(request.form.get('discount', 0))
                order.discount = discount
                order.final_price = order.total_price - discount
            elif action == 'assign':
                order.manager_id = current_user.id
            order.notes = request.form.get('notes', order.notes)
            db.session.commit()
            flash('Заказ обновлён!', 'success')
        return render_template('sales/order_detail.html', order=order,
                             statuses=Order.STATUS_CHOICES)

    @app.route('/sales/clients')
    @login_required
    @role_required('sales')
    def sales_clients():
        clients = User.query.filter_by(role='client').order_by(User.full_name).all()
        return render_template('sales/clients.html', clients=clients)

    @app.route('/sales/new_order', methods=['GET', 'POST'])
    @login_required
    @role_required('sales')
    def sales_new_order():
        if request.method == 'POST':
            client_id = request.form.get('client_id')
            car_id = request.form.get('car_id')
            discount = float(request.form.get('discount', 0))
            car = Car.query.get(car_id)

            order = Order(
                client_id=client_id,
                manager_id=current_user.id,
                car_id=car_id,
                total_price=car.price,
                discount=discount,
                final_price=car.price - discount,
                payment_method=request.form.get('payment_method', 'cash'),
                notes=request.form.get('notes', ''),
                status='processing'
            )
            car.status = 'reserved'
            db.session.add(order)
            db.session.commit()
            flash('Заказ создан!', 'success')
            return redirect(url_for('sales_orders'))

        clients = User.query.filter_by(role='client', is_active=True).all()
        cars = Car.query.filter_by(status='in_stock').all()
        return render_template('sales/new_order.html', clients=clients, cars=cars)

    # ==================== ФИНАНСОВЫЙ ОТДЕЛ ====================

    @app.route('/finance/dashboard')
    @login_required
    @role_required('finance')
    def finance_dashboard():
        total_revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed'
        ).scalar() or 0
        pending_payments = Payment.query.filter_by(status='pending').count()
        monthly_revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed',
            Payment.created_at >= date.today().replace(day=1)
        ).scalar() or 0
        orders_awaiting = Order.query.filter_by(status='payment_pending').count()
        recent_payments = Payment.query.order_by(Payment.created_at.desc()).limit(10).all()
        return render_template('finance/dashboard.html',
                             total_revenue=total_revenue, pending_payments=pending_payments,
                             monthly_revenue=monthly_revenue, orders_awaiting=orders_awaiting,
                             recent_payments=recent_payments)

    @app.route('/finance/payments')
    @login_required
    @role_required('finance')
    def finance_payments():
        status = request.args.get('status', '')
        query = Payment.query
        if status:
            query = query.filter_by(status=status)
        payments = query.order_by(Payment.created_at.desc()).all()
        return render_template('finance/payments.html', payments=payments,
                             statuses=Payment.STATUS_CHOICES, current_status=status)

    @app.route('/finance/payment/new', methods=['GET', 'POST'])
    @login_required
    @role_required('finance')
    def finance_new_payment():
        if request.method == 'POST':
            order_id = request.form.get('order_id')
            payment = Payment(
                order_id=order_id,
                amount=float(request.form.get('amount')),
                payment_type=request.form.get('payment_type'),
                status=request.form.get('status', 'pending'),
                description=request.form.get('description', ''),
                created_by_id=current_user.id,
                payment_date=datetime.utcnow() if request.form.get('status') == 'completed' else None
            )
            db.session.add(payment)

            if request.form.get('status') == 'completed':
                order = Order.query.get(order_id)
                total_paid = db.session.query(func.sum(Payment.amount)).filter(
                    Payment.order_id == order_id,
                    Payment.status == 'completed'
                ).scalar() or 0
                total_paid += float(request.form.get('amount'))
                if total_paid >= order.final_price:
                    order.status = 'paid'

            db.session.commit()
            flash('Платёж создан!', 'success')
            return redirect(url_for('finance_payments'))

        orders = Order.query.filter(Order.status.in_(['approved', 'payment_pending', 'processing'])).all()
        return render_template('finance/new_payment.html', orders=orders,
                             payment_types=Payment.TYPE_CHOICES)

    @app.route('/finance/payment/<int:payment_id>/update', methods=['POST'])
    @login_required
    @role_required('finance')
    def finance_update_payment(payment_id):
        payment = Payment.query.get_or_404(payment_id)
        new_status = request.form.get('status')
        payment.status = new_status
        if new_status == 'completed':
            payment.payment_date = datetime.utcnow()
            order = payment.order
            total_paid = db.session.query(func.sum(Payment.amount)).filter(
                Payment.order_id == order.id,
                Payment.status == 'completed'
            ).scalar() or 0
            if total_paid >= order.final_price:
                order.status = 'paid'
        db.session.commit()
        flash('Статус платежа обновлён!', 'success')
        return redirect(url_for('finance_payments'))

    @app.route('/finance/reports')
    @login_required
    @role_required('finance')
    def finance_reports():
        payments_by_month = db.session.query(
            func.strftime('%Y-%m', Payment.created_at).label('month'),
            func.sum(Payment.amount).label('total')
        ).filter(Payment.status == 'completed').group_by('month').order_by('month').all()

        payments_by_type = db.session.query(
            Payment.payment_type,
            func.sum(Payment.amount).label('total'),
            func.count(Payment.id).label('count')
        ).filter(Payment.status == 'completed').group_by(Payment.payment_type).all()

        total_cars_cost = db.session.query(func.sum(Car.purchase_price)).filter(
            Car.status == 'in_stock'
        ).scalar() or 0

        return render_template('finance/reports.html',
                             payments_by_month=payments_by_month,
                             payments_by_type=payments_by_type,
                             total_cars_cost=total_cars_cost,
                             type_choices=Payment.TYPE_CHOICES)

    # ==================== ЛОГИСТИКА И СКЛАД ====================

    @app.route('/logistics/dashboard')
    @login_required
    @role_required('logistics')
    def logistics_dashboard():
        total_cars = Car.query.count()
        in_stock = Car.query.filter_by(status='in_stock').count()
        in_transit = Car.query.filter_by(status='in_transit').count()
        reserved = Car.query.filter_by(status='reserved').count()
        active_deliveries = Delivery.query.filter(Delivery.status.in_(['planned', 'in_transit'])).count()
        recent_deliveries = Delivery.query.order_by(Delivery.created_at.desc()).limit(5).all()
        return render_template('logistics/dashboard.html',
                             total_cars=total_cars, in_stock=in_stock,
                             in_transit=in_transit, reserved=reserved,
                             active_deliveries=active_deliveries,
                             recent_deliveries=recent_deliveries)

    @app.route('/logistics/warehouse')
    @login_required
    @role_required('logistics')
    def logistics_warehouse():
        status = request.args.get('status', '')
        query = Car.query
        if status:
            query = query.filter_by(status=status)
        cars = query.order_by(Car.created_at.desc()).all()
        return render_template('logistics/warehouse.html', cars=cars,
                             statuses=Car.STATUS_CHOICES, current_status=status)

    @app.route('/logistics/car/add', methods=['GET', 'POST'])
    @login_required
    @role_required('logistics')
    def logistics_add_car():
        if request.method == 'POST':
            car = Car(
                brand=request.form.get('brand'),
                model=request.form.get('model'),
                year=int(request.form.get('year')),
                color=request.form.get('color'),
                vin=request.form.get('vin'),
                engine_type=request.form.get('engine_type'),
                engine_volume=float(request.form.get('engine_volume', 0)),
                horsepower=int(request.form.get('horsepower', 0)),
                transmission=request.form.get('transmission'),
                drive_type=request.form.get('drive_type'),
                mileage=int(request.form.get('mileage', 0)),
                price=float(request.form.get('price')),
                purchase_price=float(request.form.get('purchase_price', 0)),
                status=request.form.get('status', 'in_stock'),
                description=request.form.get('description', '')
            )
            db.session.add(car)
            db.session.commit()
            flash('Автомобиль добавлен!', 'success')
            return redirect(url_for('logistics_warehouse'))
        return render_template('logistics/car_form.html', car=None)

    @app.route('/logistics/car/<int:car_id>/edit', methods=['GET', 'POST'])
    @login_required
    @role_required('logistics')
    def logistics_edit_car(car_id):
        car = Car.query.get_or_404(car_id)
        if request.method == 'POST':
            car.brand = request.form.get('brand')
            car.model = request.form.get('model')
            car.year = int(request.form.get('year'))
            car.color = request.form.get('color')
            car.vin = request.form.get('vin')
            car.engine_type = request.form.get('engine_type')
            car.engine_volume = float(request.form.get('engine_volume', 0))
            car.horsepower = int(request.form.get('horsepower', 0))
            car.transmission = request.form.get('transmission')
            car.drive_type = request.form.get('drive_type')
            car.mileage = int(request.form.get('mileage', 0))
            car.price = float(request.form.get('price'))
            car.purchase_price = float(request.form.get('purchase_price', 0))
            car.status = request.form.get('status')
            car.description = request.form.get('description', '')
            db.session.commit()
            flash('Данные автомобиля обновлены!', 'success')
            return redirect(url_for('logistics_warehouse'))
        return render_template('logistics/car_form.html', car=car)

    @app.route('/logistics/deliveries')
    @login_required
    @role_required('logistics')
    def logistics_deliveries():
        status = request.args.get('status', '')
        query = Delivery.query
        if status:
            query = query.filter_by(status=status)
        deliveries = query.order_by(Delivery.created_at.desc()).all()
        return render_template('logistics/deliveries.html', deliveries=deliveries,
                             statuses=Delivery.STATUS_CHOICES, current_status=status)

    @app.route('/logistics/delivery/new', methods=['GET', 'POST'])
    @login_required
    @role_required('logistics')
    def logistics_new_delivery():
        if request.method == 'POST':
            car_id = request.form.get('car_id')
            delivery = Delivery(
                car_id=car_id,
                supplier=request.form.get('supplier'),
                expected_date=datetime.strptime(request.form.get('expected_date'), '%Y-%m-%d').date(),
                tracking_number=request.form.get('tracking_number', ''),
                notes=request.form.get('notes', ''),
                status='planned',
                created_by_id=current_user.id
            )
            if car_id:
                car = Car.query.get(car_id)
                if car:
                    car.status = 'in_transit'
            db.session.add(delivery)
            db.session.commit()
            flash('Поставка создана!', 'success')
            return redirect(url_for('logistics_deliveries'))
        cars = Car.query.filter(Car.status.in_(['in_transit', 'in_stock'])).all()
        return render_template('logistics/delivery_form.html', delivery=None, cars=cars)

    @app.route('/logistics/delivery/<int:delivery_id>/update', methods=['POST'])
    @login_required
    @role_required('logistics')
    def logistics_update_delivery(delivery_id):
        delivery = Delivery.query.get_or_404(delivery_id)
        new_status = request.form.get('status')
        delivery.status = new_status
        if new_status == 'delivered':
            delivery.actual_date = date.today()
            if delivery.car:
                delivery.car.status = 'in_stock'
        db.session.commit()
        flash('Статус поставки обновлён!', 'success')
        return redirect(url_for('logistics_deliveries'))

    # ==================== СЕРВИС И ТЕХ. СЛУЖБА ====================

    @app.route('/service/dashboard')
    @login_required
    @role_required('service')
    def service_dashboard():
        new_requests = ServiceRequest.query.filter_by(status='new').count()
        in_progress = ServiceRequest.query.filter_by(status='in_progress').count()
        my_tasks = ServiceRequest.query.filter_by(assigned_to_id=current_user.id).filter(
            ServiceRequest.status.in_(['accepted', 'in_progress', 'waiting_parts'])
        ).count()
        completed_today = ServiceRequest.query.filter(
            ServiceRequest.status == 'completed',
            ServiceRequest.completed_date == date.today()
        ).count()
        recent = ServiceRequest.query.order_by(ServiceRequest.created_at.desc()).limit(10).all()
        return render_template('service/dashboard.html',
                             new_requests=new_requests, in_progress=in_progress,
                             my_tasks=my_tasks, completed_today=completed_today,
                             recent=recent)

    @app.route('/service/requests')
    @login_required
    @role_required('service')
    def service_requests():
        status = request.args.get('status', '')
        view = request.args.get('view', 'all')
        query = ServiceRequest.query
        if status:
            query = query.filter_by(status=status)
        if view == 'my':
            query = query.filter_by(assigned_to_id=current_user.id)
        requests = query.order_by(ServiceRequest.created_at.desc()).all()
        return render_template('service/requests.html', requests=requests,
                             statuses=ServiceRequest.STATUS_CHOICES, current_status=status, view=view)

    @app.route('/service/request/<int:req_id>', methods=['GET', 'POST'])
    @login_required
    @role_required('service')
    def service_request_detail(req_id):
        sr = ServiceRequest.query.get_or_404(req_id)
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'update_status':
                sr.status = request.form.get('status')
                if sr.status == 'completed':
                    sr.completed_date = date.today()
            elif action == 'assign':
                sr.assigned_to_id = current_user.id
                if sr.status == 'new':
                    sr.status = 'accepted'
            elif action == 'update_cost':
                sr.estimated_cost = float(request.form.get('estimated_cost', 0))
                sr.actual_cost = float(request.form.get('actual_cost', 0)) if request.form.get('actual_cost') else None
            sr.notes = request.form.get('notes', sr.notes)
            if request.form.get('scheduled_date'):
                sr.scheduled_date = datetime.strptime(request.form.get('scheduled_date'), '%Y-%m-%d').date()
            db.session.commit()
            flash('Заявка обновлена!', 'success')
        return render_template('service/request_detail.html', sr=sr,
                             statuses=ServiceRequest.STATUS_CHOICES,
                             priorities=ServiceRequest.PRIORITY_CHOICES)

    @app.route('/service/request/new', methods=['GET', 'POST'])
    @login_required
    @role_required('service')
    def service_new_request():
        if request.method == 'POST':
            sr = ServiceRequest(
                client_id=int(request.form.get('client_id')),
                car_id=int(request.form.get('car_id')) if request.form.get('car_id') else None,
                service_type=request.form.get('service_type'),
                description=request.form.get('description'),
                priority=request.form.get('priority', 'normal'),
                assigned_to_id=current_user.id,
                estimated_cost=float(request.form.get('estimated_cost', 0)) if request.form.get('estimated_cost') else None,
                status='accepted',
                car_vin=request.form.get('car_vin', '')
            )
            if request.form.get('scheduled_date'):
                sr.scheduled_date = datetime.strptime(request.form.get('scheduled_date'), '%Y-%m-%d').date()
            db.session.add(sr)
            db.session.commit()
            flash('Заявка создана!', 'success')
            return redirect(url_for('service_requests'))

        clients = User.query.filter_by(role='client', is_active=True).all()
        cars = Car.query.all()
        return render_template('service/new_request.html', clients=clients, cars=cars,
                             service_types=ServiceRequest.SERVICE_TYPES,
                             priorities=ServiceRequest.PRIORITY_CHOICES)

    # ==================== РУКОВОДСТВО ====================

    @app.route('/management/dashboard')
    @login_required
    @role_required('management')
    def management_dashboard():
        total_cars = Car.query.count()
        cars_in_stock = Car.query.filter_by(status='in_stock').count()
        total_clients = User.query.filter_by(role='client').count()
        total_orders = Order.query.count()
        completed_orders = Order.query.filter_by(status='completed').count()
        total_revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed'
        ).scalar() or 0
        monthly_revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed',
            Payment.created_at >= date.today().replace(day=1)
        ).scalar() or 0
        total_employees = User.query.filter(User.role != 'client').count()
        pending_services = ServiceRequest.query.filter(
            ServiceRequest.status.in_(['new', 'accepted', 'in_progress'])
        ).count()
        active_deliveries = Delivery.query.filter(
            Delivery.status.in_(['planned', 'in_transit'])
        ).count()
        stock_value = db.session.query(func.sum(Car.price)).filter(
            Car.status == 'in_stock'
        ).scalar() or 0

        return render_template('management/dashboard.html',
                             total_cars=total_cars, cars_in_stock=cars_in_stock,
                             total_clients=total_clients, total_orders=total_orders,
                             completed_orders=completed_orders, total_revenue=total_revenue,
                             monthly_revenue=monthly_revenue, total_employees=total_employees,
                             pending_services=pending_services, active_deliveries=active_deliveries,
                             stock_value=stock_value)

    @app.route('/management/users')
    @login_required
    @role_required('management')
    def management_users():
        role = request.args.get('role', '')
        query = User.query
        if role:
            query = query.filter_by(role=role)
        users = query.order_by(User.created_at.desc()).all()
        return render_template('management/users.html', users=users,
                             roles=User.ROLES, current_role=role)

    @app.route('/management/user/<int:user_id>/toggle', methods=['POST'])
    @login_required
    @role_required('management')
    def management_toggle_user(user_id):
        user = User.query.get_or_404(user_id)
        if user.id == current_user.id:
            flash('Нельзя деактивировать собственный аккаунт!', 'danger')
        else:
            user.is_active = not user.is_active
            db.session.commit()
            status = 'активирован' if user.is_active else 'деактивирован'
            flash(f'Пользователь {user.full_name} {status}.', 'success')
        return redirect(url_for('management_users'))

    @app.route('/management/user/<int:user_id>/role', methods=['POST'])
    @login_required
    @role_required('management')
    def management_change_role(user_id):
        user = User.query.get_or_404(user_id)
        new_role = request.form.get('role')
        if new_role in User.ROLES:
            user.role = new_role
            db.session.commit()
            flash(f'Роль пользователя {user.full_name} изменена на "{User.ROLES[new_role]}".', 'success')
        return redirect(url_for('management_users'))

    @app.route('/management/analytics')
    @login_required
    @role_required('management')
    def management_analytics():
        sales_by_brand = db.session.query(
            Car.brand,
            func.count(Order.id).label('count'),
            func.sum(Order.final_price).label('revenue')
        ).join(Order, Order.car_id == Car.id).filter(
            Order.status.in_(['completed', 'paid'])
        ).group_by(Car.brand).all()

        sales_by_month = db.session.query(
            func.strftime('%Y-%m', Order.created_at).label('month'),
            func.count(Order.id).label('count'),
            func.sum(Order.final_price).label('revenue')
        ).filter(Order.status.in_(['completed', 'paid'])).group_by('month').order_by('month').all()

        service_stats = db.session.query(
            ServiceRequest.service_type,
            func.count(ServiceRequest.id).label('count')
        ).group_by(ServiceRequest.service_type).all()

        top_managers = db.session.query(
            User.full_name,
            func.count(Order.id).label('orders_count'),
            func.sum(Order.final_price).label('total_revenue')
        ).join(Order, Order.manager_id == User.id).filter(
            Order.status.in_(['completed', 'paid'])
        ).group_by(User.id).order_by(func.count(Order.id).desc()).limit(5).all()

        return render_template('management/analytics.html',
                             sales_by_brand=sales_by_brand,
                             sales_by_month=sales_by_month,
                             service_stats=service_stats,
                             top_managers=top_managers,
                             service_types=ServiceRequest.SERVICE_TYPES)

    @app.route('/management/orders')
    @login_required
    @role_required('management')
    def management_all_orders():
        status = request.args.get('status', '')
        query = Order.query
        if status:
            query = query.filter_by(status=status)
        orders = query.order_by(Order.created_at.desc()).all()
        return render_template('management/all_orders.html', orders=orders,
                             statuses=Order.STATUS_CHOICES, current_status=status)

    # ==================== ОБРАБОТКА ОШИБОК ====================

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('base.html', error_code=403,
                             error_message='Доступ запрещён. У вас нет прав для просмотра этой страницы.'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('base.html', error_code=404,
                             error_message='Страница не найдена.'), 404

    @app.context_processor
    def utility_processor():
        def format_price(value):
            if value is None:
                return "0"
            return f"{value:,.0f}".replace(",", " ")
        return dict(format_price=format_price)

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
'''

# ============================================================
# static/style.css
# ============================================================
files['auto_salon_crm/static/style.css'] = ''':root {
    --primary: #2563eb;
    --primary-dark: #1d4ed8;
    --primary-light: #dbeafe;
    --success: #16a34a;
    --success-light: #dcfce7;
    --danger: #dc2626;
    --danger-light: #fee2e2;
    --warning: #d97706;
    --warning-light: #fef3c7;
    --info: #0891b2;
    --info-light: #cffafe;
    --gray-50: #f9fafb;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-300: #d1d5db;
    --gray-400: #9ca3af;
    --gray-500: #6b7280;
    --gray-600: #4b5563;
    --gray-700: #374151;
    --gray-800: #1f2937;
    --gray-900: #111827;
    --shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.06);
    --shadow-md: 0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06);
    --shadow-lg: 0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05);
    --radius: 8px;
    --radius-lg: 12px;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background-color: var(--gray-50);
    color: var(--gray-800);
    line-height: 1.6;
}
.navbar {
    background: linear-gradient(135deg, var(--gray-900) 0%, var(--gray-800) 100%);
    padding: 0 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
    box-shadow: var(--shadow-md);
    position: sticky;
    top: 0;
    z-index: 1000;
}
.navbar-brand {
    color: white;
    font-size: 1.4rem;
    font-weight: 700;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.navbar-brand:hover { color: var(--primary-light); }
.navbar-nav {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    list-style: none;
}
.navbar-nav a {
    color: var(--gray-300);
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: var(--radius);
    font-size: 0.9rem;
    transition: all 0.2s;
}
.navbar-nav a:hover { color: white; background: rgba(255,255,255,0.1); }
.navbar-nav a.active { color: white; background: var(--primary); }
.navbar-user {
    display: flex;
    align-items: center;
    gap: 1rem;
    color: var(--gray-300);
    font-size: 0.9rem;
}
.navbar-user .role-badge {
    background: var(--primary);
    color: white;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}
.btn-logout {
    color: var(--gray-400);
    text-decoration: none;
    padding: 0.4rem 0.8rem;
    border-radius: var(--radius);
    font-size: 0.85rem;
    transition: all 0.2s;
}
.btn-logout:hover { color: white; background: var(--danger); }
.container { max-width: 1400px; margin: 0 auto; padding: 2rem; }
.alert {
    padding: 1rem 1.5rem;
    border-radius: var(--radius);
    margin-bottom: 1.5rem;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.alert-success { background: var(--success-light); color: var(--success); border-left: 4px solid var(--success); }
.alert-danger { background: var(--danger-light); color: var(--danger); border-left: 4px solid var(--danger); }
.alert-warning { background: var(--warning-light); color: var(--warning); border-left: 4px solid var(--warning); }
.alert-info { background: var(--info-light); color: var(--info); border-left: 4px solid var(--info); }
.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}
.page-header h1 { font-size: 1.8rem; color: var(--gray-900); font-weight: 700; }
.card {
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    overflow: hidden;
    margin-bottom: 1.5rem;
}
.card-header {
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid var(--gray-200);
    font-weight: 600;
    font-size: 1.1rem;
    color: var(--gray-800);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.card-body { padding: 1.5rem; }
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}
.stat-card {
    background: white;
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    box-shadow: var(--shadow);
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-lg); }
.stat-card .stat-label {
    font-size: 0.85rem;
    color: var(--gray-500);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}
.stat-card .stat-value { font-size: 2rem; font-weight: 700; color: var(--gray-900); }
.stat-card.primary { border-left: 4px solid var(--primary); }
.stat-card.success { border-left: 4px solid var(--success); }
.stat-card.warning { border-left: 4px solid var(--warning); }
.stat-card.danger { border-left: 4px solid var(--danger); }
.stat-card.info { border-left: 4px solid var(--info); }
.table-container { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
table th {
    background: var(--gray-50);
    padding: 0.75rem 1rem;
    text-align: left;
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--gray-600);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 2px solid var(--gray-200);
}
table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--gray-100);
    font-size: 0.95rem;
}
table tbody tr:hover { background: var(--gray-50); }
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}
.badge-new { background: var(--primary-light); color: var(--primary); }
.badge-processing, .badge-in_progress, .badge-in_transit, .badge-planned { background: var(--warning-light); color: var(--warning); }
.badge-approved, .badge-accepted, .badge-paid, .badge-completed, .badge-delivered { background: var(--success-light); color: var(--success); }
.badge-cancelled, .badge-refunded { background: var(--danger-light); color: var(--danger); }
.badge-payment_pending, .badge-pending, .badge-waiting_parts { background: var(--info-light); color: var(--info); }
.badge-in_stock { background: var(--success-light); color: var(--success); }
.badge-reserved { background: var(--warning-light); color: var(--warning); }
.badge-sold { background: var(--gray-200); color: var(--gray-600); }
.badge-in_service { background: var(--info-light); color: var(--info); }
.badge-low { background: var(--gray-100); color: var(--gray-600); }
.badge-normal { background: var(--primary-light); color: var(--primary); }
.badge-high { background: var(--warning-light); color: var(--warning); }
.badge-urgent { background: var(--danger-light); color: var(--danger); }
.btn {
    display: inline-block;
    padding: 0.6rem 1.2rem;
    border-radius: var(--radius);
    font-size: 0.9rem;
    font-weight: 600;
    text-decoration: none;
    cursor: pointer;
    border: none;
    transition: all 0.2s;
    text-align: center;
}
.btn-sm { padding: 0.35rem 0.8rem; font-size: 0.8rem; }
.btn-primary { background: var(--primary); color: white; }
.btn-primary:hover { background: var(--primary-dark); }
.btn-success { background: var(--success); color: white; }
.btn-success:hover { background: #15803d; }
.btn-danger { background: var(--danger); color: white; }
.btn-danger:hover { background: #b91c1c; }
.btn-warning { background: var(--warning); color: white; }
.btn-warning:hover { background: #b45309; }
.btn-outline { background: white; color: var(--gray-700); border: 1px solid var(--gray-300); }
.btn-outline:hover { background: var(--gray-50); border-color: var(--gray-400); }
.btn-info { background: var(--info); color: white; }
.btn-info:hover { background: #0e7490; }
.btn-group { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.form-group { margin-bottom: 1.25rem; }
.form-group label {
    display: block;
    margin-bottom: 0.4rem;
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--gray-700);
}
.form-control {
    width: 100%;
    padding: 0.65rem 1rem;
    border: 1px solid var(--gray-300);
    border-radius: var(--radius);
    font-size: 0.95rem;
    transition: border-color 0.2s, box-shadow 0.2s;
    background: white;
}
.form-control:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}
select.form-control { appearance: auto; }
textarea.form-control { resize: vertical; min-height: 100px; }
.form-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
}
.auth-container { max-width: 450px; margin: 4rem auto; padding: 0 1rem; }
.auth-card {
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    padding: 2.5rem;
}
.auth-card h2 { text-align: center; margin-bottom: 0.5rem; color: var(--gray-900); }
.auth-card .subtitle { text-align: center; color: var(--gray-500); margin-bottom: 2rem; }
.auth-card .auth-footer { text-align: center; margin-top: 1.5rem; color: var(--gray-500); font-size: 0.9rem; }
.auth-card .auth-footer a { color: var(--primary); text-decoration: none; font-weight: 600; }
.cars-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
}
.car-card {
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.car-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg); }
.car-card-image {
    height: 200px;
    background: linear-gradient(135deg, var(--primary-light), var(--gray-100));
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
    color: var(--primary);
}
.car-card-body { padding: 1.5rem; }
.car-card-title { font-size: 1.2rem; font-weight: 700; color: var(--gray-900); margin-bottom: 0.5rem; }
.car-card-info {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.4rem;
    margin-bottom: 1rem;
    font-size: 0.9rem;
    color: var(--gray-600);
}
.car-card-price { font-size: 1.4rem; font-weight: 700; color: var(--primary); margin-bottom: 1rem; }
.car-card-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid var(--gray-100);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.detail-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}
.detail-item { display: flex; flex-direction: column; gap: 0.2rem; }
.detail-label {
    font-size: 0.8rem;
    color: var(--gray-500);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}
.detail-value { font-size: 1rem; color: var(--gray-800); font-weight: 500; }
.filters {
    background: white;
    border-radius: var(--radius-lg);
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow);
    display: flex;
    gap: 1rem;
    align-items: end;
    flex-wrap: wrap;
}
.filters .form-group { margin-bottom: 0; min-width: 150px; }
.hero {
    background: linear-gradient(135deg, var(--gray-900) 0%, var(--primary-dark) 100%);
    color: white;
    padding: 4rem 2rem;
    text-align: center;
    border-radius: var(--radius-lg);
    margin-bottom: 2rem;
}
.hero h1 { font-size: 2.5rem; margin-bottom: 1rem; }
.hero p { font-size: 1.2rem; color: var(--gray-300); max-width: 600px; margin: 0 auto 2rem; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1.5rem; }
.error-page { text-align: center; padding: 4rem 2rem; }
.error-page h1 { font-size: 6rem; color: var(--gray-300); font-weight: 800; }
.error-page p { font-size: 1.2rem; color: var(--gray-500); margin-bottom: 2rem; }
.empty-state { text-align: center; padding: 3rem; color: var(--gray-400); }
.empty-state .icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-state p { font-size: 1.1rem; }
@media (max-width: 768px) {
    .navbar { padding: 0.75rem 1rem; flex-wrap: wrap; height: auto; }
    .navbar-nav { gap: 0; }
    .navbar-nav a { padding: 0.4rem 0.6rem; font-size: 0.8rem; }
    .container { padding: 1rem; }
    .stats-grid { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
    .grid-2, .grid-3 { grid-template-columns: 1fr; }
    .page-header { flex-direction: column; gap: 1rem; align-items: flex-start; }
    .hero h1 { font-size: 1.8rem; }
    .detail-grid { grid-template-columns: 1fr; }
    .filters { flex-direction: column; align-items: stretch; }
}
'''

# ============================================================
# templates/base.html
# ============================================================
files['auto_salon_crm/templates/base.html'] = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}АвтоСалон CRM{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <nav class="navbar">
        <a href="{{ url_for('index') }}" class="navbar-brand">🚗 АвтоСалон CRM</a>
        {% if current_user.is_authenticated %}
        <ul class="navbar-nav">
            {% if current_user.role == 'client' %}
                <li><a href="{{ url_for('client_dashboard') }}" class="{{ 'active' if request.endpoint == 'client_dashboard' }}">Главная</a></li>
                <li><a href="{{ url_for('client_catalog') }}" class="{{ 'active' if request.endpoint == 'client_catalog' }}">Каталог</a></li>
                <li><a href="{{ url_for('client_my_orders') }}" class="{{ 'active' if request.endpoint == 'client_my_orders' }}">Мои заказы</a></li>
                <li><a href="{{ url_for('client_my_services') }}" class="{{ 'active' if request.endpoint in ('client_my_services', 'client_new_service') }}">Сервис</a></li>
                <li><a href="{{ url_for('client_profile') }}" class="{{ 'active' if request.endpoint == 'client_profile' }}">Профиль</a></li>
            {% elif current_user.role == 'sales' %}
                <li><a href="{{ url_for('sales_dashboard') }}" class="{{ 'active' if request.endpoint == 'sales_dashboard' }}">Главная</a></li>
                <li><a href="{{ url_for('sales_orders') }}" class="{{ 'active' if request.endpoint in ('sales_orders', 'sales_order_detail') }}">Заказы</a></li>
                <li><a href="{{ url_for('sales_new_order') }}" class="{{ 'active' if request.endpoint == 'sales_new_order' }}">Новый заказ</a></li>
                <li><a href="{{ url_for('sales_clients') }}" class="{{ 'active' if request.endpoint == 'sales_clients' }}">Клиенты</a></li>
            {% elif current_user.role == 'finance' %}
                <li><a href="{{ url_for('finance_dashboard') }}" class="{{ 'active' if request.endpoint == 'finance_dashboard' }}">Главная</a></li>
                <li><a href="{{ url_for('finance_payments') }}" class="{{ 'active' if request.endpoint == 'finance_payments' }}">Платежи</a></li>
                <li><a href="{{ url_for('finance_new_payment') }}" class="{{ 'active' if request.endpoint == 'finance_new_payment' }}">Новый платёж</a></li>
                <li><a href="{{ url_for('finance_reports') }}" class="{{ 'active' if request.endpoint == 'finance_reports' }}">Отчёты</a></li>
            {% elif current_user.role == 'logistics' %}
                <li><a href="{{ url_for('logistics_dashboard') }}" class="{{ 'active' if request.endpoint == 'logistics_dashboard' }}">Главная</a></li>
                <li><a href="{{ url_for('logistics_warehouse') }}" class="{{ 'active' if request.endpoint == 'logistics_warehouse' }}">Склад</a></li>
                <li><a href="{{ url_for('logistics_add_car') }}" class="{{ 'active' if request.endpoint == 'logistics_add_car' }}">Добавить авто</a></li>
                <li><a href="{{ url_for('logistics_deliveries') }}" class="{{ 'active' if request.endpoint == 'logistics_deliveries' }}">Поставки</a></li>
            {% elif current_user.role == 'service' %}
                <li><a href="{{ url_for('service_dashboard') }}" class="{{ 'active' if request.endpoint == 'service_dashboard' }}">Главная</a></li>
                <li><a href="{{ url_for('service_requests') }}" class="{{ 'active' if request.endpoint == 'service_requests' }}">Заявки</a></li>
                <li><a href="{{ url_for('service_new_request') }}" class="{{ 'active' if request.endpoint == 'service_new_request' }}">Новая заявка</a></li>
            {% elif current_user.role == 'management' %}
                <li><a href="{{ url_for('management_dashboard') }}" class="{{ 'active' if request.endpoint == 'management_dashboard' }}">Главная</a></li>
                <li><a href="{{ url_for('management_all_orders') }}" class="{{ 'active' if request.endpoint == 'management_all_orders' }}">Заказы</a></li>
                <li><a href="{{ url_for('management_users') }}" class="{{ 'active' if request.endpoint == 'management_users' }}">Пользователи</a></li>
                <li><a href="{{ url_for('management_analytics') }}" class="{{ 'active' if request.endpoint == 'management_analytics' }}">Аналитика</a></li>
            {% endif %}
        </ul>
        <div class="navbar-user">
            <span class="role-badge">{{ current_user.role_display }}</span>
            <span>{{ current_user.full_name }}</span>
            <a href="{{ url_for('logout') }}" class="btn-logout">Выйти</a>
        </div>
        {% else %}
        <div class="navbar-user">
            <a href="{{ url_for('login') }}" class="btn-logout">Войти</a>
            <a href="{{ url_for('register') }}" class="btn btn-primary btn-sm">Регистрация</a>
        </div>
        {% endif %}
    </nav>
    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% if error_code %}
        <div class="error-page">
            <h1>{{ error_code }}</h1>
            <p>{{ error_message }}</p>
            <a href="{{ url_for('index') }}" class="btn btn-primary">На главную</a>
        </div>
        {% else %}
            {% block content %}{% endblock %}
        {% endif %}
    </div>
</body>
</html>'''

# ============================================================
# templates/login.html
# ============================================================
files['auto_salon_crm/templates/login.html'] = '''{% extends "base.html" %}
{% block title %}Вход — АвтоСалон CRM{% endblock %}
{% block content %}
<div class="auth-container">
    <div class="auth-card">
        <h2>🚗 Вход в систему</h2>
        <p class="subtitle">АвтоСалон CRM</p>
        <form method="POST">
            <div class="form-group">
                <label>Имя пользователя</label>
                <input type="text" name="username" class="form-control" required autofocus>
            </div>
            <div class="form-group">
                <label>Пароль</label>
                <input type="password" name="password" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-primary" style="width: 100%;">Войти</button>
        </form>
        <div class="auth-footer">
            Нет аккаунта? <a href="{{ url_for('register') }}">Зарегистрироваться</a>
        </div>
    </div>
</div>
{% endblock %}'''

# ============================================================
# templates/register.html
# ============================================================
files['auto_salon_crm/templates/register.html'] = '''{% extends "base.html" %}
{% block title %}Регистрация — АвтоСалон CRM{% endblock %}
{% block content %}
<div class="auth-container">
    <div class="auth-card">
        <h2>📝 Регистрация</h2>
        <p class="subtitle">Создайте аккаунт клиента</p>
        <form method="POST">
            <div class="form-group">
                <label>Имя пользователя</label>
                <input type="text" name="username" class="form-control" required>
            </div>
            <div class="form-group">
                <label>ФИО</label>
                <input type="text" name="full_name" class="form-control" required>
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" class="form-control" required>
            </div>
            <div class="form-group">
                <label>Телефон</label>
                <input type="text" name="phone" class="form-control" placeholder="+7(___) ___-__-__">
            </div>
            <div class="form-group">
                <label>Пароль</label>
                <input type="password" name="password" class="form-control" required minlength="6">
            </div>
            <button type="submit" class="btn btn-primary" style="width: 100%;">Зарегистрироваться</button>
        </form>
        <div class="auth-footer">
            Уже есть аккаунт? <a href="{{ url_for('login') }}">Войти</a>
        </div>
    </div>
</div>
{% endblock %}'''

# ============================================================
# templates/index.html
# ============================================================
files['auto_salon_crm/templates/index.html'] = '''{% extends "base.html" %}
{% block title %}АвтоСалон CRM — Главная{% endblock %}
{% block content %}
<div class="hero">
    <h1>Добро пожаловать в АвтоСалон</h1>
    <p>Широкий выбор новых автомобилей с гарантией и сервисным обслуживанием</p>
    <div class="btn-group" style="justify-content: center;">
        <a href="{{ url_for('register') }}" class="btn btn-primary">Зарегистрироваться</a>
        <a href="{{ url_for('login') }}" class="btn btn-outline" style="color: white; border-color: rgba(255,255,255,0.3);">Войти</a>
    </div>
</div>
{% if cars %}
<h2 style="margin-bottom: 1.5rem;">🔥 Автомобили в наличии</h2>
<div class="cars-grid">
    {% for car in cars %}
    <div class="car-card">
        <div class="car-card-image">🚗</div>
        <div class="car-card-body">
            <div class="car-card-title">{{ car.brand }} {{ car.model }}</div>
            <div class="car-card-info">
                <span>📅 {{ car.year }} г.</span>
                <span>🎨 {{ car.color }}</span>
                <span>⚙️ {{ car.engine_type }}</span>
                <span>🔧 {{ car.transmission }}</span>
            </div>
            <div class="car-card-price">{{ format_price(car.price) }} ₽</div>
        </div>
    </div>
    {% endfor %}
</div>
{% endif %}
{% endblock %}'''

# ============================================================
# templates/client/dashboard.html
# ============================================================
files['auto_salon_crm/templates/client/dashboard.html'] = '''{% extends "base.html" %}
{% block title %}Личный кабинет{% endblock %}
{% block content %}
<div class="page-header"><h1>👋 Добро пожаловать, {{ current_user.full_name }}!</h1></div>
<div class="stats-grid">
    <div class="stat-card primary"><span class="stat-label">Мои заказы</span><span class="stat-value">{{ orders|length }}</span></div>
    <div class="stat-card info"><span class="stat-label">Заявки в сервис</span><span class="stat-value">{{ services|length }}</span></div>
</div>
<div class="grid-2">
    <div class="card">
        <div class="card-header">Последние заказы <a href="{{ url_for('client_my_orders') }}" class="btn btn-sm btn-outline">Все заказы</a></div>
        <div class="card-body">
            {% if orders %}
            <table><thead><tr><th>№</th><th>Автомобиль</th><th>Статус</th><th>Сумма</th></tr></thead>
            <tbody>{% for order in orders %}<tr><td>#{{ order.id }}</td><td>{{ order.car.full_name }}</td>
            <td><span class="badge badge-{{ order.status }}">{{ order.status_display }}</span></td>
            <td>{{ format_price(order.final_price) }} ₽</td></tr>{% endfor %}</tbody></table>
            {% else %}<div class="empty-state"><div class="icon">📋</div><p>У вас пока нет заказов</p>
            <a href="{{ url_for('client_catalog') }}" class="btn btn-primary btn-sm" style="margin-top:1rem;">Перейти в каталог</a></div>{% endif %}
        </div>
    </div>
    <div class="card">
        <div class="card-header">Заявки в сервис <a href="{{ url_for('client_my_services') }}" class="btn btn-sm btn-outline">Все заявки</a></div>
        <div class="card-body">
            {% if services %}
            <table><thead><tr><th>№</th><th>Тип</th><th>Статус</th></tr></thead>
            <tbody>{% for sr in services %}<tr><td>#{{ sr.id }}</td><td>{{ sr.service_type_display }}</td>
            <td><span class="badge badge-{{ sr.status }}">{{ sr.status_display }}</span></td></tr>{% endfor %}</tbody></table>
            {% else %}<div class="empty-state"><div class="icon">🔧</div><p>Нет заявок</p></div>{% endif %}
        </div>
    </div>
</div>
<div class="card" style="margin-top:1rem;"><div class="card-header">Быстрые действия</div><div class="card-body"><div class="btn-group">
    <a href="{{ url_for('client_catalog') }}" class="btn btn-primary">🚗 Каталог</a>
    <a href="{{ url_for('client_new_service') }}" class="btn btn-info">🔧 Записаться на сервис</a>
    <a href="{{ url_for('client_profile') }}" class="btn btn-outline">👤 Профиль</a>
</div></div></div>
{% endblock %}'''

# ============================================================
# templates/client/catalog.html
# ============================================================
files['auto_salon_crm/templates/client/catalog.html'] = '''{% extends "base.html" %}
{% block title %}Каталог автомобилей{% endblock %}
{% block content %}
<div class="page-header"><h1>🚗 Каталог автомобилей</h1></div>
<form class="filters" method="GET">
    <div class="form-group"><label>Марка</label><select name="brand" class="form-control"><option value="">Все марки</option>
    {% for b in brands %}<option value="{{ b }}" {{ 'selected' if filters.brand == b }}>{{ b }}</option>{% endfor %}</select></div>
    <div class="form-group"><label>Цена от</label><input type="number" name="min_price" class="form-control" value="{{ filters.min_price or '' }}"></div>
    <div class="form-group"><label>Цена до</label><input type="number" name="max_price" class="form-control" value="{{ filters.max_price or '' }}"></div>
    <button type="submit" class="btn btn-primary">Найти</button>
    <a href="{{ url_for('client_catalog') }}" class="btn btn-outline">Сбросить</a>
</form>
{% if cars %}
<div class="cars-grid">{% for car in cars %}
<div class="car-card"><div class="car-card-image">🚗</div><div class="car-card-body">
    <div class="car-card-title">{{ car.brand }} {{ car.model }}</div>
    <div class="car-card-info"><span>📅 {{ car.year }}</span><span>🎨 {{ car.color }}</span>
    <span>⚙️ {{ car.engine_type }} {{ car.engine_volume }}л</span><span>🐴 {{ car.horsepower }} л.с.</span>
    <span>🔧 {{ car.transmission }}</span><span>🛣️ {{ car.drive_type }}</span></div>
    <div class="car-card-price">{{ format_price(car.price) }} ₽</div></div>
    <div class="car-card-footer"><span class="badge badge-{{ car.status }}">{{ car.status_display }}</span>
    <a href="{{ url_for('client_car_detail', car_id=car.id) }}" class="btn btn-sm btn-primary">Подробнее</a></div></div>
{% endfor %}</div>
{% else %}<div class="empty-state"><div class="icon">🔍</div><p>Автомобили не найдены</p></div>{% endif %}
{% endblock %}'''

# ============================================================
# templates/client/car_detail.html
# ============================================================
files['auto_salon_crm/templates/client/car_detail.html'] = '''{% extends "base.html" %}
{% block title %}{{ car.full_name }}{% endblock %}
{% block content %}
<div class="page-header"><h1>{{ car.brand }} {{ car.model }}</h1>
<a href="{{ url_for('client_catalog') }}" class="btn btn-outline">← Назад</a></div>
<div class="grid-2">
    <div class="card"><div class="car-card-image" style="height:300px;">🚗</div><div class="card-body">
    <h2>{{ car.full_name }}</h2><div class="car-card-price">{{ format_price(car.price) }} ₽</div>
    <p>{{ car.description or 'Описание отсутствует' }}</p></div></div>
    <div><div class="card"><div class="card-header">Характеристики</div><div class="card-body"><div class="detail-grid">
        <div class="detail-item"><span class="detail-label">Год</span><span class="detail-value">{{ car.year }}</span></div>
        <div class="detail-item"><span class="detail-label">Цвет</span><span class="detail-value">{{ car.color }}</span></div>
        <div class="detail-item"><span class="detail-label">Двигатель</span><span class="detail-value">{{ car.engine_type }} {{ car.engine_volume }}л</span></div>
        <div class="detail-item"><span class="detail-label">Мощность</span><span class="detail-value">{{ car.horsepower }} л.с.</span></div>
        <div class="detail-item"><span class="detail-label">КПП</span><span class="detail-value">{{ car.transmission }}</span></div>
        <div class="detail-item"><span class="detail-label">Привод</span><span class="detail-value">{{ car.drive_type }}</span></div>
        <div class="detail-item"><span class="detail-label">Пробег</span><span class="detail-value">{{ format_price(car.mileage) }} км</span></div>
        <div class="detail-item"><span class="detail-label">VIN</span><span class="detail-value">{{ car.vin }}</span></div>
    </div></div></div>
    {% if car.status == 'in_stock' %}
    <div class="card"><div class="card-header">Оформить заказ</div><div class="card-body">
    <form method="POST" action="{{ url_for('client_create_order', car_id=car.id) }}">
        <div class="form-group"><label>Способ оплаты</label><select name="payment_method" class="form-control">
        <option value="cash">Наличные</option><option value="card">Карта</option>
        <option value="transfer">Перевод</option><option value="credit">Кредит</option>
        <option value="leasing">Лизинг</option></select></div>
        <div class="form-group"><label>Примечания</label><textarea name="notes" class="form-control" rows="3"></textarea></div>
        <button type="submit" class="btn btn-success" style="width:100%;"
        onclick="return confirm('Подтвердить заказ?')">🛒 Оформить — {{ format_price(car.price) }} ₽</button>
    </form></div></div>
    {% endif %}</div>
</div>
{% endblock %}'''

# ============================================================
# templates/client/my_orders.html
# ============================================================
files['auto_salon_crm/templates/client/my_orders.html'] = '''{% extends "base.html" %}
{% block title %}Мои заказы{% endblock %}
{% block content %}
<div class="page-header"><h1>📋 Мои заказы</h1><a href="{{ url_for('client_catalog') }}" class="btn btn-primary">🚗 Каталог</a></div>
<div class="card"><div class="card-body">
{% if orders %}<div class="table-container"><table><thead><tr><th>№</th><th>Дата</th><th>Автомобиль</th><th>Статус</th><th>Оплата</th><th>Итого</th></tr></thead>
<tbody>{% for order in orders %}<tr><td><strong>#{{ order.id }}</strong></td><td>{{ order.created_at.strftime('%d.%m.%Y') }}</td>
<td>{{ order.car.full_name }}</td><td><span class="badge badge-{{ order.status }}">{{ order.status_display }}</span></td>
<td>{{ order.payment_method or '—' }}</td><td><strong>{{ format_price(order.final_price) }} ₽</strong></td></tr>{% endfor %}</tbody></table></div>
{% else %}<div class="empty-state"><div class="icon">📋</div><p>У вас пока нет заказов</p>
<a href="{{ url_for('client_catalog') }}" class="btn btn-primary" style="margin-top:1rem;">Каталог</a></div>{% endif %}
</div></div>
{% endblock %}'''

# ============================================================
# templates/client/my_services.html
# ============================================================
files['auto_salon_crm/templates/client/my_services.html'] = '''{% extends "base.html" %}
{% block title %}Сервис{% endblock %}
{% block content %}
<div class="page-header"><h1>🔧 Мои заявки в сервис</h1>
<a href="{{ url_for('client_new_service') }}" class="btn btn-primary">+ Новая заявка</a></div>
{% if new_form is defined and new_form %}
<div class="card" style="margin-bottom:2rem;"><div class="card-header">Новая заявка</div><div class="card-body">
<form method="POST" action="{{ url_for('client_new_service') }}">
    <div class="form-row"><div class="form-group"><label>Тип услуги</label><select name="service_type" class="form-control" required>
    {% for key, val in service_types.items() %}<option value="{{ key }}">{{ val }}</option>{% endfor %}</select></div>
    <div class="form-group"><label>VIN (если есть)</label><input type="text" name="car_vin" class="form-control"></div></div>
    <div class="form-group"><label>Описание</label><textarea name="description" class="form-control" rows="4" required></textarea></div>
    <button type="submit" class="btn btn-success">Отправить</button>
    <a href="{{ url_for('client_my_services') }}" class="btn btn-outline">Отмена</a>
</form></div></div>{% endif %}
<div class="card"><div class="card-body">
{% set services = current_user.service_requests %}
{% if services %}<table><thead><tr><th>№</th><th>Дата</th><th>Тип</th><th>Статус</th><th>Стоимость</th></tr></thead>
<tbody>{% for sr in services|sort(attribute='created_at', reverse=True) %}<tr><td>#{{ sr.id }}</td>
<td>{{ sr.created_at.strftime('%d.%m.%Y') }}</td><td>{{ sr.service_type_display }}</td>
<td><span class="badge badge-{{ sr.status }}">{{ sr.status_display }}</span></td>
<td>{{ format_price(sr.estimated_cost) if sr.estimated_cost else '—' }} ₽</td></tr>{% endfor %}</tbody></table>
{% else %}<div class="empty-state"><div class="icon">🔧</div><p>Нет заявок</p></div>{% endif %}
</div></div>
{% endblock %}'''

# ============================================================
# templates/client/profile.html
# ============================================================
files['auto_salon_crm/templates/client/profile.html'] = '''{% extends "base.html" %}
{% block title %}Профиль{% endblock %}
{% block content %}
<div class="page-header"><h1>👤 Мой профиль</h1></div>
<div class="grid-2">
<div class="card"><div class="card-header">Личные данные</div><div class="card-body">
<form method="POST">
    <div class="form-group"><label>ФИО</label><input type="text" name="full_name" class="form-control" value="{{ current_user.full_name }}" required></div>
    <div class="form-group"><label>Email</label><input type="email" name="email" class="form-control" value="{{ current_user.email }}" required></div>
    <div class="form-group"><label>Телефон</label><input type="text" name="phone" class="form-control" value="{{ current_user.phone or '' }}"></div>
    <button type="submit" class="btn btn-primary">Сохранить</button>
</form></div></div>
<div class="card"><div class="card-header">Аккаунт</div><div class="card-body"><div class="detail-grid" style="grid-template-columns:1fr;">
    <div class="detail-item"><span class="detail-label">Логин</span><span class="detail-value">{{ current_user.username }}</span></div>
    <div class="detail-item"><span class="detail-label">Роль</span><span class="detail-value">{{ current_user.role_display }}</span></div>
    <div class="detail-item"><span class="detail-label">Регистрация</span><span class="detail-value">{{ current_user.created_at.strftime('%d.%m.%Y') }}</span></div>
</div></div></div></div>
{% endblock %}'''

# ============================================================
# templates/sales/dashboard.html
# ============================================================
files['auto_salon_crm/templates/sales/dashboard.html'] = '''{% extends "base.html" %}
{% block title %}Отдел продаж{% endblock %}
{% block content %}
<div class="page-header"><h1>📊 Панель отдела продаж</h1></div>
<div class="stats-grid">
    <div class="stat-card primary"><span class="stat-label">Новые заказы</span><span class="stat-value">{{ new_orders }}</span></div>
    <div class="stat-card warning"><span class="stat-label">В обработке</span><span class="stat-value">{{ processing_orders }}</span></div>
    <div class="stat-card success"><span class="stat-label">Продаж за месяц</span><span class="stat-value">{{ total_this_month }}</span></div>
    <div class="stat-card info"><span class="stat-label">Выручка за месяц</span><span class="stat-value">{{ format_price(revenue_this_month) }} ₽</span></div>
</div>
<div class="card"><div class="card-header">Последние заказы <a href="{{ url_for('sales_orders') }}" class="btn btn-sm btn-outline">Все</a></div>
<div class="card-body"><table><thead><tr><th>№</th><th>Клиент</th><th>Авто</th><th>Статус</th><th>Сумма</th><th>Дата</th><th></th></tr></thead>
<tbody>{% for order in recent_orders %}<tr><td>#{{ order.id }}</td><td>{{ order.client.full_name }}</td><td>{{ order.car.full_name }}</td>
<td><span class="badge badge-{{ order.status }}">{{ order.status_display }}</span></td>
<td>{{ format_price(order.final_price) }} ₽</td><td>{{ order.created_at.strftime('%d.%m.%Y') }}</td>
<td><a href="{{ url_for('sales_order_detail', order_id=order.id) }}" class="btn btn-sm btn-outline">Открыть</a></td></tr>{% endfor %}</tbody></table></div></div>
{% endblock %}'''

# ============================================================
# templates/sales/orders.html
# ============================================================
files['auto_salon_crm/templates/sales/orders.html'] = '''{% extends "base.html" %}
{% block title %}Заказы — Продажи{% endblock %}
{% block content %}
<div class="page-header"><h1>📋 Заказы</h1><a href="{{ url_for('sales_new_order') }}" class="btn btn-primary">+ Новый</a></div>
<div class="filters"><div class="form-group"><label>Статус</label>
<select onchange="window.location.href='?status='+this.value" class="form-control"><option value="">Все</option>
{% for key, val in statuses.items() %}<option value="{{ key }}" {{ 'selected' if current_status == key }}>{{ val }}</option>{% endfor %}</select></div></div>
<div class="card"><div class="card-body">{% if orders %}<table><thead><tr><th>№</th><th>Клиент</th><th>Авто</th><th>Менеджер</th><th>Статус</th><th>Скидка</th><th>Итого</th><th>Дата</th><th></th></tr></thead>
<tbody>{% for order in orders %}<tr><td>#{{ order.id }}</td><td>{{ order.client.full_name }}</td><td>{{ order.car.full_name }}</td>
<td>{{ order.manager.full_name if order.manager else '—' }}</td><td><span class="badge badge-{{ order.status }}">{{ order.status_display }}</span></td>
<td>{{ format_price(order.discount) }} ₽</td><td><strong>{{ format_price(order.final_price) }} ₽</strong></td>
<td>{{ order.created_at.strftime('%d.%m.%Y') }}</td>
<td><a href="{{ url_for('sales_order_detail', order_id=order.id) }}" class="btn btn-sm btn-primary">Открыть</a></td></tr>{% endfor %}</tbody></table>
{% else %}<div class="empty-state"><p>Заказы не найдены</p></div>{% endif %}</div></div>
{% endblock %}'''

# ============================================================
# templates/sales/order_detail.html
# ============================================================
files['auto_salon_crm/templates/sales/order_detail.html'] = '''{% extends "base.html" %}
{% block title %}Заказ #{{ order.id }}{% endblock %}
{% block content %}
<div class="page-header"><h1>📋 Заказ #{{ order.id }}</h1><a href="{{ url_for('sales_orders') }}" class="btn btn-outline">← Назад</a></div>
<div class="grid-2">
<div class="card"><div class="card-header">Информация</div><div class="card-body"><div class="detail-grid">
    <div class="detail-item"><span class="detail-label">Клиент</span><span class="detail-value">{{ order.client.full_name }}</span></div>
    <div class="detail-item"><span class="detail-label">Телефон</span><span class="detail-value">{{ order.client.phone or '—' }}</span></div>
    <div class="detail-item"><span class="detail-label">Авто</span><span class="detail-value">{{ order.car.full_name }}</span></div>
    <div class="detail-item"><span class="detail-label">VIN</span><span class="detail-value">{{ order.car.vin }}</span></div>
    <div class="detail-item"><span class="detail-label">Цена</span><span class="detail-value">{{ format_price(order.total_price) }} ₽</span></div>
    <div class="detail-item"><span class="detail-label">Скидка</span><span class="detail-value">{{ format_price(order.discount) }} ₽</span></div>
    <div class="detail-item"><span class="detail-label">Итого</span><span class="detail-value" style="font-size:1.3rem;font-weight:700;color:var(--primary);">{{ format_price(order.final_price) }} ₽</span></div>
    <div class="detail-item"><span class="detail-label">Статус</span><span class="badge badge-{{ order.status }}">{{ order.status_display }}</span></div>
    <div class="detail-item"><span class="detail-label">Менеджер</span><span class="detail-value">{{ order.manager.full_name if order.manager else 'Не назначен' }}</span></div>
    <div class="detail-item"><span class="detail-label">Дата</span><span class="detail-value">{{ order.created_at.strftime('%d.%m.%Y %H:%M') }}</span></div>
</div></div></div>
<div>
{% if not order.manager_id %}<div class="card"><div class="card-body">
<form method="POST"><input type="hidden" name="action" value="assign">
<button type="submit" class="btn btn-success" style="width:100%;">✋ Взять в работу</button></form></div></div>{% endif %}
<div class="card"><div class="card-header">Изменить статус</div><div class="card-body">
<form method="POST"><input type="hidden" name="action" value="update_status">
<div class="form-group"><select name="status" class="form-control">{% for key, val in statuses.items() %}<option value="{{ key }}" {{ 'selected' if order.status == key }}>{{ val }}</option>{% endfor %}</select></div>
<div class="form-group"><label>Примечания</label><textarea name="notes" class="form-control" rows="3">{{ order.notes or '' }}</textarea></div>
<button type="submit" class="btn btn-primary">Обновить</button></form></div></div>
<div class="card"><div class="card-header">Скидка</div><div class="card-body">
<form method="POST"><input type="hidden" name="action" value="update_discount">
<div class="form-group"><label>Размер (₽)</label><input type="number" name="discount" class="form-control" value="{{ order.discount }}" min="0" step="1000"></div>
<button type="submit" class="btn btn-warning">Применить</button></form></div></div>
</div></div>
{% endblock %}'''

# ============================================================
# templates/sales/clients.html
# ============================================================
files['auto_salon_crm/templates/sales/clients.html'] = '''{% extends "base.html" %}
{% block title %}Клиенты{% endblock %}
{% block content %}
<div class="page-header"><h1>👥 Клиенты</h1></div>
<div class="card"><div class="card-body"><table><thead><tr><th>ФИО</th><th>Email</th><th>Телефон</th><th>Заказов</th><th>Регистрация</th></tr></thead>
<tbody>{% for client in clients %}<tr><td><strong>{{ client.full_name }}</strong></td><td>{{ client.email }}</td>
<td>{{ client.phone or '—' }}</td><td>{{ client.orders|length }}</td><td>{{ client.created_at.strftime('%d.%m.%Y') }}</td></tr>{% endfor %}</tbody></table></div></div>
{% endblock %}'''

# ============================================================
# templates/sales/new_order.html
# ============================================================
files['auto_salon_crm/templates/sales/new_order.html'] = '''{% extends "base.html" %}
{% block title %}Новый заказ{% endblock %}
{% block content %}
<div class="page-header"><h1>➕ Создать заказ</h1><a href="{{ url_for('sales_orders') }}" class="btn btn-outline">← Назад</a></div>
<div class="card"><div class="card-body"><form method="POST">
<div class="form-row">
    <div class="form-group"><label>Клиент</label><select name="client_id" class="form-control" required><option value="">Выберите</option>
    {% for c in clients %}<option value="{{ c.id }}">{{ c.full_name }} ({{ c.phone or c.email }})</option>{% endfor %}</select></div>
    <div class="form-group"><label>Автомобиль</label><select name="car_id" class="form-control" required><option value="">Выберите</option>
    {% for car in cars %}<option value="{{ car.id }}">{{ car.full_name }} — {{ format_price(car.price) }} ₽</option>{% endfor %}</select></div></div>
<div class="form-row">
    <div class="form-group"><label>Скидка (₽)</label><input type="number" name="discount" class="form-control" value="0" min="0" step="1000"></div>
    <div class="form-group"><label>Оплата</label><select name="payment_method" class="form-control">
    <option value="cash">Наличные</option><option value="card">Карта</option><option value="transfer">Перевод</option>
    <option value="credit">Кредит</option><option value="leasing">Лизинг</option></select></div></div>
<div class="form-group"><label>Примечания</label><textarea name="notes" class="form-control" rows="3"></textarea></div>
<button type="submit" class="btn btn-success">Создать</button></form></div></div>
{% endblock %}'''

# ============================================================
# templates/finance/dashboard.html
# ============================================================
files['auto_salon_crm/templates/finance/dashboard.html'] = '''{% extends "base.html" %}
{% block title %}Финансы{% endblock %}
{% block content %}
<div class="page-header"><h1>💰 Финансовый отдел</h1></div>
<div class="stats-grid">
    <div class="stat-card success"><span class="stat-label">Общая выручка</span><span class="stat-value">{{ format_price(total_revenue) }} ₽</span></div>
    <div class="stat-card primary"><span class="stat-label">За месяц</span><span class="stat-value">{{ format_price(monthly_revenue) }} ₽</span></div>
    <div class="stat-card warning"><span class="stat-label">Ожидающие</span><span class="stat-value">{{ pending_payments }}</span></div>
    <div class="stat-card info"><span class="stat-label">Ожидают оплаты</span><span class="stat-value">{{ orders_awaiting }}</span></div>
</div>
<div class="card"><div class="card-header">Последние платежи <a href="{{ url_for('finance_payments') }}" class="btn btn-sm btn-outline">Все</a></div>
<div class="card-body">{% if recent_payments %}<table><thead><tr><th>ID</th><th>Заказ</th><th>Сумма</th><th>Тип</th><th>Статус</th><th>Дата</th></tr></thead>
<tbody>{% for p in recent_payments %}<tr><td>#{{ p.id }}</td><td>#{{ p.order_id }}</td><td><strong>{{ format_price(p.amount) }} ₽</strong></td>
<td>{{ p.type_display }}</td><td><span class="badge badge-{{ p.status }}">{{ p.status_display }}</span></td>
<td>{{ p.created_at.strftime('%d.%m.%Y') }}</td></tr>{% endfor %}</tbody></table>
{% else %}<div class="empty-state"><p>Нет платежей</p></div>{% endif %}</div></div>
{% endblock %}'''

# ============================================================
# templates/finance/payments.html
# ============================================================
files['auto_salon_crm/templates/finance/payments.html'] = '''{% extends "base.html" %}
{% block title %}Платежи{% endblock %}
{% block content %}
<div class="page-header"><h1>💳 Платежи</h1><a href="{{ url_for('finance_new_payment') }}" class="btn btn-primary">+ Новый</a></div>
<div class="filters"><div class="form-group"><label>Статус</label>
<select onchange="window.location.href='?status='+this.value" class="form-control"><option value="">Все</option>
{% for key, val in statuses.items() %}<option value="{{ key }}" {{ 'selected' if current_status == key }}>{{ val }}</option>{% endfor %}</select></div></div>
<div class="card"><div class="card-body">{% if payments %}<table><thead><tr><th>ID</th><th>Заказ</th><th>Клиент</th><th>Сумма</th><th>Тип</th><th>Статус</th><th>Дата</th><th></th></tr></thead>
<tbody>{% for p in payments %}<tr><td>#{{ p.id }}</td><td>#{{ p.order_id }}</td><td>{{ p.order.client.full_name }}</td>
<td><strong>{{ format_price(p.amount) }} ₽</strong></td><td>{{ p.type_display }}</td>
<td><span class="badge badge-{{ p.status }}">{{ p.status_display }}</span></td><td>{{ p.created_at.strftime('%d.%m.%Y') }}</td>
<td>{% if p.status == 'pending' %}
<form method="POST" action="{{ url_for('finance_update_payment', payment_id=p.id) }}" style="display:inline;"><input type="hidden" name="status" value="completed"><button class="btn btn-sm btn-success">Провести</button></form>
<form method="POST" action="{{ url_for('finance_update_payment', payment_id=p.id) }}" style="display:inline;"><input type="hidden" name="status" value="cancelled"><button class="btn btn-sm btn-danger">Отмена</button></form>
{% endif %}</td></tr>{% endfor %}</tbody></table>
{% else %}<div class="empty-state"><p>Не найдено</p></div>{% endif %}</div></div>
{% endblock %}'''

# ============================================================
# templates/finance/new_payment.html
# ============================================================
files['auto_salon_crm/templates/finance/new_payment.html'] = '''{% extends "base.html" %}
{% block title %}Новый платёж{% endblock %}
{% block content %}
<div class="page-header"><h1>➕ Создать платёж</h1><a href="{{ url_for('finance_payments') }}" class="btn btn-outline">← Назад</a></div>
<div class="card"><div class="card-body"><form method="POST">
<div class="form-row">
    <div class="form-group"><label>Заказ</label><select name="order_id" class="form-control" required><option value="">Выберите</option>
    {% for order in orders %}<option value="{{ order.id }}">#{{ order.id }} — {{ order.client.full_name }} — {{ order.car.full_name }} ({{ format_price(order.final_price) }} ₽)</option>{% endfor %}</select></div>
    <div class="form-group"><label>Сумма (₽)</label><input type="number" name="amount" class="form-control" required min="0" step="0.01"></div></div>
<div class="form-row">
    <div class="form-group"><label>Тип</label><select name="payment_type" class="form-control" required>
    {% for key, val in payment_types.items() %}<option value="{{ key }}">{{ val }}</option>{% endfor %}</select></div>
    <div class="form-group"><label>Статус</label><select name="status" class="form-control">
    <option value="pending">Ожидает</option><option value="completed">Проведён</option></select></div></div>
<div class="form-group"><label>Описание</label><textarea name="description" class="form-control" rows="3"></textarea></div>
<button type="submit" class="btn btn-success">Создать</button></form></div></div>
{% endblock %}'''

# ============================================================
# templates/finance/reports.html
# ============================================================
files['auto_salon_crm/templates/finance/reports.html'] = '''{% extends "base.html" %}
{% block title %}Отчёты{% endblock %}
{% block content %}
<div class="page-header"><h1>📊 Финансовые отчёты</h1></div>
<div class="stats-grid"><div class="stat-card info"><span class="stat-label">Стоимость склада</span><span class="stat-value">{{ format_price(total_cars_cost) }} ₽</span></div></div>
<div class="grid-2">
<div class="card"><div class="card-header">По месяцам</div><div class="card-body">{% if payments_by_month %}<table><thead><tr><th>Месяц</th><th>Сумма</th></tr></thead>
<tbody>{% for row in payments_by_month %}<tr><td>{{ row.month }}</td><td><strong>{{ format_price(row.total) }} ₽</strong></td></tr>{% endfor %}</tbody></table>
{% else %}<div class="empty-state"><p>Нет данных</p></div>{% endif %}</div></div>
<div class="card"><div class="card-header">По типам оплаты</div><div class="card-body">{% if payments_by_type %}<table><thead><tr><th>Тип</th><th>Кол-во</th><th>Сумма</th></tr></thead>
<tbody>{% for row in payments_by_type %}<tr><td>{{ type_choices.get(row.payment_type, row.payment_type) }}</td><td>{{ row.count }}</td>
<td><strong>{{ format_price(row.total) }} ₽</strong></td></tr>{% endfor %}</tbody></table>
{% else %}<div class="empty-state"><p>Нет данных</p></div>{% endif %}</div></div></div>
{% endblock %}'''

# ============================================================
# templates/logistics/dashboard.html
# ============================================================
files['auto_salon_crm/templates/logistics/dashboard.html'] = '''{% extends "base.html" %}
{% block title %}Логистика{% endblock %}
{% block content %}
<div class="page-header"><h1>📦 Логистика и склад</h1></div>
<div class="stats-grid">
    <div class="stat-card primary"><span class="stat-label">Всего авто</span><span class="stat-value">{{ total_cars }}</span></div>
    <div class="stat-card success"><span class="stat-label">На складе</span><span class="stat-value">{{ in_stock }}</span></div>
    <div class="stat-card warning"><span class="stat-label">В пути</span><span class="stat-value">{{ in_transit }}</span></div>
    <div class="stat-card info"><span class="stat-label">Зарезервировано</span><span class="stat-value">{{ reserved }}</span></div>
    <div class="stat-card danger"><span class="stat-label">Активных поставок</span><span class="stat-value">{{ active_deliveries }}</span></div>
</div>
<div class="card"><div class="card-header">Последние поставки <a href="{{ url_for('logistics_deliveries') }}" class="btn btn-sm btn-outline">Все</a></div>
<div class="card-body">{% if recent_deliveries %}<table><thead><tr><th>ID</th><th>Авто</th><th>Поставщик</th><th>Дата</th><th>Статус</th></tr></thead>
<tbody>{% for d in recent_deliveries %}<tr><td>#{{ d.id }}</td><td>{{ d.car.full_name if d.car else '—' }}</td><td>{{ d.supplier }}</td>
<td>{{ d.expected_date.strftime('%d.%m.%Y') }}</td><td><span class="badge badge-{{ d.status }}">{{ d.status_display }}</span></td></tr>{% endfor %}</tbody></table>
{% else %}<div class="empty-state"><p>Нет поставок</p></div>{% endif %}</div></div>
<div class="btn-group" style="margin-top:1rem;"><a href="{{ url_for('logistics_add_car') }}" class="btn btn-primary">+ Авто</a>
<a href="{{ url_for('logistics_new_delivery') }}" class="btn btn-info">+ Поставка</a></div>
{% endblock %}'''

# ============================================================
# templates/logistics/warehouse.html
# ============================================================
files['auto_salon_crm/templates/logistics/warehouse.html'] = '''{% extends "base.html" %}
{% block title %}Склад{% endblock %}
{% block content %}
<div class="page-header"><h1>🏪 Склад</h1><a href="{{ url_for('logistics_add_car') }}" class="btn btn-primary">+ Добавить</a></div>
<div class="filters"><div class="form-group"><label>Статус</label>
<select onchange="window.location.href='?status='+this.value" class="form-control"><option value="">Все</option>
{% for key, val in statuses.items() %}<option value="{{ key }}" {{ 'selected' if current_status == key }}>{{ val }}</option>{% endfor %}</select></div></div>
<div class="card"><div class="card-body">{% if cars %}<table><thead><tr><th>ID</th><th>Марка/Модель</th><th>Год</th><th>Цвет</th><th>VIN</th><th>Цена</th><th>Закупка</th><th>Статус</th><th></th></tr></thead>
<tbody>{% for car in cars %}<tr><td>#{{ car.id }}</td><td><strong>{{ car.brand }} {{ car.model }}</strong></td><td>{{ car.year }}</td><td>{{ car.color }}</td>
<td><code>{{ car.vin }}</code></td><td>{{ format_price(car.price) }} ₽</td><td>{{ format_price(car.purchase_price) }} ₽</td>
<td><span class="badge badge-{{ car.status }}">{{ car.status_display }}</span></td>
<td><a href="{{ url_for('logistics_edit_car', car_id=car.id) }}" class="btn btn-sm btn-outline">Ред.</a></td></tr>{% endfor %}</tbody></table>
{% else %}<div class="empty-state"><p>Не найдено</p></div>{% endif %}</div></div>
{% endblock %}'''

# ============================================================
# templates/logistics/car_form.html
# ============================================================
files['auto_salon_crm/templates/logistics/car_form.html'] = '''{% extends "base.html" %}
{% block title %}{{ 'Редактировать' if car else 'Добавить' }} авто{% endblock %}
{% block content %}
<div class="page-header"><h1>{{ '✏️ Редактировать' if car else '➕ Добавить' }} автомобиль</h1>
<a href="{{ url_for('logistics_warehouse') }}" class="btn btn-outline">← Назад</a></div>
<div class="card"><div class="card-body"><form method="POST">
<div class="form-row">
    <div class="form-group"><label>Марка</label><input type="text" name="brand" class="form-control" value="{{ car.brand if car else '' }}" required></div>
    <div class="form-group"><label>Модель</label><input type="text" name="model" class="form-control" value="{{ car.model if car else '' }}" required></div>
    <div class="form-group"><label>Год</label><input type="number" name="year" class="form-control" value="{{ car.year if car else 2024 }}" required></div></div>
<div class="form-row">
    <div class="form-group"><label>Цвет</label><input type="text" name="color" class="form-control" value="{{ car.color if car else '' }}" required></div>
    <div class="form-group"><label>VIN</label><input type="text" name="vin" class="form-control" value="{{ car.vin if car else '' }}" required maxlength="17"></div>
    <div class="form-group"><label>Пробег</label><input type="number" name="mileage" class="form-control" value="{{ car.mileage if car else 0 }}"></div></div>
<div class="form-row">
    <div class="form-group"><label>Двигатель</label><select name="engine_type" class="form-control" required>
    {% for et in ['Бензин','Дизель','Гибрид','Электро','Газ'] %}<option value="{{ et }}" {{ 'selected' if car and car.engine_type == et }}>{{ et }}</option>{% endfor %}</select></div>
    <div class="form-group"><label>Объём (л)</label><input type="number" name="engine_volume" class="form-control" value="{{ car.engine_volume if car else '' }}" step="0.1"></div>
    <div class="form-group"><label>Мощность (л.с.)</label><input type="number" name="horsepower" class="form-control" value="{{ car.horsepower if car else '' }}"></div></div>
<div class="form-row">
    <div class="form-group"><label>КПП</label><select name="transmission" class="form-control" required>
    {% for tr in ['Автомат','Механика','Робот','Вариатор'] %}<option value="{{ tr }}" {{ 'selected' if car and car.transmission == tr }}>{{ tr }}</option>{% endfor %}</select></div>
    <div class="form-group"><label>Привод</label><select name="drive_type" class="form-control">
    {% for dt in ['Передний','Задний','Полный'] %}<option value="{{ dt }}" {{ 'selected' if car and car.drive_type == dt }}>{{ dt }}</option>{% endfor %}</select></div>
    <div class="form-group"><label>Статус</label><select name="status" class="form-control">
    {% for key, val in [('in_stock','На складе'),('in_transit','В пути'),('in_service','На обслуживании')] %}<option value="{{ key }}" {{ 'selected' if car and car.status == key }}>{{ val }}</option>{% endfor %}</select></div></div>
<div class="form-row">
    <div class="form-group"><label>Цена продажи (₽)</label><input type="number" name="price" class="form-control" value="{{ car.price if car else '' }}" required step="1000"></div>
    <div class="form-group"><label>Закупочная (₽)</label><input type="number" name="purchase_price" class="form-control" value="{{ car.purchase_price if car else '' }}" step="1000"></div></div>
<div class="form-group"><label>Описание</label><textarea name="description" class="form-control" rows="3">{{ car.description if car else '' }}</textarea></div>
<button type="submit" class="btn btn-success">{{ 'Сохранить' if car else 'Добавить' }}</button></form></div></div>
{% endblock %}'''

# ============================================================
# templates/logistics/deliveries.html
# ============================================================
files['auto_salon_crm/templates/logistics/deliveries.html'] = '''{% extends "base.html" %}
{% block title %}Поставки{% endblock %}
{% block content %}
<div class="page-header"><h1>🚚 Поставки</h1><a href="{{ url_for('logistics_new_delivery') }}" class="btn btn-primary">+ Новая</a></div>
<div class="filters"><div class="form-group"><label>Статус</label>
<select onchange="window.location.href='?status='+this.value" class="form-control"><option value="">Все</option>
{% for key, val in statuses.items() %}<option value="{{ key }}" {{ 'selected' if current_status == key }}>{{ val }}</option>{% endfor %}</select></div></div>
<div class="card"><div class="card-body">{% if deliveries %}<table><thead><tr><th>ID</th><th>Авто</th><th>Поставщик</th><th>Трек</th><th>Ожид.</th><th>Факт.</th><th>Статус</th><th></th></tr></thead>
<tbody>{% for d in deliveries %}<tr><td>#{{ d.id }}</td><td>{{ d.car.full_name if d.car else '—' }}</td><td>{{ d.supplier }}</td>
<td>{{ d.tracking_number or '—' }}</td><td>{{ d.expected_date.strftime('%d.%m.%Y') }}</td>
<td>{{ d.actual_date.strftime('%d.%m.%Y') if d.actual_date else '—' }}</td>
<td><span class="badge badge-{{ d.status }}">{{ d.status_display }}</span></td>
<td>{% if d.status == 'planned' %}<form method="POST" action="{{ url_for('logistics_update_delivery', delivery_id=d.id) }}" style="display:inline;">
<input type="hidden" name="status" value="in_transit"><button class="btn btn-sm btn-warning">В пути</button></form>
{% elif d.status == 'in_transit' %}<form method="POST" action="{{ url_for('logistics_update_delivery', delivery_id=d.id) }}" style="display:inline;">
<input type="hidden" name="status" value="delivered"><button class="btn btn-sm btn-success">Доставлена</button></form>{% endif %}</td></tr>{% endfor %}</tbody></table>
{% else %}<div class="empty-state"><p>Не найдено</p></div>{% endif %}</div></div>
{% endblock %}'''

# ============================================================
# templates/logistics/delivery_form.html
# ============================================================
files['auto_salon_crm/templates/logistics/delivery_form.html'] = '''{% extends "base.html" %}
{% block title %}Новая поставка{% endblock %}
{% block content %}
<div class="page-header"><h1>➕ Новая поставка</h1><a href="{{ url_for('logistics_deliveries') }}" class="btn btn-outline">← Назад</a></div>
<div class="card"><div class="card-body"><form method="POST">
<div class="form-row">
    <div class="form-group"><label>Автомобиль</label><select name="car_id" class="form-control" required><option value="">Выберите</option>
    {% for car in cars %}<option value="{{ car.id }}">{{ car.full_name }} ({{ car.vin }})</option>{% endfor %}</select></div>
    <div class="form-group"><label>Поставщик</label><input type="text" name="supplier" class="form-control" required></div></div>
<div class="form-row">
    <div class="form-group"><label>Ожидаемая дата</label><input type="date" name="expected_date" class="form-control" required></div>
    <div class="form-group"><label>Трек-номер</label><input type="text" name="tracking_number" class="form-control"></div></div>
<div class="form-group"><label>Примечания</label><textarea name="notes" class="form-control" rows="3"></textarea></div>
<button type="submit" class="btn btn-success">Создать</button></form></div></div>
{% endblock %}'''

# ============================================================
# templates/service/dashboard.html
# ============================================================
files['auto_salon_crm/templates/service/dashboard.html'] = '''{% extends "base.html" %}
{% block title %}Сервис{% endblock %}
{% block content %}
<div class="page-header"><h1>🔧 Сервис и тех. служба</h1></div>
<div class="stats-grid">
    <div class="stat-card primary"><span class="stat-label">Новые</span><span class="stat-value">{{ new_requests }}</span></div>
    <div class="stat-card warning"><span class="stat-label">В работе</span><span class="stat-value">{{ in_progress }}</span></div>
    <div class="stat-card info"><span class="stat-label">Мои задачи</span><span class="stat-value">{{ my_tasks }}</span></div>
    <div class="stat-card success"><span class="stat-label">Завершено сегодня</span><span class="stat-value">{{ completed_today }}</span></div>
</div>
<div class="card"><div class="card-header">Последние заявки <a href="{{ url_for('service_requests') }}" class="btn btn-sm btn-outline">Все</a></div>
<div class="card-body">{% if recent %}<table><thead><tr><th>ID</th><th>Клиент</th><th>Тип</th><th>Приоритет</th><th>Статус</th><th>Дата</th><th></th></tr></thead>
<tbody>{% for sr in recent %}<tr><td>#{{ sr.id }}</td><td>{{ sr.client.full_name }}</td><td>{{ sr.service_type_display }}</td>
<td><span class="badge badge-{{ sr.priority }}">{{ sr.priority_display }}</span></td>
<td><span class="badge badge-{{ sr.status }}">{{ sr.status_display }}</span></td>
<td>{{ sr.created_at.strftime('%d.%m.%Y') }}</td>
<td><a href="{{ url_for('service_request_detail', req_id=sr.id) }}" class="btn btn-sm btn-outline">Открыть</a></td></tr>{% endfor %}</tbody></table>
{% else %}<div class="empty-state"><p>Нет заявок</p></div>{% endif %}</div></div>
{% endblock %}'''

# ============================================================
# templates/service/requests.html
# ============================================================
files['auto_salon_crm/templates/service/requests.html'] = '''{% extends "base.html" %}
{% block title %}Заявки на сервис{% endblock %}
{% block content %}
<div class="page-header"><h1>📋 Заявки</h1><a href="{{ url_for('service_new_request') }}" class="btn btn-primary">+ Новая</a></div>
<div class="filters">
    <div class="form-group"><label>Статус</label><select onchange="window.location.href='?status='+this.value+'&view={{ view }}'" class="form-control">
    <option value="">Все</option>{% for key, val in statuses.items() %}<option value="{{ key }}" {{ 'selected' if current_status == key }}>{{ val }}</option>{% endfor %}</select></div>
    <div class="form-group"><label>Показать</label><select onchange="window.location.href='?view='+this.value+'&status={{ current_status }}'" class="form-control">
    <option value="all" {{ 'selected' if view == 'all' }}>Все</option><option value="my" {{ 'selected' if view == 'my' }}>Мои</option></select></div>
</div>
<div class="card"><div class="card-body">{% if requests %}<table><thead><tr><th>ID</th><th>Клиент</th><th>Тип</th><th>Приоритет</th><th>Статус</th><th>Исполнитель</th><th>Дата</th><th></th></tr></thead>
<tbody>{% for sr in requests %}<tr><td>#{{ sr.id }}</td><td>{{ sr.client.full_name }}</td><td>{{ sr.service_type_display }}</td>
<td><span class="badge badge-{{ sr.priority }}">{{ sr.priority_display }}</span></td>
<td><span class="badge badge-{{ sr.status }}">{{ sr.status_display }}</span></td>
<td>{{ sr.assigned_to.full_name if sr.assigned_to else '—' }}</td><td>{{ sr.created_at.strftime('%d.%m.%Y') }}</td>
<td><a href="{{ url_for('service_request_detail', req_id=sr.id) }}" class="btn btn-sm btn-primary">Открыть</a></td></tr>{% endfor %}</tbody></table>
{% else %}<div class="empty-state"><p>Не найдено</p></div>{% endif %}</div></div>
{% endblock %}'''

# ============================================================
# templates/service/request_detail.html
# ============================================================
files['auto_salon_crm/templates/service/request_detail.html'] = '''{% extends "base.html" %}
{% block title %}Заявка #{{ sr.id }}{% endblock %}
{% block content %}
<div class="page-header"><h1>🔧 Заявка #{{ sr.id }}</h1><a href="{{ url_for('service_requests') }}" class="btn btn-outline">← Назад</a></div>
<div class="grid-2">
<div class="card"><div class="card-header">Информация</div><div class="card-body"><div class="detail-grid">
    <div class="detail-item"><span class="detail-label">Клиент</span><span class="detail-value">{{ sr.client.full_name }}</span></div>
    <div class="detail-item"><span class="detail-label">Телефон</span><span class="detail-value">{{ sr.client.phone or '—' }}</span></div>
    <div class="detail-item"><span class="detail-label">Тип</span><span class="detail-value">{{ sr.service_type_display }}</span></div>
    <div class="detail-item"><span class="detail-label">Приоритет</span><span class="badge badge-{{ sr.priority }}">{{ sr.priority_display }}</span></div>
    <div class="detail-item"><span class="detail-label">Статус</span><span class="badge badge-{{ sr.status }}">{{ sr.status_display }}</span></div>
    <div class="detail-item"><span class="detail-label">Исполнитель</span><span class="detail-value">{{ sr.assigned_to.full_name if sr.assigned_to else 'Не назначен' }}</span></div>
    <div class="detail-item"><span class="detail-label">VIN</span><span class="detail-value">{{ sr.car_vin or '—' }}</span></div>
    <div class="detail-item"><span class="detail-label">Дата</span><span class="detail-value">{{ sr.created_at.strftime('%d.%m.%Y %H:%M') }}</span></div>
    <div class="detail-item"><span class="detail-label">Оценка</span><span class="detail-value">{{ format_price(sr.estimated_cost) if sr.estimated_cost else '—' }} ₽</span></div>
    <div class="detail-item"><span class="detail-label">Факт</span><span class="detail-value">{{ format_price(sr.actual_cost) if sr.actual_cost else '—' }} ₽</span></div>
</div><div style="margin-top:1rem;"><span class="detail-label">Описание</span><p>{{ sr.description }}</p></div>
{% if sr.notes %}<div style="margin-top:1rem;"><span class="detail-label">Примечания</span><p>{{ sr.notes }}</p></div>{% endif %}</div></div>
<div>
{% if not sr.assigned_to_id %}<div class="card"><div class="card-body"><form method="POST"><input type="hidden" name="action" value="assign">
<button type="submit" class="btn btn-success" style="width:100%;">✋ Взять в работу</button></form></div></div>{% endif %}
<div class="card"><div class="card-header">Статус</div><div class="card-body"><form method="POST"><input type="hidden" name="action" value="update_status">
<div class="form-group"><select name="status" class="form-control">{% for key, val in statuses.items() %}<option value="{{ key }}" {{ 'selected' if sr.status == key }}>{{ val }}</option>{% endfor %}</select></div>
<div class="form-group"><label>Дата записи</label><input type="date" name="scheduled_date" class="form-control" value="{{ sr.scheduled_date.strftime('%Y-%m-%d') if sr.scheduled_date else '' }}"></div>
<div class="form-group"><label>Примечания</label><textarea name="notes" class="form-control" rows="3">{{ sr.notes or '' }}</textarea></div>
<button type="submit" class="btn btn-primary">Обновить</button></form></div></div>
<div class="card"><div class="card-header">Стоимость</div><div class="card-body"><form method="POST"><input type="hidden" name="action" value="update_cost">
<div class="form-group"><label>Оценка (₽)</label><input type="number" name="estimated_cost" class="form-control" value="{{ sr.estimated_cost or '' }}" step="100"></div>
<div class="form-group"><label>Факт (₽)</label><input type="number" name="actual_cost" class="form-control" value="{{ sr.actual_cost or '' }}" step="100"></div>
<button type="submit" class="btn btn-warning">Обновить</button></form></div></div>
</div></div>
{% endblock %}'''

# ============================================================
# templates/service/new_request.html
# ============================================================
files['auto_salon_crm/templates/service/new_request.html'] = '''{% extends "base.html" %}
{% block title %}Новая заявка{% endblock %}
{% block content %}
<div class="page-header"><h1>➕ Новая заявка</h1><a href="{{ url_for('service_requests') }}" class="btn btn-outline">← Назад</a></div>
<div class="card"><div class="card-body"><form method="POST">
<div class="form-row">
    <div class="form-group"><label>Клиент</label><select name="client_id" class="form-control" required><option value="">Выберите</option>
    {% for c in clients %}<option value="{{ c.id }}">{{ c.full_name }} ({{ c.phone or c.email }})</option>{% endfor %}</select></div>
    <div class="form-group"><label>Тип</label><select name="service_type" class="form-control" required>
    {% for key, val in service_types.items() %}<option value="{{ key }}">{{ val }}</option>{% endfor %}</select></div></div>
<div class="form-row">
    <div class="form-group"><label>Автомобиль</label><select name="car_id" class="form-control"><option value="">Не выбран</option>
    {% for car in cars %}<option value="{{ car.id }}">{{ car.full_name }} ({{ car.vin }})</option>{% endfor %}</select></div>
    <div class="form-group"><label>VIN (если не из базы)</label><input type="text" name="car_vin" class="form-control"></div></div>
<div class="form-row">
    <div class="form-group"><label>Приоритет</label><select name="priority" class="form-control">
    {% for key, val in priorities.items() %}<option value="{{ key }}" {{ 'selected' if key == 'normal' }}>{{ val }}</option>{% endfor %}</select></div>
    <div class="form-group"><label>Дата записи</label><input type="date" name="scheduled_date" class="form-control"></div>
    <div class="form-group"><label>Оценка (₽)</label><input type="number" name="estimated_cost" class="form-control" step="100"></div></div>
<div class="form-group"><label>Описание</label><textarea name="description" class="form-control" rows="4" required></textarea></div>
<button type="submit" class="btn btn-success">Создать</button></form></div></div>
{% endblock %}'''

# ============================================================
# templates/management/dashboard.html
# ============================================================
files['auto_salon_crm/templates/management/dashboard.html'] = '''{% extends "base.html" %}
{% block title %}Руководство{% endblock %}
{% block content %}
<div class="page-header"><h1>🏢 Панель руководства</h1></div>
<div class="stats-grid">
    <div class="stat-card primary"><span class="stat-label">Всего авто</span><span class="stat-value">{{ total_cars }}</span></div>
    <div class="stat-card success"><span class="stat-label">На складе</span><span class="stat-value">{{ cars_in_stock }}</span></div>
    <div class="stat-card info"><span class="stat-label">Клиентов</span><span class="stat-value">{{ total_clients }}</span></div>
    <div class="stat-card warning"><span class="stat-label">Заказов</span><span class="stat-value">{{ total_orders }}</span></div>
    <div class="stat-card success"><span class="stat-label">Завершённых</span><span class="stat-value">{{ completed_orders }}</span></div>
    <div class="stat-card primary"><span class="stat-label">Общая выручка</span><span class="stat-value">{{ format_price(total_revenue) }} ₽</span></div>
    <div class="stat-card info"><span class="stat-label">За месяц</span><span class="stat-value">{{ format_price(monthly_revenue) }} ₽</span></div>
    <div class="stat-card warning"><span class="stat-label">Стоимость склада</span><span class="stat-value">{{ format_price(stock_value) }} ₽</span></div>
    <div class="stat-card danger"><span class="stat-label">Сервис (активные)</span><span class="stat-value">{{ pending_services }}</span></div>
    <div class="stat-card info"><span class="stat-label">Поставок в пути</span><span class="stat-value">{{ active_deliveries }}</span></div>
    <div class="stat-card primary"><span class="stat-label">Сотрудников</span><span class="stat-value">{{ total_employees }}</span></div>
</div>
<div class="card"><div class="card-header">Быстрые действия</div><div class="card-body"><div class="btn-group">
    <a href="{{ url_for('management_all_orders') }}" class="btn btn-primary">📋 Заказы</a>
    <a href="{{ url_for('management_users') }}" class="btn btn-info">👥 Пользователи</a>
    <a href="{{ url_for('management_analytics') }}" class="btn btn-success">📊 Аналитика</a>
</div></div></div>
{% endblock %}'''

# ============================================================
# templates/management/users.html
# ============================================================
files['auto_salon_crm/templates/management/users.html'] = '''{% extends "base.html" %}
{% block title %}Пользователи{% endblock %}
{% block content %}
<div class="page-header"><h1>👥 Пользователи</h1></div>
<div class="filters"><div class="form-group"><label>Роль</label>
<select onchange="window.location.href='?role='+this.value" class="form-control"><option value="">Все</option>
{% for key, val in roles.items() %}<option value="{{ key }}" {{ 'selected' if current_role == key }}>{{ val }}</option>{% endfor %}</select></div></div>
<div class="card"><div class="card-body"><table><thead><tr><th>ID</th><th>ФИО</th><th>Логин</th><th>Email</th><th>Телефон</th><th>Роль</th><th>Активен</th><th>Действия</th></tr></thead>
<tbody>{% for user in users %}<tr><td>{{ user.id }}</td><td><strong>{{ user.full_name }}</strong></td><td>{{ user.username }}</td><td>{{ user.email }}</td>
<td>{{ user.phone or '—' }}</td><td><span class="badge badge-{{ user.role }}">{{ user.role_display }}</span></td>
<td>{% if user.is_active %}<span class="badge badge-completed">Да</span>{% else %}<span class="badge badge-cancelled">Нет</span>{% endif %}</td>
<td><div class="btn-group">
<form method="POST" action="{{ url_for('management_toggle_user', user_id=user.id) }}" style="display:inline;">
<button type="submit" class="btn btn-sm {{ 'btn-danger' if user.is_active else 'btn-success' }}">{{ 'Деактив.' if user.is_active else 'Активир.' }}</button></form>
<form method="POST" action="{{ url_for('management_change_role', user_id=user.id) }}" style="display:inline-flex;gap:0.25rem;">
<select name="role" class="form-control" style="width:auto;padding:0.3rem;">{% for key, val in roles.items() %}
<option value="{{ key }}" {{ 'selected' if user.role == key }}>{{ val }}</option>{% endfor %}</select>
<button type="submit" class="btn btn-sm btn-outline">Сменить</button></form></div></td></tr>{% endfor %}</tbody></table></div></div>
{% endblock %}'''

# ============================================================
# templates/management/analytics.html
# ============================================================
files['auto_salon_crm/templates/management/analytics.html'] = '''{% extends "base.html" %}
{% block title %}Аналитика{% endblock %}
{% block content %}
<div class="page-header"><h1>📊 Аналитика</h1></div>
<div class="grid-2">
<div class="card"><div class="card-header">По маркам</div><div class="card-body">{% if sales_by_brand %}<table><thead><tr><th>Марка</th><th>Продано</th><th>Выручка</th></tr></thead>
<tbody>{% for row in sales_by_brand %}<tr><td><strong>{{ row.brand }}</strong></td><td>{{ row.count }}</td><td>{{ format_price(row.revenue) }} ₽</td></tr>{% endfor %}</tbody></table>
{% else %}<div class="empty-state"><p>Нет данных</p></div>{% endif %}</div></div>
<div class="card"><div class="card-header">По месяцам</div><div class="card-body">{% if sales_by_month %}<table><thead><tr><th>Месяц</th><th>Продано</th><th>Выручка</th></tr></thead>
<tbody>{% for row in sales_by_month %}<tr><td>{{ row.month }}</td><td>{{ row.count }}</td><td>{{ format_price(row.revenue) }} ₽</td></tr>{% endfor %}</tbody></table>
{% else %}<div class="empty-state"><p>Нет данных</p></div>{% endif %}</div></div>
<div class="card"><div class="card-header">Сервис</div><div class="card-body">{% if service_stats %}<table><thead><tr><th>Тип</th><th>Кол-во</th></tr></thead>
<tbody>{% for row in service_stats %}<tr><td>{{ service_types.get(row.service_type, row.service_type) }}</td><td>{{ row.count }}</td></tr>{% endfor %}</tbody></table>
{% else %}<div class="empty-state"><p>Нет данных</p></div>{% endif %}</div></div>
<div class="card"><div class="card-header">Топ менеджеров</div><div class="card-body">{% if top_managers %}<table><thead><tr><th>Менеджер</th><th>Продаж</th><th>Выручка</th></tr></thead>
<tbody>{% for row in top_managers %}<tr><td><strong>{{ row.full_name }}</strong></td><td>{{ row.orders_count }}</td><td>{{ format_price(row.total_revenue) }} ₽</td></tr>{% endfor %}</tbody></table>
{% else %}<div class="empty-state"><p>Нет данных</p></div>{% endif %}</div></div></div>
{% endblock %}'''

# ============================================================
# templates/management/all_orders.html
# ============================================================
files['auto_salon_crm/templates/management/all_orders.html'] = '''{% extends "base.html" %}
{% block title %}Все заказы{% endblock %}
{% block content %}
<div class="page-header"><h1>📋 Все заказы</h1></div>
<div class="filters"><div class="form-group"><label>Статус</label>
<select onchange="window.location.href='?status='+this.value" class="form-control"><option value="">Все</option>
{% for key, val in statuses.items() %}<option value="{{ key }}" {{ 'selected' if current_status == key }}>{{ val }}</option>{% endfor %}</select></div></div>
<div class="card"><div class="card-body">{% if orders %}<table><thead><tr><th>№</th><th>Клиент</th><th>Авто</th><th>Менеджер</th><th>Статус</th><th>Итого</th><th>Дата</th></tr></thead>
<tbody>{% for order in orders %}<tr><td><strong>#{{ order.id }}</strong></td><td>{{ order.client.full_name }}</td><td>{{ order.car.full_name }}</td>
<td>{{ order.manager.full_name if order.manager else '—' }}</td><td><span class="badge badge-{{ order.status }}">{{ order.status_display }}</span></td>
<td><strong>{{ format_price(order.final_price) }} ₽</strong></td><td>{{ order.created_at.strftime('%d.%m.%Y %H:%M') }}</td></tr>{% endfor %}</tbody></table>
{% else %}<div class="empty-state"><p>Не найдено</p></div>{% endif %}</div></div>
{% endblock %}'''

# ============================================================
# Создаём ZIP-архив
# ============================================================
zip_filename = 'auto_salon_crm.zip'

with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
    for filepath, content in files.items():
        zf.writestr(filepath, content)

print(f"✅ Архив '{zip_filename}' успешно создан!")
print(f"📦 Файлов в архиве: {len(files)}")
print()
print("=== Инструкция по запуску ===")
print(f"1. Распакуйте: unzip {zip_filename}")
print("2. cd auto_salon_crm")
print("3. pip install -r requirements.txt")
print("4. python init_db.py")
print("5. python app.py")
print("6. Откройте http://127.0.0.1:5000")
print()
print("=== Логины ===")
print("admin / password123      — Руководство")
print("sales1 / password123     — Отдел продаж")
print("finance1 / password123   — Финансы")
print("logistics1 / password123 — Логистика")
print("service1 / password123   — Сервис")
print("client1 / password123    — Клиент")
