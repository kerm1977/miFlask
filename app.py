# IMPORTS
from flask import Flask, render_template, request, redirect, url_for, flash, session  # Agrega 'session' aquí  # Importa las funciones necesarias de Flask (Todas las rutas y render_template dependen de esto)
from flask_migrate import Migrate  # Importa Migrate para manejar migraciones de la base de datos (Depende de db y app)
from werkzeug.security import generate_password_hash, check_password_hash # Importa funciones para manejar contraseñas seguras (Depende de la clase User)
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user # Importa funciones para manejar la autenticación de usuarios (Depende de la clase User y app)
from flask_sqlalchemy import SQLAlchemy # Importa SQLAlchemy para interactuar con la base de datos (Depende de app)
from werkzeug.utils import secure_filename # Importa secure_filename para manejar archivos cargados de forma segura (Depende de las rutas que manejan images)
import os # Importa el módulo os para interactuar con el sistema operativo (Depende de app.secret_key y rutas de images)
from datetime import datetime, timedelta
import sqlite3
from sqlalchemy import or_
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, TimeField, FloatField, IntegerField, BooleanField, FileField, SubmitField
from wtforms.validators import DataRequired
import requests
import secrets #videos
import math
import secrets
from flask import send_from_directory #Permite ver la imagen en los users
# from recuperacion_contraseña import crear_modulo_recuperacion_contraseña # Importacion del modulo.
from urllib.parse import urlparse
import csv
from flask import send_file
from io import BytesIO, StringIO # Add this line to import BytesIO and StringIO.
import io
# PARA TRABAJAR CON PDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# RECUPERACION DE CONTRASEÑA EN CASO DE QUE NO FUNCIONE BORRAR
# RECUPERACION DE CONTRASEÑA EN CASO DE QUE NO FUNCIONE BORRAR
# BORRAR TAMBIEN reset_password, RESTABLECER CONTRASEÑA
# recuperacion_contraseña forgot_password
import smtplib
from email.mime.text import MIMEText


# CONFIG BASE DE DATOS
app = Flask(__name__)  # Crea una instancia de la aplicación Flask (Todas las rutas y configuraciones dependen de esto)


# pip install pysqlite3 --user


#CONFIGURACIÓN PARA LA BASE DE DATOS LOCAL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db' # Configura la URI de la base de datos (Depende de db) LOCALMENTE
UPLOAD_FOLDER ="static/images"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



#CONFIGURACIÓN PARA LA BASE PYTHONANYWHARE
# USERNAME = os.environ.get('USERNAME')
# if USERNAME is None:
#     USERNAME = 'kenth1977'  # **FORZANDO EL NOMBRE DE USUARIO PARA PRUEBAS**
# DATABASE_NAME = 'kenth1977$db'  # El nombre de tu base de datos en PythonAnywhere
# DATABASE_PATH = f'/home/{USERNAME}/{DATABASE_NAME}'
# app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'

