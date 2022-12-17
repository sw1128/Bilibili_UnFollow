import json
import requests
from PyQt5.QtGui import QPixmap, QImage
from MainWindow import MainWindow
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QCheckBox
from PyQt5 import QtCore, QtWidgets

global cookie, userid, tagData, tableData, tagid, page

class Main(QMainWindow, MainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.setupUi(self)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.pushButton.clicked.connect(self.unFollow)
        self.pushButton_2.clicked.connect(self.getUPs)
        self.pushButton_3.clicked.connect(self.getTags)
        self.pushButton_4.clicked.connect(self.allCheck)
        self.pushButton_5.clicked.connect(self.allNotCheck)
        self.pushButton_6.clicked.connect(self.nextPage)
        self.pushButton_7.clicked.connect(self.prePage)
        self.treeWidget.itemDoubleClicked.connect(self.getUPs)

    def getFace(self):
        global cookie, userid
        url = 'https://api.bilibili.com/x/space/myinfo?jsonp=jsonp&callback=__jp0'
        headers = {
            'cookie': cookie,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
            'referer': f'https://space.bilibili.com/{userid}/fans/follow'
        }
        response = requests.get(url, headers=headers).text
        res = response.split('"face":"')[1].split('","')[0]
        FaceImg = requests.get(res)
        img = QImage.fromData(FaceImg.content)
        img = img.scaled(self.label_5.width(), self.label_5.height())
        self.label_5.setPixmap(QPixmap.fromImage(img))

    def getTags(self):
        global cookie, userid, tagData
        self.treeWidget.clear()
        try:
            cookie = self.lineEdit.text()
            if cookie == '':
                QMessageBox.information(self, '提示', '请先输入cookie')
                return
            userid = cookie.split('DedeUserID=')[1].split(';')[0]
            url = 'https://api.bilibili.com/x/relation/tags?jsonp=jsonp&callback=__jp2'
            headers = {
                'cookie': cookie,
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
                'referer': f'https://space.bilibili.com/{userid}/fans/follow'
            }
            response = requests.get(url, headers=headers).text
            res = response.split('[')[1].split(']')[0]
            res = '[' + res + ']'
            res.replace('null', 'None')
            tagData = json.loads(res)
            for i in tagData:
                self.treeWidget.addTopLevelItem(QtWidgets.QTreeWidgetItem([i["name"]]))
            self.getFace()
        except:
            QMessageBox.information(self, '提示', '获取分组失败，请检查cookie是否正确')

    def getUPs(self):
        global cookie, userid, tagData, tableData, tagid, page
        if self.treeWidget.currentItem() is None:
            QMessageBox.information(self, '提示', '请先选择分组')
            return
        tagid, page = 0, 1
        for t in tagData:
            if t['name'] == self.treeWidget.currentItem().text(0):
                tagid = t['tagid']
                break
        url = 'https://api.bilibili.com/x/relation/tag'
        headers = {
            'cookie': cookie,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
            'referer': f'https://space.bilibili.com/{userid}/fans/follow?tagid=0'
        }
        _datas = {
            'tagid': tagid,
            'pn': page,
            'ps': 50,
        }
        response = requests.get(url, headers=headers, params=_datas)
        response = response.text
        res = response.split('[')[1].split(']')[0]
        res = '[' + res + ']'
        res.replace('null', 'None')
        res = json.loads(res)
        tableData = []
        if res:
            for r in res:
                tableData.append([r['uname'], str(r['mid'])])
        self.tableWidget.setRowCount(len(tableData))
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setColumnWidth(0, 30)
        self.tableWidget.setColumnWidth(1, 90)
        self.tableWidget.setColumnWidth(2, 82)
        self.tableWidget.setHorizontalHeaderLabels(['', '用户名', 'UID'])
        self.tableWidget.verticalHeader().setVisible(False)
        for i in range(len(tableData)):
            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem())
            self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(tableData[i][0]))
            self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(tableData[i][1]))
        for i in range(len(tableData)):
            checkBox = QCheckBox()
            checkBox.setStyleSheet("margin-left: 10px;")
            checkBox.setCheckState(Qt.Unchecked)
            self.tableWidget.setCellWidget(i, 0, checkBox)
        self.pushButton.setEnabled(True)
        self.pushButton_4.setEnabled(True)
        self.pushButton_5.setEnabled(True)
        self.pushButton_6.setEnabled(True)
        self.pushButton_7.setEnabled(True)

    def allCheck(self):
        for i in range(self.tableWidget.rowCount()):
            checkBox = self.tableWidget.cellWidget(i, 0)
            checkBox.setCheckState(Qt.Checked)

    def allNotCheck(self):
        for i in range(self.tableWidget.rowCount()):
            checkBox = self.tableWidget.cellWidget(i, 0)
            checkBox.setCheckState(Qt.Unchecked)

    def unFollow(self):
        try:
            csrf = cookie.split('bili_jct=')[1].split(';')[0]
            checkList = []
            for i in range(self.tableWidget.rowCount()):
                checkBox = self.tableWidget.cellWidget(i, 0)
                if checkBox.checkState() == Qt.Checked:
                    checkList.append(self.tableWidget.item(i, 2).text())
            if checkList:
                reply = QMessageBox.question(self, '提示', '是否确认取消关注？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    for mid in checkList:
                        url = 'https://api.bilibili.com/x/relation/modify'
                        headers = {
                            'cookie': cookie,
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
                        }
                        _datas = {
                            'fid': mid,
                            'act': '2',
                            're_src': '11',
                            'csrf': csrf,
                            'extend_content': {
                                "entity": "user",
                                "entity_id": mid,
                            },
                        }
                        requests.post(url, headers=headers, data=_datas)
                    QMessageBox.information(self, '提示', '一键取消关注成功！')
                    self.getUPs()
            else:
                QMessageBox.information(self, '提示', '请选择要取消关注的UP')
        except:
            QMessageBox.information(self, '提示', '取消关注失败，请检查cookie是否正确')

    def nextPage(self):
        global page
        if self.tableWidget.rowCount() < 50:
            QMessageBox.information(self, '提示', '已经是最后一页了')
        else:
            try:
                page += 1
                url = 'https://api.bilibili.com/x/relation/tag'
                headers = {
                    'cookie': cookie,
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
                    'referer': f'https://space.bilibili.com/{userid}/fans/follow?tagid=0'
                }
                _datas = {
                    'tagid': tagid,
                    'pn': page,
                    'ps': 50,
                }
                response = requests.get(url, headers=headers, params=_datas)
                response = response.text
                res = response.split('[')[1].split(']')[0]
                res = '[' + res + ']'
                res.replace('null', 'None')
                res = json.loads(res)
                tableData = []
                if res:
                    for r in res:
                        tableData.append([r['uname'], str(r['mid'])])
                self.tableWidget.setRowCount(len(tableData))
                self.tableWidget.setColumnCount(3)
                self.tableWidget.setColumnWidth(0, 30)
                self.tableWidget.setColumnWidth(1, 90)
                self.tableWidget.setColumnWidth(2, 82)
                self.tableWidget.setHorizontalHeaderLabels(['', '用户名', 'UID'])
                self.tableWidget.verticalHeader().setVisible(False)
                for i in range(len(tableData)):
                    self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem())
                    self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(tableData[i][0]))
                    self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(tableData[i][1]))
                for i in range(len(tableData)):
                    checkBox = QCheckBox()
                    checkBox.setStyleSheet("margin-left: 10px;")
                    checkBox.setCheckState(Qt.Unchecked)
                    self.tableWidget.setCellWidget(i, 0, checkBox)
            except:
                QMessageBox.information(self, '提示', '获取数据失败，请检查cookie是否正确')

    def prePage(self):
        global page
        if page == 1:
            QMessageBox.information(self, '提示', '已经是第一页了')
        else:
            page -= 1
            url = 'https://api.bilibili.com/x/relation/tag'
            headers = {
                'cookie': cookie,
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
                'referer': f'https://space.bilibili.com/{userid}/fans/follow?tagid=0'
            }
            _datas = {
                'tagid': tagid,
                'pn': page,
                'ps': 50,
            }
            response = requests.get(url, headers=headers, params=_datas)
            response = response.text
            res = response.split('[')[1].split(']')[0]
            res = '[' + res + ']'
            res.replace('null', 'None')
            res = json.loads(res)
            tableData = []
            if res:
                for r in res:
                    tableData.append([r['uname'], str(r['mid'])])
            self.tableWidget.setRowCount(len(tableData))
            self.tableWidget.setColumnCount(3)
            self.tableWidget.setColumnWidth(0, 30)
            self.tableWidget.setColumnWidth(1, 90)
            self.tableWidget.setColumnWidth(2, 82)
            self.tableWidget.setHorizontalHeaderLabels(['', '用户名', 'UID'])
            self.tableWidget.verticalHeader().setVisible(False)
            for i in range(len(tableData)):
                self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem())
                self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(tableData[i][0]))
                self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(tableData[i][1]))
            for i in range(len(tableData)):
                checkBox = QCheckBox()
                checkBox.setStyleSheet("margin-left: 10px;")
                checkBox.setCheckState(Qt.Unchecked)
                self.tableWidget.setCellWidget(i, 0, checkBox)

if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())
