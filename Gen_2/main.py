import sys
import os
import json
from pathlib import Path

from typing import Set, Optional

from PySide6.QtWidgets import QApplication

from Widgets import chatMain, chatSettings, botSettings, warningWidget

SETTINGS_KEYS = {"Name", "Bot Path", "Temperature", "Model", "Chat"}
def find_json_with_format(
        target_folder: str,
        required_keys: Set[str],
        file_extension: str = ".json",
        recursive: bool = False
) -> Optional[Path]:
    """
    Same as above but returns the Path of the first matching file.
    Returns None if no match is found.
    """
    folder_path = Path(target_folder)

    if not folder_path.exists():
        print("No such directory")
        return None
    if not folder_path.is_dir():
        print("This is not a directory")
        return None

    search_method = folder_path.rglob if recursive else folder_path.glob

    for file_path in search_method(f"*{file_extension}"):
        #print(file_path)
        if not file_path.is_file():
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, dict) and required_keys.issubset(data.keys()):
                return file_path
        except (json.JSONDecodeError, UnicodeDecodeError, PermissionError):
            continue

    return None

class Main:
    def __init__(self):
        self.x =0
        self.setupConnectors()

    def setupConnectors(self) -> None:
        mainChat.ui.actionChat_Settings.triggered.connect(self.openChatSettings)
        mainChat.ui.actionNew_Chat.triggered.connect(self.newChatSettings)


        settingsChat.ui.pushButton_2.clicked.connect(self.newBot)
        settingsChat.ui.pushButton_3.clicked.connect(self.cancelChatSettings)
        settingsChat.ui.pushButton_5.clicked.connect(self.saveChatSettings)

        settingsBot.ui.pushButton.clicked.connect(self.exitBotSettings)

        emptyStart.ui.pushButton.clicked.connect(self.newChatSettings)

    def read_json_file(self, file_path):
        """Read a JSON file and return its contents"""
        try:
            # Convert to Path object for better handling
            json_path = Path(file_path)

            if not json_path.exists():
                print(f"❌ File not found: {file_path}")
                return None

            # Read the file
            with open(json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            print(f"✅ JSON loaded successfully from: {json_path.name}")
            return data

        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON format: {e}")
            return None
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None

    def get_currentChat(self):
        logPath = Path(parent_directory) / "Save" / ".temp.json"
        log = self.read_json_file(logPath)
        return log["LastChat"]

    def get_currentBot(self):
        chatJson = self.get_currentChat()
        botPath = chatJson["BotPath"]
        return botPath

    def cancelChatSettings(self):

        if noChats:
            warningLeaveEmpty.show()
        else:
            settingsChat.close()

    def saveChatSettings(self):
        if False:
            invalidChatSettings.show()
        else:
            settingsChat.save_settings()
            settingsChat.close()  # Close current window
            if not mainChat.isVisible():
                mainChat.show()

    def newChatSettings(self):
        settingsChat.loadSettings("")
        settingsChat.show()
        if emptyStart.isVisible():
            emptyStart.close()

    def openChatSettings(self):
        settingsChat.loadSettings(str(self.get_currentChat()))
        settingsChat.show()

    def newBot(self):
        settingsBot.loadSettings("")
        settingsBot.show()

    def loadBot(self):
        settingsBot.loadSettings(str(self.get_currentBot()))
        settingsBot.show()

    def exitBotSettings(self):
        settingsBot.close()

if __name__ == "__main__":

    current_script_path = os.path.abspath(__file__)
    parent_directory = os.path.dirname(current_script_path)
    print(parent_directory)

    app = QApplication(sys.argv)
    mainChat = chatMain.ChatMain(parent_directory)
    emptyStart = warningWidget.EmptyStart(parent_directory)
    settingsChat = chatSettings.ChatSettings(parent_directory)
    settingsBot = botSettings.BotSettings(parent_directory)
    warningLeaveEmpty = warningWidget.EmptyLeave(parent_directory)
    invalidChatSettings = warningWidget.InvalidChatSettings(parent_directory)

    connector = Main()

    if find_json_with_format(parent_directory + r"\Save\Chat", SETTINGS_KEYS) is not None:
        noChats = False
        mainChat.show()

    else:
        print(parent_directory + r"\Save\Chat")
        noChats = True
        emptyStart.show()

    sys.exit(app.exec())