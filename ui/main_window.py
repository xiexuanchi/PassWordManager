from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QInputDialog, QAbstractItemView)
from PySide6.QtCore import Qt
from ui.password_dialog import PasswordDialog

class MainWindow(QMainWindow):
    """
    程序主窗口。
    """
    def __init__(self, db_manager, crypto_manager):
        super().__init__()
        self.db = db_manager
        self.crypto = crypto_manager
        self._init_ui()
        self.refresh_table()

    def _init_ui(self):
        self.setWindowTitle("Password Manager - 密码管理器")
        self.resize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 顶部搜索和操作栏
        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("按网站或用户名搜索...")
        self.search_input.textChanged.connect(self.refresh_table)
        top_layout.addWidget(self.search_input)
        
        self.add_btn = QPushButton("新增密码")
        self.add_btn.clicked.connect(self._on_add)
        top_layout.addWidget(self.add_btn)
        
        self.add_cat_btn = QPushButton("管理分类")
        self.add_cat_btn.clicked.connect(self._on_add_category)
        top_layout.addWidget(self.add_cat_btn)
        
        main_layout.addLayout(top_layout)
        
        # 密码表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["网站", "用户名", "分类", "操作", "ID"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setColumnHidden(4, True)  # 隐藏 ID 列
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.doubleClicked.connect(self._on_edit)
        main_layout.addWidget(self.table)

    def refresh_table(self):
        search_term = self.search_input.text()
        entries = self.db.get_entries(search_term)
        
        self.table.setRowCount(len(entries))
        for i, entry in enumerate(entries):
            self.table.setItem(i, 0, QTableWidgetItem(entry['site']))
            self.table.setItem(i, 1, QTableWidgetItem(entry['username']))
            self.table.setItem(i, 2, QTableWidgetItem(entry['category_name'] or "未分类"))
            
            # 操作按钮
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            
            copy_btn = QPushButton("复制密码")
            copy_btn.clicked.connect(lambda checked, e=entry: self._on_copy_password(e))
            
            del_btn = QPushButton("删除")
            del_btn.setStyleSheet("color: red;")
            del_btn.clicked.connect(lambda checked, e=entry: self._on_delete(e))
            
            btn_layout.addWidget(copy_btn)
            btn_layout.addWidget(del_btn)
            self.table.setCellWidget(i, 3, btn_container)
            
            # 存储 ID 用于双击编辑
            self.table.setItem(i, 4, QTableWidgetItem(str(entry['id'])))

    def _on_add(self):
        cats = self.db.get_categories()
        dialog = PasswordDialog(cats, parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['site'] or not data['password']:
                QMessageBox.warning(self, "错误", "网站和密码不能为空！")
                return
                
            pwd_enc = self.crypto.encrypt(data['password'])
            notes_enc = self.crypto.encrypt(data['notes']) if data['notes'] else None
            
            self.db.add_entry(data['site'], data['username'], pwd_enc, notes_enc, data['category_id'])
            self.refresh_table()

    def _on_edit(self, index):
        row = index.row()
        entry_id = int(self.table.item(row, 4).text())
        
        # 获取原始加密数据并解密
        all_entries = self.db.get_entries()
        entry = next(e for e in all_entries if e['id'] == entry_id)
        
        try:
            decrypted_pwd = self.crypto.decrypt(entry['password_encrypted'])
            decrypted_notes = self.crypto.decrypt(entry['notes_encrypted']) if entry['notes_encrypted'] else ""
        except Exception as e:
            QMessageBox.critical(self, "错误", f"解密失败: {e}")
            return

        entry_data = {
            'site': entry['site'],
            'username': entry['username'],
            'password': decrypted_pwd,
            'notes': decrypted_notes,
            'category_id': entry['category_id']
        }
        
        cats = self.db.get_categories()
        dialog = PasswordDialog(cats, entry_data, parent=self)
        if dialog.exec():
            data = dialog.get_data()
            pwd_enc = self.crypto.encrypt(data['password'])
            notes_enc = self.crypto.encrypt(data['notes']) if data['notes'] else None
            
            self.db.update_entry(entry_id, data['site'], data['username'], pwd_enc, notes_enc, data['category_id'])
            self.refresh_table()

    def _on_copy_password(self, entry):
        try:
            pwd = self.crypto.decrypt(entry['password_encrypted'])
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(pwd)
            QMessageBox.information(self, "成功", "密码已复制到剪贴板。")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"复制失败: {e}")

    def _on_delete(self, entry):
        reply = QMessageBox.question(self, "确认", f"确定要删除 {entry['site']} 的记录吗？",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_entry(entry['id'])
            self.refresh_table()

    def _on_add_category(self):
        name, ok = QInputDialog.getText(self, "新增分类", "请输入分类名称:")
        if ok and name:
            if self.db.add_category(name):
                QMessageBox.information(self, "成功", "分类添加成功。")
            else:
                QMessageBox.warning(self, "错误", "分类已存在。")
