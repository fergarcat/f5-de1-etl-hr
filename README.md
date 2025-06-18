# FRONTEND - FastAPI - HR ETL Dashboard

Este proyecto es una aplicación basada en **FastAPI** que sirve como interfaz para el procesamiento ETL de Recursos Humanos. Incluye un frontend para visualización y una API para interactuar con los datos.

---

## 🚀 **Cómo levantar el proyecto**

### **1. Requisitos previos**
Asegúrate de tener instalados los siguientes componentes:
- **Python 3.9 o superior**
- **Pip** (gestor de paquetes de Python)
- **Entorno virtual (opcional pero recomendado)**

---

### **2. Clonar el repositorio**
Clona el repositorio en tu máquina local:

```bash
git clone <URL_DEL_REPOSITORIO>
cd f5-de1-etl-hr/fastapi
```

---

## 📂 **FastAPI - Cómo levantar el proyecto**

### **1. Requisitos previos**
Asegúrate de tener instalados los siguientes componentes:
- **Python 3.9 o superior**
- **Pip** (gestor de paquetes de Python)
- **Entorno virtual (opcional pero recomendado)**

---

### **2. Crear y activar el entorno virtual**
Desde la raíz del proyecto, ejecuta los siguientes comandos:

```bash
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual (Windows)
venv\Scripts\activate

# Activar el entorno virtual (Linux/MacOS)
source venv/bin/activate
```

---

### **3. Instalar dependencias**
Con el entorno virtual activado, instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

---

### **4. Levantar el servidor FastAPI**
Navega a la carpeta `fastapi` y ejecuta el servidor:

```bash
cd fastapi
python main.py
```

El servidor estará disponible en:
- **Frontend:** [http://localhost:8000](http://localhost:8000)
- **Documentación API (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Documentación API (ReDoc):** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### **5. Comandos útiles**

- **Detener el servidor:** Presiona `Ctrl + C` en la terminal.
- **Actualizar dependencias:**

```bash
pip freeze > requirements.txt
```
