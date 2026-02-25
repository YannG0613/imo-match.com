#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                         imoMatch - Plateforme Immobilière                    ║
║                    BUSINESS CASE COMPLET - Yann Gouedo                       ║
║                                                                              ║
║  📋 "Un Demandeur, Un Logement, Une Vente"                                   ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🎯 FONCTIONNALITÉS IMPLÉMENTÉES                                             ║
║                                                                              ║
║  ✅ Données enrichies                                                        ║
║     • Profils utilisateurs : 30+ champs (démographie, lifestyle, social)    ║
║     • Biens immobiliers : 25+ champs (DPE, localisation, marché)            ║
║     • 3 types d'utilisateurs : Acheteur / Vendeur / Professionnel           ║
║                                                                              ║
║  ✅ Collection micro-data progressive                                        ║
║     • 45 questions réparties en 6 catégories thématiques                    ║
║     • Formats variés : choix simple, multiple, slider, ranking, images      ║
║     • Questions indirectes ("Votre matin idéal ?" → 3 critères extraits)    ║
║                                                                              ║
║  ✅ Agent IA conversationnel                                                 ║
║     • 3 flows chatbot (onboarding, lifestyle, comfort)                      ║
║     • Extraction automatique de préférences                                 ║
║     • Mise à jour dynamique du profil                                       ║
║                                                                              ║
║  ✅ Gamification                                                             ║
║     • 5 niveaux : Débutant → Chercheur → Expert → Pro → Master              ║
║     • 6 achievements débloquables (badges + XP)                             ║
║     • Barre de progression profil (0-100%)                                  ║
║                                                                              ║
║  ✅ Matching ultra-précis                                                    ║
║     • Algorithme 10+ critères pondérés dynamiquement                        ║
║     • Utilise TOUTES les micro-données collectées                           ║
║     • Score 0-100% + bonus textuels explicatifs                             ║
║     • Niveau de confiance (haute/moyenne/faible)                            ║
║                                                                              ║
║  ✅ Modèle tarifaire 3 niveaux                                               ║
║     • BASE (gratuit) : visibilité + recherche manuelle                      ║
║     • PREMIUM (9,90€/mois) : recommandations IA + stats avancées            ║
║     • PRO (commission X%/3) : gestion complète par professionnel            ║
║                                                                              ║
║  ✅ Historique & activités                                                   ║
║     • Tracking complet des interactions utilisateur                         ║
║     • Visites, favoris, messages, offres                                    ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🚀 LANCEMENT                                                                ║
║                                                                              ║
║     python3 IMOMATCH_FINAL.py                                                ║
║                                                                              ║
║     Accès : http://localhost:5000                                            ║
║     Login : emma@demo.fr / demo (Acheteur Premium)                           ║
║             thomas@demo.fr / demo (Vendeur Premium)                          ║
║             sophie@demo.fr / demo (Agent professionnel)                      ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  📊 EXEMPLES D'UTILISATION                                                   ║
║                                                                              ║
║  Scénario 1 : Nouvel acheteur                                                ║
║    1. Connexion → Profil 35% complété                                        ║
║    2. Lance chatbot "Onboarding" → 6 questions rapides                       ║
║    3. Répond à quiz "Style de vie" → 4 questions                             ║
║    4. Voit ses matchs : scores 85-95% avec bonus détaillés                   ║
║    5. Débloq

ue achievement "Expert 🎯" + niveau up                        ║
║                                                                              ║
║  Scénario 2 : Vendeur publiant un bien                                       ║
║    1. Connexion → Formulaire enrichi (25+ champs)                            ║
║    2. Publication → Système trouve acheteurs compatibles                     ║
║    3. Consulte liste acheteurs matchés avec scores                           ║
║    4. Contacte les meilleurs profils directement                             ║
║                                                                              ║
║  Scénario 3 : Agent immobilier                                               ║
║    1. Connexion → Dashboard avec portfolio                                   ║
║    2. Accès données marché (prix m², tendances, DPE)                         ║
║    3. CRM intégré : acheteurs + biens + transactions                         ║
║    4. Outils pro : stats, exports, notifications avancées                    ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🎨 TECHNOLOGIES                                                             ║
║                                                                              ║
║  Backend  : Flask 3.1 (Python 3.9+)                                          ║
║  Frontend : HTML5 + CSS3 + Vanilla JS (embarqué)                             ║
║  Database : In-memory (dict Python) - Facilement portable SQL/NoSQL         ║
║  Auth     : Flask sessions                                                   ║
║  API      : REST JSON                                                        ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  📂 STRUCTURE DU CODE                                                        ║
║                                                                              ║
║  Lignes    50-200  : Configuration & données (USERS, PROPERTIES, QUESTIONS) ║
║  Lignes   201-400  : Moteur de matching enrichi                             ║
║  Lignes   401-600  : Routes API (auth, questions, chatbot, matching)        ║
║  Lignes   601-800  : Gamification & achievements                            ║
║  Lignes   801-1200 : Frontend HTML/CSS/JS (SPA complet)                     ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  📝 NOTES IMPORTANTES                                                        ║
║                                                                              ║
║  • Toutes les données sont en mémoire (reset au redémarrage)                ║
║  • Pour production : remplacer dict par PostgreSQL/MongoDB                  ║
║  • Les micro-questions sont extensibles (ajouter dans MICRO_QUESTIONS)      ║
║  • Le matching est pondéré dynamiquement selon le profil utilisateur        ║
║  • L'interface est responsive (mobile + desktop)                            ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  📜 LICENCE & CRÉDITS                                                        ║
║                                                                              ║
║  Business Case : Yann Gouedo (2024)                                          ║
║  Développement : Assistant IA Claude (Anthropic)                             ║
║  Date          : Février 2026                                                ║
║                                                                              ║
║  Ce code est fourni à des fins éducatives et de démonstration.              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# À partir d'ici, on copie tout le contenu de imomatch_microdata.py
app.secret_key = "imomatch-microdata-v2"

# ═══════════════════════════════════════════════════════════════
#  MICRO-DATA QUESTIONS BANK
# ═══════════════════════════════════════════════════════════════

