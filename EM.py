import wmi, requests, threading, speedtest, sys
from scapy.arch.windows import *
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from GUI import Ui_MainWindow


internet = {}  # Данные о вашем интернете
portiki = []
speed = ('None', 'None', 'None')
text = ['   FireWall: ', '   Приватная сеть: ',
        '   Общедоступная или гостевая сеть: ',
        '   Локальный IPv4: ', '   Шлюз IPv4: ']


# GUI
class Mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.view_p)
        self.ui.pushButton_2.clicked.connect(self.view_s)

    def view_p(self):
        global portiki

        if portiki:
            portiki = []

        self.ui.textBrowser_2.clear()
        self.ui.pushButton.setEnabled(False)

        s = threading.Thread(target=ports, args=(self.ui.comboBox.currentText(), self.ui))
        s.start()


    def view_s(self):
        self.ui.pushButton_2.setEnabled(False)

        s = threading.Thread(target=check_speed, args=(self.ui, ))
        s.start()


# Сканнер портов (2)
def scan_port(ip, port):
    global portiki

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)

    try:
        sock.connect((ip, port))
        portiki.append(str(port))
        sock.close()
    except:
        pass


# Сканнер портов (1)
def ports(ip, ui):
    for i in range(1, 65536):
        potoc = threading.Thread(target=scan_port, args=(ip, i))
        potoc.start()

    if portiki:
        for k in portiki:
            ui.textBrowser_2.insertPlainText(k + '\n')

    ui.pushButton.setEnabled(True)


# Получение собственного IP
def get_ip():
    global internet

    wmi_obj = wmi.WMI()
    wmi_sql = 'select IPAddress,DefaultIPGateway from win32_NetworkAdapterConfiguration where IPEnabled=TRUE'
    wmi_out = wmi_obj.query(wmi_sql)

    for dev in wmi_out:
        for key in internet.keys():
            if internet[key][-1] == str(dev.IPAddress[0]):
                internet[key].append(str(dev.DefaultIPGateway[0]))


# Проверка брандмауэра
def bm():
    global internet

    c = wmi.WMI(namespace="root/Microsoft/HomeNet")
    interf = get_windows_if_list()
    br_m = {}

    for obj in c.HNet_ConnectionProperties():
        if obj.IsFirewalled:
            fi = 'Вкл.'
        else:
            fi = 'Вык.'
        if obj.IsIcsPrivate:
            pr = 'Вкл.'
        else:
            pr = 'Вык.'
        if obj.IsIcsPublic:
            pu = 'Вкл.'
        else:
            pu = 'Вык.'

        br_m[f'{obj.connection[22:60]}'] = [fi, pr, pu]

    for d1 in interf:
        for d2 in br_m.keys():
            if d1['guid'] == d2:
                internet[d1['name']] = br_m[d2]

                if d1['ips']:
                    internet[d1['name']].append(d1['ips'][-1])


# Проверка работы интернета
def check_internet():
    url = 'http://www.google.com/'
    timeout = 5

    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        return False


# Speedtest
def check_speed(ui):
    test = speedtest.Speedtest()
    download = str(round(test.download()/1024/1024/8, 2))
    upload = str(round(test.upload()/1024/1024/8, 2))
    ping = str(int(test.results.ping))

    ui.label_6.setText('Скорость скачки: ' + download + ' Mb/s.')
    ui.label_7.setText('Скорость загрузки: ' + upload + ' Mb/s.')
    ui.label_8.setText('Ping: ' + ping + ' ms.')

    ui.pushButton_2.setEnabled(True)


if __name__ == '__main__':
    bm()
    get_ip()

    app = QtWidgets.QApplication([])
    application = Mywindow()
    application.setFixedSize(application.size())
    application.setWindowTitle('Ethernet Master')
    application.setWindowIcon(QIcon('network_error.png'))

    if check_internet():
        application.ui.label_5.setStyleSheet('background-color: rgb(85, 255, 0);')
    if internet:
        l = len(internet) - 1
        y = 0
        keys = [i for i in internet.keys()]

        for name in keys:
            if name[0:8] == 'Ethernet':
                if len(internet[name]) > 4:
                    application.ui.comboBox.addItem(f'{internet[name][-1]}')

            application.ui.textBrowser_3.insertPlainText('Сеть: ' + name + '\n')

            for v in range(len(internet[name])):
                if l == y:
                    if name == keys[-1] and len(internet[name]) - 1 == v:
                        application.ui.textBrowser_3.insertPlainText(text[v] + str(internet[name][v]))
                    else:
                        application.ui.textBrowser_3.insertPlainText(text[v] + str(internet[name][v]) + '\n')
                else:
                    application.ui.textBrowser_3.insertPlainText(text[v] + str(internet[name][v]) + '\n')

            if l > y:
                application.ui.textBrowser_3.insertPlainText('\n')

            y += 1


    application.show()

    sys.exit(app.exec())
