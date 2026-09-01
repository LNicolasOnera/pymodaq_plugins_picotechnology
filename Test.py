from PyQt5.QtCore import QThread
from pymodaq_plugins_picotechnology.hardware.PicoLogTC08 import PicoLogTC08
import sys
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)

class Worker(QThread):
    def run(self):
        ctrl = PicoLogTC08()
        print("ouvert :", ctrl.handle)
        ctrl.close_all_units()
        print("fermé")

for i in range(3):
    w = Worker()
    w.start()
    w.wait()
    print(f"--- cycle {i} terminé ---")

app.quit()