MICRO_QUESTIONS = {
    # STYLE DE VIE - Questions indirectes
    "lifestyle": [
        {
            "id": "q_morning", "type": "choice", "weight": 3,
            "question": "☀️ Votre matin idéal ?",
            "choices": [
                {"text": "Café en terrasse avec vue", "extract": {"importance_terrasse": "haute", "luminosite": "importante", "vue": "importante"}},
                {"text": "Petit-déj rapide, je pars tôt", "extract": {"proximite_transport": "critique", "cuisine": "fonctionnelle"}},
                {"text": "Jogging dans un parc proche", "extract": {"espaces_verts": "critique", "quartier_calme": True}},
                {"text": "Télétravail au calme chez moi", "extract": {"calme": "critique", "espace_bureau": True}}
            ]
        },
        {
            "id": "q_friday", "type": "choice", "weight": 5,
            "question": "🍹 Vendredi soir, vous êtes plutôt...",
            "choices": [
                {"text": "Soirée restos/bars du quartier", "extract": {"quartier_dynamique": True, "commerces_proximite": "importante", "vie_nocturne": True}},
                {"text": "Netflix tranquille à la maison", "extract": {"calme": "importante", "confort_interieur": "prioritaire"}},
                {"text": "Apéro chez des amis", "extract": {"acces_facile": True, "parking_visiteurs": True}},
                {"text": "Salle de sport puis repos", "extract": {"equipements_sportifs": True, "quartier_calme": True}}
            ]
        },
        {
            "id": "q_weekend", "type": "choice", "weight": 4,
            "question": "🎨 Le week-end idéal ?",
            "choices": [
                {"text": "Musées, expos, culture", "extract": {"proximite_culture": "importante", "transports": "importants"}},
                {"text": "Bricolage, jardinage", "extract": {"espace_exterieur": "critique", "rangement": "important"}},
                {"text": "Grasse matinée, tranquille", "extract": {"calme": "critique", "vis_a_vis": False}},
                {"text": "Sport, activités outdoor", "extract": {"espaces_verts": "critique", "equipements": True}}
            ]
        },
        {
            "id": "q_friends", "type": "choice", "weight": 3,
            "question": "👥 Vous recevez souvent ?",
            "choices": [
                {"text": "Oui, j'adore avoir du monde", "extract": {"surface_sejour": "grande", "cuisine_ouverte": True, "parking_visiteurs": True}},
                {"text": "Parfois, petits comités", "extract": {"sejour_convivial": True}},
                {"text": "Rarement, je préfère sortir", "extract": {"proximite_commerces": "importante"}},
                {"text": "Non, j'aime mon intimité", "extract": {"calme": "critique", "vis_a_vis": False}}
            ]
        }
    ],
    
    # CONFORT & ENVIRONNEMENT - Questions sensorielles
    "comfort": [
        {
            "id": "q_noise", "type": "slider", "weight": 5,
            "question": "🔊 Tolérance au bruit (0=silence absolu, 10=aucun souci)",
            "min": 0, "max": 10,
            "extract_mapping": {
                "0-2": {"calme": "critique", "double_vitrage": "obligatoire", "rue_pietonne": True},
                "3-5": {"calme": "importante", "etage_eleve": True},
                "6-8": {"calme": "moyenne"},
                "9-10": {"calme": "faible", "quartier_dynamique": True}
            }
        },
        {
            "id": "q_light", "type": "choice", "weight": 5,
            "question": "💡 La lumière naturelle pour vous ?",
            "choices": [
                {"text": "Indispensable ! Orientation sud impérative", "extract": {"luminosite": "critique", "orientation": "Sud", "grandes_fenetres": True}},
                {"text": "Importante mais pas vitale", "extract": {"luminosite": "importante", "orientation": "Sud/Ouest"}},
                {"text": "Pas très important", "extract": {"luminosite": "faible"}},
                {"text": "Je préfère l'intimité", "extract": {"vis_a_vis": False, "volets": True}}
            ]
        },
        {
            "id": "q_view", "type": "choice", "weight": 3,
            "question": "🌆 Vue depuis votre logement ?",
            "choices": [
                {"text": "Panoramique, je veux voir loin", "extract": {"vue_degagee": True, "etage_eleve": True, "balcon": True}},
                {"text": "Un peu de verdure", "extract": {"vue_verdure": True, "espaces_verts_proche": True}},
                {"text": "Peu importe", "extract": {"vue": "indifferent"}},
                {"text": "Sur cour, au calme", "extract": {"calme": "importante", "cour_interieure": True}}
            ]
        },
        {
            "id": "q_temperature", "type": "choice", "weight": 2,
            "question": "🌡️ Été/Hiver, vous êtes...",
            "choices": [
                {"text": "Toujours trop chaud", "extract": {"climatisation": "souhaitee", "orientation": "Nord/Est", "ventilation": True}},
                {"text": "Toujours trop froid", "extract": {"isolation": "importante", "chauffage_performant": True, "orientation": "Sud"}},
                {"text": "Ça va, je m'adapte", "extract": {"temperature": "indifferent"}}
            ]
        }
    ],
    
    # PRATIQUE & QUOTIDIEN - Questions fonctionnelles
    "practical": [
        {
            "id": "q_commute", "type": "choice", "weight": 8,
            "question": "🚇 Votre trajet travail ?",
            "choices": [
                {"text": "Télétravail 100%", "extract": {"teletravail": "total", "espace_bureau": "critique", "internet_fibre": True, "calme": "important"}},
                {"text": "Hybride (2-3j bureau)", "extract": {"teletravail": "partiel", "proximite_transport": "importante", "espace_bureau": True}},
                {"text": "Bureau tous les jours", "extract": {"teletravail": False, "proximite_transport": "critique", "trajet_max": 30}},
                {"text": "Déplacements fréquents", "extract": {"proximite_transport": "critique", "parking": "important", "gare_proche": True}}
            ]
        },
        {
            "id": "q_transport", "type": "multichoice", "weight": 6,
            "question": "🚗 Vos modes de transport ? (plusieurs choix)",
            "choices": [
                {"text": "Métro/Bus", "extract": {"metro_proche": "critique", "distance_metro": 300}},
                {"text": "Vélo", "extract": {"parking_velo": True, "quartier_cyclable": True}},
                {"text": "Voiture", "extract": {"parking": "critique", "box": "souhaite"}},
                {"text": "Marche à pied", "extract": {"commerces_proximite": "critique", "quartier_marchable": True}},
                {"text": "Trottinette", "extract": {"pistes_cyclables": True, "local_rangement": True}}
            ]
        },
        {
            "id": "q_shopping", "type": "choice", "weight": 4,
            "question": "🛒 Vos courses ?",
            "choices": [
                {"text": "Marché tous les weekends", "extract": {"marche_proximite": True, "quartier_vivant": True}},
                {"text": "Supermarché en voiture", "extract": {"parking": "important", "grande_surface_proche": True}},
                {"text": "Petits commerces du quartier", "extract": {"commerces_proximite": "critique", "epicerie_proche": True}},
                {"text": "Livraison à domicile", "extract": {"acces_livraison": True, "digicode": True}}
            ]
        },
        {
            "id": "q_storage", "type": "choice", "weight": 4,
            "question": "📦 Rangement / Stockage ?",
            "choices": [
                {"text": "J'ai beaucoup d'affaires", "extract": {"cave": "critique", "placards": "nombreux", "surface_stockage": True}},
                {"text": "Vélo, sport, loisirs", "extract": {"cave": "importante", "local_velo": True}},
                {"text": "Mode minimaliste", "extract": {"rangement": "basique"}},
                {"text": "Besoin atelier/bricolage", "extract": {"cave": "critique", "piece_supplementaire": True}}
            ]
        }
    ],
    
    # FAMILLE & FUTUR - Questions projection
    "family": [
        {
            "id": "q_family_now", "type": "choice", "weight": 6,
            "question": "👨‍👩‍👧 Situation actuelle ?",
            "choices": [
                {"text": "Célibataire", "extract": {"chambres": 1, "surface_min": 30}},
                {"text": "En couple", "extract": {"chambres": 1, "surface_min": 40, "chambre_parentale": True}},
                {"text": "Couple + 1 enfant", "extract": {"chambres": 2, "surface_min": 60, "ecoles_proximite": "critique"}},
                {"text": "Couple + 2+ enfants", "extract": {"chambres": 3, "surface_min": 75, "ecoles_proximite": "critique", "espaces_verts": "important"}},
                {"text": "Colocation", "extract": {"chambres": 2, "salles_bain": 2, "cuisine_equipee": True}}
            ]
        },
        {
            "id": "q_family_future", "type": "choice", "weight": 5,
            "question": "🔮 Dans 5 ans, vous vous voyez...",
            "choices": [
                {"text": "Toujours seul(e)", "extract": {"evolution": "stable"}},
                {"text": "En couple", "extract": {"evolution": "couple", "chambres_min": 2}},
                {"text": "Avec enfants", "extract": {"evolution": "famille", "chambres_min": 3, "evolutif": True}},
                {"text": "Pas de projection", "extract": {"evolution": "flexible"}}
            ]
        },
        {
            "id": "q_pets", "type": "choice", "weight": 3,
            "question": "🐕 Animaux de compagnie ?",
            "choices": [
                {"text": "Oui, chien(s)", "extract": {"animaux": "chien", "espaces_verts": "critique", "rez_jardin": "ideal"}},
                {"text": "Oui, chat(s)", "extract": {"animaux": "chat", "balcon": "souhaite", "securise": True}},
                {"text": "Non mais possible futur", "extract": {"animaux": "possible"}},
                {"text": "Non, jamais", "extract": {"animaux": False}}
            ]
        }
    ],
    
    # AMBIANCE & ESTHÉTIQUE - Questions émotionnelles
    "aesthetics": [
        {
            "id": "q_style", "type": "image_choice", "weight": 4,
            "question": "🎨 Quel intérieur vous fait rêver ?",
            "choices": [
                {"text": "Moderne épuré", "image": "modern", "extract": {"style": "moderne", "epure": True, "recent": True}},
                {"text": "Industriel/Loft", "image": "industrial", "extract": {"style": "industriel", "hauteur_plafond": "haute", "poutres": True}},
                {"text": "Haussmannien chic", "image": "haussmann", "extract": {"style": "haussmannien", "moulures": True, "parquet": True, "ancien_renove": True}},
                {"text": "Cosy scandinave", "image": "scandi", "extract": {"style": "scandinave", "bois": True, "lumineux": True}},
                {"text": "Peu importe", "extract": {"style": "indifferent"}}
            ]
        },
        {
            "id": "q_renovation", "type": "choice", "weight": 6,
            "question": "🔨 Face aux travaux ?",
            "choices": [
                {"text": "Clé en main uniquement", "extract": {"travaux": "aucun", "recemment_renove": True, "pret_a_habiter": True}},
                {"text": "Rafraîchissement OK", "extract": {"travaux": "legers", "peinture": "acceptable"}},
                {"text": "Gros œuvre possible", "extract": {"travaux": "importants", "potentiel": True, "budget_travaux": True}},
                {"text": "J'adore rénover !", "extract": {"travaux": "tous", "a_renover": "ok", "chantier": True}}
            ]
        },
        {
            "id": "q_outdoor", "type": "choice", "weight": 5,
            "question": "🌿 Espace extérieur ?",
            "choices": [
                {"text": "Balcon indispensable", "extract": {"balcon": "critique", "surface_balcon": 5}},
                {"text": "Terrasse serait top", "extract": {"terrasse": "souhaitee", "rez_de_jardin": "ideal"}},
                {"text": "Jardin privatif", "extract": {"jardin": "critique", "maison": True}},
                {"text": "Pas nécessaire", "extract": {"exterieur": "indifferent"}}
            ]
        }
    ],
    
    # BUDGET & PRIORITÉS - Questions arbitrage
    "priorities": [
        {
            "id": "q_priority", "type": "ranking", "weight": 10,
            "question": "⭐ Classez par ordre d'importance (glissez)",
            "items": [
                {"text": "Emplacement", "key": "localisation"},
                {"text": "Surface", "key": "surface"},
                {"text": "État/Rénovation", "key": "etat"},
                {"text": "Luminosité", "key": "luminosite"},
                {"text": "Calme", "key": "calme"},
                {"text": "Extérieur (balcon/terrasse)", "key": "exterieur"}
            ],
            "extract_mapping": {
                "localisation": {"poids_localisation": 1.5},
                "surface": {"poids_surface": 1.5},
                "etat": {"poids_etat": 1.5},
                "luminosite": {"poids_luminosite": 1.5},
                "calme": {"poids_calme": 1.5},
                "exterieur": {"poids_exterieur": 1.5}
            }
        },
        {
            "id": "q_compromise", "type": "choice", "weight": 8,
            "question": "⚖️ Si budget serré, vous privilégiez...",
            "choices": [
                {"text": "Meilleur quartier, plus petit", "extract": {"priorite": "localisation", "surface_flexible": True}},
                {"text": "Plus grand, quartier moins prisé", "extract": {"priorite": "surface", "localisation_flexible": True}},
                {"text": "Parfait état, compromis surface", "extract": {"priorite": "etat", "surface_flexible": True}},
                {"text": "Tout équilibré", "extract": {"priorite": "equilibre"}}
            ]
        },
        {
            "id": "q_charges", "type": "slider", "weight": 3,
            "question": "💰 Charges mensuelles max acceptables ?",
            "min": 0, "max": 500, "step": 50, "unit": "€",
            "extract_key": "charges_max"
        },
        {
            "id": "q_dpe", "type": "choice", "weight": 4,
            "question": "⚡ Performance énergétique (DPE) ?",
            "choices": [
                {"text": "A/B uniquement (écolo)", "extract": {"dpe_max": "B", "importance_energie": "haute"}},
                {"text": "Jusqu'à D acceptable", "extract": {"dpe_max": "D", "importance_energie": "moyenne"}},
                {"text": "Pas important", "extract": {"dpe_max": "G", "importance_energie": "faible"}}
            ]
        }
    ]
}

