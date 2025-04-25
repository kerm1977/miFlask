from imports import *
app = Flask(__name__) # Crea una instancia de la aplicación Flask (Todas las rutas y configuraciones dependen de esto)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db' # Configura la URI de la base de datos (Depende de db)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Desactiva el seguimiento de modificaciones de SQLAlchemy (Depende de db)
app.secret_key = os.urandom(24) # Genera una clave secreta para la sesión (Depende de flask_login)
UPLOAD_FOLDER = 'static/uploads/' # Define la carpeta para almacenar archivos cargados (Depende de las rutas de uploads)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} # Define las extensiones de archivo permitidas (Depende de las rutas de uploads)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Configura la carpeta de carga en la aplicación (Depende de rutas que manejan uploads)
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS # Configura las extensiones permitidas en la aplicación (Depende de rutas que manejan uploads)
db = SQLAlchemy(app) # Crea una instancia de SQLAlchemy asociada a la aplicación (Depende de app y configura la base de datos)
login_manager = LoginManager() # Crea una instancia de LoginManager para manejar la autenticación (Depende de app)
login_manager.init_app(app) # Inicializa LoginManager con la aplicación (Depende de app)
login_manager.login_view = 'login' # Define la vista de inicio de sesión (Depende de flask_login)
migrate = Migrate(app, db) # Inicializa Migrate para manejar migraciones de la base de datos (Depende de db y app)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS # No corchetes extras
