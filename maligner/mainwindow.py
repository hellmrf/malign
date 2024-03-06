import sys, os
from pathlib import Path
from typing import Optional

from rdkit import Chem
from PySide6 import QtGui, QtWidgets

from maligner.widgets.molEditWidget import MolEditWidget
from maligner.widgets.substructure_selector import SubstructureSelectorDialog


class MainWindow(QtWidgets.QMainWindow):
    # Constructor function
    def __init__(self, filename: Optional[Path | str] = None, loglevel="WARNING"):
        super(MainWindow, self).__init__()
        self.loglevels = ["Critical", "Error", "Warning", "Info", "Debug", "Notset"]
        self.editor = MolEditWidget()
        self.substructure_selector = SubstructureSelectorDialog(filename=filename)
        self._filename = filename
        self.initGUI()
        # TODO: selectionChanges ainda não existe
        # self.substructure_selector.selectionChanged.connect(self.setAtomTypeName)
        self.editor.logger.setLevel(loglevel)

    def get_pixmap(self, name: str) -> str:
        p = Path(__file__).parent / 'pixmaps' / name
        return QtGui.QPixmap(p)

    #Properties
    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename):
        if filename != self._filename:
            self._filename = filename
            self.setWindowTitle(str(filename))

    def initGUI(self):
        self.setWindowTitle(r"maligner |\ An Open-Source Molecular Alignment Tool")
        self.setWindowIcon(QtGui.QIcon(self.get_pixmap("appicon.svg.png")))
        self.setGeometry(400, 400, 200, 150)

        # self.center = self.editor
        # self.center.setFixedSize(600, 600)
        # self.setCentralWidget(self.center)

        self.filters = "MOL Files (*.mol *.mol);;Any File (*)"
        self.SetupComponents()

        self.infobar = QtWidgets.QLabel("")
        self.myStatusBar.addPermanentWidget(self.infobar, 0)

        if self.filename is not None:
            self.editor.logger.info("Loading model from %s" % self.filename)
            self.loadMolFile(self.filename)

        self.editor.sanitizeSignal.connect(self.infobar.setText)
        self.show()

    # Function to setup status bar, central widget, menu bar, tool bar
    def SetupComponents(self):
        self.myStatusBar = QtWidgets.QStatusBar()
        #        self.molcounter = QtWidgets.QLabel("-/-")
        #        self.myStatusBar.addPermanentWidget(self.molcounter, 0)
        self.setStatusBar(self.myStatusBar)
        self.myStatusBar.showMessage('Ready', 10000)

        self.CreateActions()
        self.CreateMenus()
        self.CreateToolBars()

    # Actual menu bar item creation
    def CreateMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.toolMenu = self.menuBar().addMenu("&Tools")
        self.helpMenu = self.menuBar().addMenu("&Help")

        # File
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)

        # Tools
        self.toolMenu.addAction(self.anchorAction)
        self.toolMenu.addAction(self.deleteMoleculeAction)
        self.toolMenu.addAction(self.openSelectorAction)

        #Help menu
        self.helpMenu.addAction(self.aboutAction)
        self.helpMenu.addAction(self.aboutQtAction)
        #Debug level sub menu
        self.loglevelMenu = self.helpMenu.addMenu("Logging Level")
        for loglevel in self.loglevels:
            self.loglevelMenu.addAction(self.loglevelactions[loglevel])

    def CreateToolBars(self):
        self.mainToolBar = self.addToolBar('Main')
        #Main action bar
        self.mainToolBar.addAction(self.openAction)
        self.mainToolBar.addAction(self.saveAction)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.anchorAction)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.deleteMoleculeAction)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.openSelectorAction)

    def loadMolFile(self, filename):
        self.filename = filename
        mol = Chem.MolFromMolFile(str(self.filename), sanitize=False, strictParsing=False)
        self.editor.mol = mol
        self.statusBar().showMessage("File opened")

    def openFile(self):
        self.filename, self.filterName = QtWidgets.QFileDialog.getOpenFileName(
            self, caption="Open MOL file", filter=self.filters)
        self.loadMolFile(self.filename)

    def saveFile(self):
        if self.filename != None:
            Chem.MolToMolFile(self.editor.mol, str(self.filename))
        else:
            self.saveAsFile()

    def saveAsFile(self):
        self.filename, self.filterName = QtWidgets.QFileDialog.getSaveFileName(self,
                                                                               filter=self.filters)
        if (self.filename != ''):
            if self.filename[-4:].upper() != ".MOL":
                self.filename = self.filename + ".mol"
            Chem.MolToMolFile(self.editor.mol, str(self.filename))
            #            file = open(self.fileName, 'w')
            #            file.write(self.textEdit.toPlainText())
            self.statusBar().showMessage("File saved", 2000)

    def open_selector(self):
        self.substructure_selector.show()

    def clearCanvas(self):
        self.editor.mol = None
        self.filename = None
        self.exitFile()
        self.statusBar().showMessage("Molecule removed from canvas", 2000)

    def closeEvent(self, event):
        self.exitFile()
        event.ignore()

    def exitFile(self):
        self.substructure_selector.close()
        exit(0)  #TODO, how to exit QtWidgets.QApplication from within class instance?

    def aboutHelp(self):
        QtWidgets.QMessageBox.about(
            self, "About maligner",
            """maligner is an Open-Source Molecular Alignment Tool.\n\n\nBased on RDKit: http://www.rdkit.org/\nBased on rdeditor: https://github.com/EBjerrum/rdeditor\nSome icons from: http://icons8.com\nSource code: https://github.com/hellmrf/maligner\n\nReleased under GPL-v3.0."""
        )

    def setAction(self):
        sender = self.sender()
        self.editor.setAction(sender.objectName())
        self.myStatusBar.showMessage("Action %s selected" % sender.objectName())

    def setBondType(self):
        sender = self.sender()
        self.editor.setBondType(sender.objectName())
        self.myStatusBar.showMessage("Bondtype %s selected" % sender.objectName())

    def setAtomType(self):
        sender = self.sender()
        self.editor.setAtomType(sender.objectName())
        self.myStatusBar.showMessage("Atomtype %s selected" % sender.objectName())

    def setAtomTypeName(self, atomname):
        self.editor.setAtomType(str(atomname))
        self.myStatusBar.showMessage("Atomtype %s selected" % atomname)

    # TODO: set_anchor ainda não existe
    def set_anchor(self):
        raise NotImplementedError("")

    def openSubsSelector(self):
        self.substructure_selector.show()

    def setLogLevel(self):
        loglevel = self.sender().objectName().split(':')[-1].upper()
        self.editor.logger.setLevel(loglevel)

    # Function to create actions for menus and toolbars
    def CreateActions(self):
        self.openAction = QtGui.QAction(QtGui.QIcon(self.get_pixmap("open.png")),
                                        'O&pen',
                                        self,
                                        shortcut=QtGui.QKeySequence.Open,
                                        statusTip="Open an existing file",
                                        triggered=self.openFile)

        self.saveAction = QtGui.QAction(QtGui.QIcon(self.get_pixmap("icons8-Save.png")),
                                        'S&ave',
                                        self,
                                        shortcut=QtGui.QKeySequence.Save,
                                        statusTip="Save file",
                                        triggered=self.saveFile)

        self.exitAction = QtGui.QAction(QtGui.QIcon(self.get_pixmap("icons8-Shutdown.png")),
                                        'E&xit',
                                        self,
                                        shortcut="Ctrl+Q",
                                        statusTip="Exit the Application",
                                        triggered=self.exitFile)

        self.aboutAction = QtGui.QAction(QtGui.QIcon(self.get_pixmap("about.png")),
                                         'A&bout',
                                         self,
                                         statusTip="Displays info about text editor",
                                         triggered=self.aboutHelp)

        self.aboutQtAction = QtGui.QAction("About &Qt",
                                           self,
                                           statusTip="Show the Qt library's About box",
                                           triggered=QtWidgets.QApplication.aboutQt)

        #Misc Actions
        self.deleteMoleculeAction = QtGui.QAction(
            QtGui.QIcon(self.get_pixmap("icons8-Trash.png")),
            'Delete &X',
            self,
            shortcut="Ctrl+X",
            statusTip="Remove this molecule from canvas Ctrl+X",
            triggered=self.clearCanvas,
            objectName="Clear Canvas")

        self.anchorAction = QtGui.QAction(
            QtGui.QIcon(self.get_pixmap('icons8-Anchor.png')),
            'Anchor current molecule &A',
            self,
            shortcut="A",
            statusTip="Set the selected molecule as the anchor for the alignment. (A)",
            triggered=self.set_anchor,
            objectName="Set Anchor")

        self.openSelectorAction = QtGui.QAction(
            QtGui.QIcon(self.get_pixmap('icons8-Molecule.png')),
            'Open Selector',
            self,
            shortcut="S",
            statusTip="Opens the molecule selector for some molecule",
            triggered=self.open_selector,
            objectName="Open selector")

        self.loglevelactions = {}
        for key in self.loglevels:
            self.loglevelactions[key] = QtGui.QAction(key,
                                                      self,
                                                      statusTip="Set logging level to %s" % key,
                                                      triggered=self.setLogLevel,
                                                      objectName="loglevel:%s" % key)
        self.loglevelactions["Debug"].setChecked(True)


def launch(loglevel="WARNING"):
    "Function that launches the mainWindow Application"
    myApp = QtWidgets.QApplication(sys.argv)
    argv1 = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if argv1 and argv1.is_file():
        mainWindow = MainWindow(filename=argv1, loglevel=loglevel)
    else:
        mainWindow = MainWindow(filename=None, loglevel=loglevel)
    sys.exit(myApp.exec())


if __name__ == '__main__':
    launch(loglevel="DEBUG")