# # Ruta absoluta a la carpeta static/images
# UPLOAD_FOLDER = os.path.join('/home', USERNAME, 'MI_APP_FLASK', 'static', 'images')
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Desactiva el seguimiento de modificaciones de SQLAlchemy (Depende de db)
app.secret_key = os.urandom(24) # Genera una clave secreta para la sesión (Depende de flask_login)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} # Define las extensiones de archivo permitidas (Depende de las rutas de images)
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS # Configura las extensiones permitidas en la aplicación (Depende de rutas que manejan images)
#db = SQLAlchemy(app) # Crea una instancia de SQLAlchemy asociada a la aplicación (Depende de app y configura la base de datos)
login_manager = LoginManager() # Crea una instancia de LoginManager para manejar la autenticación (Depende de app)
login_manager.init_app(app) # Inicializa LoginManager con la aplicación (Depende de app)
login_manager.login_view = 'login' # Define la vista de inicio de sesión (Depende de flask_login)
migrate = Migrate(app, db) # Inicializa Migrate para manejar migraciones de la base de datos (Depende de db y app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    first_last_name = db.Column(db.String(100), nullable=False)
    second_last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    avatar = db.Column(db.String(200))
    registration_count = db.Column(db.Integer, default=0)
    posts = db.relationship('Post', backref='author', lazy=True)
    reset_token = db.Column(db.String(100), nullable=True)  # Añadido
    reset_token_expiration = db.Column(db.DateTime, nullable=True)  # Añadido
    nombre_archivo = db.Column(db.String(255))

    # RECUPERADOR DE CONTRASEÑAS
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# RECUPERACION DE CONTRASEÑA EN CASO DE QUE NO FUNCIONE BORRAR
# RECUPERACION DE CONTRASEÑA EN CASO DE QUE NO FUNCIONE BORRAR
    def generate_reset_token(self):  # Añadido
        self.reset_token = secrets.token_urlsafe(16)
        self.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        return self.reset_token

    def reset_token_is_valid(self):  # Añadido
        return self.reset_token_expiration and self.reset_token_expiration > datetime.utcnow()

    def reset_password(self, password):  # Añadido
        self.set_password(password)
        self.reset_token = None
        self.reset_token_expiration = None
        db.session.commit()
    # RECUPERADOR DE CONTRASEÑAS

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #Relacion con el usuario, para saber quien lo creo.
    user_email = db.Column(db.String(120), nullable=True) # Agrega este campo
    fecha_salida = db.Column(db.Date, nullable=True)
    dificultad = db.Column(db.String(20), nullable=True)
    capacidad_buseta = db.Column(db.Integer, nullable=True)
    capacidad_total = db.Column(db.Integer, nullable=True)
    distancia = db.Column(db.Float, nullable=True)
    lugar_salida = db.Column(db.String(100), nullable=True)
    hora_salida = db.Column(db.Time, nullable=True)
    recogemos_en = db.Column(db.Text, nullable=True)
    tipoTerreno = db.Column(db.Text, nullable=True)
    requiere_estadía = db.Column(db.String(3), nullable=True)
    animales = db.Column(db.String(3), nullable=True)
    duchas = db.Column(db.String(10), nullable=True)
    banos = db.Column(db.String(3), nullable=True)
    bastones = db.Column(db.String(50), nullable=True)
    guantes = db.Column(db.String(10), nullable=True)
    tipo_calzado = db.Column(db.String(20), nullable=True)
    repelente = db.Column(db.String(10), nullable=True)
    bloqueador = db.Column(db.String(10), nullable=True)
    liquido = db.Column(db.String(10), nullable=True)
    snacks = db.Column(db.String(10), nullable=True)
    ropa_cambio = db.Column(db.String(10), nullable=True)
    precio_colones = db.Column(db.Float, nullable=True) # Nuevo campo para el precio en colones

class Contacto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido1 = db.Column(db.String(80), nullable=False)
    apellido2 = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    celular = db.Column(db.String(20))
    empresa = db.Column(db.String(120))
    categoria = db.Column(db.String(80))
    avatar = db.Column(db.String(200), default='img/default.png')

class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    completada = db.Column(db.Boolean, default=False)

@login_manager.user_loader # Define una función para cargar el usuario desde la base de datos (Depende de User y db)
def load_user(user_id):
    return User.query.get(int(user_id)) # Obtiene el usuario de la base de datos

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    detail = db.Column(db.Text)
    video_url = db.Column(db.String(200))
    image_url = db.Column(db.String(200))  # Nuevo campo para la URL de la imagen






@app.route("/")
@app.route("/home")
@app.route("/index")
def index():
    title = "Caminatas"
    page = request.args.get('page', 1, type=int)
    per_page = 5
    posts_pagination = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=per_page)

    for post in posts_pagination.items:
        # Imprime los IDs y tipos de datos para depuración
        if current_user.is_authenticated:
            print(f"current_user.id: {current_user.id}, type: {type(current_user.id)}")
        else:
            print("Usuario no autenticado")
        print(f"post.user_id: {post.user_id}, type: {type(post.user_id)}")

        # Asegura que user_id sea un entero
        post.user_id = int(post.user_id) if post.user_id else None

    return render_template('index.html', posts_pagination=posts_pagination, title=title)

# version
@app.route('/version', methods=['GET', 'POST'])
def version():
    if request.method == 'POST':
        if 'titulo' in request.form:
            titulo = request.form['titulo']
            nueva_tarea = Tarea(titulo=titulo)
            db.session.add(nueva_tarea)
            db.session.commit()
            return redirect(url_for('version'))  # Redirigir después de agregar

    tareas = Tarea.query.all()
    return render_template('version.html', tareas=tareas)

@app.route('/version/completar/<int:tarea_id>', methods=['POST'])
def completar_tarea(tarea_id):
    tarea = Tarea.query.get_or_404(tarea_id)
    tarea.completada = not tarea.completada
    db.session.commit()
    return redirect(url_for('version'))

@app.route('/version/borrar/<int:tarea_id>', methods=['POST'])
def borrar_tarea(tarea_id):
    tarea = Tarea.query.get_or_404(tarea_id)
    db.session.delete(tarea)
    db.session.commit()
    return redirect(url_for('version'))
# versionn








# VER IMAGENES Y POSTS
@app.route('/post/<int:post_id>')
def post(post_id):
    title = "Caminatas"
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post, title=title)

