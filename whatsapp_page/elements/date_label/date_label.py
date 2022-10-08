from copy import copy
from datetime import datetime
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

from whatsapp_page.elements.chat_box.chat_box import ChatBox
from whatsapp_page.elements.page_elements import WhatsappPageElement
from whatsapp_page.whatsapp_page import WhatsappPage


class DateLabel(WhatsappPageElement):
    LABEL_MARGIN: int = 30
    LABEL_SIZE: Tuple[int, int] = (160, 40)
    _BORDER_RADIUS: int = 10
    _LABEL_COLOR: Tuple[int, int, int] = (24, 34, 41)
    _LABEL_TEXT_COLOR: Tuple[int, int, int] = 130, 152, 168
    _LABEL_BOX: Image = Image.new(size=LABEL_SIZE, mode='RGBA')
    _LABEL_FONT: FreeTypeFont = ImageFont.truetype(ChatBox.FONT_PATH, size=18)

    def __init__(self, date_obj: datetime):
        self.date_obj = date_obj
        self.date_str = self.get_formatted_datetime()

    def render(self):
        text_box = copy(DateLabel._LABEL_BOX)
        draw = ImageDraw.Draw(text_box)

        x1 = DateLabel.LABEL_SIZE[0]
        y1 = DateLabel.LABEL_SIZE[1]
        draw.rounded_rectangle((0, 0, x1, y1), fill=DateLabel._LABEL_COLOR, radius=DateLabel._BORDER_RADIUS)
        w, h = draw.textsize(self.date_str, font=DateLabel._LABEL_FONT)
        draw.text(((x1 - w) // 2, (y1 - h) // 2), self.date_str, font=DateLabel._LABEL_FONT,
                  fill=DateLabel._LABEL_TEXT_COLOR)
        return text_box

    def render_to_page(self, page: WhatsappPage, element_number: int, curr_height_offset: int) -> int:
        text_box = self.render()
        w, h = WhatsappPage.PAGE_SIZE
        v_offset = curr_height_offset + DateLabel.LABEL_MARGIN
        h_offset = (w - DateLabel.LABEL_SIZE[0]) // 2
        page.img.paste(text_box, (h_offset, v_offset), text_box)

        return v_offset + self.get_simple_height() + DateLabel.LABEL_MARGIN

    def get_simple_size(self) -> Tuple[int, int]:
        return DateLabel.LABEL_SIZE

    def get_formatted_datetime(self) -> str:
        return self.date_obj.strftime('%d-%m-%Y')

    def get_occupied_size(self) -> Tuple[int, int]:
        w, h = DateLabel.LABEL_SIZE
        return w, h + DateLabel.LABEL_MARGIN

    def get_type(self):
        return WhatsappPageElement.ElementType.DATE_LABEL

    def __len__(self):
        return self.get_occupied_height()
