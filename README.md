# Job Scraper: Plataforma de Búsqueda y Análisis de Empleos Tecnológicos - PROYECTO UNICAMENTE CON FINES EDUCATIVOS PERSONALES.

Proyecto educativo para búsqueda, análisis y recomendación de empleos en tecnología.  Web scraping, backend (FastAPI), frontend (React/Vite), base de datos (MySQL) y microservicios (recomendaciones, predicción de salario, visualizaciones).  *Solo para fines educativos.*

## 1. Introducción

Herramienta que extrae datos de ofertas de empleo y ofrece:

*   **Interfaz:** Frontend React/Vite.
*   **API:** Backend FastAPI.
*   **Base de Datos:** MySQL.
*   **Recomendaciones:** Microservicio de ML.
*   **Predicción de Salario:** Microservicio de ML.
*  **Visualizaciones:** Microservicio de datos para gráficos.
*   **Despliegue:** Docker/Docker Compose.
*   **CI/CD:** GitHub Actions.

## 2. Tecnologías

*   **Frontend:** React, Vite, Componentes UI, Gestión de estado.
*   **Backend:** Python, FastAPI, Pydantic, uv.
*   **Scraper:** Python, Selenium, WebDriver, `time`, `Regex`.
*   **Base de Datos:** MySQL.
*   **Microservicios (Recomendación/Predicción/Visualizaciones):** Python, FastAPI, Bibliotecas ML/Visualización.
*   **Contenedores:** Docker, Docker Compose.
*   **CI/CD:** GitHub Actions.
*   **Control de Versiones:** Git, GitHub.
*   **Entorno:** VS Code.
*   **Otros:** dotenv.

## 3. Estructura del Proyecto

    job-scraper/
    ├── backend/
    │   ├── app/
    │   │   ├── __init__.py
    │   │   ├── main.py          # Punto de entrada de FastAPI
    │   │   ├── models.py        # Modelos para la base de datos
    │   │   ├── routes.py        # Definición de endpoints
    │   │   ├── database.py      # Conexión y configuraciones de la base de datos
    │   │   ├── utils.py         # Funciones auxiliares
    │   └── Dockerfile           # Dockerfile para el backend
    │   └── pyproject.toml       # Archivo de configuración de dependencias para uv
    │   └── requirements.txt     # Opcional, para desarrollo adicional si es necesario
    ├── frontend/
    │   ├── src/
    │   │   ├── components/      # Componentes React
    │   │   ├── pages/           # Páginas de la aplicación
    │   │   ├── App.jsx          # Archivo principal de React
    │   │   ├── main.jsx         # Punto de entrada de Vite
    │   ├── public/              # Archivos estáticos
    │   └── Dockerfile           # Dockerfile para el frontend
    │   └── package.json         # Configuración de dependencias de npm
    ├── scraper/
    │   ├── scraper.py           # Código principal del scraper
    │   ├── utils.py             # Funciones auxiliares para el scraping
    │   ├── Dockerfile           # Dockerfile para el scraper
    │   ├── pyproject.toml       # Archivo de configuración para uv
    │   ├── tests/               # Carpeta para las pruebas unitarias del scraper
    │   │   ├── test_scraper.py  # Pruebas unitarias para el scraper
    │   │   ├── test_utils.py    # Pruebas para funciones auxiliares
    ├── database/
    │   ├── init.sql             # Script de inicialización de la base de datos (crear tablas)
    │   └── Dockerfile           # Dockerfile para la base de datos MySQL
    ├── recommender/             # Microservicio para sistema de recomendación
    │   ├── recommender.py       # Lógica para recomendar empleos
    │   ├── models/              # Carpeta para guardar modelos de ML
    │   ├── Dockerfile           # Dockerfile para el microservicio de recomendación
    │   ├── pyproject.toml       # Configuración para uv y dependencias de ML
    ├── salary-prediction/       # Microservicio para predicción de sueldos
    │   ├── predictor.py         # Lógica para predicción de sueldos
    │   ├── models/              # Carpeta para guardar modelos de predicción
    │   ├── Dockerfile           # Dockerfile para el microservicio de predicción
    │   ├── pyproject.toml       # Configuración para uv y dependencias de ML
    ├── visualizations/          # Microservicio para gráficos y análisis
    │   ├── charts.py            # Lógica para generar datos listos para gráficos
    │   ├── Dockerfile           # Dockerfile para visualizaciones
    │   ├── pyproject.toml       # Configuración para uv
    ├── .github/
    │   ├── workflows/
    │   │   ├── main.yml         # Configuración para GitHub Actions
    ├── docker-compose.yml       # Archivo de orquestación para levantar todo
    ├── .env                     # Variables de entorno (como credenciales)
    └── README.md                # Documentación del proyecto



## 4. Instalación y Uso

1.  **Clonar:**
    ```bash
    git clone <URL>
    cd job-scraper
    ```
2.  **Variables de Entorno:** Crea `.env` y configúralo.
3.  **Docker Compose:**
    ```bash
    docker-compose up --build  # Construir y ejecutar
    ```
4.  **Acceso:**
    *   Frontend: `http://localhost:5173`
    *   Backend (API): `http://localhost:8000/docs`
5. **Ejecutar Scraper Manualmente:**
     ```bash
     docker-compose run --rm scraper
     ```
6.  **Parar:**

     ```bash
     docker-compose down     # Parar contenedores
     docker-compose down -v  # Parar y eliminar volumen de BD
     ```

## 5. Consideraciones Éticas y Legales

*   PROYECTO UNICAMENTE CON FINES EDUCATIVOS PERSONALES.
*   Respeta `robots.txt`.
*   Revisa Términos de Servicio.
*   Evita sobrecargar sitios (haz pausas).
*   Cumple con leyes de protección de datos (GDPR, etc.).
*   No uses los datos para fines ilegales.
*   Se transparente con el origen de datos.
