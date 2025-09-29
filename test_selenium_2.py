from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import csv
import time

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def extract_events_for_date(driver, date_str):
    url = f"https://www.chateauversailles.fr/actualites/agenda-chateau-versailles/fr-{date_str}"
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.views-row")))
    except:
        print(f"Aucun événement ou page inaccessible pour la date {date_str}")
        return []

    events = []
    # On cherche chaque événement dans un bloc (ex: div.views-row ou autre)
    event_blocks = driver.find_elements(By.CSS_SELECTOR, "div.views-row")
    for block in event_blocks:
        try:
            # Type d'événement (ex: petit label ou catégorie)
            type_evt = block.find_element(By.CSS_SELECTOR, ".field--name-field-categories > div").text.strip()
        except:
            type_evt = "Non spécifié"

        try:
            titre = block.find_element(By.CSS_SELECTOR, "h2 a").text.strip()
        except:
            titre = ""

        try:
            description = block.find_element(By.CSS_SELECTOR, ".field--name-body").text.strip()
        except:
            description = ""

        try:
            lieu = block.find_element(By.CSS_SELECTOR, ".field--name-field-lieux").text.strip()
        except:
            lieu = ""

        try:
            horaires = block.find_element(By.CSS_SELECTOR, ".field--name-field-horaires").text.strip()
        except:
            horaires = "Non spécifié"

        try:
            tarif = block.find_element(By.CSS_SELECTOR, ".field--name-field-tarif").text.strip()
        except:
            tarif = "Non spécifié"

        try:
            url_detail = block.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")
        except:
            url_detail = url

        events.append({
            "date": date_str,
            "type_evenement": type_evt,
            "titre": titre,
            "description": description,
            "lieu": lieu,
            "horaires": horaires,
            "tarif": tarif,
            "url": url_detail
        })

    return events

def save_events_to_csv(events, filename):
    with open(filename, "w", newline="", encoding="utf-8-sig") as csvfile:
        fieldnames = ["date", "type_evenement", "titre", "description", "lieu", "horaires", "tarif", "url"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for event in events:
            writer.writerow(event)

if __name__ == "__main__":
    driver = setup_driver()
    all_events = []

    try:
        today = datetime.today()
        days_to_scrape = 15

        for i in range(days_to_scrape):
            d = today + timedelta(days=i)
            date_str = d.strftime("%Y-%m-%d")
            print(f"Scraping événements pour la date {date_str}...")
            day_events = extract_events_for_date(driver, date_str)
            print(f"  → {len(day_events)} événements trouvés")
            all_events.extend(day_events)
            time.sleep(1)  # éviter de surcharger le serveur

    finally:
        driver.quit()

    if all_events:
        save_events_to_csv(all_events, "versailles_evenements.csv")
        print(f"Fichier 'versailles_evenements.csv' créé avec {len(all_events)} événements.")
    else:
        print("Aucun événement trouvé.")
