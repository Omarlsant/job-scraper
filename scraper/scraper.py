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
import os  # Importa el módulo os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
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

# Función para ejecutar SQL (adaptada para MySQL y con manejo de errores mejorado)
def execute_sql(sql_statements, db_config):
    conn = None  # Inicializar conn
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        for statement in sql_statements:
            cursor.execute(statement)
        conn.commit()
        logging.info("Sentencias SQL ejecutadas con éxito.")
    except mysql.connector.Error as e:
        logging.error(f"Error de MySQL: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

# Función para generar y ejecutar el SQL (adaptada para MySQL)
def generate_and_execute_sql(data, db_config):
    sql_statements = [
        "CREATE DATABASE IF NOT EXISTS infojobs_data;",
        "USE infojobs_data;",
        """CREATE TABLE IF NOT EXISTS frontend_jobs (
           id INT AUTO_INCREMENT PRIMARY KEY,
           job_title VARCHAR(255),
           company_name VARCHAR(255),
           location VARCHAR(255),
           work_format VARCHAR(100),
           publication_date VARCHAR(100),
           description TEXT,
           contract_type VARCHAR(100),
           work_type VARCHAR(100),
           salary VARCHAR(100)
        );"""
    ]

    for job in data:
        # Escapar comillas simples correctamente y manejar valores None
        values = []
        for key in ['Título del puesto', 'Empresa', 'Ubicación', 'Formato de trabajo',
                    'Fecha de publicación', 'Descripción', 'Tipo de contrato', 'Tipo de jornada', 'Salario']:
            value = job.get(key)  # Usa .get() para manejar valores faltantes
            if value is None:
                values.append("NULL") # o '' si prefieres strings vacios
            else:
                values.append(f"'{value.replace('"', "''")}'")  # Escapa comillas simples

        query = f"""INSERT INTO frontend_jobs (job_title, company_name, location, work_format,
                  publication_date, description, contract_type, work_type, salary)
                  VALUES ({", ".join(values)});"""
        sql_statements.append(query)

    execute_sql(sql_statements, db_config)

def main():
    # ---  CONFIGURACIÓN DE LA CONEXIÓN A MYSQL desde .env  ---
    db_config = {
        'host': os.getenv("DB_HOST", "localhost"),  # Valor por defecto si no está en .env
        'port': int(os.getenv("DB_PORT", "3306")),   # Convierte a entero, valor por defecto
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD"),
        'database': os.getenv("DB_DATABASE")
    }

    # --- Validación de variables de entorno esenciales ---
    required_vars = ["DB_USER", "DB_PASSWORD", "DB_DATABASE"]
    missing_vars = [var for var in required_vars if os.getenv(var) is None]
    if missing_vars:
        logging.error(f"Faltan variables de entorno esenciales: {', '.join(missing_vars)}")
        return  # Sale del programa si faltan variables


    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")  # Considera usar headless en producción
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)
    container_wait = WebDriverWait(driver, 30)
    MAX_JOBS = 10

    try:
        logging.info("Conectando a InfoJobs...")
        url = 'https://www.infojobs.net/ofertas-trabajo/frontend'
        driver.get(url)

        # Aceptar cookies
        try:
            accept_button = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
            accept_button.click()
            logging.info("Cookies aceptadas.")
            add_random_delay(2, 4)
        except Exception as e:
            logging.warning(f"No se encontró el aviso de cookies o hubo un error: {e}")

        jobs_data = []
        try:
            job_listings_container = container_wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[3]/div[1]/main/div[2]/div[2]/ul')))
            logging.info(f"Se encontraron ofertas de trabajo.")

        except TimeoutException:
            logging.error("Tiempo de espera agotado al encontrar el contenedor de ofertas.")
            return
        except Exception as e:
            logging.error(f"Error al buscar ofertas: {type(e).__name__} - {e}")
            return

        # --- BUCLE PRINCIPAL ---
        # Usar nombres de clase o XPaths *relativos* es crucial para la robustez
        for job_element in job_listings_container.find_elements(By.TAG_NAME, 'li')[:MAX_JOBS]:
            try:
                # --- XPaths RELATIVOS y BASADOS EN CLASES (Ejemplo, ajusta según la estructura real) ---
                # Intenta encontrar elementos basados en sus clases o atributos, *dentro* del job_element
                title = job_element.find_element(By.CSS_SELECTOR, 'h2.ij-OfferCardBasic-description-title').text.strip()  # Ejemplo usando CSS selector
                company = job_element.find_element(By.CSS_SELECTOR, 'h3.ij-OfferCardBasic-description-subtitle').text.strip() #Ejemplo


                # Los siguientes son ejemplos.  Adapta los selectores a la estructura ACTUAL de la página.
                # Usa las herramientas de desarrollador del navegador para inspeccionar los elementos.
                try:
                    location = job_element.find_element(By.CSS_SELECTOR, 'ul.ij-OfferCardBasic-infoList > li:nth-child(1)').text.strip()
                except NoSuchElementException:
                    location = "N/A"

                try:
                    work_format = job_element.find_element(By.CSS_SELECTOR, 'ul.ij-OfferCardBasic-infoList > li:nth-child(2)').text.strip()
                except NoSuchElementException:
                    work_format = "N/A"
                try:
                    publication_date = job_element.find_element(By.CSS_SELECTOR, 'ul.ij-OfferCardBasic-infoList > li:nth-child(3)').text.strip()
                except NoSuchElementException:
                    publication_date = "N/A"

                try:
                    description = job_element.find_element(By.CSS_SELECTOR, 'p.ij-OfferCardBasic-description-text').text.strip()
                except NoSuchElementException:
                    description = "N/A"


                try:
                    contract_type = job_element.find_element(By.CSS_SELECTOR, "ul.ij-OfferCardBasic-infoExtraList > li:nth-child(1)").text.strip()
                except NoSuchElementException:
                    contract_type = "N/A"

                try:
                     work_type = job_element.find_element(By.CSS_SELECTOR, "ul.ij-OfferCardBasic-infoExtraList > li:nth-child(2)").text.strip()
                except NoSuchElementException:
                    work_type = "N/A"

                try:
                    salary = job_element.find_element(By.CSS_SELECTOR, "ul.ij-OfferCardBasic-infoExtraList > li:nth-child(3)").text.strip()
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
                    "Salario": salary
                })

                logging.info(f"Oferta extraída: {title} en {company}")
                add_random_delay(2, 5)

            except NoSuchElementException as e:
                logging.error(f"Elemento no encontrado al extraer una oferta: {e}")
                continue  # Continua con el siguiente elemento 'li'
            except StaleElementReferenceException:
                logging.warning("Elemento 'stale'.  Reintentando...")
                continue # Intenta de nuevo con el siguiente elemento
            except Exception as e:
                logging.error(f"Error al extraer una oferta: {type(e).__name__} - {e}")
                continue

        if not jobs_data:
            logging.warning("No se han encontrado datos en la página.")
        else:
            logging.info(f"Datos extraídos: {len(jobs_data)} ofertas")

        logging.info("Generando y ejecutando sentencias SQL...")
        generate_and_execute_sql(jobs_data, db_config)
        logging.info("Datos guardados en la base de datos MySQL")

    except Exception as e:
        logging.error(f"Error general: {type(e).__name__} - {e}")
        driver.save_screenshot("general_error.png")
    finally:
        driver.quit()
        logging.info("Scraper finalizado.")

if __name__ == "__main__":
    main()