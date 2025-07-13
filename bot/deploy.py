
import logging
import os
import zipfile
import shutil
from telethon import events
from datetime import datetime

logger = logging.getLogger(__name__)

async def handle_deploy(event, client):
    """
    Handle deployment command - creates ZIP file with all bot files
    Premium feature for licensed users
    """
    try:
        user_id = event.sender_id
        
        # Check if user has premium access
        if not await is_premium_user(user_id):
            await event.respond("❌ **Accès premium requis**\n\nCette fonctionnalité est réservée aux utilisateurs premium.\nUtilisez `/valide` pour activer votre licence.")
            return
        
        await event.respond("📦 **Création du package de déploiement...**\n\n⏳ Préparation des fichiers en cours...")
        
        # Create deployment ZIP
        zip_path = await create_deployment_zip()
        
        if zip_path and os.path.exists(zip_path):
            # Send the ZIP file
            await client.send_file(
                user_id,
                zip_path,
                caption="""
🚂 **Package de déploiement Railway COMPLET**

📁 **Contenu du package :**
• Tous les fichiers du bot
• Configuration Railway (railway.json, Dockerfile, nixpacks.toml)
• Système de communication automatique Railway ↔ Replit
• Variables d'environnement (.env.example)
• Documentation complète

🚀 **Prêt pour le déploiement sur Railway.app**

📋 **Instructions :**
1. Décompressez le fichier ZIP
2. Uploadez sur GitHub
3. Déployez sur Railway.app
4. Configurez les variables d'environnement
5. Recevez automatiquement la notification de succès !

✅ **Communication automatique Railway ↔ Replit ↔ Bot intégrée**
                """,
                attributes=[],
                force_document=True
            )
            
            # Clean up
            os.remove(zip_path)
            logger.info(f"Deployment package sent to user {user_id}")
            
        else:
            await event.respond("❌ **Erreur lors de la création du package**\n\nVeuillez réessayer plus tard.")
            
    except Exception as e:
        logger.error(f"Error in deploy handling: {e}")
        await event.respond("❌ Erreur lors du traitement du déploiement. Veuillez réessayer.")

