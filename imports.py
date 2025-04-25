from flask import Flask, render_template, request, redirect, url_for, flash, session  # Agrega 'session' aquí  # Importa las funciones necesarias de Flask (Todas las rutas y render_template dependen de esto)
from flask_migrate import Migrate  # Importa Migrate para manejar migraciones de la base de datos (Depende de db y app)
from werkzeug.security import generate_password_hash, check_password_hash # Importa funciones para manejar contraseñas seguras (Depende de la clase User)
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user # Importa funciones para manejar la autenticación de usuarios (Depende de la clase User y app)
from flask_sqlalchemy import SQLAlchemy # Importa SQLAlchemy para interactuar con la base de datos (Depende de app)
from werkzeug.utils import secure_filename # Importa secure_filename para manejar archivos cargados de forma segura (Depende de las rutas que manejan uploads)
import os # Importa el módulo os para interactuar con el sistema operativo (Depende de app.secret_key y rutas de uploads)
from datetime import datetime
import sqlite3
from flask_mail import Mail, Message
from sqlalchemy import or_
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, TimeField, FloatField, IntegerField, BooleanField, FileField, SubmitField
from wtforms.validators import DataRequired
import requests
import secrets #videos
import math
import secrets
from authlib.integrations.flask_client import OAuth
from flask import send_from_directory #Permite ver la imagen en el users
# from recuperacion_contraseña import crear_modulo_recuperacion_contraseña # Importacion del modulo.
from urllib.parse import urlparse
import csv
from flask import send_file
from io import BytesIO, StringIO # Add this line to import BytesIO and StringIO.
import io
