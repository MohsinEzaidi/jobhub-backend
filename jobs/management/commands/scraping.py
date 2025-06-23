from django.core.management.base import BaseCommand
from jobs.models import Job
from datetime import datetime
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class Command(BaseCommand):
    help = 'Scraping des offres d\'emploi'

    def handle(self, *args, **kwargs):
        job_keyword = input("🔍 Entrez le métier recherché : ")
        html = self.fetch_job_listings(job_keyword)
        
        if html:
            jobs = self.parse_job_listings(html)
            results = [job for job in (self.extract_job_details(job) for job in jobs) if job]
            
            if self.save_to_json(results):
                self.stdout.write(self.style.SUCCESS("✅ Données sauvegardées dans le fichier JSON"))
                self.save_jobs_to_database(results)
            else:
                self.stdout.write(self.style.ERROR("❌ Erreur lors de l'enregistrement des données dans le fichier JSON"))

    def clean_text(self, text):
        return " ".join(text.strip().split()).replace('\n', ' ').replace('\t', ' ') if text else ""

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    def fetch_job_listings(self, job_keyword):
        url = f"https://www.rekrute.com/offres.html?clear=1&keyword={job_keyword}"
        driver = None
        try:
            driver = self.setup_driver()
            self.stdout.write("🕸️ Chargement de la page...")
            driver.get(url)
            
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-sm-10"))
            )
            return driver.page_source
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erreur : {str(e)}"))
            return None
        finally:
            if driver:
                driver.quit()

    def extract_job_details(self, job_div):
        try:
            title_tag = job_div.find("a", class_="titreJob")
            if not title_tag:
                return None  

            title_parts = title_tag.text.split("|")
            details = {
                "Titre": self.clean_text(title_parts[0]),
                "Localisation": self.clean_text(title_parts[1]) if len(title_parts) > 1 else "Non spécifiée",
                "Entreprise": self.clean_text(job_div.find("span", style="color: #5b5b5b;").text) if job_div.find("span", style="color: #5b5b5b;") else "Non spécifiée",
                "Lien": title_tag.get("href", "")
            }

            em_date = job_div.find("em", class_="date")
            if em_date:
                spans = em_date.find_all("span")
                details["Date Publication"] = self.format_date(spans[0].text) if len(spans) > 0 else "Non spécifiée"
                details["Date Limite"] = self.format_date(spans[1].text) if len(spans) > 1 else "Non spécifiée"

            postes_span = job_div.find(string=lambda t: "Postes proposés" in str(t))
            details["Postes disponibles"] = self.clean_text(postes_span.find_next("span").text) if postes_span and postes_span.next_sibling else "1"

            info_span = job_div.find("span", style="color: #5b5b5b;margin-top: 5px;")
            details["Description"] = self.clean_text(info_span.text) if info_span else "Non spécifiée"

            meta_keys = {
                "Secteur d'activité": "Secteur",
                "Fonction": "Fonction",
                "Expérience requise": "Expérience",
                "Niveau d'étude demandé": "Niveau d'études",
                "Type de contrat proposé": "Contrat"
            }

            for item in job_div.find_all("li"):
                text = self.clean_text(item.text)
                for key, dest in meta_keys.items():
                    if key in text:
                        details[dest] = text.split(":", 1)[-1].strip()
                        if key == "Type de contrat proposé":
                            contrat_parts = details[dest].split("-")
                            details["Contrat"] = contrat_parts[0].strip()
                            details["Télétravail"] = contrat_parts[1].split(":")[-1].strip() if len(contrat_parts) > 1 else "Non"
                        break

            details.setdefault("Secteur", "Non spécifié")
            details.setdefault("Fonction", "Non spécifiée")
            details.setdefault("Expérience", "Non spécifiée")
            details.setdefault("Niveau d'études", "Non spécifié")
            details.setdefault("Contrat", "Non spécifié")
            details.setdefault("Télétravail", "Non spécifié")

            return details
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️ Erreur d'extraction: {str(e)}"))
            return None

    def parse_job_listings(self, html):
        soup = BeautifulSoup(html, "html.parser")
        return soup.find_all("div", class_="col-sm-10 col-xs-12")

    def format_date(self, date_str):
        try:
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            return date_obj.strftime("%Y-%m-%d")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️ Erreur de format de date: {str(e)}"))
            return "Non spécifiée"

    def save_to_json(self, data, filename="job_offers.json"):
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erreur lors de l'enregistrement dans le fichier JSON : {str(e)}"))
            return False

    def save_jobs_to_database(self, jobs_data):
     for job_data in jobs_data:
        try:
            # Affichage pour déboguer la valeur de télétravail avant conversion
            teletravail_raw = job_data.get("Télétravail", "").strip().lower()
            self.stdout.write(self.style.NOTICE(f"Valeur brute de 'Télétravail': '{teletravail_raw}'"))

            # Vérification et conversion stricte
            if teletravail_raw in ["oui", "true", "vrai", "hybride", "partiel"]:
                teletravail = True
            elif teletravail_raw in ["non", "false", "faux"]:
                teletravail = False
            else:
                teletravail = False  # Par défaut, le télétravail est false si la valeur est inconnue

            # Affichage après conversion pour déboguer
            self.stdout.write(self.style.NOTICE(f"Valeur convertie de 'Télétravail': {teletravail}"))

            # Créer l'offre dans la base de données avec la valeur de teletravail corrigée
            job = Job.objects.create(
                titre=job_data["Titre"],
                entreprise=job_data["Entreprise"],
                localisation=job_data["Localisation"],
                description=job_data["Description"],
                date_publication=job_data["Date Publication"],
                date_limite=job_data["Date Limite"],
                postes_disponibles=job_data["Postes disponibles"],
                lien=job_data["Lien"],
                secteur=job_data["Secteur"],
                fonction=job_data["Fonction"],
                experience=job_data["Expérience"],
                niveau_etudes=job_data["Niveau d'études"],
                contrat=job_data["Contrat"],
                teletravail=teletravail  # Utiliser la valeur de teletravail corrigée
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Offre '{job_data['Titre']}' ajoutée à la base de données."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erreur lors de l'ajout de l'offre '{job_data['Titre']}': {str(e)}"))