@app.route('/new', methods=['GET', 'POST'])
@login_required
def new_post():
    titulo = "Crear Un Nuevo Post"
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image = request.files.get('image')
        category = request.form.get('category')
        tags = request.form.get('tags')
        is_published = True if request.form.get('is_published') else False
        summary = request.form.get('summary')
        fecha_salida_str = request.form.get('fecha_salida')
        # Convertir la cadena de fecha a un objeto datetime.date si no está vacío
        fecha_salida = datetime.strptime(fecha_salida_str, '%Y-%m-%d').date() if fecha_salida_str else None
        dificultad = request.form.get('dificultad')
        capacidad_buseta = request.form.get('capacidad_buseta')
        capacidad_total = request.form.get('capacidad_total')
        distancia = request.form.get('distancia')
        lugar_salida = request.form.get('lugar_salida')
        hora_salida_str = request.form.get('hora_salida')
        hora_salida = datetime.strptime(hora_salida_str, '%H:%M').time() if hora_salida_str else None
        recogemos_en = request.form.get('recogemos_en')
        tipoTerreno = request.form.get('tipoTerreno')
        requiere_estadía = request.form.get('requiere_estadía')
        animales = request.form.get('animales')
        duchas = request.form.get('duchas')
        banos = request.form.get('banos')
        bastones = request.form.get('bastones')
        guantes = request.form.get('guantes')
        tipo_calzado = request.form.get('tipo_calzado')
        repelente = request.form.get('repelente')
        bloqueador = request.form.get('bloqueador')
        liquido = request.form.get('liquido')
        snacks = request.form.get('snacks')
        ropa_cambio = request.form.get('ropa_cambio')
        precio_colones = request.form.get('precio_colones', type=float) # Obtener el precio en colones, asegurándose que sea float
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

        if image and image.filename != '':
            if len(image.read(512)) > app.config['MAX_CONTENT_LENGTH']:
                flash("El archivo es demasiado grande.", 'danger')
                return render_template('new_post.html')

            image.seek(0)

            if allowed_file(image.filename):
                filename = secure_filename(image.filename)
                try:
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    post = Post(title=title, content=content, image=filename, date_posted=datetime.utcnow(), user_id=current_user.id, user_email=current_user.email,
                                fecha_salida=fecha_salida, dificultad=dificultad, capacidad_buseta=capacidad_buseta, capacidad_total=capacidad_total,
                                distancia=distancia, lugar_salida=lugar_salida, hora_salida=hora_salida, recogemos_en=recogemos_en, tipoTerreno=tipoTerreno,
                                requiere_estadía=requiere_estadía, animales=animales, duchas=duchas, banos=banos, bastones=bastones, guantes=guantes,
                                tipo_calzado=tipo_calzado, repelente=repelente, bloqueador=bloqueador, liquido=liquido, snacks=snacks, ropa_cambio=ropa_cambio, precio_colones=precio_colones)
                    db.session.add(post)
                    db.session.commit()
                    flash('Publicación creada con éxito', 'success')
                    return redirect(url_for('index'))
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error al crear la publicación: {e}', 'danger')
                    return render_template('new_post.html', error=str(e))
            else:
                flash("Archivo no permitido", "danger")
                return render_template('new_post.html')

        else:
            post = Post(title=title, content=content, image=None, date_posted=datetime.utcnow(), user_id=current_user.id, user_email=current_user.email,
                        fecha_salida=fecha_salida, dificultad=dificultad, capacidad_buseta=capacidad_buseta, capacidad_total=capacidad_total,
                        distancia=distancia, lugar_salida=lugar_salida, hora_salida=hora_salida, recogemos_en=recogemos_en, tipoTerreno=tipoTerreno,
                        requiere_estadía=requiere_estadía, animales=animales, duchas=duchas, banos=banos, bastones=bastones, guantes=guantes,
                        tipo_calzado=tipo_calzado, repelente=repelente, bloqueador=bloqueador, liquido=liquido, snacks=snacks, ropa_cambio=ropa_cambio, precio_colones=precio_colones)
            try:
                db.session.add(post)
                db.session.commit()
                flash('Publicación creada con éxito', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error al crear la publicación: {e}', 'danger')
                return render_template('new_post.html', error=str(e))

    return render_template('new_post.html', titulo=titulo)

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    titulo = "Editar el Post"
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash("No tienes permiso para editar este post.", "danger")
        return redirect(url_for('post', post_id=post.id))

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.category = request.form.get('category')
        post.tags = request.form.get('tags')
        post.is_published = True if request.form.get('is_published') else False
        post.summary = request.form.get('summary')
        fecha_salida_str = request.form.get('fecha_salida')
        # Convertir la cadena de fecha a un objeto datetime.date si no está vacío
        post.fecha_salida = datetime.strptime(fecha_salida_str, '%Y-%m-%d').date() if fecha_salida_str else None
        post.dificultad = request.form.get('dificultad')
        post.capacidad_buseta = request.form.get('capacidad_buseta')
        post.capacidad_total = request.form.get('capacidad_total')
        post.distancia = request.form.get('distancia')
        post.lugar_salida = request.form.get('lugar_salida')
        hora_salida_str = request.form.get('hora_salida')
        post.hora_salida = datetime.strptime(hora_salida_str, '%H:%M').time() if hora_salida_str else None
        post.recogemos_en = request.form.get('recogemos_en')
        post.tipoTerreno = request.form.get('tipoTerreno')
        post.requiere_estadía = request.form.get('requiere_estadía')
        post.animales = request.form.get('animales')
        post.duchas = request.form.get('duchas')
        post.banos = request.form.get('banos')
        post.bastones = request.form.get('bastones')
        post.guantes = request.form.get('guantes')
        post.tipo_calzado = request.form.get('tipo_calzado')
        post.repelente = request.form.get('repelente')
        post.bloqueador = request.form.get('bloqueador')
        post.liquido = request.form.get('liquido')
        post.snacks = request.form.get('snacks')
        post.ropa_cambio = request.form.get('ropa_cambio')
        post.precio_colones = request.form.get('precio_colones', type=float)
        image = request.files.get('image')

        if image and image.filename != '':
            if allowed_file(image.filename):
                if post.image:
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.image))
                    except Exception as e:
                        print(f"Error al borrar la imagen antigua: {e}")
                filename = secure_filename(image.filename)
                try:
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    post.image = filename
                except Exception as e:
                    print(f"Error al guardar el archivo: {e}")
                    flash(f"Error al guardar el archivo: {e}", 'danger')
                    return render_template('edit_post.html', post=post, error=str(e))

        post.user_email = current_user.email # Actualiza el email si el usuario se edita.
        try:
            db.session.commit()
            flash('Publicación editada con éxito', 'success')
            return redirect(url_for('post', post_id=post.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al editar la publicación: {e}', 'danger')
            return render_template('edit_post.html', post=post, titulo=titulo, error=str(e))

    return render_template('edit_post.html', post=post, titulo=titulo)

@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        flash("No tienes permiso para borrar este post.", "danger")
        return redirect(url_for('post', post_id=post.id))

    if post.image:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], post.image)
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except FileNotFoundError:
                flash("Error: La imagen no fue encontrada.", "danger")
                return redirect(url_for('post', post_id=post.id))
            except OSError as e:
                flash(f"Error al borrar la imagen: {e}", "danger")
                return redirect(url_for('post', post_id=post.id))

    try:
        db.session.delete(post)
        db.session.commit()
        flash("Publicación borrada con éxito.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al borrar la publicación: {e}", "danger")
    return redirect(url_for('index'))
