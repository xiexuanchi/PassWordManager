from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QHBoxLayout)
from PySide6.QtCore import Qt

class LoginDialog(QDialog):
    """
    登录和初始化主密码的对话框。
    """
    def __init__(self, is_setup=False, parent=None):
        super().__init__(parent)
        self.is_setup = is_setup
        self.password = None
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("主密码验证" if not self.is_setup else "设置主密码")
        self.setFixedSize(350, 200)
        
        layout = QVBoxLayout(self)
        
        if self.is_setup:
            label_text = "这是您第一次启动，请设置一个强主密码：\n(请务必牢记，丢失后无法找回)"
        else:
            label_text = "请输入主密码以解锁数据库："
            
        self.label = QLabel(label_text)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        
        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("主密码")
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pwd_input)
        
        if self.is_setup:
            self.pwd_confirm = QLineEdit()
            self.pwd_confirm.setPlaceholderText("确认主密码")
            self.pwd_confirm.setEchoMode(QLineEdit.EchoMode.Password)
            layout.addWidget(self.pwd_confirm)
            
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self._on_ok)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def _on_ok(self):
        pwd = self.pwd_input.text()
        if not pwd:
            QMessageBox.warning(self, "错误", "主密码不能为空！")
            return
            
        if self.is_setup:
            pwd_confirm = self.pwd_confirm.text()
            if pwd != pwd_confirm:
                QMessageBox.warning(self, "错误", "两次输入的密码不一致！")
                return
            if len(pwd) < 8:
                QMessageBox.warning(self, "建议", "主密码长度建议至少 8 位。")
                
        self.password = pwd
        self.accept()

    def get_password(self):
        return self.password
