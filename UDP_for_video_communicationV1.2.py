

import cv2
import socket
import threading
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

class VideoReceiverThread(QtCore.QThread):
    frame_received = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, receiver_socket):
        super().__init__()
        self.receiver_socket = receiver_socket
        self.running = False

    def run(self):
        buffer_size = 1400
        data = b''
        while self.running:
            try:
                packet, _ = self.receiver_socket.recvfrom(buffer_size)
                if packet == b'FRAME_END':
                    if data:
                        np_data = np.frombuffer(data, dtype=np.uint8)
                        frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
                        if frame is not None and frame.size > 0:
                            self.frame_received.emit(frame)
                        data = b''  # Reset data after successfully decoding and displaying frame
                else:
                    data += packet
            except socket.error as e:
                if not self.running:
                    break
                print(f"Socket error: {e}")

class Ui_Dialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi()

        # Socket setup
        self.sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiver_socket.bind(('127.0.0.1', 12345))

        # Video Receiver Thread
        self.video_receiver_thread = VideoReceiverThread(self.receiver_socket)
        self.video_receiver_thread.frame_received.connect(self.display_frame)

        # Button connections
        self.SenderSendButton.clicked.connect(self.send_video)
        self.RecieverSendButton.clicked.connect(self.receive_video)
        self.CloseButton.clicked.connect(self.close_program)

        self.running = False

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(1130, 824)
        self.SenderSendButton = QtWidgets.QPushButton(self)
        self.SenderSendButton.setGeometry(QtCore.QRect(240, 730, 91, 31))
        self.SenderSendButton.setObjectName("SenderSendButton")
        self.RecieverSendButton = QtWidgets.QPushButton(self)
        self.RecieverSendButton.setGeometry(QtCore.QRect(820, 730, 91, 31))
        self.RecieverSendButton.setObjectName("RecieverSendButton")
        self.SenderBox = QtWidgets.QLineEdit(self)
        self.SenderBox.setGeometry(QtCore.QRect(200, 20, 101, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.SenderBox.setFont(font)
        self.SenderBox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.SenderBox.setToolTipDuration(-9)
        self.SenderBox.setAutoFillBackground(True)
        self.SenderBox.setReadOnly(True)
        self.SenderBox.setObjectName("SenderBox")
        self.CloseButton = QtWidgets.QPushButton(self)
        self.CloseButton.setGeometry(QtCore.QRect(1030, 790, 81, 21))
        self.CloseButton.setObjectName("CloseButton")
        self.RecieverBox = QtWidgets.QLineEdit(self)
        self.RecieverBox.setGeometry(QtCore.QRect(780, 20, 111, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.RecieverBox.setFont(font)
        self.RecieverBox.setObjectName("RecieverBox")
        self.SenderViewBox = QtWidgets.QGraphicsView(self)
        self.SenderViewBox.setGeometry(QtCore.QRect(20, 70, 531, 641))
        self.SenderViewBox.setObjectName("SenderViewBox")
        self.ReceiverViewBox = QtWidgets.QGraphicsView(self)
        self.ReceiverViewBox.setGeometry(QtCore.QRect(580, 70, 531, 641))
        self.ReceiverViewBox.setObjectName("ReceiverViewBox")

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "UDP Protocol"))
        self.SenderSendButton.setText(_translate("Dialog", "Send Video"))
        self.RecieverSendButton.setText(_translate("Dialog", "Receive Video"))
        self.SenderBox.setText(_translate("Dialog", "Sender Video"))
        self.CloseButton.setText(_translate("Dialog", "Close"))
        self.RecieverBox.setText(_translate("Dialog", "Receiver Video"))

    def send_video(self):
        self.running = True
        cap = cv2.VideoCapture(0)
        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
            self.display_frame(frame, self.SenderViewBox)  # Display on sender side
            _, buffer = cv2.imencode('.jpg', frame)
            data = buffer.tobytes()
            # Split the data into chunks
            chunk_size = 1400
            num_chunks = len(data) // chunk_size + 1
            for i in range(num_chunks):
                chunk = data[i * chunk_size: (i + 1) * chunk_size]
                self.sender_socket.sendto(chunk, ('127.0.0.1', 12345))
            # Send end-of-frame indicator
            self.sender_socket.sendto(b'FRAME_END', ('127.0.0.1', 12345))
            cv2.waitKey(1)
        cap.release()

    def receive_video(self):
        self.running = True
        self.video_receiver_thread.running = True
        self.video_receiver_thread.start()

    def display_frame(self, frame, view_box=None):
        if view_box is None:
            view_box = self.ReceiverViewBox

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        image = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(image)
        scene = QtWidgets.QGraphicsScene()
        scene.addItem(QtWidgets.QGraphicsPixmapItem(pixmap))
        view_box.setScene(scene)
        view_box.fitInView(scene.itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)
        view_box.update()

    def close_program(self):
        self.running = False
        self.video_receiver_thread.running = False
        QtCore.QTimer.singleShot(500, self.cleanup_sockets)  # Delay to ensure threads exit cleanly
        QtWidgets.QApplication.quit()

    def closeEvent(self, event):
        self.close_program()
        event.accept()  # Accept the event to close the dialog


    def cleanup_sockets(self):
        try:
            self.sender_socket.close()
        except:
            pass
        try:
            self.receiver_socket.close()
        except:
            pass


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_Dialog()
    ui.show()
    sys.exit(app.exec_())


