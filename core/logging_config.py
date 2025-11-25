"""
Configuration centralisée du logging pour résoudre les problèmes d'encodage
"""

import logging
import sys
from pathlib import Path

class UnicodeStreamHandler(logging.StreamHandler):
    """Handler qui gère correctement l'encodage Unicode sur Windows"""
    
    def emit(self, record):
        try:
            message = self.format(record)
            stream = self.stream
            # Encodage forcé en UTF-8
            if hasattr(stream, 'buffer'):
                # Pour les streams binaires (stdout/stderr)
                stream.buffer.write(message.encode('utf-8'))
                stream.buffer.write(self.terminator.encode('utf-8'))
            else:
                # Pour les streams texte
                stream.write(message + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

def setup_logging():
    """Configure le logging pour éviter les erreurs d'encodage"""
    
    # Créer le dossier logs s'il n'existe pas
    logs_dir = Path(__file__).parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Configuration du formatteur
    formatter = logging.Formatter(
        '%(levelname)s %(asctime)s %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour la console avec encodage UTF-8
    console_handler = UnicodeStreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Handler pour le fichier email.log
    email_file_handler = logging.FileHandler(
        logs_dir / 'email.log', 
        encoding='utf-8'
    )
    email_file_handler.setFormatter(formatter)
    email_file_handler.setLevel(logging.INFO)
    
    # Configuration des loggers
    loggers = {
        'core.email_service': {
            'handlers': [console_handler, email_file_handler],
            'level': 'INFO',
            'propagate': False
        },
        'core': {
            'handlers': [console_handler],
            'level': 'INFO',
            'propagate': False
        }
    }
    
    for logger_name, config in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(config['level'])
        for handler in config['handlers']:
            logger.addHandler(handler)
        logger.propagate = config.get('propagate', False)