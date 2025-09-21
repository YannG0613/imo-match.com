# ImoMatch - Application Immobilière avec IA

## 🏠 Description

ImoMatch est une application web moderne développée avec Streamlit qui utilise l'intelligence artificielle pour aider les utilisateurs à trouver leur bien immobilier idéal. L'application propose une recherche personnalisée, des recommandations basées sur l'IA, et une interface utilisateur intuitive.

## ✨ Fonctionnalités principales

- **🎨 Interface moderne** : Design responsive avec thèmes clair/sombre
- **🌐 Multilingue** : Support français et anglais
- **👤 Gestion des utilisateurs** : Système d'inscription/connexion avec plans gratuit, premium et professionnel
- **🤖 Agent IA** : Assistant personnel pour enrichir le profil utilisateur
- **🔍 Recherche avancée** : Filtres multiples et carte interactive
- **🎯 Recommandations** : Suggestions personnalisées avec radar des critères
- **📊 Tableau de bord** : Métriques et statistiques personnalisées
- **💾 Base de données** : Support SQLite intégré (extensible vers PostgreSQL/Airtable)

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner ou télécharger le code**
   ```bash
   # Si vous avez git installé
   git clone <votre-repo-url>
   cd imomatch
   ```

2. **Créer un environnement virtuel (recommandé)**
   ```bash
   python -m venv imomatch_env
   
   # Sur Windows
   imomatch_env\Scripts\activate
   
   # Sur macOS/Linux
   source imomatch_env/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Lancer l'application**
   ```bash
   streamlit run app.py
   ```

L'application sera accessible à l'adresse : `http://localhost:8501`

## 🔧 Configuration

### Base de données
L'application utilise SQLite par défaut. La base de données `imomatch.db` sera créée automatiquement au premier lancement.

### IA (OpenAI)
Pour activer les fonctionnalités IA avancées :
1. Obtenez une clé API OpenAI sur https://openai.com
2. Créez un fichier `.env` avec :
   ```
   OPENAI_API_KEY=votre_cle_api_ici
   ```

### Personnalisation des couleurs
Les couleurs sont définies dans la variable `COLORS` du fichier principal. Modifiez-les selon vos préférences :
- `primary`: Couleur principale (orange par défaut)
- `secondary`: Couleur secondaire
- `accent`: Couleur d'accent

## 📁 Structure du projet

```
imomatch/
├── app.py                 # Application principale
├── requirements.txt       # Dépendances Python
├── README.md             # Documentation
├── imomatch.db          # Base de données SQLite (créée automatiquement)
└── assets/              # Ressources (images, logos)
```

## 👥 Plans utilisateur

### 🆓 Gratuit
- 5 recherches par mois
- Support de base
- Accès limité à l'IA

### 💎 Premium (29€/mois)
- Recherches illimitées
- IA avancée
- Support prioritaire
- Notifications en temps réel
- Essai gratuit 14 jours

### 🏢 Professionnel (99€/mois)
- Toutes les fonctionnalités Premium
- Accès API
- Rapports personnalisés
- Support dédié

## 🔐 Sécurité

- Mots de passe hachés avec SHA-256
- Sessions utilisateur sécurisées
- Validation des entrées utilisateur

## 🌐 Déploiement

### Streamlit Cloud
1. Créez un compte sur https://streamlit.io
2. Connectez votre repository GitHub
3. Déployez directement depuis l'interface web

### Serveur dédié
Pour un déploiement sur serveur :
```bash
# Installation avec gunicorn pour la production
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
```

## 🎨 Personnalisation du design

