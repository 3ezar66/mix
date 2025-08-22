"""
Core configuration and utilities for the Miner Detection System
"""
from typing import Dict, Any
import logging
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# System configuration
CONFIG = {
    "project_name": "Miner Detection System",
    "version": "1.0.0",
    "ilam_bounds": {
        "north": 34.5,
        "south": 32.0,
        "east": 48.5,
        "west": 45.5,
        "center": [33.63, 46.42]
    },
    "db": {
        "url": "sqlite:///minerdb.db",
        "pool_size": 5,
        "max_overflow": 10
    },
    "api": {
        "host": "0.0.0.0",
        "port": 8000,
        "debug": True
    },
    "scan": {
        "threads": 50,
        "timeout": 3.0,
        "batch_size": 256
    }
}

def load_config(config_file: str = "config.json") -> Dict[str, Any]:
    """Load configuration from file, falling back to defaults"""
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                return {**CONFIG, **user_config}  # Merge with defaults
        except Exception as e:
            logging.error(f"Error loading config: {e}")
    return CONFIG

def setup_logging(log_file: str = None):
    """Configure logging with file output if specified"""
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logging.getLogger().addHandler(file_handler)

# Initialize system
config = load_config()
setup_logging("miner_detection.log")
