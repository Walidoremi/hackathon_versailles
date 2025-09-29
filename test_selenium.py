from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Options pour garder Chrome ouvert (utile pour debug)
options = Options()
options.add_experimental_option("detach", True)
options.add_argument("--log-level=3")  # réduire bruit logs

# Lance le driver
driver = webdriver.Chrome(options=options)

# Ouvre Google
driver.get("https://www.google.com")

# Attendre que la barre de recherche soit interactive
search_box = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "q"))
)

# Écrire dans la barre de recherche et envoyer
search_box.send_keys("Selenium WebDriver\n")

# Attendre que les résultats apparaissent
results = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h3"))
)

# Afficher les 5 premiers titres de résultats
for r in results[:5]:
    print(r.text)

# driver.quit()  # commente si tu veux garder la fenêtre ouverte