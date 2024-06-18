import sys
import subprocess

from web_scraper import WebScraper

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

# Realiza extração
scraper = WebScraper()
scraper.extract_data()

