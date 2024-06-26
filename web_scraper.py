import json
import time
import random

from urllib.parse import urlencode

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

class WebScraper:
    def __init__(self):
        self.data: list = []
        self.page: int = 1
        self.driver = None

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
        options.add_argument("--headless")
        user_agent = random.choice(user_agents)
        options.add_argument(f"user-agent={user_agent}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        # Desabilida Logs e Warnings desnecessários
        options.add_argument('--log-level=3')
        options.add_argument('--disable-dev-shm-usage')

        # Instala e configura o ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Configurações do selenium-stealth
        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True
        )

        # Mascara o uso do WebDriver para detectores de bot
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver
    
    def close_browser(self):
        self.driver.close()
        self.driver.quit()

    def extract_data(self, url):
        try:
            while self.page <= 100:
                print(f"Escaneando página {self.page}.")
                self.driver = self.config_browser()
                query = urlencode({ "pagina": self.page })
                response_url = f'{url}&{query}'
                self.driver.get(response_url)
            
                # Testa se as páginas para a pesquisa terminaram
                elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.result-empty')
                if elements:
                    print("Todas as páginas para a pesquisa foram analisadas.")
                    self.close_browser()
                    break

                script_element = self.driver.find_element(By.ID, '__NEXT_DATA__')
                if script_element:
                    data_json = json.loads(script_element.get_attribute('innerHTML'))
                    if 'initialProps' not in data_json['props']['pageProps']:
                        print(f"initialProps não encontrado!")
                        print(f"Aguardando um momento para continuar a extração.")
                        time.sleep(random.uniform(10, 16))
                        self.page = self.page + 1
                        self.close_browser()
                        continue
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
                print(f"Foram extraídos {len(self.data)} imóveis.")
                self.page = self.page + 1
                self.close_browser()

        except Exception as e:
            print(f"Erro ao processar a página {self.page}: {e}")

        print(f"Processamento finalizado com {len(self.data)} imóveis.")
        return self.data