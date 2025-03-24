import pytest
from unittest.mock import patch, MagicMock, call, ANY
from dotenv import load_dotenv
# Estas importaciones se usan indirectamente para los Mocks,
# Aunque Pylance muestre advertencia, no quitarlas.
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import mysql.connector
import time
from scraper.scraper import main, create_database_and_table, insert_data, add_random_delay

@pytest.fixture(scope="session", autouse=True)
def load_env_vars():
    """Carga las variables de entorno desde el archivo .env."""
    load_dotenv()

def test_add_random_delay_within_range():
        """Test que verifica si el retraso está en el rango correcto"""
        min_delay = 1
        max_delay = 3
        start_time = time.time()
        add_random_delay(min_delay, max_delay)
        end_time = time.time()
        elapsed_time = end_time - start_time
        assert min_delay <= elapsed_time <= max_delay

@patch("mysql.connector.connect")
def test_execute_sql_success(mock_connect):
    """Testea la ejecución exitosa de sentencias SQL."""
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    sql_statements = ["CREATE TABLE test_table (id INT)", "INSERT INTO test_table VALUES (1)"]
    db_config = {"host": "localhost", "user": "testuser"}
    try:
      create_database_and_table(db_config)
    except Exception:
      pass

    mock_connect.assert_called()
    mock_conn.cursor.assert_called()
    assert mock_cursor.execute.call_count == 3
    mock_conn.commit.assert_called()
    mock_conn.close.assert_called()

@patch("scraper.scraper.create_database_and_table")
@patch("scraper.scraper.insert_data")
@patch('scraper.scraper.webdriver.Chrome')
@patch('scraper.scraper.WebDriverWait')
def test_generate_and_execute_sql(mock_wait, mock_chrome, mock_insert_data, mock_create_db):

    # Datos de prueba
    test_data = [
        {
            "Título del puesto": "Frontend Developer",
            "Empresa": "Test Company",
            "Ubicación": "Madrid",
            "Formato de trabajo": "Remoto",
            "Fecha de publicación": "Hoy",
            "Descripción": "Test description",
            "Tipo de contrato": "Indefinido",
            "Tipo de jornada": "Completa",
            "Salario": "30000€",
            "URL": "http://test.com"
        }
    ]

    db_config = {"host": "localhost", "user": "testuser", "database": "testdb"}
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver
    mock_wait_instance = MagicMock()
    mock_wait.return_value = mock_wait_instance

    mock_job = MagicMock()
    mock_job.find_element.side_effect = [
      MagicMock(text="Frontend Developer", get_attribute=MagicMock(return_value="http://test.com")),
      MagicMock(text="Test Company"),
      MagicMock(text="Madrid"),
      MagicMock(text="Remoto"),
      MagicMock(text="Hoy"),
      MagicMock(text="Test description"),
      MagicMock(text="Indefinido"),
      MagicMock(text="Completa"),
      MagicMock(text="30000€"),
      ]

    mock_listings = MagicMock()
    mock_listings.find_elements.return_value = [mock_job]
    mock_wait_instance.until.return_value = mock_listings
    mock_insert_data.return_value = None

    main()
    mock_create_db.assert_called_once_with(ANY)
    mock_insert_data.assert_called_once_with(test_data, ANY)

@patch('scraper.scraper.webdriver.Chrome')
@patch('scraper.scraper.WebDriverWait')
def test_main_cookies_not_found(mock_wait, mock_chrome):
    """Test que simula el caso en donde no está presente el botón de cookies."""
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver
    mock_wait_instance = MagicMock()
    mock_wait.return_value = mock_wait_instance
    mock_wait_instance.until.side_effect = TimeoutException("Timeout simulado cookies")

    with patch("scraper.scraper.create_database_and_table") as mock_create_db, \
         patch("scraper.scraper.insert_data") as mock_insert_data:

        main()
        mock_driver.get.assert_called_once_with('https://www.infojobs.net/ofertas-trabajo/frontend')
        mock_wait.assert_has_calls([
            call(mock_driver, 15),
        ])

        mock_driver.quit.assert_called_once()
        mock_create_db.assert_called_once()
        mock_insert_data.assert_not_called()


@patch('scraper.scraper.webdriver.Chrome')
@patch('scraper.scraper.WebDriverWait')
def test_main_no_job_listings(mock_wait, mock_chrome):
    """
    Test para el caso en que no se encuentran ofertas de trabajo.
    """
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver
    mock_wait_instance = MagicMock()
    mock_wait.return_value = mock_wait_instance

    mock_wait_instance.until.side_effect = TimeoutException("Simulated Timeout")

    with patch("scraper.scraper.create_database_and_table") as mock_create_db, \
         patch("scraper.scraper.insert_data") as mock_insert_data:
        main()

        mock_driver.get.assert_called_once_with('https://www.infojobs.net/ofertas-trabajo/frontend')

        mock_wait.assert_has_calls([
           call(mock_driver, 15),
        ])

        mock_insert_data.assert_not_called()
        mock_driver.quit.assert_called_once()
        mock_create_db.assert_called_once()