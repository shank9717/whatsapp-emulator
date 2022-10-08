from enum import Enum
from typing import Tuple

from whatsapp_page.whatsapp_page import WhatsappPage


class WhatsappPageElement:
    MAX_ELEMENT_HEIGHT = 600

    class ElementType(Enum):
        CHAT_OBJECT = 1
        DATE_LABEL = 2

    def get_type(self) -> ElementType:
        raise NotImplementedError()

    def render_to_page(self, page: WhatsappPage, element_number: int, curr_height_offset: int) -> int:
        raise NotImplementedError()

    def get_simple_size(self) -> Tuple[int, int]:
        raise NotImplementedError()

    def get_simple_height(self) -> int:
        return self.get_simple_size()[1]

    def get_simple_width(self) -> int:
        return self.get_simple_size()[0]

    def get_occupied_size(self) -> Tuple[int, int]:
        raise NotImplementedError()

    def get_occupied_width(self) -> int:
        return self.get_occupied_size()[0]

    def get_occupied_height(self) -> int:
        return self.get_occupied_size()[1]
