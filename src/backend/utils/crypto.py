"""
Configuration Encryption Utilities

提供配置信息的加密和解密功能。
使用 Fernet 对称加密算法。
"""
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional


class ConfigCrypto:
    """配置加密工具

    使用 Fernet 对称加密算法保护敏感配置信息（如 API Token）。
    """

    def __init__(self, encryption_key: Optional[str] = None):
        """初始化加密工具

        Args:
            encryption_key: 加密密钥（32字节base64编码）。
                          如果为 None，从环境变量 WORKLOG_ENCRYPTION_KEY 读取。
                          如果环境变量也不存在，自动生成一个新密钥。

        Raises:
            ValueError: 如果提供的密钥格式无效
        """
        if encryption_key:
            # 使用提供的密钥
            if not self._is_valid_key(encryption_key):
                raise ValueError("Invalid encryption key format")
            self.cipher = Fernet(encryption_key.encode())
        else:
            # 从环境变量读取或生成新密钥
            key = os.getenv("WORKLOG_ENCRYPTION_KEY")
            if key:
                if not self._is_valid_key(key):
                    raise ValueError("Invalid WORKLOG_ENCRYPTION_KEY in environment")
                self.cipher = Fernet(key.encode())
            else:
                # 生成新密钥（仅用于开发环境）
                import warnings
                warnings.warn(
                    "No encryption key provided, using auto-generated key. "
                    "Set WORKLOG_ENCRYPTION_KEY environment variable for production.",
                    RuntimeWarning
                )
                self.cipher = Fernet.generate_key()
                print(f"Generated encryption key: {self.cipher.decode()}")

    @staticmethod
    def _is_valid_key(key: str) -> bool:
        """验证密钥格式是否有效"""
        try:
            decoded = base64.urlsafe_b64decode(key.encode())
            return len(decoded) == 32  # Fernet 密钥固定 32 字节
        except Exception:
            return False

    @staticmethod
    def generate_key() -> str:
        """生成一个新的加密密钥

        Returns:
            Base64 编码的加密密钥
        """
        return Fernet.generate_key().decode()

    @staticmethod
    def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
        """从密码派生加密密钥

        Args:
            password: 用户密码
            salt: 盐值，如果为 None 则自动生成

        Returns:
            (加密密钥, 盐值)
        """
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode())).decode()
        return key, salt

    def encrypt(self, plaintext: str) -> str:
        """加密明文

        Args:
            plaintext: 要加密的明文字符串

        Returns:
            Base64 编码的密文

        Raises:
            ValueError: 如果明文不是字符串
        """
        if not isinstance(plaintext, str):
            raise ValueError("Plaintext must be a string")

        encrypted = self.cipher.encrypt(plaintext.encode())
        return encrypted.decode()

    def decrypt(self, ciphertext: str) -> str:
        """解密密文

        Args:
            ciphertext: Base64 编码的密文

        Returns:
            解密后的明文

        Raises:
            ValueError: 如果密文格式无效或解密失败
        """
        if not isinstance(ciphertext, str):
            raise ValueError("Ciphertext must be a string")

        try:
            decrypted = self.cipher.decrypt(ciphertext.encode())
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    def encrypt_dict(self, data: dict, keys: list[str]) -> dict:
        """加密字典中的特定字段

        Args:
            data: 原始字典
            keys: 需要加密的字段名列表

        Returns:
            加密后的新字典（不修改原字典）
        """
        result = data.copy()
        for key in keys:
            if key in result and result[key] is not None:
                result[key] = self.encrypt(str(result[key]))
        return result

    def decrypt_dict(self, data: dict, keys: list[str]) -> dict:
        """解密字典中的特定字段

        Args:
            data: 加密字典
            keys: 需要解密的字段名列表

        Returns:
            解密后的新字典（不修改原字典）
        """
        result = data.copy()
        for key in keys:
            if key in result and result[key] is not None:
                try:
                    result[key] = self.decrypt(result[key])
                except ValueError:
                    # 如果解密失败，保留原值
                    pass
        return result


# 全局单例
_crypto_instance: Optional[ConfigCrypto] = None


def get_crypto() -> ConfigCrypto:
    """获取全局加密工具实例"""
    global _crypto_instance
    if _crypto_instance is None:
        _crypto_instance = ConfigCrypto()
    return _crypto_instance
