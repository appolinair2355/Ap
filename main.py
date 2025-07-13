import os
from dotenv import load_dotenv
from bot.handlers import start_bot_sync
from http_server import start_server_in_background
import threading

if __name__ == "__main__":
    # Charger les variables d'environnement
    load_dotenv()
    print("✅ Fichier .env chargé")

    # Configuration du serveur
    server_port = int(os.environ.get('PORT', 10000))
    os.environ['PORT'] = str(server_port)
    print("🚀 bot déployé avec succès")

    # Start HTTP server in background
    server_thread = start_server_in_background()
    
    # Start the bot (main process)
    start_bot_sync()