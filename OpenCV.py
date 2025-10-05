import tkinter as tk
from tkinter import simpledialog, messagebox
import cv2
import os
import numpy as np
import threading
import time as time 
from Login import cargar_usuarios, guardar_usuarios
USERS_DIR = "users_lbph"

# === Registrar rostro con OpenCV LBPH ===
def register_face_gui():
    name = simpledialog.askstring("Registro", "Ingresa tu nombre de usuario:")
    if not name:
        messagebox.showerror("Error", "Nombre inválido.")
        return

    name = name.strip().lower()
    
    if not os.path.exists(USERS_DIR):
        os.makedirs(USERS_DIR)

    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    count = 0
    faces_data = []

    messagebox.showinfo("Instrucción", "Mira a la cámara. Se capturarán 10 imágenes automáticamente.")

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "No se pudo acceder a la cámara.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face, (100, 100))
            faces_data.append(face_resized)
            count += 1

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Captura {count}/10", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("Registrando rostro", frame)

        if count >= 10 or cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if faces_data:
        mean_face = np.mean(faces_data, axis=0)  # Promediar las 10 capturas
        filepath = os.path.join(USERS_DIR, f"{name}.npy")
        np.save(filepath, mean_face)
        messagebox.showinfo("Éxito", f"Rostro guardado correctamente como '{filepath}'")
    else:
        messagebox.showwarning("Sin capturas", "No se capturó ningún rostro.")
    usuarios = cargar_usuarios()
    if name not in usuarios:
        usuarios[name] = {
            "correo": f"{name}@faceid.com",
            "contrasena": None,
            "solo_cara": True,
            "puntaje_max": 999,
            "saldo": 0.0
        }
        guardar_usuarios(usuarios)
        messagebox.showinfo("Usuario creado", f"Usuario '{name}' creado para login facial.")
    else:
        messagebox.showinfo("Usuario ya existe", f"El usuario '{name}' ya existe en el sistema.")
# === Entrenamiento del modelo LBPH ===
def train_lbph_model():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces = []
    labels = []
    label_map = {}
    label_count = 0

    for file in os.listdir(USERS_DIR):
        if file.endswith(".jpg"):
            path = os.path.join(USERS_DIR, file)
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            name = file.split("_")[0]
            if name not in label_map:
                label_map[name] = label_count
                label_count += 1
            faces.append(img)
            labels.append(label_map[name])

    if not faces:
        return None, {}

    recognizer.train(faces, np.array(labels))
    return recognizer, {v: k for k, v in label_map.items()}
def load_known_faces():
    encodings = []
    names = []

    for file in os.listdir(USERS_DIR):
        if file.endswith(".npy"):
            path = os.path.join(USERS_DIR, file)
            encoding = np.load(path).flatten()
            encodings.append(encoding)
            names.append(os.path.splitext(file)[0])

    return encodings, names
# === Login con rostro ===
# === Login con rostro automático usando OpenCV ===
def login_with_face_gui(on_login_success=None):
    def login_thread():
        try:
            known_encodings, known_names = load_known_faces()
            if not known_encodings:
                messagebox.showerror("Error", "No hay rostros registrados.")
                return

            cap = cv2.VideoCapture(0)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

            start_time = time.time()
            recognized = False

            while True:
                ret, frame = cap.read()
                if not ret:
                    messagebox.showerror("Error", "No se pudo acceder a la cámara.")
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    face = cv2.resize(gray[y:y+h, x:x+w], (100, 100)).flatten()
                    distances = [np.linalg.norm(face - known_enc) for known_enc in known_encodings]
                    min_distance = min(distances)
                    best_match_index = np.argmin(distances)

                    if min_distance < 2000:
                        name = known_names[best_match_index]
                        label = f"Reconocido: {name}"
                        color = (0, 255, 0)
                        recognized = True
                    else:
                        label = "Desconocido"
                        color = (0, 0, 255)

                    # Dibujar recuadro y etiqueta
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

                    if recognized:
                        cv2.imshow("Login con rostro", frame)
                        cv2.waitKey(1000)
                        cap.release()
                        cv2.destroyAllWindows()
                        on_login_success(name)
                        return

                cv2.imshow("Login con rostro", frame)

                if time.time() - start_time > 15:
                    break

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
            messagebox.showinfo("Login fallido", "No se reconoció ningún rostro o se canceló el login.")
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e))

    threading.Thread(target=login_thread).start()

# === Interfaz Tkinter ===
def main_gui():
    root = tk.Tk()
    root.title("Sistema de Reconocimiento Facial (LBPH)")
    root.geometry("400x250")

    tk.Label(root, text="Reconocimiento Facial (OpenCV + LBPH)", font=("Arial", 14)).pack(pady=10)

    tk.Button(root, text="Registrar nuevo rostro", command=register_face_gui, width=30, height=2).pack(pady=10)
    tk.Button(root, text="Iniciar sesión con rostro", command=login_with_face_gui, width=30, height=2).pack(pady=10)
    tk.Button(root, text="Salir", command=root.destroy, width=30, height=2).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    if not os.path.exists(USERS_DIR):
        os.makedirs(USERS_DIR)
    main_gui()
