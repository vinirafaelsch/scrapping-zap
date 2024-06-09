from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import random
import json
import time
from urllib.parse import urlencode

class WebScraper:
    def __init__(self):
        self.data: list = []
        self.page: int = 1
        self.driver = self.config_browser()

    def config_browser(self):
        # Lista de User-Agents
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
        # options.add_argument("--headless")
        user_agent = random.choice(user_agents)
        options.add_argument(f"user-agent={user_agent}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')

        # Instala e configura o ChromeDriver
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

        # Mascara o uso do WebDriver para detectores de bot
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver

    def check_button_exists(self):
        try:
            button = WebDriverWait(self.driver, 0.02).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'section.listing-wrapper__pagination nav[data-testid="l-pagination"] button[aria-label="Próxima página"]'))
            )
            return True
        except Exception as e:
            print(f"Botão não encontrado ou não clicável: {e}")
            return False

    def click_next_button(self):
        try:
            button = self.driver.find_element(By.CSS_SELECTOR, 'section.listing-wrapper__pagination nav[data-testid="l-pagination"] button[aria-label="Próxima página"]')
            self.driver.execute_script("arguments[0].scrollIntoView();", button)
            self.driver.execute_script("arguments[0].click();", button)
            self.page = self.page + 1
        except Exception as e:
            print(f"Erro ao clicar no botão: {e}")

    def extract_data(self):
        query = urlencode({ "pagina": self.page })
        response_url = f'https://www.zapimoveis.com.br/venda/?&transacao=venda&itl_id=1000072&itl_name=zap_-_botao-cta_buscar_to_zap_resultado-pesquisa&{query}'
        self.driver.get(response_url)

        try:
            actions = ActionChains(self.driver)
            while self.page <= 3:
                actions.send_keys(Keys.END).perform()
                time.sleep(random.uniform(0.3, 0.6))
                actions.send_keys(Keys.HOME).perform()
                time.sleep(random.uniform(0.3, 0.6))

                if self.check_button_exists():
                    #######
                    content = self.driver.page_source
                    with open('conteudo.html', 'w', encoding='utf-8') as file:
                        file.write(content)
                    break
                    ######
                    script_element = self.driver.find_element(By.ID, '__NEXT_DATA__')
                    if script_element:
                        data_json = json.loads(script_element.get_attribute('innerHTML'))
                        data_vector = data_json['props']['pageProps']['initialProps']['data']

                        for residence in data_vector:
                            if residence['address']['coordinate']:
                                self.data.append({
                                    "id": residence['id'] or "",
                                    "address": residence['address'] or "",
                                    "prices": residence['prices'] or "",
                                    "description": residence['description'] or "",
                                    "amenities": residence['amenities'] or "",
                                    "url": residence['href'] or "",
                                    "business": residence['business'] or "",
                                    "unitTypes": residence['unitTypes'] or ""
                                })
                        self.click_next_button()

        except Exception as e:
            print(f"Erro ao processar a página {self.page}: {e}")

        print(self.data)
        print(len(self.data))
        self.driver.quit()

scraper = WebScraper()
scraper.extract_data()