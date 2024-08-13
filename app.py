from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QPushButton, QFileDialog, QSizePolicy, QMessageBox
# from records import Database, emptyDB
from utils import newHLine

import os

def createTab():
    tab = QWidget()
    label = QLabel("TODO")
    layout = QVBoxLayout(tab)
    layout.addWidget(label)
    tab.setLayout(layout)
    return tab

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Algorithmic Nexus for Information and Knowledge Analysis")
        
        # self.db = emptyDB()
        
        # from file_manager import FileManager
        # self.fileManager = FileManager(self)


        self.resize(1280, 720)

        # Create a QTabWidget
        self.tab_widget = QTabWidget()

        # Add tabs to the QTabWidget
        self.activeEmployeesTab = QLabel("TODO")
        self.tab_widget.addTab(self.activeEmployeesTab, "Active Employees")
        self.inactiveEmployeesTab = QLabel("TODO")
        self.tab_widget.addTab(self.inactiveEmployeesTab, "Inactive Employees")
        self.pointsTab = QLabel("TODO")
        self.tab_widget.addTab(self.pointsTab, "Points and Absences")
        self.ptoTab = QLabel("TODO")
        self.tab_widget.addTab(self.ptoTab, "PTO Tracker")
        self.holidayTab = QLabel("TODO")
        self.tab_widget.addTab(self.holidayTab, "Holiday Tracker")

        self.openButton = QPushButton("Open Database")
        self.openButton.clicked.connect(self.open)
        self.saveButton = QPushButton("Save Database")
        # self.saveButton.setEnabled(not self.fileManager.filePath == None)
        self.saveButton.clicked.connect(self.save)
        self.saveAsButton = QPushButton("Save Database As")
        self.saveAsButton.clicked.connect(self.saveAs)
        
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.openButton)
        hlayout.addWidget(self.saveButton)
        hlayout.addWidget(self.saveAsButton)

        hline = newHLine(1)

        self.dbFileLabel = QLabel()
        self.setFileLabel()

        # Create a layout for the main window
        layout = QVBoxLayout(self)
        layout.addWidget(self.tab_widget)
        layout.addWidget(hline)
        layout.addLayout(hlayout)
        layout.addWidget(self.dbFileLabel)

        # Set the layout for the main window
        self.setLayout(layout)
    
    def setFileLabel(self):
        # self.dbFileLabel.setText(f"File: {self.fileManager.filePath}")
        self.dbFileLabel.setText(f"File: TODO")

    def open(self):
        self.openButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.saveAsButton.setEnabled(False)
        dbFile  = QFileDialog.getOpenFileName(self, "Open Database", os.path.expanduser("~"), "Database (*.db)")
        # if not dbFile[0] == "":
        #     if self.fileManager.setFile(dbFile[0]):
        #         self.fileManager.loadFile()
        QMessageBox.information(self, "TODO", "Feature not yet implemented!")
        self.setFileLabel()
        self.openButton.setEnabled(True)
        # self.saveButton.setEnabled(not self.fileManager.filePath == None)
        self.saveButton.setEnabled(True)
        self.saveAsButton.setEnabled(True)
    
    def save(self):
        # assert(not self.fileManager.filePath == None)
        # self.fileManager.saveFile()
        # QMessageBox.information(self, "Success", "Save successful!")
        QMessageBox.information(self, "TODO", "Feature not yet implemented!")


    def saveAs(self):
        self.openButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.saveAsButton.setEnabled(False)
        dbFile  = QFileDialog.getSaveFileName(self, "Save Database As", os.path.expanduser("~"), "Database (*.db)")
        # if not dbFile[0] == "":
        #     if self.fileManager.setFile(dbFile[0]):
        #         self.fileManager.saveFile()
        QMessageBox.information(self, "TODO", "Feature not yet implemented!")
        self.setFileLabel()
        self.openButton.setEnabled(True)
        # self.saveButton.setEnabled(not self.fileManager.filePath == None)
        self.saveButton.setEnabled(True)
        self.saveAsButton.setEnabled(True)
