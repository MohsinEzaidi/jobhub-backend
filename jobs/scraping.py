import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from jobs.models import Job  # Importer le modèle Django

def clean_text(text):
    if not text:
        return ""
    return " ".join(text.strip().split()).replace('\n', ' ').replace('\t', ' ')

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=chrome_options)

def fetch_job_listings(job_keyword):
    url = f"https://www.rekrute.com/offres.html?clear=1&keyword={job_keyword}"
    driver = None  # Déclarer driver avant l'utilisation
    try:
        driver = setup_driver()
        print("🕸️ Chargement de la page...")
        driver.get(url)
        
        while True:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-sm-10"))
            )
            page_source = driver.page_source
            yield page_source  # Cette page sera traitée par la fonction principale
            
            # Vérifier s'il y a un bouton "Suivant" pour paginer
            try:
                next_button = driver.find_element(By.CLASS_NAME, "next-page")
                next_button.click()
                WebDriverWait(driver, 10).until(
                    EC.staleness_of(next_button)
                )
            except Exception:
                break  # Sortir de la boucle si pas de page suivante

    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
    finally:
        if driver:  # Vérifier si driver est initialisé avant de tenter de le quitter
            driver.quit()



def extract_job_details(job_div):
    try:
        title_tag = job_div.find("a", class_="titreJob")
        if not title_tag:
            return None
        
        title_parts = title_tag.text.split("|")
        details = {
            "title": clean_text(title_parts[0]),
            "location": clean_text(title_parts[1]) if len(title_parts) > 1 else "Non spécifiée",
            "company": clean_text(job_div.find("span", style="color: #5b5b5b;").text) if job_div.find("span", style="color: #5b5b5b;") else "Non spécifiée",
            "link": title_tag.get("href", "")
        }

        em_date = job_div.find("em", class_="date")
        if em_date:
            spans = em_date.find_all("span")
            details["publication_date"] = spans[0].text if len(spans) > 0 else "Non spécifiée"
            details["deadline"] = spans[1].text if len(spans) > 1 else "Non spécifiée"
            postes_span = em_date.find("span", string=lambda t: "Postes proposés" in str(t))
            details["available_positions"] = clean_text(postes_span.next_sibling) if postes_span else "1"
        else:
            details.update({
                "publication_date": "Non spécifiée",
                "deadline": "Non spécifiée",
                "available_positions": "1"
            })

        info_div = job_div.find("div", class_="info")
        details["description"] = clean_text(info_div.span.text) if info_div and info_div.span else ""

        return details
    except Exception as e:
        print(f"⚠️ Erreur d'extraction: {str(e)}")
        return None

def parse_job_listings(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.find_all("div", class_="col-sm-10 col-xs-12")

def main():
    try:
        job_keyword = input("🔍 Entrez le métier recherché : ")
        for html in fetch_job_listings(job_keyword):
            jobs = parse_job_listings(html)
            for job in jobs:
                job_details = extract_job_details(job)
                if job_details:
                    # Vérifier si l'offre existe déjà par son lien
                    existing_job = Job.objects.filter(link=job_details["link"]).first()
                    if not existing_job:
                        # Enregistrer l'offre uniquement si elle n'existe pas déjà
                        Job.objects.create(
                            titre=job_details["titre"],
                            entreprise=job_details["entreprise"],
                            localisation=job_details["localisation"],
                            description=job_details["description"],
                            lien=job_details["lien"],
                            date_publication=job_details["date_publication"],
                            date_limite=job_details["date_limite"],
                            postes_disponibles=job_details["postes_disponibles"],
                            secteur=job_details["secteur"],
                            fonction=job_details["fonction"],
                            experience=job_details["experience"],
                            niveau_etudes=job_details["niveau_etudes"],
                            contrat=job_details["contrat"],
                            teletravail=job_details["teletravail"],
                            type_emploi=job_details["type"],
                            salaire=job_details["salary"]
                        )
                        print(f"✅ Offre enregistrée: {job_details['title']}")
                    else:
                        print(f"🔸 Offre déjà existante: {job_details['title']}")
            print(f"✅ {len(jobs)} offres traitées.")
    except Exception as e:
        print(f"❌ Erreur générale : {str(e)}")

if __name__ == "__main__":
    main()
