from email.message import EmailMessage
import smtplib

from app.core.config import settings
from app.core.runtime import AppError


class EmailService:
    def send_verification_code(self, email: str, code: str, purpose: str):
        if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
            raise AppError("SMTP_NOT_CONFIGURED", "邮件服务还没配置完成，暂时不能发送验证码", "auth", 503)

        purpose_label_map = {
            "register": "注册",
            "login": "登录",
            "reset_password": "找回密码",
        }
        purpose_label = purpose_label_map.get(purpose, purpose)

        message = EmailMessage()
        message["Subject"] = f"你的{purpose_label}验证码"
        message["From"] = settings.smtp_from_email or settings.smtp_user
        message["To"] = email
        message.set_content(
            "\n".join(
                [
                    "你好，",
                    "",
                    f"你本次用于{purpose_label}的验证码是：{code}",
                    f"验证码 {settings.auth_code_expire_minutes} 分钟内有效。",
                    "如果这不是你的操作，请忽略这封邮件。",
                ]
            )
        )

        if settings.smtp_use_ssl:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=20) as server:
                server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(message)
            return

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
            if settings.smtp_use_tls:
                server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(message)


email_service = EmailService()
