import threading
from pymodaq_plugins_picotechnology.hardware.PicoLogTC08 import PicoLogTC08

def cycle(i):
    print(f"--- essai {i} (thread {threading.current_thread().name}) ---")
    ctrl = PicoLogTC08()
    print("handle ouvert :", ctrl.handle)
    ctrl.close_all_units()
    print("fermé")

for i in range(3):
    t = threading.Thread(target=cycle, args=(i,))
    t.start()
    t.join()