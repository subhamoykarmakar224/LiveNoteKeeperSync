from PyQt4.QtGui import *
from PyQt4.QtCore import *
import Configuration as cfg
import datetime, calendar, threading, time, uuid
import ExcelDBOps as dbop
import FirebaseConn as fb


class MainWindowApplication(QMainWindow):
    def __init__(self):
        super(MainWindowApplication, self).__init__()
        self.setUpDBDaemon()
        self.initUi()
        self.currentWorkingDate = ''

    def setUpDBDaemon(self):
        self.thread_stop_flag = True
        self.t = threading.Thread(target=self.setUpDBDaemonLooper, args=())
        self.t.daemon = True
        self.t.start()

    def setUpDBDaemonLooper(self):
        while self.thread_stop_flag:
            # try:
            self.R()
            time.sleep(5)
            # except:
            #     print("Error in daemon.")

    def R(self):
        try:
            nFB_res_data = fb.getAllDataCount()
        except:
            return
        nDB = dbop.getAllDataCount()
        if nDB == 0 and len(nFB_res_data.keys()) > 0:
            dbop.justInsert(nFB_res_data)
            self.fillDataIntoTable()
        elif nDB > 0 and nFB_res_data is None:
            res = dbop.getAllData()
            for k in res.keys():
                data = {
                    "note": str(res[k][0]),
                    "datestamp": str(res[k][1]),
                    "hashval": str(res[k][2]),
                    "lastchanged": str(res[k][3])
                }
                try:
                    newId = fb.insertData(data)
                except:
                    return
                dbop.updateNoteID(str(k), str(newId['name']))
            self.fillDataIntoTable()
        else:
            resFb = nFB_res_data
            resDb = dbop.getAllData()

            # Local Deleted Elements
            for k in resDb:
                if resDb[k][2] == 'delete':
                    try:
                        fb.deleteNote(str(k), "")
                    except:
                        continue
                    dbop.finalDelete(k)

            # Check if the matching ID's hash is same and then if the local lastChanged > firebase lastChanged
            for k in resDb:
                try:
                    h = (resFb[k]['hashval'])
                except:
                    data = {
                        "note": str(resDb[k][0]),
                        "datestamp": str(resDb[k][1]),
                        "hashval": str(resDb[k][2]),
                        "lastchanged": str(resDb[k][3])
                    }
                    try:
                        newId = fb.insertData(data)
                    except:
                        return
                    dbop.updateNoteID(str(k), str(newId['name']))

            for k in resDb:
                if str(resDb[k][2]) != str(resFb[k]['hashval']):
                    localTimeTMP = resDb[k][3]
                    if localTimeTMP.__contains__("."):
                        localTimeTMP = localTimeTMP[:localTimeTMP.index('.')]
                    orginTimeTMP = resFb[k]['lastchanged']
                    if orginTimeTMP.__contains__("."):
                        orginTimeTMP = orginTimeTMP[:orginTimeTMP.index('.')]

                    if localTimeTMP > orginTimeTMP:
                        # print("Local id better...")
                        fb.editNode(
                            str(k),
                            str(resDb[k][1]),
                            str(resDb[k][2]),
                            str(resDb[k][3])
                        )
                    elif localTimeTMP < orginTimeTMP:
                        # print("FB id better...")
                        dbop.updateDataAsPerId(
                            str(k),
                            resFb[k]['note'],
                            resFb[k]['lastchanged']
                        )
                    else:
                        pass
                        # print("Both OK")
            self.fillDataIntoTable()

    def initUi(self):
        self.setWindowTitle(cfg.APPLICATION_TITLE)
        self.setMinimumSize(800, 650)
        self.setWindowIcon(QIcon('./src/icon_notes.png'))
        # self.setWindowFlags(Qt.FramelessWindowHint)

        self.gLayout = QVBoxLayout()

        # set Header UI
        self.uiHeader()
        self.uiTableBody()
        self.uiBottom()

        # sub layouts

        # Sub layout Prop

        # Widgets

        # Widget Props

        # Add to sub layout

        # Add to main layout

        # setting central widget
        mainVLayoutWidget = QWidget()
        mainVLayoutWidget.setLayout(self.gLayout)
        self.setCentralWidget(mainVLayoutWidget)

        self.showMaximized()
        self.show()

    def uiHeader(self):
        self.hlayoutHeader = QGridLayout()

        # sub layouts

        # Sub layout Prop

        # Widgets
        self.labelDayOfWeekAndDate = QLabel()
        self.labelMonth = QLabel()
        self.labelNoOfTasks = QLabel()
        self.btnDateSelecter = QLabel("<html><img src='./src/icon_down_arrow.png' width='32' height='32'></html>")

        # Widget Props
        self.labelDayOfWeekAndDate.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.labelDayOfWeekAndDate.setStyleSheet("font-size: 30px;")
        self.labelMonth.setStyleSheet("font-size: 15px;")
        self.labelNoOfTasks.setAlignment(Qt.AlignRight)
        self.btnDateSelecter.setAlignment(Qt.AlignLeft)
        self.btnDateSelecter.setToolTip("Date picker")

        # Add to sub layout

        # Add to main layout
        self.hlayoutHeader.addWidget(self.labelDayOfWeekAndDate, 0, 0)
        self.hlayoutHeader.addWidget(self.labelMonth, 1, 0)
        self.hlayoutHeader.addWidget(self.btnDateSelecter, 0, 1)
        self.hlayoutHeader.addWidget(self.labelNoOfTasks, 0, 2, 2, 1)

        # Listener
        self.btnDateSelecter.mousePressEvent = self.clickSelectDate

        # Initialize Texts
        today = datetime.date.today()
        self.currentWorkingDate = today
        noOfTasks = 0
        self.setHeaderLabelValues(today, noOfTasks)

        # default values
        self.gLayout.addLayout(self.hlayoutHeader)

    def setHeaderLabelValues(self, today, noOfTasks):
        self.labelDayOfWeekAndDate.setText(calendar.day_name[today.weekday()] + ", " + str(today.day))
        self.labelMonth.setText(str(calendar.month_name[today.month]) + ", " + str(today.year))
        self.labelNoOfTasks.setText(str(noOfTasks) + " Notes")

    def clickSelectDate(self, e):
        self.selectDateDialog = QDialog()
        self.vbox = QVBoxLayout()

        self.calenderWidget = QCalendarWidget()
        self.btnDone = QPushButton("Done")

        self.calenderWidget.setGridVisible(True)

        self.vbox.addWidget(self.calenderWidget)
        self.vbox.addWidget(self.btnDone)

        self.selectDateDialog.setLayout(self.vbox)

        self.btnDone.clicked.connect(self.loadDate)
        self.selectDateDialog.exec_()

    def loadDate(self):
        ca = self.calenderWidget.selectedDate()
        y = ca.year()
        m = ca.month()
        d = ca.day()
        self.selectDateDialog.close()
        self.setHeaderLabelValues(datetime.date(y, m, d), 0)
        self.fillDataIntoTable()

    def uiTableBody(self):

        # sub layouts

        # Sub layout Prop

        # Widgets
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Id", "Date", "Time", "Note"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setRowHeight(100, 100)

        # Widget Props

        # Add to sub layout

        # Add to main layout
        self.gLayout.addWidget(self.table)

        # Listener

        # Initialize Texts

        # default values
        self.fillDataIntoTable()

    def fillDataIntoTable(self):
        d = str(self.labelDayOfWeekAndDate.text()).split(" ")[1]
        tmp = str(self.labelMonth.text()).split(", ")
        y = tmp[1]
        m = datetime.datetime.strptime(tmp[0], "%B")
        m = m.month
        if len(str(m)) == 1:
            m = "0" + str(m)

        if len(str(d)) == 1:
            d = "0" + str(d)

        tmpDate = y + '-' + m + '-' + d
        data = dbop.getDataAsPerDate(str(tmpDate))
        n = len(data.keys())
        self.table.clearContents()
        self.labelNoOfTasks.setText(str(n) + " Tasks")
        self.table.setRowCount(n)
        cnt = 0
        for k in data.keys():
            hashVal = data[k][2]
            if hashVal != 'delete':
                timeStampTmp = data[k][1].split(" ")
                self.table.setItem(cnt, 0, QTableWidgetItem(k))
                self.table.setItem(cnt, 1, QTableWidgetItem(timeStampTmp[0]))
                self.table.setItem(cnt, 2, QTableWidgetItem(timeStampTmp[1]))
                self.table.setItem(cnt, 3, QTableWidgetItem(data[k][0]))
                cnt += 1

    def uiBottom(self):
        # sub layouts
        self.hboxLayoutButtons = QHBoxLayout()

        # Sub layout Prop
        self.hboxLayoutButtons.setAlignment(Qt.AlignRight)

        # Widgets
        self.btnAddNote = QLabel("<html><img src='./src/icon_add.png' width='32' height='32'></html>")
        self.btnEditNote = QLabel("<html><img src='./src/icon_edit.png' width='32' height='32'></html>")
        self.btnDeleteNote = QLabel("<html><img src='./src/icon_delete.png' width='32' height='32'></html>")

        # Widget Props
        self.btnAddNote.setToolTip("Add New Note...")
        self.btnEditNote.setToolTip("Edit Note...")
        self.btnDeleteNote.setToolTip("Delete Note...")

        # Add to sub layout
        self.hboxLayoutButtons.addWidget(self.btnAddNote)
        self.hboxLayoutButtons.addWidget(self.btnEditNote)
        self.hboxLayoutButtons.addWidget(self.btnDeleteNote)

        # Add to main layout
        self.gLayout.addLayout(self.hboxLayoutButtons)

        # Listener
        self.btnAddNote.mousePressEvent = self.clickAddNewNote
        self.btnEditNote.mousePressEvent = self.clickEditNote
        self.btnDeleteNote.mousePressEvent = self.clickDeleteNote

        # Initialize Texts

        # default values

    def clickAddNewNote(self, e):
        d = str(self.labelDayOfWeekAndDate.text()).split(" ")[1]
        tmp = str(self.labelMonth.text()).split(", ")
        y = tmp[1]
        m = datetime.datetime.strptime(tmp[0], "%B")
        m = m.month
        if len(str(m)) == 1:
            m = "0" + str(m)

        if len(str(d)) == 1:
            d = "0" + str(d)

        if datetime.date(int(y), int(m), int(d)) < datetime.date.today():
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("You cannot add new item to older dates.")
            msg.exec_()
            return
        else:
            self.addNoteDialog = QDialog()
            self.addNoteDialog.setWindowTitle("+Add Note")
            self.addNoteDialog.setWindowIcon(QIcon("./src/icon_notes.png"))
            self.addNoteDialog.setFixedSize(500, 300)

            self.editText = QTextEdit()
            self.btnSave = QPushButton("Save")
            self.btnCancel = QPushButton("Cancel")

            grid = QGridLayout()

            grid.addWidget(QLabel("Note"), 0, 0)
            grid.addWidget(self.editText, 1, 0, 1, 3)
            grid.addWidget(self.btnSave, 2, 1)
            grid.addWidget(self.btnCancel, 2, 2)

            self.addNoteDialog.setLayout(grid)

            self.btnSave.clicked.connect(self.saveNewNote)
            self.btnCancel.clicked.connect(lambda: self.addNoteDialog.close())

            self.addNoteDialog.exec_()

    def saveNewNote(self):
        id= ''
        timestamp = datetime.datetime.now()
        data = {
            "note": str(self.editText.toPlainText()),
            "datestamp": str(timestamp),
            "hashval": hash(str(timestamp)),
            "lastchanged": str(timestamp)
        }
        try:
            id = fb.insertData(data)
        except:
            msg = QMessageBox()
            msg.setWindowTitle("Error!")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("You are not connected to internet. Please connect for a better experience.")
            msg.exec_()

        if id == '':
            id = uuid.uuid1()

        dbop.insertDatSQL(id, str(self.editText.toPlainText()), str(timestamp))
        today = datetime.date.today()
        self.currentWorkingDate = today
        self.fillDataIntoTable()
        self.addNoteDialog.close()

        msg = QMessageBox()
        msg.setWindowTitle("Done!")
        msg.setText("New Note Saved.")
        msg.exec_()

    def clickEditNote(self, e):
        index = self.table.selectionModel().currentIndex()
        tmpNote = index.sibling(index.row(), 3).data()
        # tmpTimeStamp = index.sibling(index.row(), 1).data() + " " + index.sibling(index.row(), 2).data()
        tmpId = index.sibling(index.row(), 0).data()

        if tmpId is None:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("There are not items in this date for you to edit or you have not yet selected any note. "
                        "Please select a note you want to edit and try again")
            msg.exec_()
            return
        else:
            self.editNoteDialog = QDialog()
            self.editNoteDialog.setWindowTitle("Edit Note")
            self.editNoteDialog.setWindowIcon(QIcon("./src/icon_notes.png"))
            self.editNoteDialog.setFixedSize(500, 300)

            self.editText = QTextEdit()
            self.btnEditSave = QPushButton("Save")
            self.btnCancel = QPushButton("Cancel")

            self.editText.setText(tmpNote)

            grid = QGridLayout()

            grid.addWidget(QLabel("Note"), 0, 0)
            grid.addWidget(self.editText, 1, 0, 1, 3)
            grid.addWidget(self.btnEditSave, 2, 1)
            grid.addWidget(self.btnCancel, 2, 2)

            self.editNoteDialog.setLayout(grid)

            self.btnEditSave.clicked.connect(lambda : self.saveEditNote(tmpId))
            self.btnCancel.clicked.connect(lambda: self.editNoteDialog.close())

            self.editNoteDialog.exec_()

    def saveEditNote(self, id):
        dm = datetime.datetime.now()
        try:
            fb.editNode(id, self.editText.toPlainText(), hash(str(dm), str(dm)))
        except:
            msg = QMessageBox()
            msg.setWindowTitle("Error!")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("You are not connected to internet. Please connect for a better experience.")
            msg.exec_()

        dbop.updateDataAsPerId(id, self.editText.toPlainText(), dm)
        self.editNoteDialog.close()

        msg = QMessageBox()
        msg.setWindowTitle("Done!")
        msg.setText("Note has been updated.")
        msg.exec_()

        self.fillDataIntoTable()

    def clickDeleteNote(self, e):
        index = self.table.selectionModel().currentIndex()
        tmpId = index.sibling(index.row(), 0).data()
        print(tmpId)
        if tmpId is None or tmpId == '':
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("You cannot add new item to older dates.")
            msg.exec_()
            return
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Delete!")
            msg.setIcon(QMessageBox.Information)
            msg.setText("Are you sure you want to delete this note?")
            msg.addButton(QMessageBox.Yes)
            msg.addButton(QMessageBox.No)
            res = msg.exec_()
            if res == QMessageBox.Yes:
                dm = str(datetime.datetime.now())
                try:
                    fb.deleteNote(tmpId, dm)
                except:
                    msg = QMessageBox()
                    msg.setWindowTitle("Error")
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("You are not connected to the internet. Please connect to internet for a better experience.")
                    msg.exec_()

                dbop.deleteNoteById(tmpId, dm)
                msg = QMessageBox()
                msg.setWindowTitle("Done!")
                msg.setText("Note has been deleted.")
                msg.exec_()
                self.fillDataIntoTable()

    def close(self):
        self.thread_stop_flag = False
