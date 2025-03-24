import random
import time
import logging
import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración del logger
logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Función para añadir un retraso aleatorio
def add_random_delay(min_delay=2, max_delay=5):
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)

def create_database_and_table(db_config):
    """Crea la base de datos y la tabla si no existen."""
    conn = None
    try:
        # --- CONEXIÓN (¡Importante el charset!) ---
        conn = mysql.connector.connect(**db_config, charset='utf8mb4') # Conexión genérica
        cursor = conn.cursor()

        # --- CREAR BASE DE DATOS (con utf8mb4) ---
        cursor.execute("CREATE DATABASE IF NOT EXISTS infojobs_data CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.execute("USE infojobs_data;") # Cambio de DB

        # --- CREAR TABLA (con utf8mb4 en las columnas de texto) ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS frontend_jobs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_title VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
                company_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
                location VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
                work_format VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
                publication_date VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
                description TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
                contract_type VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
                work_type VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
                salary VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
                url VARCHAR(255)
            );
        """)
        conn.commit()
        logging.info("Base de datos y tabla creadas (o ya existían).")

    except mysql.connector.Error as e:
        logging.error(f"Error al crear la base de datos/tabla: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()

def insert_data(data, db_config):
    """Inserta los datos de las ofertas en la base de datos,
       solo si son ofertas completas (sin N/A en campos clave).
    """
    conn = None
    try:
        conn = mysql.connector.connect(**db_config, charset='utf8mb4')  # <--- AQUÍ
        cursor = conn.cursor()

        for job in data:
            # --- VERIFICACIÓN DE CAMPOS CLAVE (¡Importante!) ---
            if (job.get('Título del puesto') != "N/A" and
                job.get('Empresa') != "N/A"):  # Puedes añadir más campos aquí

                # --- Usa parámetros de consulta ---
                query = """
                    INSERT INTO frontend_jobs (job_title, company_name, location, work_format,
                                              publication_date, description, contract_type, work_type, salary, url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                params = (
                    job.get('Título del puesto'),
                    job.get('Empresa'),
                    job.get('Ubicación'),
                    job.get('Formato de trabajo'),
                    job.get('Fecha de publicación'),
                    job.get('Descripción'),
                    job.get('Tipo de contrato'),
                    job.get('Tipo de jornada'),
                    job.get('Salario'),
                    job.get('URL')
                )
                cursor.execute(query, params)
        conn.commit()
        logging.info("Datos insertados correctamente (solo ofertas completas).")  # Mensaje actualizado

    except mysql.connector.Error as e:
        logging.error(f"Error al insertar datos: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()

def main():
    db_config = {
        'host': os.getenv("DB_HOST", "localhost"),
        'port': int(os.getenv("DB_PORT", "3306")),
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD"),
        'database': os.getenv("DB_DATABASE")  # Necesario para insert_data
    }
    #Validación
    required_vars = ["DB_USER", "DB_PASSWORD", "DB_DATABASE"]
    missing_vars = [var for var in required_vars if os.getenv(var) is None]
    if missing_vars:
        logging.error(f"Faltan variables de entorno: {', '.join(missing_vars)}")
        return

    # --- 1. Crea la base de datos y la tabla (UNA SOLA VEZ) ---
    create_database_and_table(db_config)

    # --- CONFIGURACIÓN DE SELENIUM (con --lang=es) ---
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument('--lang=es')  # <--- AQUÍ: Idioma español
    # options.add_argument("--headless")  # Descomentar en producción
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 15)

    MAX_JOBS = 10

    try:
        logging.info("Conectando a InfoJobs...")
        url = 'https://www.infojobs.net/ofertas-trabajo/frontend'
        driver.get(url)

        try:
            accept_button = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
            accept_button.click()
            logging.info("Cookies aceptadas.")
            add_random_delay()
        except Exception as e:
             logging.warning("No se encontró el aviso de cookies o hubo un error.", exc_info=True)

        jobs_data = []

        # Encuentra el contenedor y verifica
        try:
            job_listings_container = wait.until(
                EC.presence_of_element_located((By.XPATH, "//ul[contains(@class, 'ij-List')]"))
            )
        except TimeoutException:
            logging.error("Tiempo de espera para el contenedor.")
            driver.save_screenshot("timeout_container.png")
            return
        except Exception as e:
            logging.error(f"Error al buscar contenedor: {e}")
            return

        # Bucle principal (solo si se encuentra el contenedor)
        if job_listings_container:
            for job_element in job_listings_container.find_elements(By.XPATH, ".//li[contains(@class, 'ij-List-item')]")[:MAX_JOBS]:
                try:
                    # Extracción de datos (XPaths relativos, manejo de errores)
                    try:
                        title_element = job_element.find_element(By.XPATH, ".//h2/a")
                        title = title_element.text.strip()
                        job_url = title_element.get_attribute("href")
                    except NoSuchElementException:
                        title = "N/A"
                        job_url = "N/A"

                    try:
                        company = job_element.find_element(By.XPATH, ".//h3/a").text.strip()
                    except NoSuchElementException:
                        company = "N/A"

                    try:
                        location = job_element.find_element(By.XPATH, ".//ul[contains(@class, 'ij-OfferCardContent-description-list')]/li[1]").text.strip()
                    except NoSuchElementException:
                        location = "N/A"

                    try:
                        work_format = job_element.find_element(By.XPATH, ".//ul[contains(@class, 'ij-OfferCardContent-description-list')]/li[contains(., 'Teletrabajo') or contains(., 'Híbrido')]").text.strip()
                    except NoSuchElementException:
                        work_format = "N/A"

                    try:
                        publication_date = job_element.find_element(By.XPATH, ".//span[contains(@class, 'ij-FormatterSincedate')]").text.strip()
                    except NoSuchElementException:
                        publication_date = "N/A"

                    try:
                        description = job_element.find_element(By.XPATH, ".//p[contains(@class, 'ij-OfferCardContent-description-description')]").text.strip()
                    except NoSuchElementException:
                        description = "N/A"

                    try:
                        contract_type = job_element.find_element(By.XPATH,".//ul[contains(@class, 'ij-OfferCardContent-description-list')]/li[contains(.,'Contrato')]").text.strip()
                    except NoSuchElementException:
                        contract_type = "N/A"

                    try:
                        work_type = job_element.find_element(By.XPATH,".//ul[contains(@class, 'ij-OfferCardContent-description-list')]/li[contains(.,'ornada')]").text.strip()
                    except NoSuchElementException:
                        work_type = "N/A"

                    try:
                        salary_element = job_element.find_element(By.XPATH, ".//span[contains(@class, 'ij-OfferCardContent-description-salary')]")
                        salary = salary_element.text.strip() if salary_element else "N/A"
                    except NoSuchElementException:
                        salary = "N/A"


                    jobs_data.append({
                        "Título del puesto": title,
                        "Empresa": company,
                        "Ubicación": location,
                        "Formato de trabajo": work_format,
                        "Fecha de publicación": publication_date,
                        "Descripción": description,
                        "Tipo de contrato": contract_type,
                        "Tipo de jornada": work_type,
                        "Salario": salary,
                        "URL": job_url,
                    })

                    logging.info(f"Extraído: {title} en {company}")  # Mensaje corregido
                    add_random_delay(2, 4)

                except StaleElementReferenceException:
                    logging.warning("Elemento stale, saltando.")
                    continue
                except Exception as e:
                    logging.error(f"Error al extraer datos: {e}", exc_info=True)
                    driver.save_screenshot(f"error_extraccion_{len(jobs_data)}.png")
                    continue

        if not jobs_data:
            logging.warning("No se extrajeron datos.")
        else:
            logging.info(f"Total extraído: {len(jobs_data)} ofertas")

            # --- 2. Inserta los datos (DESPUÉS de extraerlos) ---
            logging.info("Guardando en la base de datos...")
            insert_data(jobs_data, db_config)
            logging.info("Datos guardados.")

    except Exception as e:
        logging.error(f"Error principal: {e}", exc_info=True)
        driver.save_screenshot("error_general.png")
    finally:
        driver.quit()
        logging.info("Scraper finalizado.")

if __name__ == "__main__":
    main()