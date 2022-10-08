from copy import copy
from typing import List, Tuple

from PIL import Image

import constants


class WhatsappPage:
    _PADDINGS: Tuple[int, int] = [10, 30]
    _BACKGROUND_IMG_PATH: str = f'{constants.RESOURCES_PATH}/2224392.png'
    _BACKGROUND_IMG: Image = Image.open(_BACKGROUND_IMG_PATH)
    INIT_COORDINATES: Tuple[int, int] = 10, 20
    PAGE_SIZE: Tuple[int, int] = _BACKGROUND_IMG.size
    INNER_PAGE_WIDTH: int = PAGE_SIZE[0] - (_PADDINGS[0] * 2)
    INNER_PAGE_HEIGHT: int = PAGE_SIZE[1] - (_PADDINGS[1] * 2)

    def __init__(self, text_boxes: List['WhatsappPageElement']) -> None:
        self.text_boxes: List['WhatsappPageElement'] = text_boxes
        self.img: Image = copy(WhatsappPage._BACKGROUND_IMG)
        self.rendered = False

    def render_page(self) -> Image:
        curr_offset = WhatsappPage.INIT_COORDINATES[1]
        for idx, text_box in enumerate(self.text_boxes):
            curr_offset = text_box.render_to_page(self, idx, curr_offset)
        self.rendered = True
        return self.img

    def show(self):
        if self.rendered:
            self.img.show()
        else:
            self.render_page().show()

    def get_chat_items(self) -> int:
        return sum(obj.get_type().value == 1 for obj in self.text_boxes)

    def save(self, file_name):
        if self.rendered:
            self.img.save(file_name, format='png')
        else:
            self.render_page().save(file_name, format='png')