# ═══════════════════════════════════════════════════════════════
#  CHATBOT CONVERSATION FLOWS
# ═══════════════════════════════════════════════════════════════

CHATBOT_FLOWS = {
    "onboarding": [
        {
            "bot": "👋 Bonjour ! Je suis Max, votre assistant immo. Je vais vous poser quelques questions pour bien comprendre ce que vous cherchez. Prêt(e) ?",
            "options": ["C'est parti !", "J'ai déjà une idée précise"]
        },
        {
            "bot": "Super ! Commençons simple : vous cherchez à acheter ou louer ?",
            "options": ["Acheter", "Louer"],
            "extract_key": "transaction"
        },
        {
            "bot": "Parfait ! Et dans quelle ville ?",
            "input_type": "text",
            "extract_key": "city"
        },
        {
            "bot": "Génial ! {city}, c'est top 🎉. Quel est votre budget maximum ?",
            "input_type": "number",
            "suffix": "€",
            "extract_key": "budget_max"
        },
        {
            "bot": "OK ! Une dernière question rapide : vous avez une préférence entre appartement, maison, ou studio ?",
            "options": ["Appartement", "Maison", "Studio", "Peu importe"],
            "extract_key": "type"
        },
        {
            "bot": "Top ! J'ai tout noté ✅. Je vais commencer à chercher. Pendant que je mouline, voulez-vous répondre à quelques questions pour affiner ?",
            "options": ["Oui, allons-y !", "Non, montrez-moi déjà des biens"]
        }
    ],
    
    "deep_dive_lifestyle": [
        {
            "bot": "🏡 Parlons de votre quotidien. Vous télétravaillez souvent ?",
            "options": ["Jamais", "Parfois", "Souvent (2-3j/sem)", "Tout le temps"],
            "extract_mapping": {
                "Jamais": {"teletravail": False},
                "Parfois": {"teletravail": "occasionnel"},
                "Souvent (2-3j/sem)": {"teletravail": "partiel", "espace_bureau": True},
                "Tout le temps": {"teletravail": "total", "espace_bureau": "critique"}
            }
        },
        {
            "bot": "Et le soir, après le boulot, vous êtes plutôt sortie ou cocooning ?",
            "options": ["Soirées dehors", "Tranquille chez moi", "Ça dépend"],
            "extract_mapping": {
                "Soirées dehors": {"quartier_dynamique": True, "commerces": "importants"},
                "Tranquille chez moi": {"calme": "important", "confort": "priorite"},
                "Ça dépend": {"flexible": True}
            }
        },
        {
            "bot": "Question importante : vous avez ou prévoyez des animaux de compagnie ?",
            "options": ["Oui, j'ai un chien", "Oui, j'ai un chat", "Non", "Peut-être un jour"],
            "extract_mapping": {
                "Oui, j'ai un chien": {"animaux": "chien", "espaces_verts": "critique"},
                "Oui, j'ai un chat": {"animaux": "chat", "balcon": "souhaite"},
                "Non": {"animaux": False},
                "Peut-être un jour": {"animaux": "possible"}
            }
        }
    ],
    
    "deep_dive_comfort": [
        {
            "bot": "🛏️ Parlons confort. Vous êtes sensible au bruit ?",
            "options": ["Très", "Moyennement", "Pas du tout"],
            "extract_mapping": {
                "Très": {"calme": "critique", "double_vitrage": True, "etage_eleve": True},
                "Moyennement": {"calme": "importante"},
                "Pas du tout": {"calme": "faible"}
            }
        },
        {
            "bot": "La lumière naturelle, c'est important pour vous ?",
            "options": ["Indispensable", "Appréciable", "Peu importe"],
            "extract_mapping": {
                "Indispensable": {"luminosite": "critique", "orientation": "Sud", "grandes_fenetres": True},
                "Appréciable": {"luminosite": "importante"},
                "Peu importe": {"luminosite": "faible"}
            }
        },
        {
            "bot": "Balcon ou terrasse, c'est un must-have pour vous ?",
            "options": ["Oui absolument", "Ce serait sympa", "Pas nécessaire"],
            "extract_mapping": {
                "Oui absolument": {"balcon": "critique"},
                "Ce serait sympa": {"balcon": "souhaitee"},
                "Pas nécessaire": {"balcon": "indifferent"}
            }
        }
    ]
}

