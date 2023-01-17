# Author: Sunil Mathew
# Date: 17 Jan 2023

import openai

from qtpy import uic
from qtpy.QtWidgets import QApplication, QMainWindow, QWidget

class Ui(QMainWindow):

    #region Initialization

    def __init__(self):
        super().__init__()
        uic.loadUi('chat.ui', self)

        self.init_ui()

    def init_ui(self):
        widget = QWidget()
        widget.setLayout(self.hLytMain)
        self.setCentralWidget(widget)

        self.init_openai()
        self.register_events()

    def register_events(self):
        self.btnSubmit.clicked.connect(self.gen_results)    
    
    #endregion Initialization

    #region OpenAI

    def init_openai(self):
        # openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key_path = 'chat.env'

    def gen_results(self):
        text_input = self.txtInput.toPlainText()
        text_input = text_input.strip()

        if not text_input:
            return

        response = openai.Completion.create(
        model="text-davinci-003",
        prompt=text_input,
        temperature=0.3,
        max_tokens=2048,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
        )
        res = response['choices'][0]['text']
        self.txtOutput.clear()
        self.txtOutput.setPlainText(res)
        # print(ch)

    #endregion OpenAI

app = QApplication([])
mainWindow = Ui()
mainWindow.show()
app.exec()