import os
from datetime import datetime, timedelta
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'onbarber-secret-key-futurista-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///onbarber.db'

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def save_uploaded_file(file, prefix='file'):
  if not file or file.filename == '':
    return None
  os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
  ext = os.path.splitext(file.filename)[1].lower()
  if not ext:
    ext = '.jpg'
  timestamp = int(datetime.now().timestamp())
  filename = f'{prefix}_{timestamp}{ext}'
  filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
  file.save(filepath)
  return url_for('static', filename=f'uploads/{filename}')


# --- CONFIGURAÇÃO DE TEMAS E FUNDOS ---
THEMES = [
    {
        'id': 'emerald',
        'name': 'Emerald Neon',
        'primary': '#10b981',
        'bg_gradient': 'from-emerald-500 to-teal-700',
    },
    {
        'id': 'cyan',
        'name': 'Cyber Cyan',
        'primary': '#06b6d4',
        'bg_gradient': 'from-cyan-500 to-blue-600',
    },
    {
        'id': 'purple',
        'name': 'Purple Haze',
        'primary': '#a855f7',
        'bg_gradient': 'from-purple-600 to-indigo-800',
    },
    {
        'id': 'gold',
        'name': 'Imperial Gold',
        'primary': '#eab308',
        'bg_gradient': 'from-yellow-500 to-amber-700',
    },
    {
        'id': 'crimson',
        'name': 'Crimson Red',
        'primary': '#ef4444',
        'bg_gradient': 'from-red-600 to-rose-800',
    },
]

BACKGROUNDS = {
    'preto': {
        'name': 'Preto Absoluto',
        'bg_class': 'bg-[#121214]',
        'card_bg': 'bg-[#1a1a1e]',
        'sidebar_bg': 'bg-[#18181b]',
        'text_color': 'text-gray-100',
    },
    'branco': {
        'name': 'Branco Limpo',
        'bg_class': 'bg-gray-100',
        'card_bg': 'bg-white',
        'sidebar_bg': 'bg-white',
        'text_color': 'text-gray-900',
    },
    'cinza': {
        'name': 'Cinza Metálico',
        'bg_class': 'bg-zinc-900',
        'card_bg': 'bg-zinc-800',
        'sidebar_bg': 'bg-zinc-950',
        'text_color': 'text-zinc-100',
    },
    'dourado': {
        'name': 'Dourado Escuro',
        'bg_class': 'bg-[#1a1814]',
        'card_bg': 'bg-[#26221c]',
        'sidebar_bg': 'bg-[#1f1b16]',
        'text_color': 'text-amber-100',
    },
    'roxo': {
        'name': 'Roxo Noturno',
        'bg_class': 'bg-[#13111c]',
        'card_bg': 'bg-[#1c1829]',
        'sidebar_bg': 'bg-[#161322]',
        'text_color': 'text-purple-100',
    },
}


# --- MODELOS ---
class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  email = db.Column(db.String(100), unique=True, nullable=False)
  password = db.Column(db.String(200), nullable=False)
  role = db.Column(db.String(20), nullable=False)
  balance = db.Column(db.Float, default=0.0)
  points = db.Column(db.Integer, default=0)
  bio = db.Column(
      db.Text, default='Profissional focado em proporcionar a melhor experiência.'
  )
  theme_id = db.Column(db.String(30), default='emerald')
  bg_id = db.Column(db.String(30), default='preto')
  avatar_url = db.Column(
      db.String(300),
      default='https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&q=80&w=200',
  )

  barbershop = db.relationship(
      'Barbershop', backref='owner', uselist=False, cascade='all, delete'
  )
  appointments_as_client = db.relationship(
      'Appointment', foreign_keys='Appointment.client_id', backref='client'
  )
  appointments_as_barber = db.relationship(
      'Appointment', foreign_keys='Appointment.barber_id', backref='barber'
  )
  deposits = db.relationship(
      'DepositRequest', backref='client', cascade='all, delete'
  )