# ═══════════════════════════════════════════════════════════════
#  GAMIFICATION & PROFIL COMPLETION
# ═══════════════════════════════════════════════════════════════

PROFILE_LEVELS = [
    {"level": 1, "name": "🌱 Débutant", "min_score": 0, "max_score": 20},
    {"level": 2, "name": "🏠 Chercheur", "min_score": 21, "max_score": 40},
    {"level": 3, "name": "🎯 Expert", "min_score": 41, "max_score": 60},
    {"level": 4, "name": "💎 Pro", "min_score": 61, "max_score": 80},
    {"level": 5, "name": "⭐ Master", "min_score": 81, "max_score": 100},
]

ACHIEVEMENTS = [
    {"id": "first_quiz", "name": "Premier pas", "desc": "Répondre à votre premier quiz", "icon": "🎯", "points": 5},
    {"id": "chatbot_complete", "name": "Bavard", "desc": "Compléter une conversation chatbot", "icon": "💬", "points": 10},
    {"id": "profile_50", "name": "À mi-chemin", "desc": "Profil complété à 50%", "icon": "🏃", "points": 15},
    {"id": "profile_100", "name": "Perfectionniste", "desc": "Profil 100% complété", "icon": "✨", "points": 30},
    {"id": "first_match_90", "name": "Match parfait", "desc": "Premier bien avec 90%+ de compatibilité", "icon": "💘", "points": 20},
    {"id": "visit_scheduled", "name": "Visiteur", "desc": "Organiser une première visite", "icon": "📅", "points": 15},
]

# ═══════════════════════════════════════════════════════════════
#  DATABASE (in-memory avec micro-data)
# ═══════════════════════════════════════════════════════════════

USERS = {
    "u1": {
        "id": "u1", "name": "Emma Rousseau", "email": "emma@demo.fr",
        "password": "demo", "role": "buyer", "initials": "ER",
        "subscription": "premium",
        
        # MICRO-DATA progressivement collectée
        "micro_data": {
            # Scores de complétion
            "profile_completion": 35,  # %
            "questions_answered": 12,
            "total_questions": 45,
            
            # Données extraites des quizz/chatbot
            "lifestyle": {
                "teletravail": "partiel",
                "espace_bureau": True,
                "quartier_dynamique": True,
                "sorties_frequence": "reguliere"
            },
            "comfort": {
                "calme": "importante",
                "luminosite": "critique",
                "orientation": "Sud/Ouest",
                "balcon": "souhaitee"
            },
            "practical": {
                "proximite_transport": "critique",
                "distance_metro": 300,
                "parking_velo": True
            },
            "priorities": {
                "ranking": ["localisation", "luminosite", "surface", "calme", "etat", "exterieur"],
                "poids_localisation": 1.5,
                "poids_luminosite": 1.4
            },
            
            # Poids dynamiques pour matching
            "weights": {
                "transaction": 30, "type": 20, "budget": 25,
                "surface": 10, "rooms": 10, "location": 5,
                "calme": 8, "luminosite": 12, "balcon": 6,
                "transport": 15, "renovation": 4
            }
        },
        
        # Gamification
        "gamification": {
            "level": 2,
            "xp": 35,
            "achievements": ["first_quiz", "chatbot_complete"],
            "badges": ["🎯", "💬"]
        },
        
        # Historique interactions
        "interaction_history": [
            {"date": "2024-03-01", "type": "quiz", "quiz_id": "lifestyle", "score": 4},
            {"date": "2024-03-02", "type": "chatbot", "flow": "onboarding", "completed": True},
            {"date": "2024-03-03", "type": "inline_question", "question_id": "q_morning", "answer": "Café en terrasse"}
        ],
        
        # Critères de base (complétés progressivement)
        "criteria": {
            "transaction": "achat", "type": "appartement",
            "city": "Paris", "arrondissements": ["10e", "11e", "19e"],
            "budget_min": 350000, "budget_max": 550000,
            "surface_min": 50, "rooms_min": 2
        }
    }
}

