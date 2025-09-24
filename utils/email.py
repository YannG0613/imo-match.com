"""
Système d'envoi d'emails pour ImoMatch
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import List, Dict, Any, Optional
import os
from datetime import datetime
import json

from config.settings import NOTIFICATION_CONFIG

logger = logging.getLogger(__name__)

class EmailManager:
    """Gestionnaire pour l'envoi d'emails"""
    
    def __init__(self):
        self.smtp_config = NOTIFICATION_CONFIG.get('email', {})
        self.smtp_server = self.smtp_config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = self.smtp_config.get('smtp_port', 587)
        self.username = self.smtp_config.get('username')
        self.password = self.smtp_config.get('password')
        
        # Templates d'emails
        self.templates = {
            'welcome': self._get_welcome_template(),
            'property_alert': self._get_property_alert_template(),
            'password_reset': self._get_password_reset_template(),
            'subscription_confirmation': self._get_subscription_template(),
            'new_property_match': self._get_new_match_template()
        }
    
    def send_welcome_email(self, user_email: str, user_name: str, 
                          plan: str = 'free') -> bool:
        """
        Envoie un email de bienvenue
        
        Args:
            user_email: Email du destinataire
            user_name: Nom de l'utilisateur
            plan: Plan choisi
            
        Returns:
            bool: True si envoyé avec succès
        """
        try:
            subject = "🏠 Bienvenue sur ImoMatch !"
            
            # Contenu personnalisé selon le plan
            from config.settings import PLANS
            plan_info = PLANS.get(plan, PLANS['free'])
            
            template_vars = {
                'user_name': user_name,
                'plan_name': plan_info['name'],
                'plan_features': plan_info['features'],
                'login_url': 'https://imo-match.streamlit.app',
                'support_email': 'support@imomatch.fr'
            }
            
            html_content = self.templates['welcome'].format(**template_vars)
            
            return self._send_email(
                to_email=user_email,
                subject=subject,
                html_content=html_content,
                email_type='welcome'
            )
            
        except Exception as e:
            logger.error(f"Erreur envoi email bienvenue: {e}")
            return False
    
    def send_property_alert(self, user_email: str, user_name: str,
                           properties: List[Dict[str, Any]], 
                           search_name: str) -> bool:
        """
        Envoie une alerte de nouvelles propriétés
        
        Args:
            user_email: Email du destinataire
            user_name: Nom de l'utilisateur
            properties: Liste des nouvelles propriétés
            search_name: Nom de la recherche sauvegardée
            
        Returns:
            bool: True si envoyé avec succès
        """
        try:
            if not properties:
                return False
            
            subject = f"🆕 {len(properties)} nouvelle{'s' if len(properties) > 1 else ''} propriété{'s' if len(properties) > 1 else ''} pour '{search_name}'"
            
            # Générer le HTML des propriétés
            properties_html = self._generate_properties_html(properties)
            
            template_vars = {
                'user_name': user_name,
                'search_name': search_name,
                'properties_count': len(properties),
                'properties_html': properties_html,
                'app_url': 'https://imo-match.streamlit.app'
            }
            
            html_content = self.templates['property_alert'].format(**template_vars)
            
            return self._send_email(
                to_email=user_email,
                subject=subject,
                html_content=html_content,
                email_type='alert'
            )
            
        except Exception as e:
            logger.error(f"Erreur envoi alerte propriété: {e}")
            return False
    
    def send_password_reset(self, user_email: str, reset_token: str) -> bool:
        """
        Envoie un email de réinitialisation de mot de passe
        
        Args:
            user_email: Email du destinataire
            reset_token: Token de réinitialisation
            
        Returns:
            bool: True si envoyé avec succès
        """
        try:
            subject = "🔒 Réinitialisation de votre mot de passe ImoMatch"
            
            reset_url = f"https://imo-match.streamlit.app/reset-password?token={reset_token}"
            
            template_vars = {
                'reset_url': reset_url,
                'expiry_hours': 24,
                'support_email': 'support@imomatch.fr'
            }
            
            html_content = self.templates['password_reset'].format(**template_vars)
            
            return self._send_email(
                to_email=user_email,
                subject=subject,
                html_content=html_content,
                email_type='password_reset'
            )
            
        except Exception as e:
            logger.error(f"Erreur envoi reset password: {e}")
            return False
    
    def send_subscription_confirmation(self, user_email: str, user_name: str,
                                     plan: str, amount: float) -> bool:
        """
        Envoie une confirmation d'abonnement
        
        Args:
            user_email: Email du destinataire
            user_name: Nom de l'utilisateur
            plan: Plan souscrit
            amount: Montant payé
            
        Returns:
            bool: True si envoyé avec succès
        """
        try:
            from config.settings import PLANS
            plan_info = PLANS.get(plan, PLANS['premium'])
            
            subject = f"✅ Confirmation de votre abonnement {plan_info['name']}"
            
            template_vars = {
                'user_name': user_name,
                'plan_name': plan_info['name'],
                'amount': amount,
                'features': plan_info['features'],
                'billing_date': datetime.now().strftime('%d/%m/%Y'),
                'app_url': 'https://imo-match.streamlit.app'
            }
            
            html_content = self.templates['subscription_confirmation'].format(**template_vars)
            
            return self._send_email(
                to_email=user_email,
                subject=subject,
                html_content=html_content,
                email_type='subscription'
            )
            
        except Exception as e:
            logger.error(f"Erreur envoi confirmation abonnement: {e}")
            return False
    
    def send_property_recommendation(self, user_email: str, user_name: str,
                                   recommended_properties: List[Dict[str, Any]]) -> bool:
        """
        Envoie des recommandations de propriétés personnalisées
        
        Args:
            user_email: Email du destinataire
            user_name: Nom de l'utilisateur
            recommended_properties: Propriétés recommandées
            
        Returns:
            bool: True si envoyé avec succès
        """
        try:
            if not recommended_properties:
                return False
            
            subject = f"💡 {len(recommended_properties)} recommandations personnalisées pour vous"
            
            properties_html = self._generate_recommendations_html(recommended_properties)
            
            template_vars = {
                'user_name': user_name,
                'properties_count': len(recommended_properties),
                'properties_html': properties_html,
                'app_url': 'https://imo-match.streamlit.app'
            }
            
            html_content = self.templates['new_property_match'].format(**template_vars)
            
            return self._send_email(
                to_email=user_email,
                subject=subject,
                html_content=html_content,
                email_type='recommendation'
            )
            
        except Exception as e:
            logger.error(f"Erreur envoi recommandations: {e}")
            return False
    
    def send_bulk_newsletter(self, recipients: List[Dict[str, str]],
                           subject: str, content: str) -> Dict[str, int]:
        """
        Envoie une newsletter en masse
        
        Args:
            recipients: Liste des destinataires [{'email': str, 'name': str}]
            subject: Sujet de la newsletter
            content: Contenu HTML de la newsletter
            
        Returns:
            Dict avec statistiques d'envoi
        """
        stats = {'sent': 0, 'failed': 0, 'total': len(recipients)}
        
        try:
            for recipient in recipients:
                try:
                    # Personnaliser le contenu
                    personalized_content = content.replace(
                        '{user_name}', 
                        recipient.get('name', 'Cher(e) utilisateur/trice')
                    )
                    
                    success = self._send_email(
                        to_email=recipient['email'],
                        subject=subject,
                        html_content=personalized_content,
                        email_type='newsletter'
                    )
                    
                    if success:
                        stats['sent'] += 1
                    else:
                        stats['failed'] += 1
                        
                except Exception as e:
                    logger.error(f"Erreur envoi newsletter à {recipient.get('email')}: {e}")
                    stats['failed'] += 1
            
            logger.info(f"Newsletter envoyée: {stats['sent']}/{stats['total']} succès")
            return stats
            
        except Exception as e:
            logger.error(f"Erreur envoi newsletter en masse: {e}")
            stats['failed'] = stats['total']
            return stats
    
    def _send_email(self, to_email: str, subject: str, html_content: str,
                   text_content: str = None, email_type: str = 'general') -> bool:
        """
        Méthode privée pour envoyer un email
        
        Args:
            to_email: Destinataire
            subject: Sujet
            html_content: Contenu HTML
            text_content: Contenu texte (optionnel)
            email_type: Type d'email pour les logs
            
        Returns:
            bool: True si succès
        """
        try:
            # Vérification de la configuration
            if not self.username or not self.password:
                logger.warning("Configuration email manquante, simulation d'envoi")
                return self._simulate_email_send(to_email, subject, email_type)
            
            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Contenu texte (fallback)
            if not text_content:
                text_content = self._html_to_text(html_content)
            
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Connexion SMTP et envoi
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email {email_type} envoyé avec succès à {to_email}")
            return True
            
        except smtplib.SMTPException as e:
            logger.error(f"Erreur SMTP envoi email à {to_email}: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur générale envoi email à {to_email}: {e}")
            return False
    
    def _simulate_email_send(self, to_email: str, subject: str, email_type: str) -> bool:
        """Simule l'envoi d'email quand la configuration n'est pas disponible"""
        logger.info(f"SIMULATION - Email {email_type} à {to_email}: {subject}")
        return True
    
    def _html_to_text(self, html_content: str) -> str:
        """Convertit le contenu HTML en texte simple"""
        try:
            # Remplacement simple des balises HTML courantes
            import re
            
            text = re.sub(r'<br[^>]*>', '\n', html_content)
            text = re.sub(r'<p[^>]*>', '\n', text)
            text = re.sub(r'</p>', '\n', text)
            text = re.sub(r'<h[1-6][^>]*>', '\n**', text)
            text = re.sub(r'</h[1-6]>', '**\n', text)
            text = re.sub(r'<[^>]+>', '', text)  # Supprimer toutes les autres balises
            
            # Nettoyer les espaces multiples
            text = re.sub(r'\n\s*\n', '\n\n', text)
            text = re.sub(r' +', ' ', text)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Erreur conversion HTML vers texte: {e}")
            return "Veuillez consulter la version HTML de cet email."
    
    def _generate_properties_html(self, properties: List[Dict[str, Any]]) -> str:
        """Génère le HTML pour afficher une liste de propriétés"""
        html_parts = []
        
        for prop in properties[:5]:  # Limiter à 5 propriétés par email
            # Image
            img_html = ""
            if prop.get('images'):
                img_html = f'<img src="{prop["images"][0]}" style="width: 100%; max-width: 200px; height: 150px; object-fit: cover; border-radius: 8px;" alt="Propriété">'
            
            # Caractéristiques
            details = []
            if prop.get('bedrooms'):
                details.append(f"{prop['bedrooms']} ch.")
            if prop.get('surface'):
                details.append(f"{prop['surface']}m²")
            if prop.get('bathrooms'):
                details.append(f"{prop['bathrooms']} sdb")
            
            details_text = " • ".join(details)
            
            prop_html = f"""
            <div style="border: 1px solid #ddd; border-radius: 12px; padding: 20px; margin: 20px 0; background: #f9f9f9;">
                <div style="display: flex; gap: 20px; align-items: flex-start;">
                    <div style="flex-shrink: 0;">
                        {img_html}
                    </div>
                    <div style="flex-grow: 1;">
                        <h3 style="margin: 0 0 10px 0; color: #FF6B35;">{prop['title']}</h3>
                        <p style="font-size: 1.2em; font-weight: bold; color: #FF6B35; margin: 5px 0;">
                            💰 {prop['price']:,}€
                        </p>
                        <p style="margin: 5px 0; color: #666;">
                            🏠 {prop['property_type']} • {details_text}
                        </p>
                        <p style="margin: 5px 0; color: #666;">
                            📍 {prop['location']}
                        </p>
                        <a href="https://imo-match.streamlit.app" 
                           style="display: inline-block; background: #FF6B35; color: white; 
                                  padding: 8px 16px; text-decoration: none; border-radius: 6px; 
                                  margin-top: 10px;">
                            Voir les détails
                        </a>
                    </div>
                </div>
            </div>
            """
            html_parts.append(prop_html)
        
        return "".join(html_parts)
    
    def _generate_recommendations_html(self, properties: List[Dict[str, Any]]) -> str:
        """Génère le HTML pour les recommandations avec scores"""
        html_parts = []
        
        for prop in properties[:3]:  # Limiter à 3 recommandations par email
            score = prop.get('match_score', 0) * 100
            score_color = '#28a745' if score >= 80 else '#ffc107' if score >= 60 else '#dc3545'
            
            prop_html = f"""
            <div style="border: 2px solid {score_color}; border-radius: 12px; padding: 20px; margin: 20px 0;">
                <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #FF6B35;">{prop['title']}</h3>
                    <div style="background: {score_color}; color: white; padding: 5px 10px; 
                                border-radius: 20px; font-weight: bold;">
                        {score:.0f}% compatible
                    </div>
                </div>
                
                <p style="font-size: 1.2em; font-weight: bold; margin: 10px 0;">
                    💰 {prop['price']:,}€
                </p>
                
                <p style="margin: 10px 0; color: #666;">
                    🏠 {prop['property_type']} • 📐 {prop.get('surface', 'N/A')}m² • 📍 {prop['location']}
                </p>
                
                <p style="margin: 10px 0; font-style: italic; color: #555;">
                    {prop.get('match_explanation', 'Recommandé selon vos préférences')}
                </p>
                
                <a href="https://imo-match.streamlit.app" 
                   style="display: inline-block; background: #FF6B35; color: white; 
                          padding: 10px 20px; text-decoration: none; border-radius: 6px; 
                          margin-top: 15px;">
                    Découvrir cette propriété
                </a>
            </div>
            """
            html_parts.append(prop_html)
        
        return "".join(html_parts)
    
    # === TEMPLATES D'EMAILS ===
    
    def _get_welcome_template(self) -> str:
        """Template d'email de bienvenue"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Bienvenue sur ImoMatch</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; background: linear-gradient(135deg, #FF6B35, #F7931E); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px;">
                <h1 style="margin: 0; font-size: 2.5em;">🏠</h1>
                <h2 style="margin: 10px 0;">Bienvenue sur ImoMatch !</h2>
                <p style="margin: 0; opacity: 0.9;">Votre recherche immobilière avec l'IA commence maintenant</p>
            </div>
            
            <div style="padding: 20px;">
                <h2>Bonjour {user_name} ! 👋</h2>
                
                <p>Félicitations ! Vous venez de rejoindre ImoMatch et nous sommes ravis de vous accompagner dans votre recherche immobilière.</p>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #FF6B35; margin-top: 0;">Votre Plan : {plan_name}</h3>
                    <ul style="margin: 0; padding-left: 20px;">
                        {features_list}
                    </ul>
                </div>
                
                <h3>🚀 Pour commencer :</h3>
                <ol>
                    <li><strong>Définissez vos préférences</strong> : Budget, type de bien, localisation...</li>
                    <li><strong>Lancez votre première recherche</strong> avec nos filtres intelligents</li>
                    <li><strong>Discutez avec notre IA</strong> pour affiner vos critères</li>
                    <li><strong>Sauvegardez vos favoris</strong> et activez les alertes</li>
                </ol>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{login_url}" style="display: inline-block; background: #FF6B35; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                        Commencer ma recherche 🔍
                    </a>
                </div>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #666; font-size: 0.9em;">
                    Besoin d'aide ? Contactez-nous à <a href="mailto:{support_email}">{support_email}</a><br>
                    L'équipe ImoMatch
                </p>
            </div>
        </body>
        </html>
        """
    
    def _get_property_alert_template(self) -> str:
        """Template d'alerte de nouvelles propriétés"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Nouvelles propriétés disponibles</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; background: linear-gradient(135deg, #FF6B35, #F7931E); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h1 style="margin: 0;">🆕 Nouvelles propriétés !</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">{properties_count} nouvelle{'s' if properties_count > 1 else ''} propriété{'s' if properties_count > 1 else ''} pour "{search_name}"</p>
            </div>
            
            <div style="padding: 20px;">
                <h2>Bonjour {user_name} !</h2>
                
                <p>Bonne nouvelle ! Nous avons trouvé {properties_count} nouvelle{'s' if properties_count > 1 else ''} propriété{'s' if properties_count > 1 else ''} correspondant à votre recherche sauvegardée "<strong>{search_name}</strong>".</p>
                
                {properties_html}
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{app_url}" style="display: inline-block; background: #FF6B35; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                        Voir toutes les propriétés
                    </a>
                </div>
                
                <p style="color: #666; font-size: 0.9em;">
                    Vous recevez cet email car vous avez activé les alertes pour cette recherche. 
                    Vous pouvez modifier vos préférences d'alertes dans votre profil.
                </p>
            </div>
        </body>
        </html>
        """
    
    def _get_password_reset_template(self) -> str:
        """Template de réinitialisation de mot de passe"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Réinitialisation de mot de passe</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; padding: 20px;">
                <h1 style="color: #FF6B35;">🔒 Réinitialisation de mot de passe</h1>
            </div>
            
            <div style="padding: 20px;">
                <p>Vous avez demandé la réinitialisation de votre mot de passe ImoMatch.</p>
                
                <p>Cliquez sur le bouton ci-dessous pour créer un nouveau mot de passe :</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="display: inline-block; background: #FF6B35; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                        Réinitialiser mon mot de passe
                    </a>
                </div>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <p style="margin: 0;"><strong>Important :</strong></p>
                    <ul style="margin: 10px 0 0 20px;">
                        <li>Ce lien est valide pendant {expiry_hours} heures</li>
                        <li>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email</li>
                        <li>Pour votre sécurité, ne partagez jamais ce lien</li>
                    </ul>
                </div>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #666; font-size: 0.9em;">
                    Besoin d'aide ? Contactez-nous à <a href="mailto:{support_email}">{support_email}</a>
                </p>
            </div>
        </body>
        </html>
        """
    
    def _get_subscription_template(self) -> str:
        """Template de confirmation d'abonnement"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Confirmation d'abonnement</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px;">
                <h1 style="margin: 0; font-size: 2.5em;">✅</h1>
                <h2 style="margin: 10px 0;">Abonnement confirmé !</h2>
                <p style="margin: 0; opacity: 0.9;">Bienvenue dans le plan {plan_name}</p>
            </div>
            
            <div style="padding: 20px;">
                <h2>Merci {user_name} ! 🎉</h2>
                
                <p>Votre abonnement au plan <strong>{plan_name}</strong> est maintenant actif !</p>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #FF6B35; margin-top: 0;">Récapitulatif</h3>
                    <p><strong>Plan :</strong> {plan_name}</p>
                    <p><strong>Montant :</strong> {amount}€/mois</p>
                    <p><strong>Date de facturation :</strong> {billing_date}</p>
                </div>
                
                <h3>🎁 Vos nouveaux avantages :</h3>
                <ul>
                    {features_list}
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{app_url}" style="display: inline-block; background: #FF6B35; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                        Découvrir mes nouveaux avantages
                    </a>
                </div>
                
                <p style="color: #666; font-size: 0.9em;">
                    Votre abonnement sera renouvelé automatiquement chaque mois. 
                    Vous pouvez modifier ou annuler votre abonnement à tout moment dans votre profil.
                </p>
            </div>
        </body>
        </html>
        """
    
    def _get_new_match_template(self) -> str:
        """Template de nouvelles recommandations"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Nouvelles recommandations</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; background: linear-gradient(135deg, #6f42c1, #e83e8c); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h1 style="margin: 0;">💡 Recommandations pour vous</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Notre IA a sélectionné {properties_count} propriété{'s' if properties_count > 1 else ''} parfaite{'s' if properties_count > 1 else ''}</p>
            </div>
            
            <div style="padding: 20px;">
                <h2>Bonjour {user_name} !</h2>
                
                <p>Notre intelligence artificielle a analysé vos préférences et votre historique pour vous proposer {properties_count} recommandation{'s' if properties_count > 1 else ''} personnalisée{'s' if properties_count > 1 else ''} :</p>
                
                {properties_html}
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{app_url}" style="display: inline-block; background: #FF6B35; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                        Voir plus de recommandations
                    </a>
                </div>
                
                <div style="background: #e7f3ff; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff;">
                    <p style="margin: 0;"><strong>💡 Conseil :</strong> Plus vous utilisez ImoMatch (favoris, recherches, préférences), plus nos recommandations deviennent précises !</p>
                </div>
            </div>
        </body>
        </html>
        """


