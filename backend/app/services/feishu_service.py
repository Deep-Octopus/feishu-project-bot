import hashlib
import hmac
import base64
import json
import time
import logging
import httpx
from ..core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

FEISHU_API_BASE = "https://open.feishu.cn/open-apis"
_token_cache = {"token": "", "expires_at": 0}


async def get_tenant_access_token() -> str:
    if time.time() < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal",
            json={"app_id": settings.feishu_app_id, "app_secret": settings.feishu_app_secret},
        )
        data = resp.json()
        _token_cache["token"] = data["tenant_access_token"]
        _token_cache["expires_at"] = time.time() + data.get("expire", 7200)
        return _token_cache["token"]


def verify_signature(timestamp: str, nonce: str, body: bytes, signature: str) -> bool:
    """Verify feishu event signature."""
    content = timestamp + nonce + settings.feishu_encrypt_key + body.decode()
    computed = hashlib.sha256(content.encode()).hexdigest()
    return hmac.compare_digest(computed, signature)


def decrypt_event(encrypt: str) -> dict:
    """Decrypt AES-256-CBC encrypted event."""
    key = hashlib.sha256(settings.feishu_encrypt_key.encode()).digest()
    encrypted_bytes = base64.b64decode(encrypt)
    iv = encrypted_bytes[:16]
    cipher_text = encrypted_bytes[16:]

    from Crypto.Cipher import AES
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(cipher_text)
    # Remove PKCS7 padding
    pad_len = decrypted[-1]
    decrypted = decrypted[:-pad_len]
    return json.loads(decrypted.decode())


async def send_message(receive_id: str, msg_type: str, content: dict, receive_id_type: str = "chat_id"):
    token = await get_tenant_access_token()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{FEISHU_API_BASE}/im/v1/messages?receive_id_type={receive_id_type}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "receive_id": receive_id,
                "msg_type": msg_type,
                "content": json.dumps(content),
            },
        )
        if resp.status_code != 200:
            logger.error(f"Failed to send message: {resp.text}")
        return resp.json()


async def send_text(chat_id: str, text: str):
    return await send_message(chat_id, "text", {"text": text})


async def send_card(chat_id: str, card: dict):
    return await send_message(chat_id, "interactive", card)


async def get_user_info(user_id: str) -> dict:
    token = await get_tenant_access_token()
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{FEISHU_API_BASE}/contact/v3/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        return resp.json().get("data", {}).get("user", {})
