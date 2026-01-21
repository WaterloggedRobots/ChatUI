import llmClient

from PySide6.QtWidgets import QMainWindow, QSizePolicy
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt
import json
from pathlib import Path
import os

class ChatMain(QMainWindow):
    def __init__(self, pd):
        super().__init__()
        self.isShowImgWindow = True
        self.isShowImgWindowLock = False
        self.isShowChatList = False
        self.directoryParent = pd
        self.llm = llmClient.LLMClient()
        self.load_ui()
        self.setup_connections()
        # Store the initial stretch for the graphicsView column (e.g., 1)
        self.graphics_view_column_stretch = 1

        self.client = llm.LLMClient()
        self.client.token.connect(self.on_token)
        self.client.done.connect(self.on_done)

    def load_ui(self):
        """Load the UI file"""
        try:
            ui_file = QFile(self.directoryParent+r"\UI\Chat Window.ui")  # Change to your .ui file name
            if not ui_file.open(QFile.ReadOnly):
                print(f"Cannot open UI file: {ui_file.errorString()}")
                return

            loader = QUiLoader()
            self.ui = loader.load(ui_file)
            ui_file.close()

            if self.ui:
                self.setCentralWidget(self.ui)
                self.setWindowTitle("ChatUI")
                self.hideChatList()
                lastChat = self.get_lastChat()
                self.load_chat(lastChat)
                # Connect signals and slots here
                # Example: self.ui.button.clicked.connect(self.on_button_click)

        except Exception as e:
            print(f"Error loading UI: {e}")

    def setup_connections(self):
        """Connect button signals to functions"""
        # Connect the toggle button - replace 'pushButton_7' with your actual button name
        self.ui.pushButton.clicked.connect(self.toggle_graphics_view)
        self.ui.pushButton_2.clicked.connect(self.toggle_chat_list)

        self.ui.actionNew_Chat.setShortcut("Ctrl+N")
        self.ui.actionChat_Settings.setShortcut("Ctrl+E")

        self.input = self.ui.plainTextEdit
    def on_token(self, text):
        self.chat.insertPlainText(text)
        self.chat.ensureCursorVisible()

    def on_done(self, full_text):
        self.chat.insertPlainText("\n\n")
        print(self.chat)

    def keyPressEvent(self, event):
        if self.input.hasFocus():
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                if event.modifiers() & Qt.ShiftModifier:
                    self.input.insertPlainText("\n")
                else:
                    text = self.input.toPlainText().strip()
                    self.input.clear()
                    if text:
                        self.chat.append(f"\nYou:\n{text}\n\nModel:\n")
                        self.client.add_user_message(text)
                        self.client.generate()
                return
        super().keyPressEvent(event)

    def toggle_graphics_view(self):
        """Toggle graphics view visibility by adjusting width constraints"""
        if self.isShowImgWindow:
            self.hideImgWindow()
            self.isShowImgWindow = False
        elif not self.isShowImgWindowLock:
            self.showImgWindow()
            self.isShowImgWindow = True

    def hideImgWindow(self):
        layoutH3 = self.ui.horizontalLayout_3
        # HIDE: Set max width to 0, disable the widget, and collapse layout space
        self.ui.graphicsView.setMaximumWidth(0)
        self.ui.graphicsView.setMinimumWidth(0)

        layoutH3.itemAt(3).changeSize(0, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)
        # layoutH3.itemAt(5).changeSize(0,20, QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.ui.pushButton_7.setMaximumWidth(0)
        self.ui.pushButton_7.setEnabled(False)
        self.ui.graphicsView.setEnabled(False)

        # Optional: Also hide it visually
        self.ui.graphicsView.setVisible(False)

        # Update button text
        self.ui.pushButton.setText("<<")

        # Optional: Adjust layout column stretch if using gridLayout
        # This helps textBrowser expand into the freed space
        if hasattr(self.ui, 'gridLayout'):
            self.ui.gridLayout.setColumnStretch(1, 0)  # Column 1 is graphicsView

    def showImgWindow(self):
        layoutH3 = self.ui.horizontalLayout_3
        # SHOW: Restore original width constraints and enable
        self.ui.graphicsView.setMaximumWidth(16777215)
        self.ui.graphicsView.setMinimumWidth(0)

        layoutH3.itemAt(3).changeSize(40, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)
        # layoutH3.itemAt(5).changeSize(30, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.ui.graphicsView.setEnabled(True)
        self.ui.graphicsView.setVisible(True)

        # Update button text
        self.ui.pushButton.setText(">>")

        self.ui.pushButton_7.setMaximumWidth(16777215)
        self.ui.pushButton_7.setEnabled(True)

        self.is_graphics_view_visible = True

        # Force layout update
        self.ui.graphicsView.parentWidget().updateGeometry()

    def toggle_chat_list(self):
        """Toggle graphics view visibility by adjusting width constraints"""
        if self.isShowChatList:
            self.hideChatList()
            self.ui.pushButton_2.setText(">>")
        else:
            self.showChatList()
            self.ui.pushButton_2.setText("<<")

    def hideChatList(self):
        self.ui.listWidget.setVisible(False)
        self.isShowChatList = False
        if not self.isShowImgWindowLock and self.isShowImgWindow:
            self.showImgWindow()
            self.ui.pushButton.setEnabled(True)

    def showChatList(self):
        self.ui.listWidget.setVisible(True)
        self.hideImgWindow()
        self.isShowChatList = True
        self.ui.pushButton.setEnabled(False)

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

    def get_first_json_file_os(self,directory: str, recursive: bool = False):
        """Using os module instead of pathlib"""
        if not os.path.exists(directory):
            print(f"Directory does not exist: {directory}")
            return None

        if not os.path.isdir(directory):
            print(f"Path is not a directory: {directory}")
            return None

        if recursive:
            # Walk through all subdirectories
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.json'):
                        return os.path.abspath(os.path.join(root, file))
        else:
            # Check only the given directory
            for file in os.listdir(directory):
                if file.lower().endswith('.json'):
                    return os.path.abspath(os.path.join(directory, file))

        print(f"No .json files found in: {directory}")
        return None

    def get_lastChat(self):
        logPath = Path(self.directoryParent) / "Save" / ".temp.json"
        log = self.read_json_file(logPath)
        return log["LastChat"]

    def update_lastChat(self, path):
        logPath = Path(self.directoryParent) / "Save" / ".temp.json"
        log = self.read_json_file(logPath)
        log_new = log.copy()
        log_new["LastChat"] = path

        with open(logPath, "w", encoding="utf-8") as f:
            json.dump(log_new, f, indent=4)

    def load_chat(self,path):
        if path =="":
            savePath = Path(self.directoryParent) / "Save" / "Chat"
            path = self.get_first_json_file_os(str(savePath))
            if path is None:
                return
        chatHist = self.read_json_file(path)

        self.update_lastChat(path)
        self.ui.lineEdit.setText(chatHist["Name"])
        self.ui.textBrowser.setText(chatHist["Chat"])
        self.load_bot(chatHist["Bot Path"])

        self.llm.chatHist = chatHist["Chat"] #visible chat history
        self.llm.chatJson = chatHist["Payload"] #invisible complete payload
        self.llm.temp = chatHist["Temperature"]

    def load_bot(self,path):
        botJsonPath = path + "/Bot Description.json"
        botJson = self.read_json_file(botJsonPath)

        self.llm.model = botJson["Model"]   #model name
        self.llm.chara = botJson["Description"]  #bot preset instructions
        self.llm.workflow = botJson["Workflow"] # comfyUI workflow path, to be developed later via comfyui api

        if botJson['WorkflowPath'] =="":
            self.isShowImgWindowLock = True
            self.hideImgWindow()
            self.ui.pushButton.setEnabled(False)
        else:
            self.isShowImgWindowLock = False
            self.showImgWindow()
            self.ui.pushButton.setEnabled(True)
