from PyQt5.QtCore import QRunnable, QCoreApplication

import logging
import pickle

from Utils.redisconn import redisServerSetup

status, r, p = redisServerSetup()

logging.basicConfig(format="%(message)s", level=logging.INFO)


# 1. Subclass QRunnable
class SendMouseRightClickRunnable(QRunnable):
    def __init__(self, id, theIdIamControlling):
        super().__init__()
        self.id = id
        self.theIdIamControlling = theIdIamControlling
        self.setAutoDelete(True)

    def run(self):
        logging.info("Mouse Right Click Send!")
        r.publish(
            "logs",
            pickle.dumps(
                {
                    "to": f"{self.theIdIamControlling}",
                    "from": f"{self.id}",
                    "log_type": "mouse_right_click",
                }
            ),
        )
        self.autoDelete()