class EmailTemplateManager:
    """Gestionnaire de templates d'emails personnalisés"""
    
    def __init__(self):
        self.custom_templates = {}
    
    def add_custom_template(self, template_name: str, html_content: str,
                           variables: List[str] = None):
        """Ajoute un template personnalisé"""
        self.custom_templates[template_name] = {
            'html': html_content,
            'variables': variables or []
        }
    
    def render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Rend un template avec les variables"""
        if template_name not in self.custom_templates:
            raise ValueError(f"Template {template_name} non trouvé")
        
        template = self.custom_templates[template_name]
        return template['html'].format(**variables)


# Instance globale
email_manager = EmailManager()
template_manager = EmailTemplateManager()

def get_email_manager() -> EmailManager:
    """Retourne l'instance du gestionnaire d'emails"""
    return email_manager

def send_welcome_email(user_email: str, user_name: str, plan: str = 'free') -> bool:
    """Fonction utilitaire pour envoyer un email de bienvenue"""
    return email_manager.send_welcome_email(user_email, user_name, plan)

def send_property_alert(user_email: str, user_name: str,
                       properties: List[Dict[str, Any]], search_name: str) -> bool:
    """Fonction utilitaire pour envoyer une alerte de propriétés"""
    return email_manager.send_property_alert(user_email, user_name, properties, search_name)