class Barbershop(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  image_url = db.Column(
      db.String(300),
      default='https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&q=80&w=400',
  )
  theme_id = db.Column(db.String(30), default='emerald')
  bg_id = db.Column(db.String(30), default='preto')
  barber_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class AdminSettings(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  pix_qrcode_url = db.Column(db.String(300), nullable=True)


class Appointment(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  barber_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  service_name = db.Column(db.String(100), default='Corte Simples')
  date = db.Column(db.String(20), nullable=False)
  time = db.Column(db.String(10), nullable=False)
  price = db.Column(db.Float, default=35.00)
  points_earned = db.Column(db.Integer, default=6)
  status = db.Column(db.String(20), default='Confirmado')
  payment_method = db.Column(db.String(30), default='Na Barbearia')
  is_paid = db.Column(db.Boolean, default=False)


class DepositRequest(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  amount = db.Column(db.Float, nullable=False)
  status = db.Column(db.String(20), default='Pendente')
  created_at = db.Column(
      db.String(30), default=lambda: datetime.now().strftime('%d/%m/%Y %H:%M')
  )


class PlanConfig(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  price_text = db.Column(db.String(50), nullable=False)
  description = db.Column(db.String(250), nullable=False)
  features = db.Column(db.Text, nullable=False)


@login_manager.user_loader
def load_user(user_id):
  return db.session.get(User, int(user_id))


@app.context_processor
def inject_theme():
  theme_styles = {
      'emerald': {
          'text': 'text-emerald-400',
          'border': 'border-emerald-500',
          'bg_10': 'bg-emerald-500/10',
          'badge': 'bg-emerald-500/20 text-emerald-400',
      },
      'cyan': {
          'text': 'text-cyan-400',
          'border': 'border-cyan-500',
          'bg_10': 'bg-cyan-500/10',
          'badge': 'bg-cyan-500/20 text-cyan-400',
      },
      'purple': {
          'text': 'text-purple-400',
          'border': 'border-purple-500',
          'bg_10': 'bg-purple-500/10',
          'badge': 'bg-purple-500/20 text-purple-400',
      },
      'gold': {
          'text': 'text-amber-400',
          'border': 'border-amber-500',
          'bg_10': 'bg-amber-500/10',
          'badge': 'bg-amber-500/20 text-amber-400',
      },
      'crimson': {
          'text': 'text-rose-400',
          'border': 'border-rose-500',
          'bg_10': 'bg-rose-500/10',
          'badge': 'bg-rose-500/20 text-rose-400',
      },
  }

  active_theme = theme_styles['emerald']
  active_bg = BACKGROUNDS['preto']
  shop_name = 'OnBarber'

  if current_user.is_authenticated:
    if current_user.theme_id in theme_styles:
      active_theme = theme_styles[current_user.theme_id]
    if current_user.bg_id in BACKGROUNDS:
      active_bg = BACKGROUNDS[current_user.bg_id]

    if current_user.role == 'barber' and current_user.barbershop:
      shop_name = current_user.barbershop.name
    elif current_user.role == 'client':
      shop = Barbershop.query.first()
      if shop:
        shop_name = shop.name

  admin_settings = AdminSettings.query.first()
  global_pix = admin_settings.pix_qrcode_url if admin_settings else None

  return dict(
      theme=active_theme,
      bg_style=active_bg,
      custom_shop_name=shop_name,
      global_pix=global_pix,
  )


SERVICES = {
    'corte': {'name': 'Corte Simples', 'price': 35.00, 'points': 6},
    'corte_barba': {'name': 'Corte e Barba', 'price': 60.00, 'points': 12},
    'corte_barba_hidra': {
        'name': 'Corte, Barba e Hidratação',
        'price': 90.00,
        'points': 20,
    },
}


@app.route('/')
def index():
  if current_user.is_authenticated:
    if current_user.role == 'admin':
      return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'barber':
      return redirect(url_for('barber_inicio'))
    else:
      return redirect(url_for('client_dashboard'))
  return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
      login_user(user)
      return redirect(url_for('index'))
    flash('E-mail ou senha incorretos!', 'error')
  return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    name = request.form.get('name')
    email = request.form.get('email')
    password = generate_password_hash(request.form.get('password'))
    role = request.form.get('role')
    theme_id = request.form.get('theme_id', 'emerald')
    bg_id = request.form.get('bg_id', 'preto')

    if User.query.filter_by(email=email).first():
      flash('Este e-mail já está cadastrado.', 'error')
      return redirect(url_for('register'))

    avatar_url = 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&q=80&w=200'
    if 'avatar' in request.files:
      uploaded_url = save_uploaded_file(
          request.files['avatar'], prefix=f'user_{datetime.now().microsecond}'
      )
      if uploaded_url:
        avatar_url = uploaded_url

    new_user = User(
        name=name,
        email=email,
        password=password,
        role=role,
        theme_id=theme_id,
        bg_id=bg_id,
        avatar_url=avatar_url,
    )
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)

    if role == 'barber':
      return redirect(url_for('add_barbershop'))
    return redirect(url_for('client_dashboard'))

  return render_template(
      'register.html', themes=THEMES, backgrounds=BACKGROUNDS
  )


@app.route('/add-barbershop', methods=['GET', 'POST'])
@login_required
def add_barbershop():
  if current_user.role != 'barber':
    return redirect(url_for('index'))
  if current_user.barbershop:
    return redirect(url_for('barber_inicio'))

  if request.method == 'POST':
    name = request.form.get('name')
    theme_id = request.form.get('theme_id', 'emerald')
    bg_id = request.form.get('bg_id', 'preto')

    image_url = 'https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&q=80&w=400'
    if 'shop_image' in request.files:
      uploaded_url = save_uploaded_file(
          request.files['shop_image'], prefix=f'shop_{current_user.id}'
      )
      if uploaded_url:
        image_url = uploaded_url

    shop = Barbershop(
        name=name,
        image_url=image_url,
        theme_id=theme_id,
        bg_id=bg_id,
        barber_id=current_user.id,
    )
    db.session.add(shop)
    db.session.commit()
    db.session.refresh(current_user)
    return redirect(url_for('barber_inicio'))

  return render_template(
      'add_barbershop.html', themes=THEMES, backgrounds=BACKGROUNDS
  )


# --- ADMIN DASHBOARD ---
@app.route('/admin/dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
  if current_user.role != 'admin':
    return redirect(url_for('index'))

  admin_settings = AdminSettings.query.first()
  if not admin_settings:
    admin_settings = AdminSettings()
    db.session.add(admin_settings)
    db.session.commit()

  if request.method == 'POST':
    if 'admin_pix' in request.files:
      uploaded_url = save_uploaded_file(
          request.files['admin_pix'], prefix='admin_pix_global'
      )
      if uploaded_url:
        admin_settings.pix_qrcode_url = uploaded_url
        db.session.commit()
        flash('QR Code geral do Admin atualizado com sucesso!', 'success')
        return redirect(url_for('admin_dashboard'))

  barbers = User.query.filter_by(role='barber').all()
  clients = User.query.filter_by(role='client').all()
  appointments = Appointment.query.all()
  pending_deposits = DepositRequest.query.filter_by(status='Pendente').all()
  all_deposits = DepositRequest.query.order_by(
      DepositRequest.id.desc()
  ).all()

  return render_template(
      'admin_dashboard.html',
      barbers=barbers,
      clients=clients,
      appointments=appointments,
      pending_deposits=pending_deposits,
      all_deposits=all_deposits,
      admin_settings=admin_settings,
  )


@app.route('/admin/deposit/<int:id>/<action>')
@login_required
def process_deposit(id, action):
  if current_user.role != 'admin':
    return redirect(url_for('index'))

  dep = DepositRequest.query.get_or_404(id)
  if dep.status == 'Pendente':
    if action == 'approve':
      dep.status = 'Aprovado'
      dep.client.balance += dep.amount
      flash(
          f'Depósito de R$ {dep.amount:.2f} aprovado para {dep.client.name}!',
          'success',
      )
    elif action == 'reject':
      dep.status = 'Recusado'
      flash(f'Depósito de R$ {dep.amount:.2f} recusado.', 'error')
    db.session.commit()
  return redirect(url_for('admin_dashboard'))


# --- PAINEL DO BARBEIRO ---
@app.route('/barber/inicio')
@login_required
def barber_inicio():
  if current_user.role != 'barber':
    return redirect(url_for('index'))

  filter_type = request.args.get('filter', 'month')
  today_dt = datetime.now()
  today_str = today_dt.strftime('%Y-%m-%d')

  all_appts = Appointment.query.filter_by(barber_id=current_user.id).all()
  
  # Considera válido se estiver Concluído ou se já foi pago pelo app (mesmo que ainda esteja como Confirmado)
  valid_appts = [
      a for a in all_appts if a.status == 'Concluído' or (a.status == 'Confirmado' and a.is_paid)
  ]

  daily_rev = sum([a.price for a in valid_appts if a.date == today_str])
  week_ago_dt = today_dt - timedelta(days=7)
  weekly_rev = sum(
      [a.price for a in valid_appts if a.date >= week_ago_dt.strftime('%Y-%m-%d')]
  )
  monthly_rev = sum([a.price for a in valid_appts])

  if filter_type == 'day':
    filtered_appointments = [a for a in valid_appts if a.date == today_str]
    filter_title = f'Cortes de Hoje ({today_str})'
  elif filter_type == 'week':
    filtered_appointments = [
        a for a in valid_appts if a.date >= week_ago_dt.strftime('%Y-%m-%d')
    ]
    filter_title = 'Cortes da Última Semana'
  else:
    filtered_appointments = valid_appts
    filter_title = 'Cortes do Mês'

  chart_labels, chart_data = [], []
  for i in range(6, -1, -1):
    day_target = today_dt - timedelta(days=i)
    day_str = day_target.strftime('%Y-%m-%d')
    chart_labels.append(day_target.strftime('%d/%m'))
    chart_data.append(sum([a.price for a in valid_appts if a.date == day_str]))

  return render_template(
      'barber_inicio.html',
      daily_rev=daily_rev,
      weekly_rev=weekly_rev,
      monthly_rev=monthly_rev,
      filtered_appointments=filtered_appointments,
      filter_title=filter_title,
      current_filter=filter_type,
      chart_labels=chart_labels,
      chart_data=chart_data,
  )


@app.route('/barber/agendamentos')
@login_required
def barber_agendamentos():
  if current_user.role != 'barber':
    return redirect(url_for('index'))
  selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
  all_times = [
      '09:00',
      '10:00',
      '11:00',
      '13:00',
      '14:00',
      '15:00',
      '16:00',
      '17:00',
      '18:00',
      '19:00',
  ]
  booked = (
      Appointment.query.filter_by(barber_id=current_user.id, date=selected_date)
      .filter(Appointment.status.in_(['Confirmado', 'Concluído']))
      .all()
  )
  booked_times = [b.time for b in booked]
  appointments = (
      Appointment.query.filter_by(barber_id=current_user.id)
      .order_by(Appointment.date.desc())
      .all()
  )
  clients_ranking = (
      User.query.filter_by(role='client')
      .order_by(User.points.desc())
      .limit(10)
      .all()
  )
  return render_template(
      'barber_agendamentos.html',
      selected_date=selected_date,
      all_times=all_times,
      booked_times=booked_times,
      appointments=appointments,
      clients_ranking=clients_ranking,
  )


@app.route('/barber/complete-appointment/<int:id>')
@login_required
def complete_appointment(id):
  app_item = Appointment.query.get_or_404(id)
  if app_item.barber_id == current_user.id and app_item.status == 'Confirmado':
    app_item.status = 'Concluído'
    app_item.client.points += app_item.points_earned
    db.session.commit()
    flash(
        f'Corte concluído! {app_item.points_earned} pontos creditados.',
        'success',
    )
  return redirect(request.referrer or url_for('barber_agendamentos'))


# --- PLANOS E EDIÇÃO ---
@app.route('/shared/planos', methods=['GET', 'POST'])
@login_required
def shared_planos():
  if request.method == 'POST' and (
      current_user.role == 'barber' or current_user.role == 'admin'
  ):
    plan_id = request.form.get('plan_id')
    title = request.form.get('title')
    price_text = request.form.get('price_text')
    description = request.form.get('description')
    features = request.form.get('features')

    plan = PlanConfig.query.get(plan_id)
    if plan:
      plan.title = title
      plan.price_text = price_text
      plan.description = description
      plan.features = features
      db.session.commit()
      flash('Plano atualizado com sucesso!', 'success')
    return redirect(url_for('shared_planos'))

  plans = PlanConfig.query.all()
  if not plans:
    p1 = PlanConfig(
        title='Plano Pro',
        price_text='R$ 49,90 /mês',
        description='Agendamentos ilimitados e benefícios exclusivos.',
        features='Atendimento Prioritário\nPontuação Dobrada nos Cortes\nSuporte VIP 24/7',
    )
    p2 = PlanConfig(
        title='Plano VIP Gold',
        price_text='R$ 119,90 /mês',
        description='Plano completo com descontos em serviços parceiros.',
        features='Desconto de 20% em todos os cortes\nReserva de horário VIP garantida\nBrindes mensais na barbearia',
    )
    db.session.add_all([p1, p2])
    db.session.commit()
    plans = PlanConfig.query.all()

  return render_template('planos.html', plans=plans)


@app.route('/barber/perfil', methods=['GET', 'POST'])
@login_required
def barber_perfil():
  if current_user.role != 'barber':
    return redirect(url_for('index'))

  if request.method == 'POST':
    bio = request.form.get('bio')
    theme_id = request.form.get('theme_id')
    bg_id = request.form.get('bg_id')

    current_user.bio = bio
    if theme_id:
      current_user.theme_id = theme_id
    if bg_id:
      current_user.bg_id = bg_id

    if 'avatar' in request.files:
      up = save_uploaded_file(
          request.files['avatar'], prefix=f'avatar_{current_user.id}'
      )
      if up:
        current_user.avatar_url = up

    db.session.commit()
    flash('Perfil atualizado com sucesso!', 'success')
    return redirect(url_for('barber_perfil'))

  return render_template(
      'barber_perfil.html', themes=THEMES, backgrounds=BACKGROUNDS
  )


# --- PAINEL DO CLIENTE ---
@app.route('/client/dashboard', methods=['GET', 'POST'])
@login_required
def client_dashboard():
  if current_user.role != 'client':
    return redirect(url_for('index'))

  barbers = User.query.filter_by(role='barber').all()
  selected_barber_id = request.args.get('barber_id', type=int)
  selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
  all_times = [
      '09:00',
      '10:00',
      '11:00',
      '13:00',
      '14:00',
      '15:00',
      '16:00',
      '17:00',
      '18:00',
      '19:00',
  ]
  booked_times = []

  if selected_barber_id:
    booked = (
        Appointment.query.filter_by(
            barber_id=selected_barber_id, date=selected_date
        )
        .filter(Appointment.status.in_(['Confirmado', 'Concluído']))
        .all()
    )
    booked_times = [b.time for b in booked]

  if request.method == 'POST':
    barber_id = request.form.get('barber_id')
    date = request.form.get('date')
    time = request.form.get('time')
    service_key = request.form.get('service_key', 'corte')
    pay_with_balance = request.form.get('pay_with_balance') == 'on'

    service_info = SERVICES.get(service_key, SERVICES['corte'])
    price = service_info['price']
    points_earned = service_info['points']
    service_name = service_info['name']

    exists = (
        Appointment.query.filter_by(
            barber_id=barber_id, date=date, time=time
        )
        .filter(Appointment.status.in_(['Confirmado', 'Concluído']))
        .first()
    )
    if exists:
      flash('Este horário acabou de ser reservado.', 'error')
      return redirect(
          url_for('client_dashboard', barber_id=barber_id, date=date)
      )

    is_paid = False
    payment_method = 'Na Barbearia'
    if pay_with_balance:
      if current_user.balance >= price:
        current_user.balance -= price
        is_paid = True
        payment_method = 'Saldo da Conta'
        points_earned *= 2
      else:
        flash('Saldo insuficiente!', 'error')
        return redirect(
            url_for('client_dashboard', barber_id=barber_id, date=date)
        )

    new_app = Appointment(
        barber_id=barber_id,
        client_id=current_user.id,
        service_name=service_name,
        date=date,
        time=time,
        price=price,
        points_earned=points_earned,
        payment_method=payment_method,
        is_paid=is_paid,
    )
    db.session.add(new_app)
    db.session.commit()
    flash(f'Agendamento ({service_name}) realizado com sucesso!', 'success')
    return redirect(
        url_for('client_dashboard', barber_id=barber_id, date=date)
    )

  my_appointments = (
      Appointment.query.filter_by(client_id=current_user.id)
      .order_by(Appointment.id.desc())
      .all()
  )
  clients_ranking = (
      User.query.filter_by(role='client')
      .order_by(User.points.desc())
      .limit(10)
      .all()
  )
  return render_template(
      'client_dashboard.html',
      barbers=barbers,
      selected_barber_id=selected_barber_id,
      selected_date=selected_date,
      all_times=all_times,
      booked_times=booked_times,
      my_appointments=my_appointments,
      clients_ranking=clients_ranking,
      services=SERVICES,
  )


@app.route('/client/deposit', methods=['GET', 'POST'])
@login_required
def client_deposit():
  if current_user.role != 'client':
    return redirect(url_for('index'))

  if request.method == 'POST':
    try:
      amount = float(request.form.get('amount', 0))
      if amount > 0:
        dep = DepositRequest(client_id=current_user.id, amount=amount)
        db.session.add(dep)
        db.session.commit()
        flash(
            'Solicitação de depósito enviada com sucesso! Aguarde a aprovação'
            ' do administrador.',
            'success',
        )
      else:
        flash('Digite um valor válido.', 'error')
    except ValueError:
      flash('Valor inválido.', 'error')
    return redirect(url_for('client_deposit'))

  my_deposits = (
      DepositRequest.query.filter_by(client_id=current_user.id)
      .order_by(DepositRequest.id.desc())
      .all()
  )
  return render_template('client_deposit.html', my_deposits=my_deposits)


@app.route('/client/perfil')
@login_required
def client_perfil():
  if current_user.role != 'client':
    return redirect(url_for('index'))
  return render_template('client_perfil.html')


@app.route('/appointment/cancel/<int:id>')
@login_required
def cancel_appointment(id):
  app_item = Appointment.query.get_or_404(id)
  if (
      current_user.role == 'admin'
      or app_item.barber_id == current_user.id
      or app_item.client_id == current_user.id
  ):
    if app_item.is_paid and app_item.status in ['Confirmado', 'Concluído']:
      app_item.client.balance += app_item.price
    app_item.status = 'Cancelado'
    db.session.commit()
    flash('Agendamento cancelado com sucesso.', 'success')
  return redirect(request.referrer or url_for('index'))


@app.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('login'))


if __name__ == '__main__':
  with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@onbarber.com').first():
      admin = User(
          name='Valdiney França',
          email='admin@onbarber.com',
          password=generate_password_hash('123456'),
          role='admin',
      )
      db.session.add(admin)
      db.session.commit()
  app.run(debug=True, port=5000)