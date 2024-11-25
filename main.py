from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException
import uuid
import mimetypes
import bcrypt

import boto3
from botocore.exceptions import NoCredentialsError

import aws_services

app = Flask(__name__)
api = Api(app)

# EC2 instance DNS
BASE_URL = "http://ec2-54-144-75-112.compute-1.amazonaws.com"
#Testing
#BASE_URL = "http://127.0.0.1:5000"

# Database Endpoint and Credentials
endpoint = "rest-database.cluster-cw4mgxm6dnhr.us-east-1.rds.amazonaws.com"
username = "admin"
password = "admin-password"
database_name = "rest_database"

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'mysql+pymysql://{username}:{password}@{endpoint}:3306/{database_name}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



# Modelos
class Alumno(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    matricula = db.Column(db.String(50), nullable=False)
    promedio = db.Column(db.Float, nullable=False)
    fotoPerfilUrl = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(128), nullable=False)

class Profesor(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numeroEmpleado = db.Column(db.String(50), nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    horasClase = db.Column(db.Integer, nullable=False)

# Helper functions for validations
def validate_alumno(data):
    required_fields = ["password", "nombres", "apellidos", "matricula", "promedio"]
    for field in required_fields:
        if field not in data or not data[field]:
            return f"El campo '{field}' es obligatorio y no puede estar vacío."
        if field in ["nombres", "apellidos", "matricula","password"] and not isinstance(data[field], str):
            return f"El campo '{field}' debe ser un string."
        if field == "promedio" and not isinstance(data[field], (int, float)):
            return f"El campo 'promedio' debe ser un número."
    return None

def validate_profesor(data):
    required_fields = ["numeroEmpleado", "nombres", "apellidos", "horasClase"]
    for field in required_fields:
        if field not in data or not data[field]:
            return f"El campo '{field}' es obligatorio y no puede estar vacío."
        if field in ["nombres", "apellidos","password"] and not isinstance(data[field], str):
            return f"El campo '{field}' debe ser un string."
        if field in ["promedio","horasClase"] and not isinstance(data[field], (int, float)):
            return f"El campo 'promedio' debe ser un número."
    return None

# Crear la base de datos
with app.app_context():
    db.create_all()

# Recursos
class AlumnoResource(Resource):
    def get(self, id=None):
        if id is None:
            alumnos = Alumno.query.all()
            return jsonify([
                {"id": a.id, "nombres": a.nombres, "apellidos": a.apellidos,
                 "matricula": a.matricula, "promedio": a.promedio,
                 "fotoPerfilUrl": a.fotoPerfilUrl}
                for a in alumnos
            ])
        alumno = Alumno.query.get(id)
        if alumno:
            return {
                "id": alumno.id,
                "nombres": alumno.nombres,
                "apellidos": alumno.apellidos,
                "matricula": alumno.matricula,
                "promedio": alumno.promedio,
                "fotoPerfilUrl": alumno.fotoPerfilUrl
            }, 200
        return {"error": "Alumno no encontrado"}, 404

    def post(self):
        data = request.get_json()
        error = validate_alumno(data)
        if error != None:
            return {"error": error}, 400
        new_alumno = Alumno(**data)
        db.session.add(new_alumno)
        db.session.commit()
        return {"mensaje": "Alumno creado exitosamente", "id": new_alumno.id}, 201

    def put(self, id):
        data = request.get_json()
        error = validate_alumno(data)
        if error != None:
            return {"error": error}, 400
        alumno = Alumno.query.get(id)
        if not alumno:
            return {"error": "Alumno no encontrado"}, 404
        for key, value in data.items():
            setattr(alumno, key, value)
        db.session.commit()
        return {"mensaje": "Alumno actualizado exitosamente"}, 200

    def delete(self, id = None):
        if id is None:
            return {"error": "No permitido"}, 405
        alumno = Alumno.query.get(id)
        if not alumno:
            return {"error": "Alumno no encontrado"}, 404
        db.session.delete(alumno)
        db.session.commit()
        return {"mensaje": "Alumno eliminado exitosamente"}, 200

class ProfesorResource(Resource):
    def get(self, id=None):
        if id is None:
            profesores = Profesor.query.all()
            return jsonify([{"id": p.id, "numeroEmpleado": p.numeroEmpleado, "nombres": p.nombres, "apellidos": p.apellidos, "horasClase": p.horasClase} for p in profesores])
        profesor = Profesor.query.get(id)
        if profesor:
            return {"id": profesor.id, "numeroEmpleado": profesor.numeroEmpleado, "nombres": profesor.nombres, "apellidos": profesor.apellidos, "horasClase": profesor.horasClase}, 200
        return {"error": "Profesor no encontrado"}, 404

    def post(self):
        data = request.get_json()
        error = validate_profesor(data)
        if error:
            return {"error": error}, 400
        new_profesor = Profesor(**data)
        db.session.add(new_profesor)
        db.session.commit()
        return {"mensaje": "Profesor creado exitosamente", "id": new_profesor.id}, 201

    def put(self, id):
        data = request.get_json()
        error = validate_profesor(data)
        if error:
            return {"error": error}, 400
        profesor = Profesor.query.get(id)
        if not profesor:
            return {"error": "Profesor no encontrado"}, 404
        for key, value in data.items():
            setattr(profesor, key, value)
        db.session.commit()
        return {"mensaje": "Profesor actualizado exitosamente"}, 200

    def delete(self, id = None):
        if id is None:
            return {"error": "No permitido"}, 405
        profesor = Profesor.query.get(id)
        if not profesor:
            return {"error": "Profesor no encontrado"}, 404
        db.session.delete(profesor)
        db.session.commit()
        return {"mensaje": "Profesor eliminado exitosamente"}, 200
    
@app.route('/alumnos/<string:id>/fotoPerfil', methods=['POST'])
def upload_foto_perfil(id):
    # Validate that the alumno exists
    alumno = Alumno.query.get(id)
    if not alumno:
        return {"error": "Alumno no encontrado"}, 404

    # Validate that a file is provided with the key 'foto'
    if 'foto' not in request.files:
        return {"error": "No se encontró el archivo 'foto' en la solicitud"}, 400

    file = request.files['foto']
    if file.filename == '':
        return {"error": "El archivo no tiene un nombre válido"}, 400

    # Determine the content type
    content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'

    # Create a unique filename for S3
    filename = f"alumno_{id}/{file.filename}"

    try:
        # Upload the file to S3
        file_url = aws_services.upload_file(file, filename, content_type)

        # Save the file URL to the alumno record
        alumno.fotoPerfilUrl = file_url
        db.session.commit()

        # Return the file URL in the response
        return {"mensaje": "Foto de perfil subida exitosamente", "fotoPerfilUrl": file_url}, 200
    except NoCredentialsError:
        return {"error": "Credenciales de AWS no configuradas correctamente"}, 500
    except Exception as e:
        return {"error": str(e)}, 500
    
@app.route('/alumnos/<string:id>/email', methods=['POST'])
def enviar_email(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return {"error": "Alumno no encontrado"}, 404

    # Datos del alumno
    nombres = alumno.nombres
    apellidos = alumno.apellidos
    promedio = alumno.promedio

    # Contenido del mensaje
    mensaje = (
        f"Estimado {nombres} {apellidos},\n"
        f"Tu promedio actual es {promedio}.\n"
        "Saludos cordiales."
    )
    try:
        # Enviar notificación SNS
        response = aws_services.enviar_notificacion_sns(mensaje)
        return {"mensaje": "Notificación enviada exitosamente", "snsResponse": response}, 200
    except Exception as e:
        return {"error": str(e)}, 500
    
@app.route('/clean_database', methods=['POST'])
def clean_database():
    try:
        # Delete all rows from tables
        Alumno.query.delete()
        Profesor.query.delete()
        db.session.commit()
        return {"mensaje": "Base de datos limpiada exitosamente."}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500
    
@app.route('/reset_database', methods=['POST'])
def reset_database():
    try:
        # Drop all tables
        db.drop_all()  
        # Recreate all tables
        db.create_all()  
        return {"mensaje": "Base de datos reiniciada exitosamente."}, 200
    except Exception as e:
        return {"error": str(e)}, 500
    
@app.route('/alumnos/<string:id>/session/login', methods=['POST'])
def login(id):
    # Get the request data
    data = request.get_json()
    password = data.get('password')

    # Validate the request
    if not password:
        return {"error": "Password is required"}, 400

    # Retrieve the alumno from the database
    alumno = Alumno.query.get(id)
    if not alumno:
        return {"error": "Alumno not found"}, 404

    # Compare the password
    if not password == alumno.password:
        return {"error": "Invalid password"}, 400

    session_credentials = aws_services.login(id)

    return {
        "message": "Login successful",
        "sessionId": session_credentials['id'],
        "sessionString": session_credentials['sessionString']
    }, 200

@app.route('/alumnos/<string:id>/session/verify', methods=['POST'])
def verify_session(id):
    # Get the request data
    data = request.get_json()
    session_string = data.get('sessionString')

    # Validate the request
    if not session_string:
        return {"error": "Session string is required"}, 400

    response = aws_services.verify_session(id, session_string)
    items = response.get('Items', [])

    if not items:
        return {"error": "Session not found"}, 400

    session = items[0]
    if not session['active']:
        return {"error": "Session is inactive"}, 400

    return {"message": "Session is valid"}, 200

@app.route('/alumnos/<string:id>/session/logout', methods=['POST'])
def logout(id):
    # Get the request data
    data = request.get_json()
    session_string = data.get('sessionString')

    # Validate the request
    if not session_string:
        return {"error": "Session string is required"}, 400

    # Query DynamoDB for the session
    response = aws_services.verify_session(id, session_string)
    items = response.get('Items', [])

    if not items:
        return {"error": "Session not found"}, 400

    # Update the session to inactive
    session = items[0]
    session_id = session['id']

    aws_services.logout(session_id)

    return {"message": "Session logged out successfully"}, 200

# Endpoint Routing
api.add_resource(AlumnoResource, "/alumnos", "/alumnos/<string:id>")
api.add_resource(ProfesorResource, "/profesores", "/profesores/<string:id>")

@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"error": e.description}), e.code

if __name__ == "__main__":
    app.run(debug=True)