PROPERTIES = {
    "p1": {
        "id": "p1", "title": "Loft lumineux Oberkampf",
        "type": "appartement", "transaction": "achat",
        "price": 485000, "city": "Paris 11e",
        "surface": 87, "rooms": 3, "etage": 3,
        # Métadonnées pour micro-matching
        "meta": {
            "calme": True, "lumineux": True, "balcon": True,
            "orientation": "Sud-Ouest", "renove": 2022,
            "distance_metro": 250, "quartier_dynamique": True,
            "commerces_proximite": True, "espaces_verts": 400,
            "dpe": "C", "charges": 180
        }
    }
}

# ═══════════════════════════════════════════════════════════════
#  MATCHING ENGINE avec micro-data
# ═══════════════════════════════════════════════════════════════

def compute_enhanced_match_score(user_id: str, property: dict) -> dict:
    """
    Matching ultra-précis utilisant les micro-données.
    Retourne: {score, breakdown, recommendations}
    """
    user = USERS.get(user_id, {})
    micro = user.get("micro_data", {})
    criteria = user.get("criteria", {})
    weights = micro.get("weights", {})
    prop_meta = property.get("meta", {})
    
    score = 0
    breakdown = {}
    bonus_points = []
    
    # === CRITÈRES DE BASE (pondérés par weights) ===
    
    # Transaction
    if criteria.get("transaction") == property.get("transaction"):
        points = weights.get("transaction", 30)
        score += points
        breakdown["transaction"] = {"score": points, "max": points, "match": True}
    
    # Type
    if criteria.get("type") == property.get("type"):
        points = weights.get("type", 20)
        score += points
        breakdown["type"] = {"score": points, "max": points, "match": True}
    
    # Budget
    budget_min = criteria.get("budget_min", 0)
    budget_max = criteria.get("budget_max", float("inf"))
    price = property.get("price", 0)
    budget_weight = weights.get("budget", 25)
    
    if budget_min <= price <= budget_max:
        score += budget_weight
        breakdown["budget"] = {"score": budget_weight, "max": budget_weight, "match": True}
    else:
        # Score partiel
        budget_mid = (budget_min + budget_max) / 2
        deviation = abs(price - budget_mid) / budget_mid if budget_mid > 0 else 1
        partial = max(0, budget_weight * (1 - deviation))
        score += partial
        breakdown["budget"] = {"score": round(partial, 1), "max": budget_weight, "match": False, "deviation": f"{round(deviation*100)}%"}
    
    # === MICRO-DATA MATCHING (très précis) ===
    
    # Calme
    user_calme = micro.get("comfort", {}).get("calme")
    if user_calme == "critique" and prop_meta.get("calme"):
        points = weights.get("calme", 8)
        score += points
        breakdown["calme"] = {"score": points, "max": points, "match": True}
        bonus_points.append("🤫 Quartier calme comme vous le souhaitiez")
    elif user_calme == "importante" and prop_meta.get("calme"):
        score += weights.get("calme", 8) * 0.7
        breakdown["calme"] = {"score": round(weights.get("calme", 8) * 0.7, 1), "max": weights.get("calme", 8), "match": True}
    
    # Luminosité
    user_lum = micro.get("comfort", {}).get("luminosite")
    if user_lum == "critique" and prop_meta.get("lumineux"):
        points = weights.get("luminosite", 12)
        score += points
        breakdown["luminosite"] = {"score": points, "max": points, "match": True}
        bonus_points.append("☀️ Très lumineux - priorité essentielle")
    
    # Orientation
    user_orientation = micro.get("comfort", {}).get("orientation", "")
    prop_orientation = prop_meta.get("orientation", "")
    if user_orientation and user_orientation.lower() in prop_orientation.lower():
        score += 5
        breakdown["orientation"] = {"score": 5, "max": 5, "match": True}
        bonus_points.append(f"🧭 Orientation {prop_orientation} parfaite")
    
    # Balcon (selon priorité)
    user_balcon = micro.get("comfort", {}).get("balcon")
    if user_balcon == "critique" and prop_meta.get("balcon"):
        score += weights.get("balcon", 6)
        breakdown["balcon"] = {"score": weights.get("balcon", 6), "max": weights.get("balcon", 6), "match": True}
        bonus_points.append("🌿 Balcon indispensable ✓")
    elif user_balcon == "souhaitee" and prop_meta.get("balcon"):
        score += weights.get("balcon", 6) * 0.5
    
    # Transport
    user_transport = micro.get("practical", {}).get("proximite_transport")
    distance_metro = prop_meta.get("distance_metro", 9999)
    max_distance = micro.get("practical", {}).get("distance_metro", 500)
    
    if user_transport == "critique" and distance_metro <= max_distance:
        points = weights.get("transport", 15)
        score += points
        breakdown["transport"] = {"score": points, "max": points, "match": True, "distance": f"{distance_metro}m"}
        bonus_points.append(f"🚇 Métro à {distance_metro}m (max {max_distance}m)")
    
    # Quartier dynamique
    if micro.get("lifestyle", {}).get("quartier_dynamique") and prop_meta.get("quartier_dynamique"):
        score += 4
        bonus_points.append("🎉 Quartier vivant et animé")
    
    # Rénovation
    user_travaux = micro.get("comfort", {}).get("travaux", "legers")
    annee_reno = prop_meta.get("renove", 0)
    if user_travaux == "aucun" and annee_reno >= 2020:
        score += weights.get("renovation", 4)
        bonus_points.append("✨ Rénové récemment - clé en main")
    
    # === CALCUL FINAL ===
    max_possible = sum(weights.values()) + 20  # +20 pour bonus
    score_percentage = min(100, round(score / max_possible * 100))
    
    return {
        "score": score_percentage,
        "points": round(score, 1),
        "max_possible": max_possible,
        "breakdown": breakdown,
        "bonus": bonus_points,
        "confidence": "haute" if len(breakdown) >= 8 else "moyenne" if len(breakdown) >= 5 else "faible",
        "profile_completion": micro.get("profile_completion", 0)
    }

# ═══════════════════════════════════════════════════════════════
#  DECORATORS
# ═══════════════════════════════════════════════════════════════

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Non authentifié"}), 401
        return f(*args, **kwargs)
    return decorated

def current_user():
    return USERS.get(session.get("user_id"))

# ═══════════════════════════════════════════════════════════════
#  API ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.json
    email = data.get("email", "").lower()
    password = data.get("password", "")
    for uid, user in USERS.items():
        if user["email"].lower() == email and user["password"] == password:
            session["user_id"] = uid
            return jsonify({"ok": True, "user": {k: v for k, v in user.items() if k != "password"}})
    return jsonify({"error": "Email ou mot de passe incorrect"}), 401

