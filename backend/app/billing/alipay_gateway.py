from __future__ import annotations

import base64
import json
from datetime import UTC, datetime
from urllib.parse import urlencode

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from app.core.config import settings


ALIPAY_GATEWAY_URL = "https://openapi.alipay.com/gateway.do"


def _normalize_pem(value: str, *, key_type: str) -> bytes:
    text = (value or "").strip().replace("\\n", "\n")
    if text and "BEGIN" not in text:
        body = "\n".join(text[i:i + 64] for i in range(0, len(text), 64))
        if key_type == "private":
            text = f"-----BEGIN PRIVATE KEY-----\n{body}\n-----END PRIVATE KEY-----"
        else:
            text = f"-----BEGIN PUBLIC KEY-----\n{body}\n-----END PUBLIC KEY-----"
    return text.encode("utf-8")


def _build_sign_content(params: dict[str, str]) -> str:
    pairs: list[str] = []
    for key in sorted(params.keys()):
        value = params[key]
        if value is None or value == "" or key == "sign":
            continue
        pairs.append(f"{key}={value}")
    return "&".join(pairs)


class AlipayGateway:
    def is_ready(self) -> bool:
        return bool(settings.alipay_app_id and settings.alipay_private_key and settings.alipay_public_key)

    def build_page_pay_url(
        self,
        *,
        external_order_id: str,
        amount_cents: int,
        subject: str,
        return_url: str,
        notify_url: str,
    ) -> str:
        amount_yuan = f"{amount_cents / 100:.2f}"
        params = {
            "app_id": settings.alipay_app_id,
            "method": "alipay.trade.page.pay",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "notify_url": notify_url,
            "return_url": return_url,
            "biz_content": json.dumps(
                {
                    "out_trade_no": external_order_id,
                    "product_code": "FAST_INSTANT_TRADE_PAY",
                    "total_amount": amount_yuan,
                    "subject": subject,
                },
                ensure_ascii=False,
                separators=(",", ":"),
            ),
        }
        params["sign"] = self.sign(params)
        gateway_url = settings.alipay_gateway_url or ALIPAY_GATEWAY_URL
        return f"{gateway_url}?{urlencode(params)}"

    def sign(self, params: dict[str, str]) -> str:
        sign_content = _build_sign_content(params)
        private_key = serialization.load_pem_private_key(
            _normalize_pem(settings.alipay_private_key, key_type="private"),
            password=None,
        )
        signature = private_key.sign(sign_content.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
        return base64.b64encode(signature).decode("utf-8")

    def verify(self, params: dict[str, str], sign: str) -> bool:
        if not sign:
            return False
        sign_content = _build_sign_content(params)
        public_key = serialization.load_pem_public_key(
            _normalize_pem(settings.alipay_public_key, key_type="public")
        )
        try:
            public_key.verify(
                base64.b64decode(sign),
                sign_content.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False


alipay_gateway = AlipayGateway()
