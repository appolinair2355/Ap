"""
Système de communication automatique Serveur ↔ Bot
Communication silencieuse et automatique sans messages visibles
"""

import os
import asyncio
import aiohttp
import logging
import time
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AutoCommunicationSystem:
    """Système de communication automatique entre le serveur et le Bot"""
    
    def __init__(self, bot_client, admin_id):
        self.bot_client = bot_client
        self.admin_id = admin_id
        self.server_url = os.getenv('SERVER_URL', 'http://localhost:10000')
        self.bot_token = os.getenv('BOT_TOKEN')
        self.last_ping_time = time.time()
        self.communication_active = True
        
    async def start_auto_communication(self):
        """Démarrer le système de communication automatique"""
        logger.info("🔄 Démarrage du système de communication automatique")
        
        # Démarrer les tâches en parallèle
        tasks = [
            asyncio.create_task(self.ping_loop()),
            asyncio.create_task(self.health_monitor())
        ]
        
        # Notifier le déploiement réussi
        await self.notify_deployment_success()
        
        # Exécuter toutes les tâches
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def notify_deployment_success(self):
        """Notifier automatiquement le déploiement réussi"""
        try:
            # Attendre que le bot soit complètement démarré
            await asyncio.sleep(5)
            
            # Message de confirmation de déploiement
            success_message = f"""
🚀 **DÉPLOIEMENT RÉUSSI**

✅ Bot TeleFeed déployé avec succès
🌐 URL Serveur: {self.server_url}
⏰ Déployé le: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}

🔄 **Statut des communications:**
• Serveur → Bot: ✅ Opérationnel
• Bot → Serveur: ✅ Actif
• Monitoring: ✅ Configuré

🎯 Toutes les redirections sont actives et le système de maintien d'activité fonctionne automatiquement.
            """
            
            # Envoyer via l'API Telegram
            await self.send_telegram_message(success_message)
            logger.info("✅ Notification de déploiement envoyée")
            
        except Exception as e:
            logger.error(f"Erreur notification déploiement: {e}")
    

    
    async def ping_loop(self):
        """Boucle de ping automatique silencieux"""
        while self.communication_active:
            try:
                await asyncio.sleep(60)  # Ping toutes les 60 secondes
                
                # Ping silencieux vers le serveur local
                await self.silent_ping_server()
                
                self.last_ping_time = time.time()
                
            except Exception as e:
                logger.error(f"Erreur dans ping loop: {e}")
                await asyncio.sleep(30)
    
    async def silent_ping_server(self):
        """Ping silencieux vers le serveur local pour maintenir l'activité"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.server_url}/ping",
                    timeout=10
                ) as response:
                    if response.status == 200:
                        logger.debug("🔄 Ping serveur silencieux réussi")
                    
        except Exception as e:
            logger.debug(f"Ping serveur failed: {e}")
    
    async def health_monitor(self):
        """Surveillance de santé automatique"""
        while self.communication_active:
            try:
                await asyncio.sleep(300)  # Vérification toutes les 5 minutes
                
                # Vérifier la santé du serveur
                server_health = await self.check_server_health()
                if not server_health:
                    await self.wake_up_server()
                
            except Exception as e:
                logger.error(f"Erreur dans health monitor: {e}")
                await asyncio.sleep(60)
    
    async def check_server_health(self):
        """Vérifier la santé du serveur"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.server_url}/health",
                    timeout=5
                ) as response:
                    return response.status == 200
        except:
            return False
    
    async def wake_up_server(self):
        """Réveiller le serveur silencieusement"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.server_url}/wake-up",
                    timeout=10
                ) as response:
                    if response.status == 200:
                        logger.info("🔔 Serveur réveillé automatiquement")
        except Exception as e:
            logger.error(f"Erreur réveil serveur: {e}")
    

    
    async def send_telegram_message(self, message):
        """Envoyer un message Telegram via API"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                data = {
                    'chat_id': self.admin_id,
                    'text': message,
                    'parse_mode': 'Markdown'
                }
                
                async with session.post(url, json=data, timeout=10) as response:
                    if response.status == 200:
                        logger.info("📨 Message Telegram envoyé")
                    else:
                        logger.error(f"Erreur envoi Telegram: {response.status}")
                        
        except Exception as e:
            logger.error(f"Erreur envoi message: {e}")
    
    def stop_communication(self):
        """Arrêter le système de communication"""
        self.communication_active = False
        logger.info("🛑 Système de communication automatique arrêté")
    
    def get_communication_status(self):
        """Obtenir le statut de communication"""
        return {
            'active': self.communication_active,
            'server_url': self.server_url,
            'last_ping': datetime.fromtimestamp(self.last_ping_time).strftime('%H:%M:%S')
        }