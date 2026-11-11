# ColdWatch — Surveillance frigorifique IoT

Projet Django REST Framework + interface web Django Templates, prêt à configurer pour PythonAnywhere.

## Fonctionnalités
- Tableau de bord responsive, deux cartes température/humidité, historique graphique (8 valeurs maximum), rafraîchissement chaque minute.
- Mesures JSON reçues depuis ESP8266 / DHT11 toutes les 20 minutes.
- Détection d'excursions, création automatique d'incident, journal d'événements.
- Notifications **dans l'application** pour les trois premiers utilisateurs actifs du groupe `Operateurs`.
- Acquittement, commentaires, clôture et suivi des incidents.
- Détection visuelle de l'absence de données lorsque le tableau de bord est consulté.
- Connexion utilisateurs, administration et paramètres configurables.

## Installation locale (Windows PowerShell)
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# MODIFIER .env AVANT DE DÉMARRER
python manage.py migrate
python manage.py setup_operators
python manage.py createsuperuser
python manage.py runserver 192.168.1.40:8000
```

Créer trois comptes actifs dans `/admin/`, les ajouter au groupe `Operateurs`. Les comptes administrateurs peuvent régler les seuils depuis `/configuration/`.

## API
POST `/api/post` — JSON `{"temp":4.5,"hum":60}` sans authentification de carte. Renvoie HTTP 201 et la mesure. Compatible avec le corps JSON original ESP8266 ; aucun changement nécessaire dans le code Arduino.
GET `/api/data` — 200 dernières mesures, connexion utilisateur requise.
GET `/api/incidents` — incidents, connexion requise.
GET `/api/notifications` — notifications du compte, connexion requise.

Test API local :
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/post' -Method POST -ContentType 'application/json' -Body '{"temp":11.5,"hum":55}'
```

### Modification minimale du code ESP8266
```cpp
const char* serverName = "https://YOUR_USERNAME.pythonanywhere.com/api/post";
// IMPORTANT: HTTPS nécessite WiFiClientSecure, pas WiFiClient.
// Utilisez un certificat CA valide avec client.setTrustAnchors(...) selon le firmware.
// Évitez setInsecure() en production.
// Aucun header X-Device-Key requis.
```
Le fichier `esp8266_example.ino` utilise HTTP pour les tests locaux. Pour PythonAnywhere, utilisez HTTPS et une validation TLS correcte.

## Déploiement PythonAnywhere
1. Créer un compte PythonAnywhere et ouvrir une console Bash.
2. Uploader le projet ou `git clone` dans `/home/YOUR_USERNAME/coldwatch`.
3. Créer un virtualenv : `mkvirtualenv --python=python3.11 coldwatch-env` (adapter à une version Python disponible), puis `pip install -r requirements.txt`.
4. Copier `.env.example` en `.env`, définir SECRET_KEY fort, DEBUG=False, ALLOWED_HOSTS=YOUR_USERNAME.pythonanywhere.com, CSRF_TRUSTED_ORIGINS=https://YOUR_USERNAME.pythonanywhere.com.
5. Configurer `DATABASE_URL` vers une base PostgreSQL **accessible depuis votre compte PythonAnywhere**. La disponibilité PostgreSQL dépend de l'offre; sinon SQLite est disponible pour démonstration.
6. Exécuter `python manage.py migrate && python manage.py setup_operators && python manage.py createsuperuser && python manage.py collectstatic --noinput`.
7. Onglet **Web** > Add a new web app > Manual configuration > Python version compatible.
8. Configurer le virtualenv dans l'onglet Web. Éditer le fichier WSGI :
```python
import os,sys
project='/home/YOUR_USERNAME/coldwatch'
if project not in sys.path:sys.path.insert(0,project)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','coldwatch.settings')
from django.core.wsgi import get_wsgi_application
application=get_wsgi_application()
```
9. Reload et visiter `https://YOUR_USERNAME.pythonanywhere.com/`.
10. Vérifier que votre offre PythonAnywhere permet les connexions sortantes nécessaires depuis le réseau de l'ESP8266 et l'accès à PostgreSQL. Les plans gratuits ont des limitations; vérifier les conditions en vigueur.

## Notes de sécurité / limitations
- Le point d'ingestion est protégé par clé d'appareil, les pages et lectures API par authentification Django; ne jamais exposer la clé dans une page web publique.
- La clé est transmise uniquement via HTTPS en production. Ne pas utiliser le `WiFiClient` HTTP original pour une URL HTTPS.
- Les notifications sont **internes à l'application** (pas d'email/SMS/push). Les 3 opérateurs doivent être configurés.
- Le statut hors ligne est calculé à l'ouverture/actualisation du tableau de bord; aucune tâche planifiée ne crée de notification de panne réseau.
- Un incident reste actif jusqu'à clôture manuelle. Les nouvelles mesures hors seuil sont journalisées dans l'incident actif.
- Les seuils par défaut 2–8 °C sont des exemples, à adapter à l'enceinte et aux produits.
- Chart.js et Google Fonts sont chargés depuis des CDN externes; connexion internet nécessaire pour les graphiques/polices.
- SQLite pour développement, PostgreSQL recommandé selon le cahier des charges.

## Tests
`python manage.py test`

## Cahier des charges
Version basée sur le document fourni « ColdWatch — Système intelligent de surveillance d'une enceinte frigorifique ». Le cahier demande React.js; cette livraison utilise des templates Django pour un déploiement PythonAnywhere monolithique, sans build frontend Node.js.

## Compatibilité ESP8266 et sécurité
Le point d'entrée `POST /api/post` accepte sans clé le JSON `{"temp":23.3,"hum":47.6}` envoyé par le code Arduino original. Les endpoints de consultation et le tableau de bord conservent l'authentification utilisateur.

**Attention :** cet endpoint est public et accepte des données non authentifiées. Pour un déploiement Internet, n'utilisez pas ce montage pour une surveillance de sécurité critique : un tiers peut envoyer de fausses mesures et déclencher de faux incidents. Prévoir authentification, limitation de débit et HTTPS dans une version de production.

Pour démarrer localement, utilisez `DATABASE_URL=` vide et une configuration SQLite valide. Si votre copie de `settings.py` construit la base via `dj_database_url`, assurez-vous qu'une URL vide utilise bien SQLite.
