import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Lista de bibliotecas a serem instaladas
packages = [
    "selenium",
    "selenium-stealth",
    "webdriver_manager",
    "requests"
]

# Instalando as bibliotecas
for package in packages:
    try:
        __import__(package)
    except ImportError:
        install(package)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import random
import json
import time
from urllib.parse import urlencode

# Defina uma lista de User-Agents
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.66',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, como Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (Linux; Android 10; SM-A505FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36'
]

# Configurações do Selenium
options = Options()
# options.add_argument("--headless")  # Executar em modo headless (opcional)
user_agent = random.choice(user_agents)
options.add_argument(f"user-agent={user_agent}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--disable-infobars')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')

# Instale e configure o ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Configurações do selenium-stealth
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True)

# Desabilitar a detecção do WebDriver
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

data = []

def scroll_page(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollBy(0, 250);")  # Scrollar para baixo em 300 pixels
        time.sleep(0.1)  # Aguardar o carregamento dos dados
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            driver.execute_script("window.scrollBy(0, -350);")
        last_height = new_height

        # Verificar se o botão existe e clicar nele
        # click_button_if_exists(driver)

def click_button_if_exists(driver):
    try:
        # Esperar até que o botão esteja presente e clicável
        button = WebDriverWait(driver, 0.05).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'section.listing-wrapper__pagination nav[data-testid="l-pagination"] button[aria-label="Próxima página"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView();", button)
        # time.sleep(1)  # Aguardar o carregamento e a visibilidade do botão
        driver.execute_script("arguments[0].click();", button)
        print("Botão clicado.")
    except Exception as e:
        print(f"Botão não encontrado ou não clicável: {e}")


for page in range(2, 100):
    query = urlencode({"pagina": page})
    response_url = f'https://www.zapimoveis.com.br/venda/?&transacao=venda&itl_id=1000072&itl_name=zap_-_botao-cta_buscar_to_zap_resultado-pesquisa&{query}'
    
    try:
        driver.get(response_url)

        # Scrollar gradualmente a página
        scroll_page(driver)

        script_tag = driver.find_element(By.ID, '_NEXT_DATA_')
        
        if script_tag:
            data_json = json.loads(script_tag.get_attribute('innerHTML'))
            data_vector = data_json['props']['pageProps']['initialProps']['data']

            for residence in data_vector:
                if residence['address']['coordinate']:
                    data.append({
                        "address": residence['address'],
                        "prices": residence['prices']
                    })

            print(len(data))
        else:
            print("Tag <script> com ID '_NEXT_DATA_' não encontrada.")
    except Exception as e:
        print(f"Erro ao processar a página {page}: {e}")
        continue

driver.quit()

print("data: ", data)
print("data quantidade: ", len(data))