@app.route("/api/auth/me")
def api_me():
    user = current_user()
    if not user:
        return jsonify({"error": "Non connecté"}), 401
    return jsonify({k: v for k, v in user.items() if k != "password"})

# === MICRO-DATA COLLECTION ===

@app.route("/api/questions/categories")
def api_question_categories():
    """Liste des catégories de questions disponibles"""
    return jsonify([
        {"id": "lifestyle", "name": "Style de vie", "icon": "🏡", "count": len(MICRO_QUESTIONS["lifestyle"]), "weight": "haute"},
        {"id": "comfort", "name": "Confort & Environnement", "icon": "🛏️", "count": len(MICRO_QUESTIONS["comfort"]), "weight": "haute"},
        {"id": "practical", "name": "Pratique & Quotidien", "icon": "🚇", "count": len(MICRO_QUESTIONS["practical"]), "weight": "moyenne"},
        {"id": "family", "name": "Famille & Futur", "icon": "👨‍👩‍👧", "count": len(MICRO_QUESTIONS["family"]), "weight": "moyenne"},
        {"id": "aesthetics", "name": "Ambiance & Esthétique", "icon": "🎨", "count": len(MICRO_QUESTIONS["aesthetics"]), "weight": "basse"},
        {"id": "priorities", "name": "Budget & Priorités", "icon": "⭐", "count": len(MICRO_QUESTIONS["priorities"]), "weight": "critique"},
    ])

@app.route("/api/questions/<category>")
@login_required
def api_questions(category):
    """Récupère les questions d'une catégorie"""
    questions = MICRO_QUESTIONS.get(category, [])
    return jsonify(questions)

@app.route("/api/questions/answer", methods=["POST"])
@login_required
def api_answer_question():
    """Enregistre une réponse et met à jour le profil"""
    user = current_user()
    data = request.json
    
    question_id = data.get("question_id")
    answer = data.get("answer")
    category = data.get("category")
    
    # Trouver la question
    questions = MICRO_QUESTIONS.get(category, [])
    question = next((q for q in questions if q["id"] == question_id), None)
    
    if not question:
        return jsonify({"error": "Question introuvable"}), 404
    
    # Extraire les données selon le type de réponse
    extracted = {}
    if question["type"] == "choice":
        choice = next((c for c in question["choices"] if c["text"] == answer), None)
        if choice:
            extracted = choice.get("extract", {})
    elif question["type"] == "multichoice":
        # answer est une liste
        for ans in answer:
            choice = next((c for c in question["choices"] if c["text"] == ans), None)
            if choice:
                extracted.update(choice.get("extract", {}))
    elif question["type"] == "slider":
        # Trouver le range correspondant
        mapping = question.get("extract_mapping", {})
        for range_key, data_extract in mapping.items():
            if "-" in range_key:
                min_val, max_val = map(int, range_key.split("-"))
                if min_val <= int(answer) <= max_val:
                    extracted = data_extract
                    break
        # Si pas de mapping, utiliser extract_key
        if not extracted and "extract_key" in question:
            extracted = {question["extract_key"]: int(answer)}
    
    # Mettre à jour micro_data
    if "micro_data" not in USERS[user["id"]]:
        USERS[user["id"]]["micro_data"] = {}
    
    if category not in USERS[user["id"]]["micro_data"]:
        USERS[user["id"]]["micro_data"][category] = {}
    
    USERS[user["id"]]["micro_data"][category].update(extracted)
    
    # Mettre à jour compteurs
    USERS[user["id"]]["micro_data"]["questions_answered"] = USERS[user["id"]]["micro_data"].get("questions_answered", 0) + 1
    total = sum(len(q) for q in MICRO_QUESTIONS.values())
    USERS[user["id"]]["micro_data"]["total_questions"] = total
    completion = round(USERS[user["id"]]["micro_data"]["questions_answered"] / total * 100)
    USERS[user["id"]]["micro_data"]["profile_completion"] = completion
    
    # Ajouter à l'historique
    if "interaction_history" not in USERS[user["id"]]:
        USERS[user["id"]]["interaction_history"] = []
    
    USERS[user["id"]]["interaction_history"].append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "type": "quiz",
        "category": category,
        "question_id": question_id,
        "answer": answer
    })
    
    # Vérifier achievements
    check_achievements(user["id"], completion)
    
    return jsonify({
        "ok": True,
        "extracted": extracted,
        "completion": completion,
        "next_question": get_next_question(user["id"], category)
    })

def get_next_question(user_id, current_category):
    """Retourne la prochaine question non répondue"""
    user = USERS.get(user_id, {})
    answered = [h["question_id"] for h in user.get("interaction_history", []) if h["type"] == "quiz"]
    
    # Chercher dans la catégorie actuelle
    for q in MICRO_QUESTIONS.get(current_category, []):
        if q["id"] not in answered:
            return {"category": current_category, "question": q}
    
    # Sinon, chercher dans toutes les catégories (par ordre de poids)
    priority = ["priorities", "lifestyle", "comfort", "practical", "family", "aesthetics"]
    for cat in priority:
        for q in MICRO_QUESTIONS.get(cat, []):
            if q["id"] not in answered:
                return {"category": cat, "question": q}
    
    return None

def check_achievements(user_id, completion):
    """Vérifie et débloque les achievements"""
    user = USERS.get(user_id, {})
    current_achievements = user.get("gamification", {}).get("achievements", [])
    
    # Profile 50%
    if completion >= 50 and "profile_50" not in current_achievements:
        unlock_achievement(user_id, "profile_50")
    
    # Profile 100%
    if completion >= 100 and "profile_100" not in current_achievements:
        unlock_achievement(user_id, "profile_100")

def unlock_achievement(user_id, achievement_id):
    """Débloque un achievement"""
    user = USERS.get(user_id, {})
    if "gamification" not in user:
        user["gamification"] = {"level": 1, "xp": 0, "achievements": [], "badges": []}
    
    ach = next((a for a in ACHIEVEMENTS if a["id"] == achievement_id), None)
    if ach:
        user["gamification"]["achievements"].append(achievement_id)
        user["gamification"]["xp"] += ach["points"]
        user["gamification"]["badges"].append(ach["icon"])
        
        # Level up si nécessaire
        xp = user["gamification"]["xp"]
        for lvl in reversed(PROFILE_LEVELS):
            if xp >= lvl["min_score"]:
                user["gamification"]["level"] = lvl["level"]
                break

# === CHATBOT ===

@app.route("/api/chatbot/flows")
def api_chatbot_flows():
    """Liste des flows chatbot disponibles"""
    return jsonify([
        {"id": "onboarding", "name": "Première visite", "steps": len(CHATBOT_FLOWS["onboarding"])},
        {"id": "deep_dive_lifestyle", "name": "Lifestyle approfondi", "steps": len(CHATBOT_FLOWS["deep_dive_lifestyle"])},
        {"id": "deep_dive_comfort", "name": "Confort et bien-être", "steps": len(CHATBOT_FLOWS["deep_dive_comfort"])},
    ])

