
import time
from threading import Thread
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QHBoxLayout, QVBoxLayout, QListWidget, \
    QListWidgetItem
from PyQt5.QtCore import QThread, pyqtSignal

from mp4rec import fileReco
from drives import HardDrives
from mediaplayerqt import VideoWindow




class Worker(QThread):
    listupdater = pyqtSignal(object)

    def __init__(self, fileR, parent_op):
        QThread.__init__(self)
        self.fileR = fileR
        self.switch = True
        self.parent_op = parent_op

    def stop(self):
        self.switch = False

    def run(self):
        """Long-running task."""
        self.switch = True
        while self.switch:

            self.listupdater.emit("new")

            if not self.fileR.searching:
                self.parent_op.start_b.setDisabled(False)

            time.sleep(1)


class Window(QWidget):

    def __init__(self):
        super().__init__()
        self.hard_disk = HardDrives()
        self.drives_list = []
        self.fileR = fileReco("\\\\.\\f:")
        self.result = []

        self.setMinimumSize(810, 600)
        self.setWindowTitle("JPG Recovery")

        self.vbox = QVBoxLayout(self)
        self.hbox = QHBoxLayout()
        self.hboxbotom = QHBoxLayout()

        self.vbox.addLayout(self.hbox)
        self.vbox.addLayout(self.hboxbotom)

        self.drives_cb = QComboBox()
        self.hbox.addWidget(self.drives_cb)

        self.refresh_cb_b = QPushButton()
        self.refresh_cb_b.setText("refresh")
        self.refresh_cb_b.clicked.connect(self.set_drives_cb)
        self.hbox.addWidget(self.refresh_cb_b)

        self.start_b = QPushButton()
        self.start_b.setText("start")
        self.start_b.clicked.connect(self.start_f)
        self.hbox.addWidget(self.start_b)

        self.stop_b = QPushButton()
        self.stop_b.setText("stop")
        self.stop_b.clicked.connect(self.stop_f)
        self.hbox.addWidget(self.stop_b)

        self.save_b = QPushButton()
        self.save_b.setText("save selected")
        self.save_b.clicked.connect(self.save_f)
        self.hbox.addWidget(self.save_b)

        self.result_listview = QListWidget()

        self.result_listview.itemClicked.connect(self.set_player)

        self.hboxbotom.addWidget(self.result_listview)
        self.resultviewer = VideoWindow()

        self.resultviewer.setFixedSize(800, 600)

        self.hboxbotom.addWidget(self.resultviewer)
        self.worker = Worker(self.fileR, self)
        self.worker.listupdater.connect(self.addto_result_listview)
        self.worker.start()
        self.set_drives_cb()

    def set_player(self):
        selected = self.result_listview.currentRow()
        data = self.result[selected].get_tmp_data()
        if data:
            self.resultviewer.set_player_data(data)

    def set_result_listview(self):
        self.result_listview.clear()
        self.result = self.fileR.get_result()
        for i, file in enumerate(self.result):
            item = QListWidgetItem(str(file.start))
            item.setCheckState(0)
            self.result_listview.addItem(item)

    def addto_result_listview(self, mmm=""):
        newresult = self.fileR.get_result()
        if len(newresult) > len(self.result):
            for i, file in enumerate(newresult[len(self.result):]):
                item = QListWidgetItem(str(file.start))
                item.setCheckState(0)
                self.result_listview.addItem(item)
            self.result = newresult

    def set_drives_cb(self):
        self.drives_cb.clear()
        self.hard_disk.reload()
        self.drives_list = self.hard_disk.get_available_list()
        for drive in self.drives_list:
            newstr = f""" {drive["Path"]} Total : {drive["Total"]} (Used: {drive["Used"]}, Free: {drive["Free"]})"""
            self.drives_cb.addItem(newstr, drive["name"])

    def start_f(self):
        if not self.fileR.searching:
            selected = self.drives_cb.currentData()
            self.fileR.resultspos.clear()
            self.fileR.results.clear()
            self.result.clear()
            self.result_listview.clear()
            self.fileR.set_path(selected)
            self.fileR.startthread()

            self.start_b.setDisabled(True)

    def stop_f(self):
        self.fileR.stop()
        self.set_result_listview()
        self.start_b.setDisabled(False)

    def save_f(self):
        def savethread():

            indexes = []
            res = True
            for i in range(len(self.result)):
                item = self.result_listview.item(i)
                if item.checkState():
                    indexes.append(i)
            for i in indexes:
                res = res and self.result[i].save(str(self.result[i].start))

            if res:
                print("all saved successfully")
            else:
                print("there was error saving")

        Thread(target=savethread).start()
        self.fileR.saveresultspos("results")

    def closeEvent(self, event):
        self.fileR.stop()



