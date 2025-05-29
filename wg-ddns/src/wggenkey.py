
import os
import base64

from cryptography.hazmat.primitives.asymmetric import x25519


class WireGuardKeyGenerator:
    def __init__(self):
        """
        初始化 WireGuardKeyGenerator。
        私钥不会立即生成（直到调用 genkey() 方法）。
        """
        self._private_key_raw: bytes | None = None
        self._public_key_raw: bytes | None = None

    def genkey(self) -> str:
        """
        生成一个新的 WireGuard 私钥，并将其内部存储，
        然后返回其 Base64 编码表示。
        这等同于 `wg genkey` 命令。
        """
        self._private_key_raw = os.urandom(32)
        # 生成私钥时自动派生并存储公钥
        private_key_obj = x25519.X25519PrivateKey.from_private_bytes(self._private_key_raw)
        public_key_obj = private_key_obj.public_key()
        self._public_key_raw = public_key_obj.public_bytes_raw()
        return base64.b64encode(self._private_key_raw).decode('utf-8')

    def genpub(self) -> str:
        """
        返回与内部存储私钥对应的 Base64 编码公钥。
        调用此方法前必须先调用 `genkey()`。
        这等同于 `wg pubkey` 命令。
        """
        if self._private_key_raw is None or self._public_key_raw is None:
            raise ValueError("私钥尚未生成。请先调用 genkey()。")
        return base64.b64encode(self._public_key_raw).decode('utf-8')

    @staticmethod
    def genpsk() -> str:
        """
        生成一个新的 WireGuard 预共享密钥 (preshared key)，并返回其 Base64 编码表示。
        这等同于 `wg genpsk` 命令。
        此方法是静态的，因为它不依赖于实例的私钥/公钥对。
        """
        psk_raw = os.urandom(32)
        return base64.b64encode(psk_raw).decode('utf-8')

    # --- 可选：如果需要获取原始密钥字节，可以使用以下方法 ---
    def get_raw_private_key(self) -> bytes | None:
        """返回原始私钥字节。"""
        return self._private_key_raw

    def get_raw_public_key(self) -> bytes | None:
        """返回原始公钥字节。"""
        return self._public_key_raw