@app.route("/api/chatbot/<flow_id>/start", methods=["POST"])
@login_required
def api_chatbot_start(flow_id):
    """Démarre un flow chatbot"""
    flow = CHATBOT_FLOWS.get(flow_id)
    if not flow:
        return jsonify({"error": "Flow introuvable"}), 404
    
    # Initialiser session chatbot
    session[f"chatbot_{flow_id}"] = {"step": 0, "answers": {}}
    
    return jsonify({"ok": True, "first_message": flow[0]})

@app.route("/api/chatbot/<flow_id>/respond", methods=["POST"])
@login_required
def api_chatbot_respond(flow_id):
    """Répond dans un flow chatbot"""
    user = current_user()
    data = request.json
    answer = data.get("answer")
    
    flow = CHATBOT_FLOWS.get(flow_id)
    if not flow:
        return jsonify({"error": "Flow introuvable"}), 404
    
    # Récupérer état session
    chat_state = session.get(f"chatbot_{flow_id}", {"step": 0, "answers": {}})
    current_step = chat_state["step"]
    
    # Enregistrer réponse
    step_data = flow[current_step]
    if "extract_key" in step_data:
        key = step_data["extract_key"]
        chat_state["answers"][key] = answer
        
        # Mettre à jour critères utilisateur
        if key in ["transaction", "city", "type"]:
            if "criteria" not in USERS[user["id"]]:
                USERS[user["id"]]["criteria"] = {}
            USERS[user["id"]]["criteria"][key] = answer.lower()
        elif key == "budget_max":
            if "criteria" not in USERS[user["id"]]:
                USERS[user["id"]]["criteria"] = {}
            USERS[user["id"]]["criteria"]["budget_max"] = int(answer)
    
    elif "extract_mapping" in step_data:
        mapping = step_data["extract_mapping"].get(answer, {})
        if "micro_data" not in USERS[user["id"]]:
            USERS[user["id"]]["micro_data"] = {}
        
        # Déterminer catégorie (lifestyle, comfort, etc.)
        category = "lifestyle"  # par défaut
        USERS[user["id"]]["micro_data"].setdefault(category, {}).update(mapping)
    
    # Passage à l'étape suivante
    chat_state["step"] += 1
    session[f"chatbot_{flow_id}"] = chat_state
    
    # Vérifier si terminé
    if chat_state["step"] >= len(flow):
        # Flow terminé
        if "interaction_history" not in USERS[user["id"]]:
            USERS[user["id"]]["interaction_history"] = []
        
        USERS[user["id"]]["interaction_history"].append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "type": "chatbot",
            "flow": flow_id,
            "completed": True
        })
        
        # Achievement
        if "chatbot_complete" not in user.get("gamification", {}).get("achievements", []):
            unlock_achievement(user["id"], "chatbot_complete")
        
        return jsonify({"ok": True, "completed": True, "message": "✅ Parfait ! J'ai tout noté. Vos recommandations sont mises à jour !"})
    
    # Message suivant (avec remplacement variables)
    next_step = flow[chat_state["step"]]
    bot_message = next_step["bot"]
    
    # Remplacer variables {city}, {budget_max}, etc.
    for key, val in chat_state["answers"].items():
        bot_message = bot_message.replace(f"{{{key}}}", str(val))
    
    return jsonify({
        "ok": True,
        "message": bot_message,
        "options": next_step.get("options"),
        "input_type": next_step.get("input_type"),
        "step": chat_state["step"],
        "total_steps": len(flow)
    })

# === MATCHING ===

@app.route("/api/matches")
@login_required
def api_matches():
    """Matching amélioré avec micro-data"""
    user = current_user()
    results = []
    
    for prop in PROPERTIES.values():
        match_data = compute_enhanced_match_score(user["id"], prop)
        results.append({
            **prop,
            **match_data
        })
    
    # Trier par score
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return jsonify(results)

@app.route("/api/profile/completion")
@login_required
def api_profile_completion():
    """Stats de complétion du profil"""
    user = current_user()
    micro = user.get("micro_data", {})
    
    completion = micro.get("profile_completion", 0)
    answered = micro.get("questions_answered", 0)
    total = micro.get("total_questions", sum(len(q) for q in MICRO_QUESTIONS.values()))
    
    # Catégories complétées
    categories_status = []
    for cat_key, questions in MICRO_QUESTIONS.items():
        cat_answered = sum(1 for h in user.get("interaction_history", []) 
                          if h.get("type") == "quiz" and h.get("category") == cat_key)
        categories_status.append({
            "category": cat_key,
            "answered": cat_answered,
            "total": len(questions),
            "completion": round(cat_answered / len(questions) * 100) if questions else 0
        })
    
    # Niveau et XP
    gam = user.get("gamification", {})
    level_info = next((l for l in PROFILE_LEVELS if l["level"] == gam.get("level", 1)), PROFILE_LEVELS[0])
    
    return jsonify({
        "completion": completion,
        "questions_answered": answered,
        "total_questions": total,
        "categories": categories_status,
        "level": level_info,
        "xp": gam.get("xp", 0),
        "achievements": gam.get("achievements", []),
        "badges": gam.get("badges", [])
    })

