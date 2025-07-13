"""
Module de gestion d'erreurs robuste pour TeleFeed Bot
Gère les erreurs Telethon et les problèmes de connectivité
"""

import logging
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)

class TeleFeedErrorHandler:
    """Gestionnaire d'erreurs centralisé pour le bot"""
    
    @staticmethod
    def handle_telethon_error(func):
        """Décorateur pour gérer les erreurs Telethon courantes"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_msg = str(e)
                
                # Erreurs d'entité non trouvée
                if "Could not find the input entity" in error_msg:
                    logger.warning(f"Entity not found in {func.__name__}: {error_msg}")
                    return None
                
                # Erreurs d'accès refusé
                elif "You can't retrieve the information" in error_msg:
                    logger.warning(f"Access denied in {func.__name__}: {error_msg}")
                    return None
                
                # Erreurs de réseau
                elif "Network error" in error_msg or "Connection reset" in error_msg:
                    logger.error(f"Network error in {func.__name__}: {error_msg}")
                    await asyncio.sleep(5)  # Attendre avant de réessayer
                    return None
                
                # Erreurs de limite de taux
                elif "Too Many Requests" in error_msg or "FLOOD_WAIT" in error_msg:
                    logger.warning(f"Rate limit in {func.__name__}: {error_msg}")
                    await asyncio.sleep(10)  # Attendre plus longtemps
                    return None
                
                # Erreur PeerUser spécifique
                elif "PeerUser" in error_msg and "100" in error_msg:
                    logger.warning(f"PeerUser error in {func.__name__}: {error_msg}")
                    return None
                
                # Autres erreurs
                else:
                    logger.error(f"Unexpected error in {func.__name__}: {error_msg}")
                    return None
                    
        return wrapper
    
    @staticmethod
    def safe_get_entity(client, entity_id):
        """Récupération sécurisée d'une entité Telethon"""
        @TeleFeedErrorHandler.handle_telethon_error
        async def _get_entity():
            return await client.get_entity(entity_id)
        return _get_entity()
    
    @staticmethod
    def safe_send_message(client, chat_id, message):
        """Envoi sécurisé de message"""
        @TeleFeedErrorHandler.handle_telethon_error
        async def _send_message():
            return await client.send_message(chat_id, message)
        return _send_message()
    
    @staticmethod
    def safe_forward_message(client, chat_id, message):
        """Transfert sécurisé de message"""
        @TeleFeedErrorHandler.handle_telethon_error
        async def _forward_message():
            return await client.forward_messages(chat_id, message)
        return _forward_message()
    
    @staticmethod
    def safe_edit_message(client, chat_id, message_id, text):
        """Édition sécurisée de message"""
        @TeleFeedErrorHandler.handle_telethon_error
        async def _edit_message():
            return await client.edit_message(chat_id, message_id, text)
        return _edit_message()
    
    @staticmethod
    def safe_delete_message(client, chat_id, message_id):
        """Suppression sécurisée de message"""
        @TeleFeedErrorHandler.handle_telethon_error
        async def _delete_message():
            return await client.delete_messages(chat_id, message_id)
        return _delete_message()

# Instance globale du gestionnaire d'erreurs
error_handler = TeleFeedErrorHandler()