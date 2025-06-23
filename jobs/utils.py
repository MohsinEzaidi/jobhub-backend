def send_offer_notification(user_email, job):
    subject = f"Nouvelle offre : {job.titre}"  # Changed from title
    message = f"""
Bonjour,

Une nouvelle offre correspond à vos intérêts !

Intitulé : {job.titre}
Entreprise : {job.entreprise}  # Changed from company_name
Lieu : {job.localisation}  # Changed from location
"""