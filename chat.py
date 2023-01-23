# Author: Sunil Mathew
# Created date: 17 Jan 2023
import os
import openai

from qtpy import uic, QtGui
from qtpy.QtWidgets import QApplication, QMainWindow, QTreeWidget, QWidget, QTreeWidgetItem
from qtpy.QtGui import QStandardItemModel

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

        self.fontsize_update()
        self.init_history_view()
        self.init_openai()
        self.register_events()

    def init_ui_font(self):
        font = QtGui.QFont()
        font.setPointSize(20)

        self.txtInput.setFont(font)
        self.txtOutput.setFont(font)

    def register_events(self):
        self.dlFontSize.valueChanged.connect(self.fontsize_update)
        self.btnSubmit.clicked.connect(self.gen_results)    
    
    #endregion Initialization

    #region UI

    def init_history_view(self):
        self.prompt_count = 0
        self.history = {}

        #adding the tree widget to a frame
        self.frameHistory.setLayout(self.vLytHistory)
        self.treeHistory.clicked.connect(self.treeWidgetClicked)
        self.treeHistory.setHeaderLabels(["History"])

        self.chkHistory.toggled.connect(self.show_hide_history)
    
    def show_hide_history(self):
        if self.chkHistory.isChecked():
            self.frameHistory.show()
        else:
            self.frameHistory.hide()

    def treeWidgetClicked(self, qModelIndex):
        item = self.treeHistory.currentItem()
        txtInput = list(self.history[item.text(0)].keys())[0]
        txtOutput = list(self.history[item.text(0)].values())[0]
        self.txtInput.setPlainText(txtInput)
        self.txtOutput.setHtml(txtOutput)

    def fontsize_update(self):
        font_sz = self.dlFontSize.value()
        self.lblFontSize.setText("Font size: " + str(font_sz))

        font = QtGui.QFont()
        font.setPointSize(font_sz)

        self.txtInput.setFont(font)
        self.txtOutput.setFont(font)

    #endregion UI

    #region OpenAI

    def init_openai(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        # openai.api_key_path = 'chat.env'

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
        txtOutput = '<span style="white-space: pre;"><code>'+res+'</code></span>'
        self.txtOutput.setHtml(txtOutput)
        # print(res)

        self.prompt_count += 1
        hist_item = QTreeWidgetItem(self.treeHistory)
        key = 'Prompt ' + str(self.prompt_count)
        hist_item.setText(0, key)
        self.history[key] = {text_input : txtOutput}

    #endregion OpenAI

app = QApplication([])
mainWindow = Ui()
mainWindow.show()
app.exec()
