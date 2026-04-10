import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

class CryptoManager:
    """
    加密管理类，负责密钥派生和 AES-256-GCM 加密/解密。
    """
    
    ITERATIONS = 100000
    KEY_LENGTH = 32  # 256 bits

    def __init__(self, master_password: str, salt: bytes = None):
        """
        初始化加密管理器。
        :param master_password: 用户输入的主密码
        :param salt: 派生密钥所需的盐值，如果为 None 则生成新的（用于首次设置）
        """
        if salt is None:
            self.salt = os.urandom(16)
        else:
            self.salt = salt
            
        self.key = self._derive_key(master_password, self.salt)
        self.aesgcm = AESGCM(self.key)

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        使用 PBKDF2HMAC 从主密码派生密钥。
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_LENGTH,
            salt=salt,
            iterations=self.ITERATIONS,
        )
        return kdf.derive(password.encode())

    def encrypt(self, data: str) -> str:
        """
        使用 AES-256-GCM 加密数据。
        返回格式: base64(nonce + ciphertext)
        """
        nonce = os.urandom(12)  # GCM 推荐 12 字节 nonce
        ciphertext = self.aesgcm.encrypt(nonce, data.encode(), None)
        return base64.b64encode(nonce + ciphertext).decode('utf-8')

    def decrypt(self, encrypted_data: str) -> str:
        """
        使用 AES-256-GCM 解密数据。
        """
        try:
            raw_data = base64.b64decode(encrypted_data)
            nonce = raw_data[:12]
            ciphertext = raw_data[12:]
            decrypted_data = self.aesgcm.decrypt(nonce, ciphertext, None)
            return decrypted_data.decode('utf-8')
        except (InvalidTag, ValueError):
            raise ValueError("解密失败：可能是主密码错误或数据损坏。")

    @staticmethod
    def generate_random_password(length=20):
        """
        生成强随机密码。
        """
        import string
        import secrets
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(alphabet) for _ in range(length))
