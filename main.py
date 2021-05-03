import sys

import paramiko as paramiko
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWidgets import QGridLayout, QLabel, QGroupBox, QRadioButton, QHBoxLayout, QPlainTextEdit, \
    QLineEdit, QMainWindow, QApplication, QWidget, QPushButton, QFileDialog


class MainWindowViewModel(QObject):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)

        self.window = parent

        self.grid = QGridLayout()

        self.username_label = QLabel('User Name')
        self.password_label = QLabel('Password')

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('User Name')

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)

        self.ip_address_label = QLabel('IP Address')
        self.protocol_label = QLabel('Protocol')

        self.ip_address_input = QLineEdit()

        self.telnet_radio_button = QRadioButton('Telnet')
        self.ssh_radio_button = QRadioButton('SSH')

        self.protocol_group_layout = QHBoxLayout()
        self.protocol_group_layout.addWidget(self.telnet_radio_button)
        self.protocol_group_layout.addWidget(self.ssh_radio_button)

        self.protocol_group = QGroupBox()
        self.protocol_group.setLayout(self.protocol_group_layout)

        self.private_file_key_label = QLabel('Private Key File (required)')
        self.private_file_key_input = QLineEdit()
        self.private_file_key_input.setPlaceholderText('Path to file')
        self.private_file_key_button = QPushButton('Open')

        self.grid.addWidget(self.username_label, 0, 0)
        self.grid.addWidget(self.username_input, 0, 1)
        self.grid.addWidget(self.password_label, 1, 0)
        self.grid.addWidget(self.password_input, 1, 1)

        self.grid.addWidget(self.ip_address_label, 0, 2)
        self.grid.addWidget(self.ip_address_input, 0, 3)
        self.grid.addWidget(self.protocol_label, 1, 2)
        self.grid.addWidget(self.protocol_group, 1, 3)

        self.script_input = QPlainTextEdit()
        self.script_input.setPlaceholderText('Script: eg. ls -a')

        self.script_output = QPlainTextEdit()
        self.script_output.setReadOnly(True)
        self.script_output_label = QLabel('Output')

        self.run_button = QPushButton('Run')

        self.private_file_key_group_layout = QHBoxLayout()

        self.private_file_key_group_layout.addWidget(self.private_file_key_label)
        self.private_file_key_group_layout.addWidget(self.private_file_key_input)
        self.private_file_key_group_layout.addWidget(self.private_file_key_button)

        self.private_file_key_button.clicked.connect(self._on_select_key_file)

        self.grid.addWidget(self.run_button, 2, 3)
        self.grid.addWidget(self.script_input, 3, 0, 1, 5)
        self.grid.addWidget(self.script_output_label, 4, 0, 1, 5)
        self.grid.addWidget(self.script_output, 5, 0, 1, 5)
        self.grid.addLayout(self.private_file_key_group_layout, 0, 4)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.grid)
        parent.setCentralWidget(self.central_widget)

        self.telnet_radio_button.setEnabled(False)
        self.ssh_radio_button.setChecked(True)

        self.run_button.clicked.connect(self._on_run_script)

    @pyqtSlot()
    def _on_select_key_file(self):
        filename, _ = QFileDialog.getOpenFileName(self.window,
                                                  'Open Private Key File',
                                                  filter='Private Key File (*.pem)')
        self.private_file_key_input.setText(filename)

    @pyqtSlot()
    def _on_run_script(self):
        username = self.username_input.text()
        password = self.password_input.text() or None
        host = self.ip_address_input.text()
        ssh_protocol = self.ssh_radio_button.isChecked()
        script = self.script_input.toPlainText()

        if ssh_protocol:
            key = paramiko.RSAKey.from_private_key_file(self.private_file_key_input.text())
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, username=username, password=password, pkey=key)
            _, stdout, _ = client.exec_command(script)

            lines = [line.strip() for line in stdout]
            client.close()
            output = '\n'.join(lines)

            self.script_output.setPlainText(output)
        else:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    view_model = MainWindowViewModel(window)

    window.show()

    r = app.exec_()

    print(r)
