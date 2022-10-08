import math
import textwrap
from typing import Tuple

from PIL import ImageFont, Image, ImageDraw
from PIL.ImageFont import FreeTypeFont

import constants
from constants import Participants
from models.whatsapp_text import WhatsappText
from whatsapp_page.elements.page_elements import WhatsappPageElement
from whatsapp_page.whatsapp_page import WhatsappPage


class ChatBox(WhatsappPageElement):
    FONT_PATH: str = f'{constants.RESOURCES_PATH}/ConsolasM.ttf'
    _BORDER_RADIUS: int = 15
    _ARROW_WIDTH: int = 12
    _TEXT_SPACING: int = 6
    _TEXT_BOX_PADDING: Tuple[int, int] = (106, 32)
    _GREEN_BOX_COLOR: Tuple[int, int, int] = (0, 92, 75)
    _BLACK_BOX_COLOR: Tuple[int, int, int] = (32, 44, 51)
    MIN_MARGIN: int = 5
    MAX_MARGIN: int = 30
    LETTERS_PER_LINE: int = 110
    PAGE_SIZE_WIDTH = WhatsappPage.INNER_PAGE_WIDTH
    MAX_BOX_WIDTH = math.ceil(0.75 * PAGE_SIZE_WIDTH)
    TEXT_MESSAGE_FONT: FreeTypeFont = ImageFont.truetype(FONT_PATH, size=24)
    DATETIME_FONT: FreeTypeFont = ImageFont.truetype(FONT_PATH, size=14)

    def __init__(self, text_msg: WhatsappText, consecutive_msg: bool = False) -> None:
        self.text_msg = text_msg
        self.consecutive_msg = consecutive_msg
        self.margin = ChatBox.MIN_MARGIN if consecutive_msg else ChatBox.MAX_MARGIN
        self.box_color = ChatBox._GREEN_BOX_COLOR if self.text_msg.sender.value == Participants.main_participant() \
            else ChatBox._BLACK_BOX_COLOR
        self.rendered = False
        self.img = None

    def render(self) -> Image:
        w, h = self.get_box_size(self.text_msg.message, ChatBox.TEXT_MESSAGE_FONT)
        box_size = w + ChatBox._TEXT_BOX_PADDING[0], h + ChatBox._TEXT_BOX_PADDING[1]
        centre = box_size[0] // 2, box_size[1] // 2
        img = Image.new(size=box_size, mode='RGBA')
        draw = ImageDraw.Draw(img)

        x0 = (centre[0] - (w + ChatBox._TEXT_BOX_PADDING[0]) // 2)
        y0 = (centre[1] - (h + ChatBox._TEXT_BOX_PADDING[1]) // 2)
        x1 = (centre[0] + (w + ChatBox._TEXT_BOX_PADDING[0]) // 2)
        y1 = (centre[1] + (h + ChatBox._TEXT_BOX_PADDING[1]) // 2)
        draw.rounded_rectangle((x0, y0, x1, y1), fill=self.box_color, radius=ChatBox._BORDER_RADIUS)

        self._add_text_message(ChatBox.TEXT_MESSAGE_FONT, draw)
        self._add_timestamp(ChatBox.DATETIME_FONT, draw, w, h)

        if not self.consecutive_msg:
            img = self._add_pointer(img)

        self.img = img
        self.rendered = True
        return img

    def _add_timestamp(self, time_stamp_font: FreeTypeFont, draw: ImageDraw,
                       box_width: float, box_height: float) -> None:
        x_offset, y_offset = 6, 8
        draw.text((box_width + ChatBox._TEXT_BOX_PADDING[0] - x_offset,
                   box_height + ChatBox._TEXT_BOX_PADDING[1] - y_offset),
                  self.get_formatted_time_text(),
                  fill='white',
                  anchor='rs',
                  font=time_stamp_font)

    def _add_text_message(self, font: FreeTypeFont, draw: ImageDraw) -> None:
        x_offset = y_offset = 20
        for line in self.text_msg.message.splitlines(keepends=False):
            for row in textwrap.wrap(line, width=ChatBox.LETTERS_PER_LINE, replace_whitespace=False):
                draw.text((x_offset, y_offset), row, fill='white', lign='left', font=font, embedded_color=True)
                y_offset += font.getsize(line)[1] + ChatBox._TEXT_SPACING

    def get_approximate_size(self):
        w, h = self.get_box_size(self.text_msg.message)
        box_size = w + ChatBox._TEXT_BOX_PADDING[0] + ChatBox._ARROW_WIDTH, h + ChatBox._TEXT_BOX_PADDING[1]
        return box_size

    @staticmethod
    def get_box_size(text_msg: str,
                     font: FreeTypeFont = ImageFont.truetype(FONT_PATH, size=24)) -> Tuple[float, float]:
        max_width = ChatBox.MAX_BOX_WIDTH
        lines = ''
        total_lines = 0
        for line in text_msg.splitlines(keepends=False):
            for row in textwrap.wrap(line, width=ChatBox.LETTERS_PER_LINE, replace_whitespace=False):
                lines += row + '\n'
                total_lines += 1

        image = Image.new("RGB", (3000, 3000))
        draw = ImageDraw.Draw(image)

        w, h = draw.multiline_textsize(text=text_msg, font=font, spacing=ChatBox._TEXT_SPACING)

        if w > max_width:
            width_bars = math.ceil(w / max_width)
            # height * width_bars + (line spacing * lines) + padding
            return max_width, (h + 2) * (width_bars + 1) + (total_lines * ChatBox._TEXT_SPACING) + 10
        else:
            return w, h + (total_lines * ChatBox._TEXT_SPACING) + 10

    def get_formatted_time_text(self) -> str:
        timestamp = self.text_msg.delivery_time
        return timestamp.strftime('%H:%M')

    def _add_pointer(self, img: Image) -> Image:
        img = img.convert('RGBA')
        pointer = 'arrow-right' if self.text_msg.sender.value == Participants.main_participant() else 'arrow-left'
        file_name = f'{constants.RESOURCES_PATH}/{pointer}.png'
        pointer_img = Image.open(file_name, 'r').convert('RGBA')
        bg_w, bg_h = pointer_img.size
        img_w, img_h = img.size

        offset = (img_w, 0) if self.text_msg.sender.value == Participants.main_participant() else (0, 0)

        new_size = img_w + bg_w, img_h
        layer = Image.new('RGBA', new_size, (255, 255, 255, 0))
        layer.paste(img, tuple(map(lambda x: math.ceil((x[0] - x[1]) / 2), zip(new_size, img.size))))
        layer.paste(pointer_img, offset, pointer_img)
        return layer

    def get_occupied_size(self) -> Tuple[int, int]:
        if self.rendered:
            w, h = self.img.size
            return w, h + self.margin
        else:
            raise Exception('Image not rendered')

    def get_simple_size(self) -> Tuple[int, int]:
        if self.rendered:
            return self.img.size
        else:
            raise Exception('Image not rendered')

    def show(self) -> None:
        if self.rendered:
            self.img.show()
        else:
            raise Exception('Image not rendered')

    def render_to_page(self, page: WhatsappPage, element_number: int, curr_height_offset: int) -> int:
        if not self.rendered:
            self.render()
        h_offset = WhatsappPage.INIT_COORDINATES[0]
        v_offset = curr_height_offset
        w, h = WhatsappPage.PAGE_SIZE
        if self.text_msg.sender.value == Participants.main_participant():
            h_offset = w - self.get_occupied_size()[0] - h_offset
            h_offset -= (ChatBox._ARROW_WIDTH if self.consecutive_msg else 0)
        else:
            h_offset += (ChatBox._ARROW_WIDTH if self.consecutive_msg else 0)
        if element_number > 0:
            v_offset += (ChatBox.MIN_MARGIN if self.consecutive_msg else ChatBox.MAX_MARGIN)
        page.img.paste(self.img, (h_offset, v_offset), self.img)

        return v_offset + self.get_simple_height()

    def get_type(self):
        return WhatsappPageElement.ElementType.CHAT_OBJECT

    def __len__(self) -> int:
        return self.get_occupied_height()
