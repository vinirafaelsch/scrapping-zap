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
data = scraper.extract_data()

filler = HandleFile(data)
filler.data2geojson()