# FIN VER IMAGENES Y POSTS








@app.route('/create_vids')
def create_vids():
    return render_template('create_vids.html')


@app.route('/videos', methods=['GET', 'POST'])
def videos():
    title = "Videos de La Tribu"
    if request.method == 'POST':
        title = request.form['titulo']
        detail = request.form['descripcion']
        enlace = request.form['enlace']

        imagen = request.files['imagen']

        filename = None
        if imagen and allowed_file(imagen.filename):
            filename = secure_filename(imagen.filename)
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        video = Video(title=title, detail=detail, image_url=filename, video_url=enlace) # Usa 'video_url' aquí
        db.session.add(video)
        db.session.commit()
        return redirect(url_for('videos'))

    videos = Video.query.all()
    return render_template('videos.html', videos=videos, title=title)



@app.route('/videos/edit/<int:video_id>', methods=['GET', 'POST'])
def edit_video(video_id):
    video = Video.query.get_or_404(video_id)
    if request.method == 'POST':
        video.title = request.form['title']
        video.detail = request.form['detail']
        video.video_url = request.form['video_url']
        image = request.files.get('image')

        if image:
            filename = secure_filename(image.filename) # Usar secure_filename aquí también
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(filepath)
            video.image_url = filename # Guarda solo el nombre del archivo
        db.session.commit()
        flash('Video actualizado correctamente', 'success')
        return redirect(url_for('videos'))
    return render_template('edit_video.html', video=video)


@app.route('/videos/delete/<int:tarea_id>', methods=['POST'])
def borrar_video(tarea_id):
    video = Video.query.get_or_404(tarea_id) # Usar 'tarea_id' aquí
    try:
        if video.image_url:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], video.image_url))
    except FileNotFoundError:
        flash(f"La imagen {video.image_url} no fue encontrada y no pudo ser eliminada.", 'warning')
    except Exception as e:
        flash(f"Ocurrió un error al eliminar la imagen: {str(e)}", 'danger')
    db.session.delete(video)
    db.session.commit()
    flash('Video eliminado correctamente.', 'success')
    return redirect(url_for('videos'))

