from datetime import datetime

from constants import Participants


class WhatsappText:
    def __init__(self, message: str, delivery_time: datetime, sender: Participants) -> None:
        self.message = message
        self.delivery_time = delivery_time
        self.sender = sender

    def __repr__(self) -> str:
        return f'{self.sender.value} ({self.delivery_time}): {self.message}'
