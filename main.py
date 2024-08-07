import re
import sys
import subprocess

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Lista de bibliotecas a serem instaladas
packages = [
    "selenium",
    "selenium-stealth",
    "webdriver_manager"
]

url = input("Insira a URL para começar a extração: ")
# Remove paramentro 'pagina=X' da url
url = re.sub(r'&pagina=[0-9]', '', url)
print("url: ", url)

# Instalando as bibliotecas
for package in packages:
    try:
        __import__(package)
    except ImportError:
        install(package)

from web_scraper import WebScraper
from handle_file import HandleFile

# Realiza extração
scraper = WebScraper()
data = scraper.extract_data(url)

filler = HandleFile(data)
filler.create_file()


