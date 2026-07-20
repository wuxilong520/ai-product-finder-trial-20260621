from email.message import EmailMessage
import smtplib

from app.core.config import settings
from app.core.config_center import config_center
from app.core.environment_manager import environment_manager
from app.core.runtime import log_info


class EmailService:
    def _smtp_ready(self) -> bool:
        smtp_config = config_center.smtp()
        return bool(smtp_config["host"] and smtp_config["user"] and smtp_config["password"] and smtp_config["port"])

    def send_verification_code(self, email: str, code: str, purpose: str):
        purpose_label_map = {
            "register": "注册",
            "login": "登录",
            "reset_password": "找回密码",
        }
        purpose_label = purpose_label_map.get(purpose, purpose)
        smtp_config = config_center.smtp()

        if not self._smtp_ready():
            if environment_manager.is_production():
                log_info(
                    f"SMTP_DISABLED | email={email} | purpose={purpose_label} | reason=smtp_not_configured_in_production"
                )
                return {
                    "success": False,
                    "delivery_mode": "disabled",
                    "config_status": "smtp_not_configured",
                    "message": "当前生产环境还没配置邮件发送，验证码注册/验证码登录暂时不可用。请先使用账号密码登录，或由管理员发测试账号。",
                }
            log_info(
                f"SMTP_DEV_CODE | email={email} | purpose={purpose_label} | code={code} | reason=smtp_not_configured"
            )
            return {
                "success": True,
                "delivery_mode": "dev_console",
                "config_status": "dev_simulated",
                "dev_code": code,
                "message": "当前是开发环境模拟验证码模式，邮件不会真的发出。你可以直接使用这次生成的验证码继续测试。",
            }

        message = EmailMessage()
        message["Subject"] = f"你的{purpose_label}验证码"
        message["From"] = smtp_config["from_email"]
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

        if smtp_config["use_ssl"]:
            with smtplib.SMTP_SSL(smtp_config["host"], smtp_config["port"], timeout=20) as server:
                server.login(smtp_config["user"], smtp_config["password"])
                server.send_message(message)
            return {
                "success": True,
                "delivery_mode": "smtp",
                "config_status": "configured",
                "message": f"验证码已发送到 {email}",
            }

        with smtplib.SMTP(smtp_config["host"], smtp_config["port"], timeout=20) as server:
            if smtp_config["use_tls"]:
                server.starttls()
            server.login(smtp_config["user"], smtp_config["password"])
            server.send_message(message)
        return {
            "success": True,
            "delivery_mode": "smtp",
            "config_status": "configured",
            "message": f"验证码已发送到 {email}",
        }


email_service = EmailService()