### Couleurs et thèmes
L'application utilise un système de couleurs basé sur l'orange pour l'innovation :
- **Orange principal** (#FF6B35) : Actions importantes, CTA
- **Orange secondaire** (#F7931E) : Éléments interactifs
- **Orange clair** (#FFB84D) : Accents et highlights

### Logo personnalisé
Le logo est généré automatiquement avec les initiales "IM". Pour utiliser votre propre logo :
1. Ajoutez votre fichier logo dans le dossier `assets/`
2. Modifiez la fonction `create_logo()` dans le code

## 📊 Base de données

### Structure des tables

#### Table `users`
- `id`: Identifiant unique
- `email`: Email de connexion
- `password_hash`: Mot de passe haché
- `first_name`, `last_name`: Nom et prénom
- `phone`: Numéro de téléphone
- `age`: Âge de l'utilisateur
- `profession`: Profession
- `plan`: Plan tarifaire (free/premium/professional)
- `trial_end_date`: Date de fin d'essai
- `created_at`, `updated_at`: Horodatage

#### Table `user_preferences`
- `user_id`: Référence vers l'utilisateur
- `budget_min`, `budget_max`: Fourchette de budget
- `property_type`: Type de bien recherché
- `bedrooms`, `bathrooms`: Nombre de pièces
- `surface_min`: Surface minimale
- `location`: Localisation préférée
- `criteria`: Critères personnalisés (JSON)

#### Table `properties`
- `id`: Identifiant du bien
- `title`: Titre de l'annonce
- `price`: Prix du bien
- `property_type`: Type de bien
- `bedrooms`, `bathrooms`, `surface`: Caractéristiques
- `location`: Adresse
- `latitude`, `longitude`: Coordonnées GPS
- `description`: Description détaillée
- `features`: Équipements (JSON)
- `images`: Images (JSON)

### Migration vers PostgreSQL
Pour utiliser PostgreSQL au lieu de SQLite :

1. Installez psycopg2 :
   ```bash
   pip install psycopg2-binary
   ```

2. Modifiez la classe `DatabaseManager` :
   ```python
   import psycopg2
   
   class DatabaseManager:
       def __init__(self, db_url="postgresql://user:password@localhost/imomatch"):
           self.db_url = db_url
   ```

### Migration vers Airtable
Pour utiliser Airtable :

1. Installez pyairtable :
   ```bash
   pip install pyairtable
   ```

2. Configurez vos clés API Airtable dans `.env`

## 🤖 Agent IA

L'Agent IA utilise une approche conversationnelle pour :
- Enrichir le profil utilisateur
- Affiner les critères de recherche
- Donner des conseils personnalisés
- Analyser le marché immobilier

### Intégration OpenAI
Pour une IA plus avancée, intégrez l'API OpenAI :

```python
import openai

def generate_ai_response(user_input, user_context):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Tu es un expert immobilier..."},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content
```

## 🗺️ Cartes interactives

L'application utilise Folium pour les cartes interactives :
- Affichage des biens sur une carte
- Markers personnalisés avec informations
- Navigation et zoom
- Clustering pour les zones denses

## 📈 Métriques et analytics

### Tableau de bord utilisateur
- Recherches sauvegardées
- Biens en favoris
- Alertes actives
- Visites planifiées

### Graphiques disponibles
- Évolution des prix par zone
- Répartition des types de biens
- Score de compatibilité (radar chart)
- Comparaisons prix/m²

## 🔒 Sécurité et conformité

### Protection des données
- Hachage des mots de passe (SHA-256)
- Sessions sécurisées
- Validation des entrées

### RGPD
- Consentement explicite requis
- Droit à l'effacement des données
- Export des données personnelles

## 🐛 Dépannage

### Problèmes courants

1. **Erreur de base de données**
   ```
   Solution: Vérifiez que le fichier imomatch.db est accessible en écriture
   ```

2. **Problème avec Folium**
   ```bash
   pip uninstall streamlit-folium
   pip install streamlit-folium==0.13.0
   ```

3. **Erreur de thème**
   ```
   Solution: Videz le cache Streamlit avec Ctrl+Shift+R
   ```

### Logs de débogage
Activez les logs détaillés :
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Roadmap

### Version 1.1 (à venir)
- [ ] Notifications push
- [ ] Import de données externes (APIs immobilières)
- [ ] Système de reviews et notations
- [ ] Chat en temps réel avec agents

### Version 1.2
- [ ] Application mobile (PWA)
- [ ] Réalité virtuelle pour visites 360°
- [ ] Blockchain pour transparence des transactions

## 📞 Support

### Contact
- **Email** : support@imomatch.fr
- **Téléphone** : +33 1 23 45 67 89
- **Documentation** : https://docs.imomatch.fr

### Communauté
- **Discord** : https://discord.gg/imomatch
- **Forum** : https://forum.imomatch.fr

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 💡 Concernant le nom de domaine

### Question : Faut-il acheter imo-match.fr ?

**Recommandation : OUI, absolument !**

#### Avantages d'acheter votre nom de domaine :

1. **🎯 Professionnalisme**
   - URL personnalisée (www.imo-match.fr)
   - Crédibilité accrue auprès des utilisateurs
   - Image de marque cohérente

2. **📈 SEO et Marketing**
   - Meilleur référencement Google
   - Facilité de mémorisation
   - Possibilité d'emails personnalisés (@imo-match.fr)

3. **🛡️ Protection de marque**
   - Évite qu'un concurrent achète le nom
   - Contrôle total sur votre identité numérique

4. **💰 Coût minimal**
   - ~10-15€/an pour un .fr
   - Investissement négligeable vs bénéfices

#### Extensions recommandées à acheter :
- `imo-match.fr` (principal)
- `imo-match.com` (international)
- `imomatch.fr` (variante sans tiret)
- `imomatch.com` (protection)

#### Où acheter :
- **OVH** (français, support français)
- **Gandi** (interface claire)
- **Namecheap** (prix compétitifs)

### Déploiement avec nom de domaine personnalisé

1. **Achetez le domaine**
2. **Configurez les DNS** vers votre hébergement
3. **Activez HTTPS** (Let's Encrypt gratuit)
4. **Configurez Streamlit** :
   ```toml
   # .streamlit/config.toml
   [server]
   baseUrlPath = "/"
   enableCORS = false
   ```

**Conclusion** : L'achat du nom de domaine imo-match.fr est un investissement essentiel pour la crédibilité et le succès de votre projet. C'est une étape cruciale pour passer d'un prototype à un véritable produit commercial.

---

*Développé avec ❤️ pour révolutionner la recherche immobilière*
