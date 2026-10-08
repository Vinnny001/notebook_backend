from dataclasses import dataclass


@dataclass(frozen=True)
class EmailMessage:
    to: str
    subject: str
    body: str


class EmailProvider:
    def send(self, message: EmailMessage) -> None:
        print(f"email queued to={message.to} subject={message.subject}")
