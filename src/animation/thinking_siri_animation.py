# # gif_player.py
# import sys
# from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
# from PyQt5.QtGui import QMovie, QPalette, QColor
# from PyQt5.QtCore import Qt, QSize

# class GIFPlayer(QMainWindow):
#     def __init__(self, app, gif_path="images/siri.gif", width=100, height=100):
#         super().__init__()

#         self.app = app
#         self.desired_width = width
#         self.desired_height = height

#         # Set window properties
#         self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
#         self.setAttribute(Qt.WA_TranslucentBackground)
#         self.setGeometry(100, 100, self.desired_width, self.desired_height)

#         self.label = QLabel(self)
#         self.label.setGeometry(0, 0, self.desired_width, self.desired_height)
#         self.movie = QMovie(gif_path)
#         self.movie.setScaledSize(QSize(self.desired_width, self.desired_height))
#         self.label.setMovie(self.movie)

#         # Start the GIF
#         self.movie.start()

#         # Set window background to be transparent
#         palette = self.palette()
#         palette.setColor(QPalette.Background, QColor(0, 0, 0, 0))
#         self.setPalette(palette)

# # The application instance should not be created in the module.


import Cocoa
from PyObjCTools import AppHelper

class AppDelegate(Cocoa.NSObject):
    def applicationDidFinishLaunching_(self, aNotification):
        print("Application did finish launching")
        screen = Cocoa.NSScreen.mainScreen().frame().size
        self.window = Cocoa.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            ((0, screen.height-100), (100, 100)),
            Cocoa.NSWindowStyleMaskBorderless,
            Cocoa.NSBackingStoreBuffered, False)
        self.window.setTitle_("GIF Viewer")
        self.window.setLevel_(Cocoa.NSFloatingWindowLevel)
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(Cocoa.NSColor.clearColor())
        print("Window created")

        self.imageView = Cocoa.NSImageView.alloc().init()
        self.imageView.setFrame_(((0, 0), (100, 100)))
        self.imageView.setImageScaling_(Cocoa.NSImageScaleProportionallyUpOrDown)
        gifPath = "images/siri.gif"
        self.image = Cocoa.NSImage.alloc().initWithContentsOfFile_(gifPath)
        if self.image:
            print("GIF loaded successfully")
        else:
            print("Failed to load GIF")
        self.imageView.setImage_(self.image)
        self.window.contentView().addSubview_(self.imageView)
        self.window.makeKeyAndOrderFront_(None)
        self.showWindow()

    def showWindow(self):
        print("Showing window")
        self.window.setIsVisible_(True)

    def hideWindow(self):
        print("Hiding window")
        self.window.setIsVisible_(False)

if __name__ == "__main__":
    app = Cocoa.NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()
    