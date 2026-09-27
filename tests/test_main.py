from types import SimpleNamespace

from telegram_ai_assistant import main as main_module


class FakeApplication:
    def __init__(self):
        self.polling_called = False

    def run_polling(self):
        self.polling_called = True


def test_main_creates_telegram_application_without_openai(monkeypatch):
    fake_application = FakeApplication()
    config = SimpleNamespace(log_level="INFO")
    monkeypatch.setattr(main_module, "load_config", lambda: config)
    monkeypatch.setattr(main_module, "configure_logging", lambda level: None)
    monkeypatch.setattr(main_module, "create_telegram_app", lambda received_config: fake_application)
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-be-used")

    main_module.main()

    assert fake_application.polling_called is True
