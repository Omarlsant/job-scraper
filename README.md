# Job Scraper: Plataforma de Búsqueda y Análisis de Empleos Tecnológicos - PROYECTO UNICAMENTE CON FINES EDUCATIVOS PERSONALES.

Proyecto educativo para búsqueda, análisis y recomendación de empleos en tecnología.  Web scraping, backend (FastAPI), frontend (React/Vite), base de datos (MySQL) y microservicios (recomendaciones, predicción de salario, visualizaciones).  *Solo para fines educativos.*

## 1. Introducción

Herramienta que extrae datos de ofertas de empleo y ofrece:

*   **Base de Datos:** MySQL.
*   **Despliegue:** Docker/Docker Compose.

## 2. Tecnologías

*   **Scraper:** Python, Selenium.
*   **Base de Datos:** MySQL.
*   **Contenedores:** Docker, Docker Compose.
*   **Control de Versiones:** Git, GitHub.
*   **Entorno:** VS Code.
*   **Otros:** dotenv.

## 3. Estructura del Proyecto

    job-scraper/
    ├── scraper/
    │   ├── scraper.py           # Código principal del scraper
    │   ├── Dockerfile           # Dockerfile para el scraper
    │   ├── pyproject.toml       # Archivo de configuración para uv
    │   ├── tests/               # Carpeta para las pruebas unitarias del scraper
    │   │   ├── test_scraper.py  # Pruebas unitarias para el scraper
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