@app.route('/actualizar_video/<int:id>', methods=['GET', 'POST'])
def actualizar_video(id):
    video = Video.query.get_or_404(id)
    if request.method == 'POST':
        video.title = request.form['titulo']
        video.detail = request.form['descripcion']
        video.video_url = request.form['enlace']
        imagen = request.files['imagen']

        if imagen and allowed_file(imagen.filename):
            if video.image_url:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], video.image_url))
            filename = secure_filename(imagen.filename)
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            video.image_url = filename

        db.session.commit()
        return redirect(url_for('videos'))

    return render_template('create_vids.html', video=video)






# REGISTRO DE USUARIO
@app.route('/registro', methods=['GET', 'POST']) # Define la ruta para el registro de usuarios (Depende de render_template, request, flash, User, generate_password_hash, login_user y url_for)
def registro(): # Define la función para el registro de usuarios
    title = "Registro"
    if request.method == 'POST': # Verifica si la solicitud es POST
        nombre = request.form['nombre'].title().replace(" ", "") # Obtiene el nombre del formulario
        apellido1 = request.form['apellido1'].title().replace(" ", "") # Obtiene el primer apellido del formulario
        apellido2 = request.form['apellido2'].title().replace(" ", "") # Obtiene el segundo apellido del formulario
        email = request.form['email'].lower().replace(" ", "") # Obtiene el correo electrónico del formulario
        telefono = request.form['telefono'] # Obtiene el teléfono del formulario
        password = request.form['password'] # Obtiene la contraseña del formulario
        confirmar_password = request.form['confirmar_password'] # Obtiene la confirmación de la contraseña del formulario

        if password != confirmar_password: # Verifica si las contraseñas coinciden
            flash("Las contraseñas no coinciden", "danger") # Muestra un mensaje flash de error
            return render_template('registro.html') # Renderiza la plantilla registro.html

        existing_user = User.query.filter_by(email=email).first() # Verifica si el correo electrónico ya existe
        if existing_user: # Si el correo electrónico ya existe
            flash("El correo electrónico ya está registrado", "danger") # Muestra un mensaje flash de error
            return render_template('registro.html') # Renderiza la plantilla registro.html

        hashed_password = generate_password_hash(password) # Genera el hash de la contraseña

        if 'avatar' in request.files: # Verifica si se cargó un avatar
            file = request.files['avatar'] # Obtiene el archivo del avatar
            if file and allowed_file(file.filename): # Verifica si el archivo es válido
                filename = secure_filename(file.filename) # Obtiene el nombre seguro del archivo
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # Guarda el archivo
                avatar_path = 'images/' + filename # Define la ruta del avatar
            else: # Si el archivo no es válido
                avatar_path = None # Define la ruta del avatar como None
        else: # Si no se cargó un avatar
            avatar_path = None # Define la ruta del avatar como None

        new_user = User(name=nombre, first_last_name=apellido1, second_last_name=apellido2, email=email, phone_number=telefono, password_hash=hashed_password, avatar=avatar_path) # Crea un nuevo usuario
        new_user.registration_count = 0 # Inicializa el contador de registros
        new_user.registration_count += 1 # Incrementa el contador de registros
        db.session.add(new_user) # Agrega el usuario a la sesión de la base de datos
        db.session.commit() # Guarda los cambios en la base de datos

        login_user(new_user) # Inicia sesión con el nuevo usuario
        return redirect(url_for('login')) # Redirige a la página de inicio de sesión
    return render_template('registro.html', title=title) # Renderiza la plantilla registro.html



 # from flask import send_from_directory
@app.route('/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/users', methods=['GET'])
@login_required
def users():
    titulo = "Lista de Usuarios"
    search_term = request.args.get('search', '').lower()  # Convertir a minúsculas

    if search_term:
        # Búsqueda por nombre, apellido, teléfono, email o cualquier coincidencia parcial
        users = User.query.filter(
            db.or_(
                User.name.ilike('%' + search_term + '%'),
                User.first_last_name.ilike('%' + search_term + '%'),
                User.second_last_name.ilike('%' + search_term + '%'),
                User.phone_number.ilike('%' + search_term + '%'),
                User.email.ilike('%' + search_term + '%')
            )
        ).all()

        user_count = len(users)
        users_by_letter = {}
        for user in users:
            first_letter = user.name[0].upper()
            if first_letter not in users_by_letter:
                users_by_letter[first_letter] = []
            users_by_letter[first_letter].append(user)
    else:
        # Si no hay término de búsqueda, muestra todos los usuarios
        users = User.query.all()
        user_count = len(users)
        users_by_letter = {}
        for user in users:
            first_letter = user.name[0].upper()
            if first_letter not in users_by_letter:
                users_by_letter[first_letter] = []
            users_by_letter[first_letter].append(user)

    return render_template('users.html', titulo=titulo, users_by_letter=users_by_letter, user_count=user_count, search_term=search_term)




