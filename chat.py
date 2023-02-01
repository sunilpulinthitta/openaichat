# Author: Sunil Mathew
# Created date: 17 Jan 2023
import os
import traceback
import openai

from qtpy import uic, QtGui, QtCore
from qtpy.QtWidgets import QApplication, QMainWindow, QTreeWidget, QWidget, QTreeWidgetItem, QMenu, QAction, QVBoxLayout
from qtpy.QtGui import QFontDatabase
from qtpy.QtWebEngineWidgets import QWebEngineView

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

        self.init_ui_font()
        self.fontsize_update()
        self.init_history_view()
        self.init_openai()
        self.register_events()
        self.init_webview()

    def init_webview(self):
        self.vLytWebView = QVBoxLayout(self)

        self.webEngineView = QWebEngineView()

        self.vLytWebView.addWidget(self.webEngineView)

        self.frameWebView.setLayout(self.vLytWebView)

    def init_ui_font(self):
        fonts = QFontDatabase.families()
        for f in fonts:
            self.cmbFontFamily.addItem(f)

        self.cmbFontFamily.setCurrentText("Arial")


    def register_events(self):
        self.cmbModel.currentIndexChanged.connect(self.gen_results)
        self.cmbFontFamily.currentIndexChanged.connect(self.fontsize_update)
        self.spbFontSize.valueChanged.connect(self.fontsize_update)
        self.btnSubmit.clicked.connect(self.gen_results)    

    def resizeEvent(self, event):
        """
        To resize webview
        """
        try:
            self.wv_h = str(self.vLytWebView.geometry().height())
            self.wv_w = str(self.vLytWebView.geometry().width())

            QMainWindow.resizeEvent(self, event)

        except:
            print("resizeEvent")
            print(traceback.format_exc())
    
    #endregion Initialization

    #region UI

    #region History

    def context_menu(self, pos):
        item = self.treeHistory.currentItem()
        self.display_prompt(item)
        menu = QMenu()
        removeItem = menu.addAction("Remove")
        action = menu.exec_(self.mapToGlobal(self.mapFromGlobal(QtGui.QCursor.pos())))
        if action == removeItem:
            del self.history[item.text(0)]
            root = self.treeHistory.invisibleRootItem()
            root.removeChild(item)
            self.txtInput.clear()
            self.webEngineView.setHtml('')

    def init_history_view(self):
        self.prompt_count = 0
        self.history = {}

        #adding the tree widget to a frame
        self.frameHistory.setLayout(self.vLytHistory)
        self.treeHistory.clicked.connect(self.treeWidgetClicked)
        self.treeHistory.setHeaderLabels(["History"])

        self.chkHistory.toggled.connect(self.show_hide_history)        

        #show the context menu when the user right clicks on the tree widget
        self.treeHistory.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeHistory.customContextMenuRequested.connect(self.context_menu)
    
    def show_hide_history(self):
        if self.chkHistory.isChecked():
            self.frameHistory.show()
        else:
            self.frameHistory.hide()

    def treeWidgetClicked(self, qModelIndex):
        item = self.treeHistory.currentItem()
        self.display_prompt(item)
    
    def display_prompt(self, item):
        txtInput = list(self.history[item.text(0)].keys())[0]
        res = list(self.history[item.text(0)].values())[0]
        txtOutput = self.wrap_html(res=res)
        self.txtInput.setPlainText(txtInput)
        self.webEngineView.setHtml(txtOutput)

    #endregion History

    def wrap_html(self, res):
        return '<span style="white-space: pre-line; word-wrap: break-word; font-family:'+self.cmbFontFamily.currentText()+'; font-size: '+str(self.font_sz)+'px;">'+res+'</span>'

    def fontsize_update(self):
        self.font_sz = self.spbFontSize.value()

        font = QtGui.QFont(self.cmbFontFamily.currentText())
        font.setPointSize(self.font_sz)

        self.txtInput.setFont(font)

        if hasattr(self, "res"):
            txtOutput = self.wrap_html(res=self.res)
            self.webEngineView.setHtml(txtOutput)

    #endregion UI

    #region OpenAI

    def init_openai(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        # openai.api_key_path = 'chat.env'

        self.cmbModel.addItem('text-davinci-003')
        self.cmbModel.addItem('text-ada-001')
        self.cmbModel.addItem('text-babbage-001')
        self.cmbModel.addItem('text-curie-001')

    def gen_results(self):
        text_input = self.txtInput.toPlainText()
        text_input = text_input.strip()

        if not text_input:
            return

        try:
            response = openai.Completion.create(
            model=self.cmbModel.currentText(),
            prompt=text_input,
            temperature=0.3,
            max_tokens=2048 - len(text_input),
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
            )
            res = response['choices'][0]['text']

            self.wv_h = str(self.vLytWebView.sizeHint().height())
            self.wv_w = str(self.vLytWebView.sizeHint().width())

            txtOutput = self.wrap_html(res=res)
            self.webEngineView.setHtml(txtOutput)
            # print(res)

            self.prompt_count += 1
            hist_item = QTreeWidgetItem(self.treeHistory)
            key = 'Prompt ' + str(self.prompt_count)
            hist_item.setText(0, key)
            self.history[key] = {text_input : res}
            self.res = res
        except:
            print(traceback.print_exc())

    #endregion OpenAI

    #region Dummy
    #endregion Dummy

app = QApplication([])
mainWindow = Ui()
mainWindow.show()
app.exec()
