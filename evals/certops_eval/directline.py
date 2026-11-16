import time

import requests

DEFAULT_DOMAIN = "https://directline.botframework.com"
USER_ID = "eval-user"


class DirectLineClient:
    """Asks a published Copilot Studio agent one question per conversation over the Direct Line API.

    The token endpoint comes from Copilot Studio: Settings > Channels > Mobile app (no authentication).
    """

    def __init__(self, token_endpoint: str, domain: str = DEFAULT_DOMAIN, timeout_s: float = 60,
                 quiet_s: float = 3, poll_s: float = 1, session: requests.Session | None = None,
                 clock=time.monotonic, sleep=time.sleep):
        self.token_endpoint = token_endpoint
        self.domain = domain.rstrip("/")
        self.timeout_s = timeout_s
        self.quiet_s = quiet_s
        self.poll_s = poll_s
        self.session = session or requests.Session()
        self.clock = clock
        self.sleep = sleep

    def ask(self, question: str) -> str:
        token = self._get(self.token_endpoint).json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        conversation = self._post(f"{self.domain}/v3/directline/conversations", headers).json()
        base = f"{self.domain}/v3/directline/conversations/{conversation['conversationId']}/activities"
        self._post(base, headers, json={
            "type": "message", "from": {"id": USER_ID}, "locale": "en-US", "text": question,
        })
        return self._collect_reply(base, headers)

    def _collect_reply(self, url: str, headers: dict) -> str:
        """Waits for the agent's messages, then for quiet_s without new ones, since answers can span messages."""
        messages: list[str] = []
        watermark = None
        deadline = self.clock() + self.timeout_s
        last_message_at = None
        while self.clock() < deadline:
            params = {"watermark": watermark} if watermark else None
            body = self._get(url, headers, params=params).json()
            watermark = body.get("watermark", watermark)
            for activity in body.get("activities", []):
                if activity.get("type") == "message" and activity.get("from", {}).get("id") != USER_ID:
                    messages.append(activity.get("text") or "")
                    last_message_at = self.clock()
            if last_message_at is not None and self.clock() - last_message_at >= self.quiet_s:
                break
            self.sleep(self.poll_s)
        if not messages:
            raise TimeoutError(f"no reply within {self.timeout_s}s")
        return "\n".join(messages)

    def _get(self, url, headers=None, params=None):
        response = self.session.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response

    def _post(self, url, headers, json=None):
        response = self.session.post(url, headers=headers, json=json, timeout=30)
        response.raise_for_status()
        return response
