from enum import Enum

CHAT_PATH: str = '/resources/CompleteChat.txt'
OUTPUT_PATH: str = 'chat_dir/'
RESOURCES_PATH: str = 'resources'


class Participants(Enum):
    SHASHANK = "Shashank Ullas"
    SHRAVYA = "Shravya"

    @staticmethod
    def get_participant(sender: str):
        if Participants.SHASHANK.value.lower() == sender.lower():
            return Participants.SHASHANK
        else:
            return Participants.SHRAVYA

    @staticmethod
    def main_participant():
        return Participants.SHRAVYA.value
