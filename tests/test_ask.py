from types import SimpleNamespace

from app import ask


def test_main_keeps_chat_history_for_follow_up_questions(monkeypatch, capsys):
    sent_messages = []
    created_models = []

    class FakeChat:
        def send_message(self, message):
            sent_messages.append(message)
            return SimpleNamespace(
                text=f"answer to {message}",
                usage_metadata=None,
            )

    class FakeChats:
        def create(self, *, model):
            created_models.append(model)
            return FakeChat()

    class FakeClient:
        def __init__(self, *, api_key):
            self.chats = FakeChats()

    inputs = iter(["follow-up question", ""])
    monkeypatch.setattr(ask.genai, "Client", FakeClient)
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")
    monkeypatch.setattr("builtins.input", lambda _prompt: next(inputs))
    monkeypatch.setattr("sys.argv", ["app.ask", "initial question"])

    ask.main()

    assert len(created_models) == 1
    assert sent_messages == ["initial question", "follow-up question"]
    assert "answer to follow-up question" in capsys.readouterr().out
