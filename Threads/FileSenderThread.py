from PyQt5.QtCore import QThread, pyqtSignal

import pickle
import logging
import os
import math

from Utils.redisconn import redisServerSetup

status, r, p = redisServerSetup()

logging.basicConfig(format="%(message)s", level=logging.INFO)


class FileSenderThread(QThread):

    progress_level = pyqtSignal(float)
    finished = pyqtSignal()

    def __init__(self, path, id, who_is):
        super().__init__()
        self.file_path = path
        self.id = id
        self.who_is = who_is
        # Dosya boyutunu almak
        self.file_size = os.path.getsize(self.file_path)
        # Redis maximum 65535 byte kabul ettigi icin buyuk verileri parcaliyoruz
        self.packet_count = math.ceil(self.file_size / 65535)
        a, b = os.path.split(self.file_path)
        self.file_extension = os.path.splitext(b)[1]
        # Paket sayisini progress barda gorsel olarak gosteriyoruz
        self.progress_step_amount = 100 / self.packet_count

    def run(self):
        logging.info("Dosya gonderiliyor...")
        p.subscribe("file")
        f = open(self.file_path, "rb")
        data = f.read(65535)
        current_packet = 0
        while data:
            current_packet += 1
            # Dosya paketinin kayip olmamasi icin belirli parametrelerle birlikte gonderiyor
            # kacinci paket gidiyor,Dosyanin tam boyutu nedir,Dosya uzantasi gibi...
            r.publish(
                "file",
                pickle.dumps(
                    {
                        "from": f"{self.id}",
                        "to": f"{self.who_is}",
                        "file_size": self.file_size,
                        "packet_count": self.packet_count,
                        "current_packet": current_packet,
                        "bytes": data,
                        "extension": f"{self.file_extension}",
                    }
                ),
            )
            # islemin ilerleyisini takip ediyoruz.
            # Arayuzde dinamik bir sekilde degistiriyoruz
            self.progress_level.emit(
                math.ceil(current_packet * self.progress_step_amount)
            )
            data = f.read(65535)
        logging.info("Dosya gonderme islemi tamamlandi!")
        # Dosya gonderme isleminin bittigine dair GUIyi haberdar ediyoruz
        self.finished.emit()
