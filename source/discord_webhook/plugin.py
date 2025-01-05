import requests
from unmanic.libs.unplugins.settings import PluginSettings

class Settings(PluginSettings):
    settings = {
        "Webhook URL": "",
        "Webhook Username": "",
        "Webhook Avatar URL": "",
        "Display Absolute Paths?": False,
        "Ping Everyone?": False
    }

def on_worker_process(data):
    settings = Settings(library_id=data.get['library_id'])

    webhookUrl = settings.get("Webhook URL")
    absolutePaths = settings.get("Display Absolute Paths?")
    pingEveryone = settings.get("Ping Everyone?")
    username = settings.get("Webhook Username")
    avatarUrl = settings.get("Webhook Avatar URL")

    file = data["file_in"] if absolutePaths else data["file_in"].split("/")[-1]

    body = {
        "content": "@everyone" if pingEveryone else None,
        "username": username if len(username) > 0 else None,
        "avatar_url": avatar_url if len(avatar_url) > 0 else None,
        "embeds": [
            {
                "title": "Task Started",
                "description": "A file processing task has begun."
                "type": "rich",
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

    requests.post(webhookUrl, body)
    return

def on_postprocessor_task_results(data):
    settings = Settings(library_id=data['library_id'])

    webhookUrl = settings.get("Webhook URL")
    absolutePaths = settings.get("Display Absolute Paths?")
    pingEveryone = settings.get("Ping Everyone?")
    username = settings.get("Webhook Username")
    avatarUrl = settings.get("Webhook Avatar URL")

    destination_files = ''.join(file if absolutePaths else file.split("/")[-1] for file in data["destination_files"])
    source_file = data["source_data"]["abspath"] if absolutePaths else data["source_data"]["basename"]

    if (data["task_processing_success"] and data["file_move_processes_success"]):
        body = {
            "content": "@everyone" if pingEveryone else None,
            "username": username if len(username) > 0 else None,
            "avatar_url": avatar_url if len(avatar_url) > 0 else None,
            "embeds": [
                {
                    "title": "Task Completed",
                    "description": "A file processing task successfully completed."
                    "type": "rich",
                    "color": 0x00FF00,
                    "fields": [
                        {
                            "name": "File(s) Created",
                            "value": "```{}```".format(destination_files if len(destination_files) > 0 else "None")
                        }
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
            "avatar_url": avatar_url if len(avatar_url) > 0 else None,
            "embeds": [
                {
                    "title": "Task Failed",
                    "description": "A file processing task failed during {}.".format("processing" if data["task_processing_success"] else "file movement")
                    "type": "rich",
                    "color": 0xFF0000,
                    "fields": [
                        {
                            "name": "File(s) Created",
                            "value": "```{}```".format(destination_files if len(destination_files) > 0 else "None")
                        }
                        {
                            "name": "Original (Source) File",
                            "value": "```{}```".format(source_file),
                            "inline": False
                        },
                    ]
                }
            ]
        }

    requests.post(webhookUrl, body)
    return