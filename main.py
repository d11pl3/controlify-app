# Filename: main.py
import sys
import time

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import redis
from redis.exceptions import *

from datetime import datetime


import pickle

__version__ = "0.1"
__authors__ = ["Ahmet Yusuf Başaran ", "Yusufcan Günay"]


# * ____________________________________________
# * ______________<&>|EKRANLAR|<&>______________
# * ____________________________________________
# ? ANA EKRAN
class Controlify(QMainWindow):
    def __init__(self, r, p):
        super().__init__()
        # ? Redis Instance
        # * ------------
        self.r = r
        self.p = p
        # * ------------

        # ? Unique ID creation for every client
        # * ------------
        now = datetime.now()
        id = str.join("", str(datetime.timestamp(now)).split("."))
        self.id = id
        # * ------------
        # Log to Redis server that this client is activated
        self.r.publish(
            "logs",
            pickle.dumps(
                {
                    "id": f"{self.id}",
                    "log_type": "client_activated",
                }
            ),
        )
        # Ana ekran Ozelliklerini tanimliyoruz
        self.setWindowTitle("Controlify")
        self.setFixedSize(QSize(750, 500))
        # Ana Ekranin Merkezine bir Widget ekliyoruz Ve Genel Bir Yerleşim alani oluşturuyoruz
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)

        # Ana Ekranin Icindeki Widgetlarin Olusturulmasi
        self._createHeader()
        self._createIpList()
        self._createConnTypeRadioBtns()
        self._createToBeConnectedSection()
        self._createConnectButton()
        self._createExitButton()

        self._centralWidget.setLayout(self.generalLayout)

        # ! To Activate Always Running Threads
        self.logListenerThread = LogListenerThread(self.r, self.p)
        self.logListenerThread.start()
        # self.logListenerThread.exit()
        # self.logListenerThread.quit()

    # todo Ana Ekrana Ait Event(Olay Kontrol Methodlari Pencere Kapatilmasi,Mouse Hareketleri vs.)
    # ? Sol ustden uygulamayi kapatirken kontrol edilen method
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Message",
            "Are you sure to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            # Kapanirken IPyi siler
            # self.r.lrem("ip_list", 1, my_local_ip)

            event.accept()
        else:
            event.ignore()

    # todo Arayuz Elemanlarini olusturan methodlar
    def _createHeader(self):
        horizantalBoxLayout1 = QHBoxLayout()
        connected_ips_label = QLabel("Aktif Bilgisayarlarim")
        id_label = QLabel(f"ID:{self.id}")
        horizantalBoxLayout1.addWidget(connected_ips_label)
        horizantalBoxLayout1.addStretch()
        horizantalBoxLayout1.addWidget(id_label)
        self.generalLayout.addLayout(horizantalBoxLayout1)

    def _createIpList(self):
        """
        [Bağlı Bilgisayarların ip addresslerinin listesini gösteren widget]
        [Sürekli Güncel]
        """
        self.connected_ips_listwidget = QListWidget()
        self.connected_ips_listwidget.addItem("192.168.1.2")
        self.connected_ips_listwidget.addItem("192.168.2.55")
        self.generalLayout.addWidget(self.connected_ips_listwidget)

    def _createPcControlScreen(self):
        self.pc_control_screen = PcControlScreen()

    def _createConnTypeRadioBtns(self):
        horizantalBoxLayout2 = QHBoxLayout()
        self.pcControlTypeRadioBtn = QRadioButton("Bilgisayar Yönetimi")
        self.fileTransferTypeRadioBtn = QRadioButton("Dosya Transferi")
        # Varsayilan Olarak Bilgisayar Kontolu secimini belirledik!
        self.pcControlTypeRadioBtn.setChecked(True)
        horizantalBoxLayout2.addStretch()
        horizantalBoxLayout2.addWidget(self.pcControlTypeRadioBtn)
        horizantalBoxLayout2.addWidget(self.fileTransferTypeRadioBtn)
        horizantalBoxLayout2.addStretch()
        self.generalLayout.addLayout(horizantalBoxLayout2)

    def _createToBeConnectedSection(self):
        horizantalBoxLayout3 = QHBoxLayout()
        to_be_connLabel = QLabel("Baglanilacak Bilgisayar")
        self.to_be_connLineEdit = QLineEdit()
        horizantalBoxLayout3.addWidget(to_be_connLabel)
        horizantalBoxLayout3.addWidget(self.to_be_connLineEdit)
        self.generalLayout.addLayout(horizantalBoxLayout3)

    def _createConnectButton(self):
        self.connBtn = QPushButton("Bağlan")
        self.connBtn.clicked.connect(self.connectToPc)
        self.generalLayout.addWidget(self.connBtn)

    def _createExitButton(self):
        self.exitBtn = QPushButton("Çıkış Yap")
        self.exitBtn.clicked.connect(self.close)
        self.generalLayout.addWidget(self.exitBtn)

    # todo Aksiyon alinan methodlar(Pc ye baglanma istegi gonderme,Guncel Ipleri alma vs.)
    def connectToPc(self):
        # self.to_be_connLineEdit.setText("192.168.1.2")
        self.r.publish(
            "logs",
            pickle.dumps(
                {
                    "id": f"{self.id}",
                    "log_type": "client_activated",
                }
            ),
        )


# ? Bilgisayar Kontrol Ekrani
class PcControlScreen(QWidget):
    def __init__():
        super().__init__()


# ? Dosya Paylasimi Ekrani
class FileTransferScreen(QWidget):
    def __init__():
        super().__init__()


# * ______________THREADLER______________
class LogListenerThread(QThread):
    new_client_goes_online = pyqtSignal(dict)
    new_connection_request_taken = pyqtSignal(dict)

    def __init__(self, r, p):
        super().__init__()
        # Redis Instance
        self.r = r
        self.p = p

    def run(self):
        while True:
            # time.sleep(0.01)
            log = self.p.get_message()
            if log:
                print(log)


# * ______________Redis Baglantisi______________
def redisServerSetup():
    """
    [
    ! Canli veri alisverisini saglayabilen
    ! ayni zamanda NoSQL gibi calisan, key:value seklinde ram hafizasinda veri saklayabilen bir database
    ]
    """
    try:
        # r = redis.Redis("localhost")
        r = redis.Redis(
            host="redis-11907.c135.eu-central-1-1.ec2.cloud.redislabs.com",
            password="jPHWcbukgy7r1qmBwa9VxNRHZmfeD9N9",
            port=11907,
            db=0,
        )
        p = r.pubsub(ignore_subscribe_messages=True)
        p.subscribe("logs")
        # ? Requsts yani (logs)kayitlar kanalina abone olduk burda tum cihazlarin yapmak istedikleri islemlerin trafigini logluyacagiz
        # ? Buna gore clientlari uyaracagiz hali hazirda baglanti durumunda olan clientlara baglanti istegi gonderilmesini engelliyecegiz
        return (True, r, p)
    except:
        return (False, None, None)


# * ______________MAIN______________
def main():
    redisServerStatus, r, p = redisServerSetup()
    if redisServerStatus:
        try:
            controlify = QApplication(sys.argv)
            view = Controlify(r, p)
            # ! Uygulama penceresini göstermek
            view.show()
            # ! Uygulamanin ana döngüsünü oluşturmak
            sys.exit(controlify.exec_())
        except:
            print("PyQt uygulamasi kapatildi!")
            print("Yada")
            print("PyQt uygulamasinin baslatilmasinda sorun yasandi!")
    else:
        print("Redis Baglanti Sorunu Yasiyor...")


if __name__ == "__main__":
    main()