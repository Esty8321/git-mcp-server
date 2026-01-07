from services.email_service import EmailService
from settings import Settings
from utils import errors

class FakeSMTP:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.started_tls = False
        self.logged_in = False
        self.sent = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def starttls(self):
        self.started_tls = True

    def login(self, user, pwd):
        self.logged_in = True

    def send_message(self, msg):
        self.sent = True

def test_email_missing_config():
    settings = Settings(
        SMTP_HOST=None,
        SMTP_PORT=None,
        SMTP_USERNAME=None,
        SMTP_PASSWORD=None,
        FROM_EMAIL=None,
    )
    svc = EmailService(settings=settings)
    res = svc.send("a@b.com", "s", "b")
    assert res.ok is False
    assert res.error.code == errors.EMAIL_CONFIG_MISSING

def test_email_success(monkeypatch):
    settings = Settings(
        SMTP_HOST="smtp.example.com",
        SMTP_PORT="587",
        SMTP_USERNAME="u",
        SMTP_PASSWORD="p",
        FROM_EMAIL="from@example.com",
    )
    monkeypatch.setattr("services.email_service.smtplib.SMTP", FakeSMTP)

    svc = EmailService(settings=settings)
    res = svc.send("to@example.com", "sub", "body")
    assert res.ok is True
    assert res.data["to"] == "to@example.com"