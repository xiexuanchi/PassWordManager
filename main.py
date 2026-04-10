import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from core.db_manager import DatabaseManager
from core.crypto_manager import CryptoManager
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # 初始化数据库
    db = DatabaseManager()
    
    # 检查是否已设置主密码
    salt = db.get_salt()
    is_setup = (salt is None)
    
    # 显示登录/设置对话框
    login_dlg = LoginDialog(is_setup=is_setup)
    if login_dlg.exec():
        master_password = login_dlg.get_password()
        
        try:
            if is_setup:
                # 首次设置：创建加密管理器并保存盐值
                crypto = CryptoManager(master_password)
                db.set_salt(crypto.salt)
            else:
                # 后续登录：使用保存的盐值验证
                crypto = CryptoManager(master_password, salt=salt)
                # 简单验证：尝试获取一个加密项（如果有）或者直接信任派生结果
                # 在此例中，我们将在解密具体项时捕获错误
            
            # 启动主窗口
            window = MainWindow(db, crypto)
            window.show()
            sys.exit(app.exec())
            
        except Exception as e:
            QMessageBox.critical(None, "错误", f"初始化失败: {str(e)}")
            sys.exit(1)
    else:
        # 用户取消登录
        sys.exit(0)

if __name__ == "__main__":
    main()