@app.route('/actualizar_usuario/<int:user_id>', methods=['GET', 'POST'])
@login_required
def actualizar_usuario(user_id):
    usuario = User.query.get_or_404(user_id)

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido1 = request.form['apellido1']
        apellido2 = request.form['apellido2']
        telefono = request.form['telefono']
        email = request.form['email']

        # Verifica si los datos son los mismos
        if (nombre == usuario.name and
            apellido1 == usuario.first_last_name and
            apellido2 == usuario.second_last_name and
            telefono == usuario.phone_number and
            email == usuario.email):
            flash("No se realizaron cambios en la información del usuario.", "info")
            return redirect(url_for('actualizar_usuario', user_id=user_id))

        usuario.name = nombre
        usuario.first_last_name = apellido1
        usuario.second_last_name = apellido2
        usuario.phone_number = telefono
        usuario.email = email

        if request.form.get('eliminar_usuario'):
            db.session.delete(usuario)
            db.session.commit()
            flash("Usuario eliminado correctamente.", "success")
            return redirect(url_for('users'))

        db.session.commit()
        flash("Usuario actualizado correctamente.", "success")
        return redirect(url_for('perfil'))

    return render_template('actualizar_usuario.html', usuario=usuario)


@app.route('/editar_usuario/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(usuario_id):
    usuario = User.query.get_or_404(usuario_id) # Cambio user_id a usuario_id
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido1 = request.form['apellido1']
        apellido2 = request.form['apellido2']
        telefono = request.form['telefono']
        email = request.form['email']

        # Verifica si los datos son los mismos
        if (nombre == usuario.name and
            apellido1 == usuario.first_last_name and
            apellido2 == usuario.second_last_name and
            telefono == usuario.phone_number and
            email == usuario.email):
            flash("No se realizaron cambios en la información del usuario.", "info")
            return redirect(url_for('editar_usuario', usuario_id=usuario_id)) # Cambio user_id a usuario_id

        usuario.name = nombre
        usuario.first_last_name = apellido1
        usuario.second_last_name = apellido2
        usuario.phone_number = telefono
        usuario.email = email
        db.session.commit()
        flash("Usuario actualizado correctamente.", "success")
        return redirect(url_for('users'))
    return render_template('editar_usuario.html', usuario=usuario)



@app.route('/eliminar_usuario/<int:usuario_id>', methods=['POST'])
@login_required
def eliminar_usuario(usuario_id):
    usuario = User.query.get_or_404(usuario_id) # Cambio user_id a usuario_id
    db.session.delete(usuario)
    db.session.commit()
    flash("Usuario eliminado correctamente.", "success")
    return redirect(url_for('users'))









@app.route('/login', methods=['GET', 'POST']) # Define la ruta para el inicio de sesión (Depende de render_template, request, User, check_password_hash, login_user y url_for)
def login(): # Define la función para el inicio de sesión
    title="Iniciar Sesión"
    if request.method == 'POST': # Verifica si la solicitud es POST
        email = request.form['email'] # Obtiene el correo electrónico del formulario
        password = request.form['password'] # Obtiene la contraseña del formulario
        usuario = User.query.filter_by(email=email).first() # Obtiene el usuario de la base de datos

        if usuario and usuario.check_password(password): # Verifica si el usuario existe y la contraseña es correcta
            login_user(usuario) # Inicia sesión con el usuario
            return redirect(url_for('index')) # Redirige a la página de perfil
        else: # Si el usuario no existe o la contraseña es incorrecta
            flash("Email o contraseña incorrectos") # Muestra un mensaje de error
    return render_template('login.html',title=title) # Renderiza la plantilla login.html












@app.route('/perfil') # Define la ruta para el perfil del usuario (Depende de render_template, current_user y login_required)
@login_required # Requiere que el usuario esté autenticado
def perfil(): # Define la función para el perfil del usuario
    return render_template('perfil.html', usuario=current_user) # Renderiza la plantilla perfil.html

@app.route('/avatar/<filename>')
def serve_avatar(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/actualizar_avatar', methods=['GET', 'POST'])
@login_required
def actualizar_avatar():
    usuario = current_user
    if request.method == 'POST':
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                usuario.avatar = filename  # Guarda solo el nombre del archivo
                db.session.commit()
                return redirect(url_for('perfil'))
            else:
                return "Archivo no permitido"
        else:
            return "No se seleccionó ningún archivo"

    current_avatar_filename = usuario.avatar if usuario.avatar else None
    return render_template('actualizar_avatar.html', current_avatar=current_avatar_filename)



@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión finalizada", "notification is-warning")
    return redirect(url_for("index"))  # Cambiado de "home" a "index"


# MODO NOCTURNO
@app.route('/toggle_dark_mode')
def toggle_dark_mode():
    session['dark_mode'] = not session.get('dark_mode', False)
    return redirect(request.referrer)  # Redirige a la página anterior

@app.context_processor
def inject_dark_mode():
    return dict(dark_mode=session.get('dark_mode', False))
# FINAL MODO NOCURNO

@app.errorhandler(404) # Define un manejador de errores para errores 404 (Depende de render_template)
def page_not_found(e): # Define la función para manejar errores 404
    return render_template('404.html'), 404 # Renderiza la plantilla 404.html

@app.errorhandler(500) # Define un manejador de errores para errores 500 (Depende de render_template)
def server_not_found(e): # Define la función para manejar errores 500
    return render_template('500.html'), 500 # Renderiza la plantilla 500.html




@app.route('/agenda', methods=['GET', 'POST'])
@login_required
def agenda():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            apellido1 = request.form['apellido1']
            apellido2 = request.form['apellido2']
            email = request.form['email']
            telefono = request.form['telefono']
            celular = request.form['celular']
            empresa = request.form['empresa']
            categoria = request.form['categoria']

            avatar_path = 'img/default.png'
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    avatar_path = 'images/' + filename

            nuevo_contacto = Contacto(nombre=nombre, apellido1=apellido1, apellido2=apellido2, email=email, telefono=telefono, celular=celular, empresa=empresa, categoria=categoria, avatar=avatar_path)
            db.session.add(nuevo_contacto)
            db.session.commit()
            flash('Contacto agregado correctamente.', 'success')
            return redirect(url_for('agenda'))
        except Exception as e:
            flash(f'Error al agregar contacto: {e}', 'danger')
            return redirect(url_for('agenda'))

    contactos = Contacto.query.all()
    cantidad_contactos = Contacto.query.count()
    return render_template('agenda.html', contactos=contactos, cantidad_contactos=cantidad_contactos)



@app.route('/editar_contacto/<int:contacto_id>', methods=['GET', 'POST'])
def editar_contacto(contacto_id):
    contacto = Contacto.query.get_or_404(contacto_id)
    original_avatar = contacto.avatar

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido1 = request.form['apellido1']
        apellido2 = request.form['apellido2']
        email = request.form['email']
        telefono = request.form['telefono']
        celular = request.form['celular']
        empresa = request.form['empresa']
        categoria = request.form['categoria']

        new_avatar = None

        if 'avatar' in request.files:
            avatar = request.files['avatar']
            if avatar.filename != '':
                filename = secure_filename(avatar.filename)
                avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_avatar = 'images/' + filename #Guardamos la ruta relativa a images

        if (nombre == contacto.nombre and
            apellido1 == contacto.apellido1 and
            apellido2 == contacto.apellido2 and
            email == contacto.email and
            telefono == contacto.telefono and
            celular == contacto.celular and
            empresa == contacto.empresa and
            categoria == contacto.categoria and
            new_avatar is None):
            flash("No se realizaron cambios en la información del contacto.", "info")
            return redirect(url_for('editar_contacto', contacto_id=contacto_id))

        contacto.nombre = nombre
        contacto.apellido1 = apellido1
        contacto.apellido2 = apellido2
        contacto.email = email
        contacto.telefono = telefono
        contacto.celular = celular
        contacto.empresa = empresa
        contacto.categoria = categoria

        if new_avatar:
            contacto.avatar = new_avatar

        db.session.commit()
        flash("Contacto actualizado correctamente.", "success")
        return redirect(url_for('agenda'))

    return render_template('editar_contacto.html', contacto=contacto)

@app.route('/agenda/borrar/<int:contacto_id>', methods=['POST'])
@login_required
def borrar_contacto(contacto_id):
    contacto = Contacto.query.get_or_404(contacto_id)
    db.session.delete(contacto)
    db.session.commit()
    return redirect(url_for('agenda'))




@app.route('/agenda/vcard/<int:contacto_id>')
@login_required
def contacto_vcard(contacto_id):
    contacto = Contacto.query.get_or_404(contacto_id)

    vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{contacto.nombre} {contacto.apellido1} {contacto.apellido2}
N:{contacto.apellido1};{contacto.nombre};;;
TEL;TYPE=WORK,VOICE:{contacto.telefono}
TEL;TYPE=CELL,VOICE:{contacto.celular}
EMAIL:{contacto.email}
ORG:{contacto.empresa}
CATEGORIES:{contacto.categoria}
END:VCARD
"""

    output = BytesIO(vcard.encode('utf-8'))

    return send_file(output, download_name=f'{contacto.nombre}_{contacto_id}.vcf', mimetype='text/vcard', as_attachment=True)

login_manager = LoginManager() # Crea una instancia de LoginManager para manejar la autenticación (Depende de app)
login_manager.init_app(app) # Inicializa LoginManager con la aplicación (Depende de app)
login_manager.login_view = "login" # Define la vista de inicio de sesión (Depende de flask_login)
login_manager.login_message = u"Primero necesitas iniciar sesión" # Define el mensaje para cuando se requiere inicio de sesión (Depende de flask_login)
@login_manager.user_loader # Define una función para cargar el usuario desde la base de datos (Depende de User y db)
def load_user(user_id): # Define la función para cargar el usuario
    return User.query.get(int(user_id)) # Obtiene el usuario de la base de datos


# RECUPERACION DE CONTRASEÑA EN CASO DE QUE NO FUNCIONE BORRAR
# RECUPERACION DE CONTRASEÑA EN CASO DE QUE NO FUNCIONE BORRAR
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.generate_reset_token()
            msg = Message('Restablecer contraseña', recipients=[user.email])
            msg.body = f'Sigue este enlace para restablecer tu contraseña: {url_for("reset_password", token=token, _external=True)}'
            mail.send(msg)
            flash('Se ha enviado un enlace para restablecer tu contraseña a tu correo electrónico.', 'info')
            return redirect(url_for('login'))
        else:
            flash('No se encontró ningún usuario con ese correo electrónico.', 'danger')
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.reset_token_is_valid():
        flash('Token inválido o expirado.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('reset_password.html', token=token)
        user.reset_password(password)
        flash('Tu contraseña ha sido restablecida.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', token=token)





# ADMINISTRADOR DE ARCHIVOS

@app.route('/archivos')
@login_required
def archivos():
    archivos = os.listdir(UPLOAD_FOLDER)
    archivos_con_usuarios = []
    for archivo in archivos:
        es_imagen = archivo.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
        archivos_con_usuarios.append({'nombre_archivo': archivo, 'usuario': None, 'es_imagen': es_imagen})

    return render_template('archivos.html', archivos=archivos_con_usuarios, upload_folder=UPLOAD_FOLDER)

@app.route('/borrar/<nombre_archivo>')
@login_required
def borrar(nombre_archivo):
    ruta_archivo = os.path.join(UPLOAD_FOLDER, nombre_archivo)
    try:
        os.remove(ruta_archivo)
        flash('Archivo borrado con éxito.', 'success')
    except FileNotFoundError:
        flash('El archivo no existe.', 'error')
    return redirect(url_for('archivos'))

@app.route('/subir', methods=['POST'])
@login_required
def subir():
    if 'miArchivo' not in request.files:
        flash('No se seleccionó ningún archivo.', 'error')
        return redirect(url_for('archivos'))
    archivo = request.files['miArchivo']
    if archivo.filename == '':
        flash('No se seleccionó ningún archivo.', 'error')
        return redirect(url_for('archivos'))
    if archivo and allowed_file(archivo.filename):
        nombre_archivo = secure_filename(archivo.filename)
        archivo.save(os.path.join(UPLOAD_FOLDER, nombre_archivo))
        flash('Archivo subido con éxito.', 'success')
        return redirect(url_for('archivos'))
    else:
        flash('Tipo de archivo no permitido.', 'error')
        return redirect(url_for('archivos'))



# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------
# ALERTA DE ERRORES
# Error URL Invalida
@app.errorhandler(404)
# Error página no encontrada
def page_not_found(e):

    return render_template('404.html'), 404

# Error Servidor Interno
@app.errorhandler(500)
# Servidor no encontrada
def server_not_found(e):

    return render_template('500.html'), 500
# -----------------------





if __name__ == '__main__': # Verifica si el script se ejecuta directamente
    # db.create_all()
    # db.upgrade_all()
    # db.drop_all() #Solo se ejecuta para migrar nuevos campos a la db pero borra el contenido
    app.run(debug=True, port=3000) # Ejecuta la aplicación Flask


   # Migraciones Cmder
        # set FLASK_APP=main.py     <--Crea un directorio de migraciones
        # flask db init             <--
        # $ flask db stamp head
        # $ flask db migrate
        # $ flask db migrate -m "mensaje x"
        # $ flask db upgrade

        # ERROR [flask_migrate] Error: Target database is not up to date.
        # $ flask db stamp head
        # $ flask db migrate
        # $ flask db upgrade
        # git clone https://github.com/kerm1977/MI_APP_FLASK.git
        # mysql> DROP DATABASE kenth1977$db; PYTHONANYWHATE
# -----------------------