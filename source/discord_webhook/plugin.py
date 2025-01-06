import requests
import logging
from unmanic.libs.unplugins.settings import PluginSettings

logger = logging.getLogger("Unmanic.Plugin.discord_webhook")

class Settings(PluginSettings):
    settings = {
        "Webhook URL": "",
        "Webhook Username": "",
        "Webhook Avatar URL": "",
        "Display Absolute Paths?": False,
        "Ping Everyone?": False
    }

def on_worker_process(data):
    logger.info("Sending notification to webhook for a started task.")
    settings = Settings(library_id=data['library_id'])

    webhookUrl = settings.get_setting("Webhook URL")
    absolutePaths = settings.get_setting("Display Absolute Paths?")
    pingEveryone = settings.get_setting("Ping Everyone?")
    username = settings.get_setting("Webhook Username")
    avatarUrl = settings.get_setting("Webhook Avatar URL")

    file = data["file_in"] if absolutePaths else data["file_in"].split("/")[-1]

    body = {
        "content": "@everyone" if pingEveryone else None,
        "username": username if len(username) > 0 else None,
        "avatar_url": avatarUrl if len(avatarUrl) > 0 else None,
        "embeds": [
            {
                "title": "Task Started",
                "description": "A file processing task has begun.",
                "color": 0xFFFF00,
                "fields": [
                    {
                        "name": "File",
                        "value": "```{}```".format(file),
                        "inline": False
                    },
                ]
            }
        ]
    }

    resp = requests.post(webhookUrl, body)
    if not resp.ok:
        logger.error("Got a bad response (%d) from Discord: %s", resp.json())

    return data

def on_postprocessor_task_results(data):
    settings = Settings(library_id=data['library_id'])

    webhookUrl = settings.get_setting("Webhook URL")
    absolutePaths = settings.get_setting("Display Absolute Paths?")
    pingEveryone = settings.get_setting("Ping Everyone?")
    username = settings.get_setting("Webhook Username")
    avatarUrl = settings.get_setting("Webhook Avatar URL")

    destination_files = ''.join(file if absolutePaths else file.split("/")[-1] for file in data["destination_files"])
    source_file = data["source_data"]["abspath"] if absolutePaths else data["source_data"]["basename"]

    if (data["task_processing_success"] and data["file_move_processes_success"]):
        body = {
            "content": "@everyone" if pingEveryone else None,
            "username": username if len(username) > 0 else None,
            "avatar_url": avatarUrl if len(avatarUrl) > 0 else None,
            "embeds": [
                {
                    "title": "Task Completed",
                    "description": "A file processing task successfully completed.",
                    "color": 0x00FF00,
                    "fields": [
                        {
                            "name": "File(s) Created",
                            "value": "```{}```".format(destination_files if len(destination_files) > 0 else "None"),
                            "inline": False
                        },
                        {
                            "name": "Original (Source) File",
                            "value": "```{}```".format(source_file),
                            "inline": False
                        },
                    ]
                }
            ]
        }
    else:
        body = {
            "content": "@everyone" if pingEveryone else None,
            "username": username if len(username) > 0 else None,
            "avatar_url": avatarUrl if len(avatarUrl) > 0 else None,
            "embeds": [
                {
                    "title": "Task Failed",
                    "description": "A file processing task failed during {}.".format("processing" if data["task_processing_success"] else "file movement"),
                    "color": 0xFF0000,
                    "fields": [
                        {
                            "name": "File(s) Created",
                            "value": "```{}```".format(destination_files if len(destination_files) > 0 else "None")
                        },
                        {
                            "name": "Original (Source) File",
                            "value": "```{}```".format(source_file),
                            "inline": False
                        },
                    ]
                }
            ]
        }

    resp = requests.post(webhookUrl, body)
    if not resp.ok:
        logger.error("Got a bad response (%d) from Discord: %s", resp.json())

    return data