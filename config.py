import os
from dotenv import load_dotenv
import logging
from logging.config import dictConfig


load_dotenv()
DISCORD_TOKEN = os.getenv("TOKEN")

TEST_GUILD_ID = 1067126862167421040
FEEDBACK_CHANNEL_ID = 1114241735237845133

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "[%(levelname)-10s] %(asctime)s - %(filename)-15s (%(name)-10s) : %(message)s"
        },
        "default": {
            "format": "[%(levelname)-10s] %(asctime)s - %(filename)-15s : %(message)s"
        },
        "command": {
            "format": "%(asctime)s : %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "WARNING",
            "formatter": "default",
            "class": "logging.StreamHandler"
        },
        "verbose_console": {
            "level": "DEBUG",
            "formatter": "verbose",
            "class": "logging.StreamHandler"
        },
        "file": {
            "level": "INFO",
            "formatter": "verbose",
            "class": "logging.FileHandler",
            "filename": "logs/botexe.log",
            "mode": "w"
        },
        "commands": {
            "level": "INFO",
            "formatter": "command",
            "class": "logging.FileHandler",
            "filename": "logs/command_calls.log",
            "mode": "w"
        }
    },
    "loggers": {
        "bot": {
            "handlers": ["console", "file"],
            "level": "INFO"
        },
        "commands": {
            "handlers": ["commands"],
            "level": "INFO"
        },
        "discord": {
            "handlers": ["verbose_console", "file"],
            "level": "INFO"
        }
    }
}

dictConfig(LOGGING_CONFIG)