async def create_deployment_zip():
    """Create a ZIP file with all necessary deployment files including Railway support"""
    try:
        # Get parent directory (project root)
        parent_dir = os.path.dirname(os.getcwd()) if os.path.basename(os.getcwd()) == 'bot' else os.getcwd()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"TeleFeed_Railway_Complete_{timestamp}.zip"
        zip_path = os.path.join(parent_dir, zip_filename)
        
        # Individual files to include - Railway complete package
        files_to_include = [
            'main.py',
            'main_railway.py',
            'auto_communication.py',
            'http_server.py',
            'railway_keep_alive.py',
            'keep_alive.py',
            'requirements.txt',
            'railway.json',
            'railway.toml',
            'Dockerfile',
            'nixpacks.toml',
            'start_railway.sh',
            'Procfile',
            'runtime.txt',
            'user_data.json',
            'RAILWAY_DEPLOYMENT.md',
            'PROJECT_OVERVIEW.md',
            'README.md'
        ]
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Change to parent directory for file operations
            os.chdir(parent_dir)
            
            # Add individual files
            for item in files_to_include:
                if os.path.exists(item):
                    zipf.write(item, os.path.basename(item))
                    logger.info(f"Added file to ZIP: {item}")
                else:
                    logger.warning(f"File not found: {item}")
            
            # Add all bot files with bot/ structure
            bot_dir = 'bot'
            if os.path.exists(bot_dir):
                for file in os.listdir(bot_dir):
                    file_path = os.path.join(bot_dir, file)
                    if os.path.isfile(file_path) and not file.endswith('.session') and '__pycache__' not in file:
                        zipf.write(file_path, f"bot/{file}")
                        logger.info(f"Added bot file to ZIP: {file}")
            
            # Add all config files with config/ structure
            config_dir = 'config'
            if os.path.exists(config_dir):
                for file in os.listdir(config_dir):
                    file_path = os.path.join(config_dir, file)
                    if os.path.isfile(file_path) and '__pycache__' not in file:
                        zipf.write(file_path, f"config/{file}")
                        logger.info(f"Added config file to ZIP: {file}")
            
            # Create deployment instructions for Railway
            instructions = f"""
# 🚂 TeleFeed Bot - Package Déploiement Railway Complet

## 📦 Contenu du Package
Ce package contient tous les fichiers nécessaires pour déployer TeleFeed Bot sur Railway.app avec toutes les fonctionnalités.

## ✅ Fonctionnalités Incluses
- ✅ Système de licences premium
- ✅ Connexion par numéro de téléphone
- ✅ Redirections automatiques de messages
- ✅ Transformations de messages
- ✅ Filtres whitelist et blacklist
- ✅ Gestion des chats connectés
- ✅ Panel d'administration complet
- ✅ Base de données PostgreSQL
- ✅ Système de sessions persistantes
- ✅ Gestion d'erreurs robuste
- ✅ Déploiement automatique
- ✅ Keep-alive avancé

## 🚀 Instructions de Déploiement Railway

### 1. Préparer le Repository GitHub
1. Créer un nouveau repository sur GitHub
2. Uploader tous ces fichiers dans le repository
3. Commit et push

### 2. Déployer sur Railway.app
1. Aller sur https://railway.app
2. Connecter votre compte GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Sélectionner votre repository

### 3. Ajouter une Base de Données PostgreSQL
1. Dans Railway, cliquer "Add Service"
2. Choisir "PostgreSQL"
3. Railway génère automatiquement la DATABASE_URL

### 4. Configurer les Variables d'Environnement Railway
```
API_ID=VOTRE_API_ID
API_HASH=VOTRE_API_HASH
BOT_TOKEN=VOTRE_BOT_TOKEN
ADMIN_ID=VOTRE_ADMIN_ID
RAILWAY_DEPLOYMENT=true
DATABASE_URL=postgresql://... (généré automatiquement)
PORT=8080
```

### 4. Fonctionnalités Automatiques
✅ Communication automatique Railway ↔ Replit ↔ Bot
✅ Notification de déploiement réussi dans Telegram
✅ Système de maintien d'activité intelligent
✅ Réveil automatique des plateformes
✅ Redirections automatiques actives
✅ Interface admin complète (/railway commands)

### 5. Déploiement Automatique
Railway va automatiquement :
- Détecter la configuration (railway.json)
- Construire l'image Docker
- Déployer le bot
- Envoyer une notification de succès dans Telegram

## 📞 Vérification
Une fois déployé, utilisez `/railway` dans le bot pour vérifier le statut.

Package créé le : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
Communication Railway ↔ Replit ↔ Bot : ACTIVE

1. Créez un nouveau service Web
2. Connectez votre repository
3. Configurez les variables d'environnement
4. Le bot se lancera automatiquement avec `python main.py`

## Fonctionnalités incluses

- ✅ Gestion des sessions persistantes
- ✅ Redirections automatiques
- ✅ Système de licences
- ✅ Paiements intégrés
- ✅ Administration complète

## Support

Pour toute assistance, contactez le support TeleFeed.
            """
            
            zipf.writestr("DEPLOYMENT_INSTRUCTIONS.md", instructions)
            
            # Create .env.example if it doesn't exist
            env_example = """
# TeleFeed Bot Configuration
API_ID=your_api_id_here
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here
DATABASE_URL=postgresql://user:password@host:port/database
ADMIN_ID=your_admin_id_here
            """
            
            if not os.path.exists('.env.example'):
                zipf.writestr(".env.example", env_example)
        
        logger.info(f"Deployment ZIP created: {zip_path}")
        return zip_path
        
    except Exception as e:
        logger.error(f"Error creating deployment ZIP: {e}")
        return None

async def is_premium_user(user_id):
    """Check if user has premium access"""
    try:
        from bot.database_postgres import db
        return db.is_user_licensed(user_id)
    except Exception:
        # Fallback to file-based system
        from bot.database import is_user_licensed
        return await is_user_licensed(user_id)
