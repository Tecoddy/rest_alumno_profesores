import requests
import os

from main import BASE_URL


def test_alumnos():
    print("Testing Alumno Endpoints:")

    # Create a new Alumno
    alumno_data = {
        "nombres": "Juan",
        "apellidos": "Pérez",
        "matricula": "A001",
        "promedio": 9.5,
        "password": "securepassword"  # Ensure this matches your password hashing setup
    }
    response = requests.post(f"{BASE_URL}/alumnos", json=alumno_data)
    print("POST /alumnos:", response.json())

    # Get the ID of the created alumno
    alumno_id = response.json()["id"]

    # Get all Alumnos
    response = requests.get(f"{BASE_URL}/alumnos")
    print("GET /alumnos:", response.json())

    # Upload a profile photo
    #test_upload_foto(alumno_id)

    # Get a single Alumno with photo
    response = requests.get(f"{BASE_URL}/alumnos/{alumno_id}")
    print("GET /alumnos/<id>:", response.json())

    # Delete the created Alumno
    response = requests.delete(f"{BASE_URL}/alumnos/{alumno_id}")
    print("DELETE /alumnos/<id>:", response.json())


def test_upload_foto(alumno_id):
    print(f"Testing profile photo upload for Alumno ID {alumno_id}:")

    # Path to the image
    image_path = os.path.join(os.getcwd(), "image.jpg")
    if not os.path.exists(image_path):
        print(f"Image not found at {image_path}")
        return

    # Open the file in binary mode and send it as part of the request
    with open(image_path, "rb") as image_file:
        files = {
            "fotoPerfil": (os.path.basename(image_path), image_file, "image/jpeg")
        }

        # Send the POST request
        response = requests.post(f"{BASE_URL}/alumnos/{alumno_id}/fotoPerfil", files=files)

        # Output the response
        print("POST /alumnos/<id>/fotoPerfil:", response.status_code, response.json())

def test_profesores():
    print("Testing Profesor Endpoints:")

    # Create a new Profesor
    profesor_data = {
        "numeroEmpleado": "EMP001",
        "nombres": "Laura",
        "apellidos": "García",
        "horasClase": 20
    }
    response = requests.post(f"{BASE_URL}/profesores", json=profesor_data)
    print("POST /profesores:", response.json())

    # Get all Profesores
    response = requests.get(f"{BASE_URL}/profesores")
    print("GET /profesores:", response.json())

    # Update a Profesor
    profesor_id = response.json()[0]["id"]
    updated_data = {
        "numeroEmpleado": "EMP001",
        "nombres": "Laura María",
        "apellidos": "García",
        "horasClase": 25
    }
    response = requests.put(f"{BASE_URL}/profesores/{profesor_id}", json=updated_data)
    print("PUT /profesores/<id>:", response.json())

    # Get a single Profesor
    response = requests.get(f"{BASE_URL}/profesores/{profesor_id}")
    print("GET /profesores/<id>:", response.json())

    # Delete a Profesor
    response = requests.delete(f"{BASE_URL}/profesores/{profesor_id}")
    print("DELETE /profesores/<id>:", response.json())

def test_enviar_email():
    print("Testing email notification for Alumno ID...")

    # Crear un alumno para la prueba
    alumno_data = {
        "nombres": "Juan",
        "apellidos": "Pérez",
        "matricula": "A001",
        "promedio": 9.5,
        "password": "securepassword"  # Ensure this matches your password hashing setup
    }
    response = requests.post(f"{BASE_URL}/alumnos", json=alumno_data)
    alumno_id = response.json()["id"]

    # Enviar el correo
    response = requests.post(f"{BASE_URL}/alumnos/{alumno_id}/email")
    print("POST /alumnos/<id>/email:", response.status_code, response.json())

def test_session_login(alumno_id, password):
    print(f"Testing session login for Alumno ID {alumno_id}:")

    # Request payload with the password
    payload = {"password": password}
    response = requests.post(f"{BASE_URL}/alumnos/{alumno_id}/session/login", json=payload)
    # Print raw response for debugging
    print("Raw Response Content:", response.text)
    # Output the response
    print("POST /alumnos/<id>/session/login:", response.status_code, response.json())

    if response.status_code == 200:
        return response.json().get("sessionString"), response.json().get("sessionId")
    else:
        return None, None

def test_session_verify(alumno_id, session_string):
    print(f"Testing session verification for Alumno ID {alumno_id}:")

    # Request payload with the session string
    payload = {"sessionString": session_string}
    response = requests.post(f"{BASE_URL}/alumnos/{alumno_id}/session/verify", json=payload)

    # Output the response
    print("POST /alumnos/<id>/session/verify:", response.status_code, response.json())

def test_session_logout(alumno_id, session_string):
    print(f"Testing session logout for Alumno ID {alumno_id}:")

    # Request payload with the session string
    payload = {"sessionString": session_string}
    response = requests.post(f"{BASE_URL}/alumnos/{alumno_id}/session/logout", json=payload)

    # Output the response
    print("POST /alumnos/<id>/session/logout:", response.status_code, response.json())

def test_session_management():
    print("Testing session management endpoints:")

    # Create a new Alumno for testing
    alumno_data = {
        "nombres": "Test",
        "apellidos": "User",
        "matricula": "T12345",
        "promedio": 9.0,
        "password": "securepassword"  # Ensure this matches your password hashing setup
    }
    response = requests.post(f"{BASE_URL}/alumnos", json=alumno_data)
    print("POST /alumnos:", response.json())
    alumno_id = response.json().get("id")

    # Test login
    session_string, session_id = test_session_login(alumno_id, "securepassword")
    if not session_string:
        print("Login failed. Exiting session tests.")
        return

    # Test verify
    test_session_verify(alumno_id, session_string)

    # Test logout
    test_session_logout(alumno_id, session_string)

    # Verify again after logout (should fail)
    test_session_verify(alumno_id, session_string)


if __name__ == "__main__":
    test_alumnos()
    test_profesores()
    #test_enviar_email()
    #test_session_management()