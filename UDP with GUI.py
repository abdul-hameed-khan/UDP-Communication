from PyQt5 import QtCore, QtGui, QtWidgets

import socket
import threading

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(999, 623)
        self.SenderSendButton = QtWidgets.QPushButton(Dialog)
        self.SenderSendButton.setGeometry(QtCore.QRect(180, 180, 91, 31))
        self.SenderSendButton.setObjectName("SenderSendButton")
        self.SenderInputText = QtWidgets.QTextEdit(Dialog)
        self.SenderInputText.setGeometry(QtCore.QRect(30, 70, 411, 91))
        self.SenderInputText.setObjectName("SenderInputText")
        self.RecieverSendButton = QtWidgets.QPushButton(Dialog)
        self.RecieverSendButton.setGeometry(QtCore.QRect(700, 180, 91, 31))
        self.RecieverSendButton.setObjectName("RecieverSendButton")
        self.SenderBox = QtWidgets.QLineEdit(Dialog)
        self.SenderBox.setGeometry(QtCore.QRect(180, 20, 81, 31))
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
        self.CloseButton = QtWidgets.QPushButton(Dialog)
        self.CloseButton.setGeometry(QtCore.QRect(870, 580, 81, 21))
        self.CloseButton.setObjectName("CloseButton")
        self.RecieverBox = QtWidgets.QLineEdit(Dialog)
        self.RecieverBox.setGeometry(QtCore.QRect(690, 20, 91, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.RecieverBox.setFont(font)
        self.RecieverBox.setObjectName("RecieverBox")
        self.RecieverTextBox = QtWidgets.QTextEdit(Dialog)
        self.RecieverTextBox.setGeometry(QtCore.QRect(520, 230, 411, 301))
        self.RecieverTextBox.setObjectName("RecieverTextBox")
        self.SenderTextBox = QtWidgets.QTextEdit(Dialog)
        self.SenderTextBox.setGeometry(QtCore.QRect(30, 230, 411, 301))
        self.SenderTextBox.setObjectName("SenderTextBox")
        self.RecieverInputText = QtWidgets.QTextEdit(Dialog)
        self.RecieverInputText.setGeometry(QtCore.QRect(520, 70, 411, 91))
        self.RecieverInputText.setObjectName("RecieverInputText")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        # Set up UDP sockets
        self.sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Allow socket address reuse
        self.receiver_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.receiver_socket.bind(('127.0.0.5', 12345))  # Bind to a local address and port for receiving messages

        # Connect buttons to methods
        self.SenderSendButton.clicked.connect(self.send_message_to_receiver)
        self.RecieverSendButton.clicked.connect(self.send_message_to_sender)
        self.CloseButton.clicked.connect(self.close_program)


        # Start a separate thread for receiving messages
        self.running = True
        self.receiver_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receiver_thread.start()
        

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "UDP Protocol"))
        self.SenderSendButton.setText(_translate("Dialog", "Send Message"))
        self.RecieverSendButton.setText(_translate("Dialog", "Send Message"))
        self.SenderBox.setText(_translate("Dialog", "Sender Box"))
        self.CloseButton.setText(_translate("Dialog", "Close"))
        self.RecieverBox.setText(_translate("Dialog", "Reciever Box"))

    def send_message_to_receiver(self):
        message = self.SenderInputText.toPlainText()
        if message:
            self.sender_socket.sendto(message.encode(), ('127.0.0.5', 12345))  # Send message to the receiver's port
            self.SenderTextBox.append(f"Sent: {message}")
            self.SenderInputText.clear()

    def send_message_to_sender(self):
        message = self.RecieverInputText.toPlainText()
        if message:
            self.SenderTextBox.append(f"Received: {message}")
            self.RecieverTextBox.append(f"Sent: {message}")
            self.RecieverInputText.clear()

    def receive_messages(self):
        while self.running:
            try:
                message, _ = self.receiver_socket.recvfrom(1024)
                self.RecieverTextBox.append(f"Received: {message.decode()}")
            except socket.error as e:
                if self.running:  # Only print the error if not shutting down
                    print(f"Error receiving message: {e}")

    def close_program(self):
        self.running = False
        self.receiver_socket.close()
        self.sender_socket.close()
        QtWidgets.QApplication.quit()
        # Dialog.close()
    



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())


