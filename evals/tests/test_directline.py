import pytest

from certops_eval.directline import USER_ID, DirectLineClient


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def json(self):
        return self.body

    def raise_for_status(self):
        pass


class FakeDirectLine:
    """Serves a token, a conversation, then the queued activity batches one poll at a time."""

    def __init__(self, batches):
        self.batches = list(batches)
        self.posted = []

    def get(self, url, headers=None, params=None, timeout=None):
        if url == "https://token":
            return FakeResponse({"token": "t"})
        batch = self.batches.pop(0) if self.batches else []
        return FakeResponse({"activities": batch, "watermark": str(len(self.batches))})

    def post(self, url, headers=None, json=None, timeout=None):
        assert headers == {"Authorization": "Bearer t"}
        if url.endswith("/conversations"):
            return FakeResponse({"conversationId": "abc"})
        self.posted.append((url, json))
        return FakeResponse({"id": "1"})


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def bot(text):
    return {"type": "message", "from": {"id": "agent"}, "text": text}


def client(fake, clock, **kwargs):
    return DirectLineClient("https://token", "https://dl", session=fake, clock=clock, sleep=clock.sleep, **kwargs)


def test_sends_question_and_joins_bot_messages_until_quiet():
    fake = FakeDirectLine([
        [{"type": "message", "from": {"id": USER_ID}, "text": "echo"}, {"type": "typing", "from": {"id": "agent"}}],
        [bot("payments-gateway is CRITICAL.")],
        [bot("Follow the emergency runbook.")],
        [], [], [],
    ])
    clock = FakeClock()

    answer = client(fake, clock).ask("What is critical?")

    assert answer == "payments-gateway is CRITICAL.\nFollow the emergency runbook."
    url, activity = fake.posted[0]
    assert url == "https://dl/v3/directline/conversations/abc/activities"
    assert activity["text"] == "What is critical?"
    assert activity["from"] == {"id": USER_ID}


def test_times_out_when_the_agent_never_replies():
    clock = FakeClock()

    with pytest.raises(TimeoutError):
        client(FakeDirectLine([]), clock, timeout_s=5).ask("hello")
