import os
from asyncio import Future
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

from tqdm import tqdm

import constants
from whatsapp_page.elements.chat_box.chat_box import ChatBox
from whatsapp_page.elements.date_label.date_label import DateLabel
from whatsapp_page.elements.page_elements import WhatsappPageElement
from whatsapp_page.whatsapp_page import WhatsappPage

futures: List[Future] = []


def save_all(pages: List[WhatsappPage], offset: int) -> None:
    global futures
    with ThreadPoolExecutor() as executor:
        for page_number, page in enumerate(pages):
            futures.append(executor.submit(WhatsappPaginator.save_page, page, page_number + 1 + offset))


class WhatsappPaginator:
    @staticmethod
    def get_pages(all_texts: List[ChatBox], save: bool = False) -> Optional[List[WhatsappPage]]:
        global futures
        pages = []
        remaining_texts = all_texts
        total_texts = len(remaining_texts)
        curr_page_number, offset = 0, 0
        print('Getting pages...\n', flush=True)
        progress_bar = tqdm(total=total_texts)
        while remaining_texts:
            new_page = WhatsappPaginator.split_page(remaining_texts)
            curr_page_number += 1
            progress_bar.update(new_page.get_chat_items())
            pages.append(new_page)
            if save and len(pages) == 100:
                save_all(pages, offset)
                offset += len(pages)
                pages = []
        if save and len(pages) > 0:
            save_all(pages, offset)
            offset += len(pages)
            pages = []
        progress_bar.close()
        if not save:
            return pages
        else:
            print('Waiting for all jobs to complete...\n', flush=True)
            for future in tqdm(futures):
                future.result()

    @staticmethod
    def split_page(texts: List[ChatBox]) -> WhatsappPage:
        page_texts: List[WhatsappPageElement] = []

        curr_length = 0
        previous_date = None
        previous_text: Optional[ChatBox] = None
        while texts:
            text_box = texts[0]
            curr_length += text_box.get_approximate_size()[1] + \
                           WhatsappPaginator.get_chat_margin(text_box, previous_text)
            curr_date = text_box.text_msg.delivery_time.date()
            if curr_date != previous_date:
                curr_length += DateLabel.LABEL_SIZE[1] + (DateLabel.LABEL_MARGIN * 2)
            if curr_length > WhatsappPage.INNER_PAGE_HEIGHT:
                break
            texts.pop(0)
            if curr_date != previous_date:
                date_label = DateLabel(text_box.text_msg.delivery_time)
                page_texts.append(date_label)
            page_texts.append(text_box)
            previous_date = curr_date
            previous_text = text_box

        return WhatsappPage(page_texts)

    @staticmethod
    def save_page(new_page: WhatsappPage, page_number: int) -> None:
        save_path = constants.OUTPUT_PATH
        if not os.path.exists(save_path):
            os.makedirs(save_path, exist_ok=True)

        file_name = os.path.join(save_path, f'{page_number}.png')
        new_page.save(file_name)

    @staticmethod
    def get_chat_margin(text_box: ChatBox, previous_text: Optional[ChatBox]):
        if previous_text is None or text_box.text_msg.sender != previous_text.text_msg.sender:
            return ChatBox.MAX_MARGIN
        return ChatBox.MIN_MARGIN
