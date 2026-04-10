from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QPushButton, QComboBox, QTextEdit, QHBoxLayout, 
                             QLabel, QMessageBox)
from core.crypto_manager import CryptoManager

class PasswordDialog(QDialog):
    """
    新增或编辑密码项的对话框。
    """
    def __init__(self, categories, entry_data=None, parent=None):
        super().__init__(parent)
        self.entry_data = entry_data
        self.categories = categories
        self._init_ui()
        if entry_data:
            self._fill_data()

    def _init_ui(self):
        self.setWindowTitle("添加密码项" if not self.entry_data else "编辑密码项")
        self.setFixedSize(400, 450)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.site_input = QLineEdit()
        self.site_input.setPlaceholderText("网站/应用名称 (如: Github)")
        form.addRow("网站/应用:", self.site_input)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("用户名/邮箱")
        form.addRow("用户名:", self.user_input)
        
        # 密码输入和生成器
        pwd_layout = QHBoxLayout()
        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("密码")
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_layout.addWidget(self.pwd_input)
        
        self.gen_btn = QPushButton("生成")
        self.gen_btn.setToolTip("生成 20 位强密码")
        self.gen_btn.clicked.connect(self._generate_password)
        pwd_layout.addWidget(self.gen_btn)
        
        self.show_btn = QPushButton("👁")
        self.show_btn.setFixedWidth(30)
        self.show_btn.setCheckable(True)
        self.show_btn.toggled.connect(self._toggle_password_visibility)
        pwd_layout.addWidget(self.show_btn)
        
        form.addRow("密码:", pwd_layout)
        
        self.cat_combo = QComboBox()
        for cat in self.categories:
            self.cat_combo.addItem(cat['name'], cat['id'])
        form.addRow("分类:", self.cat_combo)
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("额外备注...")
        form.addRow("备注:", self.notes_input)
        
        layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def _fill_data(self):
        self.site_input.setText(self.entry_data.get('site', ''))
        self.user_input.setText(self.entry_data.get('username', ''))
        self.pwd_input.setText(self.entry_data.get('password', ''))
        self.notes_input.setPlainText(self.entry_data.get('notes', ''))
        
        index = self.cat_combo.findData(self.entry_data.get('category_id'))
        if index >= 0:
            self.cat_combo.setCurrentIndex(index)

    def _generate_password(self):
        pwd = CryptoManager.generate_random_password(20)
        self.pwd_input.setText(pwd)
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Normal)
        self.show_btn.setChecked(True)

    def _toggle_password_visibility(self, checked):
        if checked:
            self.pwd_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)

    def get_data(self):
        return {
            "site": self.site_input.text(),
            "username": self.user_input.text(),
            "password": self.pwd_input.text(),
            "category_id": self.cat_combo.currentData(),
            "notes": self.notes_input.toPlainText()
        }
