#!/usr/bin/python
from gi.repository import Notify
import time
Notify.init("Notification example")
notification = Notify.Notification.new("Example notification", "This
is your initial notification.", None)
notification.show()
time.sleep(3)
notification.update("Replacement notification", "This is a
notification that supercedes the first one.", None)
notification.show()