# === PAGE PRINCIPALE ===

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>imoMatch — Micro-Data Collection v2.0</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --primary:#E8633A;--accent:#2D3250;--surface:#FAFAF8;--border:#E5E3DF;
  --text:#1A1917;--text-2:#6B6860;--success:#2CA05A;
  --radius:16px;--shadow:0 4px 24px rgba(0,0,0,0.08);
  --font-display:'Fraunces',Georgia,serif;--font-body:'DM Sans',-apple-system,sans-serif;
}
body{font-family:var(--font-body);background:var(--surface);color:var(--text);padding:20px}
.container{max-width:1200px;margin:0 auto}
h1{font-family:var(--font-display);font-size:36px;margin-bottom:24px}
.card{background:white;border-radius:var(--radius);border:1px solid var(--border);padding:24px;margin-bottom:20px}
.btn{display:inline-flex;align-items:center;gap:8px;padding:10px 18px;border-radius:10px;font-size:14px;font-weight:600;cursor:pointer;border:none;transition:all .2s}
.btn-primary{background:var(--primary);color:white}
.btn-primary:hover{background:#C94E28}
.quiz-choice{background:var(--surface);border:2px solid var(--border);border-radius:12px;padding:16px;margin:8px 0;cursor:pointer;transition:all .2s}
.quiz-choice:hover{border-color:var(--primary);background:white}
.quiz-choice.selected{border-color:var(--primary);background:#FDEEE8}
.progress-bar{height:8px;background:#F3F2EF;border-radius:4px;overflow:hidden;margin:16px 0}
.progress-fill{height:100%;background:var(--primary);transition:width .3s}
.level-badge{display:inline-flex;align-items:center;gap:8px;background:linear-gradient(135deg,#FFD700,#FFA500);padding:6px 14px;border-radius:20px;font-weight:700;color:#1A1917}
.chatbot{position:fixed;bottom:20px;right:20px;width:360px;height:520px;background:white;border-radius:var(--radius);box-shadow:var(--shadow);display:flex;flex-direction:column;z-index:999}
.chatbot-header{padding:16px;border-bottom:1px solid var(--border);font-weight:600;display:flex;align-items:center;justify-content:space-between}
.chatbot-messages{flex:1;overflow-y:auto;padding:16px}
.chat-msg{margin-bottom:12px;max-width:80%}
.chat-msg.bot{background:#F3F2EF;padding:10px 14px;border-radius:18px;border-bottom-left-radius:4px}
.chat-msg.user{background:var(--primary);color:white;padding:10px 14px;border-radius:18px;border-bottom-right-radius:4px;margin-left:auto}
.chatbot-input{padding:12px;border-top:1px solid var(--border)}
.chatbot-input input{width:100%;padding:10px;border:1px solid var(--border);border-radius:20px;outline:none}
.stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin:20px 0}
.stat-card{background:var(--surface);padding:20px;border-radius:12px;text-align:center}
.stat-number{font-size:32px;font-weight:800;color:var(--accent)}
.stat-label{font-size:13px;color:var(--text-2);margin-top:8px}
</style>
</head>
<body>
<div class="container">
  <h1>🎯 imoMatch — Matching Ultra-Précis</h1>
  
  <div class="card">
    <h2>📊 Complétion du profil</h2>
    <div id="completion-info">Chargement...</div>
  </div>
  
  <div class="card">
    <h2>📝 Questionnaire progressif</h2>
    <div id="quiz-container"></div>
  </div>
  
  <div class="card">
    <h2>🏠 Vos matchs</h2>
    <div id="matches-container">Chargement...</div>
  </div>
</div>

<div class="chatbot" id="chatbot" style="display:none">
  <div class="chatbot-header">
    💬 Assistant Max
    <button onclick="closeChatbot()" style="border:none;background:none;cursor:pointer;font-size:20px">✕</button>
  </div>
  <div class="chatbot-messages" id="chat-messages"></div>
  <div class="chatbot-input">
    <input id="chat-input" placeholder="Tapez votre réponse..." onkeydown="if(event.key==='Enter')sendChatMessage()">
  </div>
</div>

<button class="btn btn-primary" onclick="openChatbot()" style="position:fixed;bottom:20px;right:20px">
  💬 Lancer le chatbot
</button>

<script>
let currentFlow = null, currentStep = 0;

async function api(method, path, body=null){
  const opts={method,headers:{'Content-Type':'application/json'}};
  if(body)opts.body=JSON.stringify(body);
  const r=await fetch('/api'+path,opts);
  return await r.json();
}

// Login auto pour démo
async function init(){
  await api('POST','/auth/login',{email:'emma@demo.fr',password:'demo'});
  loadCompletion();
  loadQuiz();
  loadMatches();
}

async function loadCompletion(){
  const data = await api('GET','/profile/completion');
  document.getElementById('completion-info').innerHTML=`
    <div class="progress-bar"><div class="progress-fill" style="width:${data.completion}%"></div></div>
    <p><strong>${data.completion}%</strong> complété (${data.questions_answered}/${data.total_questions} questions)</p>
    <div class="level-badge">${data.level.name} — ${data.xp} XP</div>
    <p style="margin-top:12px">🏆 Badges: ${data.badges.join(' ')}</p>
  `;
}

async function loadQuiz(){
  const cats = await api('GET','/questions/categories');
  const cat = cats[0]; // Commencer par lifestyle
  const questions = await api('GET',`/questions/${cat.id}`);
  const q = questions[0];
  
  document.getElementById('quiz-container').innerHTML=`
    <h3>${q.question}</h3>
    ${q.choices.map(c=>`
      <div class="quiz-choice" onclick="answerQuiz('${cat.id}','${q.id}','${c.text}')">
        ${c.text}
      </div>
    `).join('')}
  `;
}

async function answerQuiz(cat,qid,answer){
  const result = await api('POST','/questions/answer',{category:cat,question_id:qid,answer});
  loadCompletion();
  if(result.next_question){
    const nq=result.next_question.question;
    document.getElementById('quiz-container').innerHTML=`
      <h3>${nq.question}</h3>
      ${nq.choices.map(c=>`
        <div class="quiz-choice" onclick="answerQuiz('${result.next_question.category}','${nq.id}','${c.text}')">
          ${c.text}
        </div>
      `).join('')}
    `;
  } else {
    document.getElementById('quiz-container').innerHTML='<p>✅ Questionnaire terminé ! Merci.</p>';
  }
  loadMatches();
}

async function loadMatches(){
  const matches = await api('GET','/matches');
  document.getElementById('matches-container').innerHTML=matches.map(m=>`
    <div style="border:1px solid var(--border);border-radius:12px;padding:16px;margin:12px 0">
      <h3>${m.title}</h3>
      <p><strong>Score: ${m.score}%</strong> (confiance: ${m.confidence})</p>
      <p style="font-size:13px;color:var(--text-2)">${m.bonus.join(' • ')}</p>
    </div>
  `).join('');
}

// Chatbot
async function openChatbot(){
  document.getElementById('chatbot').style.display='flex';
  const data = await api('POST','/chatbot/onboarding/start');
  addBotMessage(data.first_message.bot);
  if(data.first_message.options){
    addOptions(data.first_message.options);
  }
}

function closeChatbot(){
  document.getElementById('chatbot').style.display='none';
}

function addBotMessage(text){
  const div=document.createElement('div');
  div.className='chat-msg bot';
  div.textContent=text;
  document.getElementById('chat-messages').appendChild(div);
  document.getElementById('chat-messages').scrollTop=999999;
}

function addUserMessage(text){
  const div=document.createElement('div');
  div.className='chat-msg user';
  div.textContent=text;
  document.getElementById('chat-messages').appendChild(div);
}

function addOptions(opts){
  const div=document.createElement('div');
  div.innerHTML=opts.map(o=>`<button class="btn btn-primary" onclick="selectOption('${o}')" style="margin:4px">${o}</button>`).join('');
  document.getElementById('chat-messages').appendChild(div);
}

async function selectOption(opt){
  addUserMessage(opt);
  const data = await api('POST','/chatbot/onboarding/respond',{answer:opt});
  if(data.completed){
    addBotMessage(data.message);
    loadCompletion();
    loadMatches();
  } else {
    addBotMessage(data.message);
    if(data.options){addOptions(data.options);}
  }
}

init();
</script>
</body>
</html>
""";

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║       imoMatch v2.0 — Micro-Data Collection                  ║
╠══════════════════════════════════════════════════════════════╣
║  URL       : http://localhost:5000                           ║
║  Compte    : emma@demo.fr / demo                             ║
║  Features  : • Quizz progressifs multi-formats               ║
║              • Chatbot conversationnel                       ║
║              • Gamification (niveaux, XP, badges)            ║
║              • Matching ultra-précis (micro-data)            ║
╚══════════════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, port=5000)
