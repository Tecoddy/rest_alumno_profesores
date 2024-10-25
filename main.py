from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
api = Api(app)

# In-memory data storage
alumnos = []
profesores = []

# Models
class Alumno:
    def __init__(self, id, nombres, apellidos, matricula, promedio):
        self.id = id
        self.nombres = nombres
        self.apellidos = apellidos
        self.matricula = matricula
        self.promedio = promedio

class Profesor:
    def __init__(self, id, numero_empleado, nombres, apellidos, horas_clase):
        self.id = id
        self.numero_empleado = numero_empleado
        self.nombres = nombres
        self.apellidos = apellidos
        self.horas_clase = horas_clase

# Helper functions for validations
def validate_alumno(data):
    required_fields = ["id", "nombres", "apellidos", "matricula", "promedio"]
    for field in required_fields:
        if field not in data or not data[field]:
            return f"El campo '{field}' es obligatorio y no puede estar vacío."
        if field in ["id", "matricula"] and not isinstance(data[field], int):
            return f"El campo '{field}' debe ser un entero."
        if field == "promedio" and not isinstance(data[field], (int, float)):
            return f"El campo 'promedio' debe ser un número."
    return None

def validate_profesor(data):
    required_fields = ["id", "numero_empleado", "nombres", "apellidos", "horas_clase"]
    for field in required_fields:
        if field not in data or not data[field]:
            return f"El campo '{field}' es obligatorio y no puede estar vacío."
        if field in ["id", "numero_empleado", "horas_clase"] and not isinstance(data[field], int):
            return f"El campo '{field}' debe ser un entero."
    return None

# Resources
class AlumnoResource(Resource):
    def get(self, id=None):
        if id is None:
            return jsonify([vars(alumno) for alumno in alumnos])
        for alumno in alumnos:
            if alumno.id == id:
                return vars(alumno), 200
        return {"error": "Alumno no encontrado"}, 404

    def post(self):
        data = request.get_json()
        error = validate_alumno(data)
        if error:
            return {"error": error}, 400
        new_alumno = Alumno(**data)
        alumnos.append(new_alumno)
        return {"mensaje": "Alumno creado exitosamente"}, 201

    def put(self, id):
        data = request.get_json()
        error = validate_alumno(data)
        if error:
            return {"error": error}, 400
        for i, alumno in enumerate(alumnos):
            if alumno.id == id:
                alumnos[i] = Alumno(**data)
                return {"mensaje": "Alumno actualizado exitosamente"}, 200
        return {"error": "Alumno no encontrado"}, 404

    def delete(self, id):
        global alumnos
        alumnos = [alumno for alumno in alumnos if alumno.id != id]
        return {"mensaje": "Alumno eliminado exitosamente"}, 200

class ProfesorResource(Resource):
    def get(self, id=None):
        if id is None:
            return jsonify([vars(profesor) for profesor in profesores])
        for profesor in profesores:
            if profesor.id == id:
                return vars(profesor), 200
        return {"error": "Profesor no encontrado"}, 404

    def post(self):
        data = request.get_json()
        error = validate_profesor(data)
        if error:
            return {"error": error}, 400
        new_profesor = Profesor(**data)
        profesores.append(new_profesor)
        return {"mensaje": "Profesor creado exitosamente"}, 201

    def put(self, id):
        data = request.get_json()
        error = validate_profesor(data)
        if error:
            return {"error": error}, 400
        for i, profesor in enumerate(profesores):
            if profesor.id == id:
                profesores[i] = Profesor(**data)
                return {"mensaje": "Profesor actualizado exitosamente"}, 200
        return {"error": "Profesor no encontrado"}, 404

    def delete(self, id):
        global profesores
        profesores = [profesor for profesor in profesores if profesor.id != id]
        return {"mensaje": "Profesor eliminado exitosamente"}, 200

# Endpoint Routing
api.add_resource(AlumnoResource, "/alumnos", "/alumnos/<int:id>")
api.add_resource(ProfesorResource, "/profesores", "/profesores/<int:id>")

@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"error": e.description}), e.code

if __name__ == "__main__":
    app.run(debug=True)
