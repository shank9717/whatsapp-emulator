import datetime
import re
import textwrap
from typing import List

from tqdm import tqdm

from constants import Participants, CHAT_PATH
from models.whatsapp_text import WhatsappText
from whatsapp_page.elements.chat_box.chat_box import ChatBox
from whatsapp_page.elements.page_elements import WhatsappPageElement
from whatsapp_page.whatsapp_paginator import WhatsappPaginator


def load_chat(filename):
    with open(filename, encoding='utf-8') as f:
        return f.read()


def get_sent_time(sent_time: str, previous_time: datetime.datetime) -> datetime.datetime:
    sent_time1 = None
    try:
        sent_time1 = datetime.datetime.strptime(sent_time, '%d/%m/%Y, %H:%M')
        if sent_time1 is None:
            print('')
        if sent_time1.microsecond - previous_time.microsecond < 0:
            sent_time1 = None
    except ValueError:
        pass
    try:
        sent_time2 = datetime.datetime.strptime(sent_time, '%m/%d/%Y, %H:%M')
        if sent_time1 is None:
            return sent_time2
        if sent_time2.microsecond - previous_time.microsecond < 0:
            return sent_time1
    except ValueError:
        return sent_time1

    if sent_time1.microsecond - previous_time.microsecond < sent_time2.microsecond - previous_time.microsecond:
        return sent_time1
    else:
        return sent_time2


def split(message: str) -> List[str]:
    smaller_messages = []
    curr_msg_part = ''
    for line in message.splitlines(keepends=False):
        for row in textwrap.wrap(line, width=ChatBox.LETTERS_PER_LINE, replace_whitespace=False):
            estimated_size = ChatBox.get_box_size(curr_msg_part + row + '\n')
            estimated_height = estimated_size[1]
            if estimated_height < WhatsappPageElement.MAX_ELEMENT_HEIGHT:
                curr_msg_part += row + '\n'
                continue
            smaller_messages.append(curr_msg_part)
            curr_msg_part = row + '\n'

    if curr_msg_part:
        smaller_messages.append(curr_msg_part)
    return smaller_messages


def add_new_text(all_texts: List[ChatBox], message: str, sent_time: datetime,
                 sender: Participants, previous_sender: Participants) -> None:
    new_text = WhatsappText(message=message, delivery_time=sent_time, sender=sender)

    chat_box = ChatBox(new_text, (sender == previous_sender))
    all_texts.append(chat_box)


def parse_chat(chat_text: str, limit: int = float('inf')) -> List[ChatBox]:
    all_texts = []
    first_message_timestamp, first_message_time_format = '15/05/2016, 15:50', '%d/%m/%Y, %H:%M'
    pattern = r'(\d{2}\/\d{2}\/\d{4}, \d{2}:\d{2}) - (' + \
              Participants.SHRAVYA.value + '|' + Participants.SHASHANK.value + \
              r'): (.*?)(?=\d{2}\/\d{2}\/\d{4}, \d{2}:\d{2})'
    parsed_list = re.findall(pattern, chat_text, re.S | re.M)
    parsed_list = parsed_list if limit > len(parsed_list) else parsed_list[:limit]
    previous_time = datetime.datetime.strptime(first_message_timestamp, first_message_time_format)
    previous_sender = None
    for (sent_time, sender, message) in tqdm(parsed_list, total=len(parsed_list), position=0, leave=True):
        sent_time, sender, message = get_sent_time(sent_time, previous_time), \
                                     Participants.get_participant(sender), \
                                     message.rstrip()
        estimated_size = ChatBox.get_box_size(message)
        estimated_height = estimated_size[1]
        if estimated_height > WhatsappPageElement.MAX_ELEMENT_HEIGHT:
            messages = split(message)
            for small_message in messages:
                add_new_text(all_texts, small_message, sent_time, sender, previous_sender)
                previous_sender = sender
        else:
            add_new_text(all_texts, message, sent_time, sender, previous_sender)

        previous_time, previous_sender = sent_time, sender

    return all_texts


def main():
    print('Reading chat into memory...', flush=True)
    chat_text = load_chat(CHAT_PATH)
    print('Loaded chat...', flush=True)
    print('Parsing chats...', flush=True)
    all_texts = parse_chat(chat_text, limit=500)
    print('Parsed through chats...', flush=True)
    WhatsappPaginator.get_pages(all_texts, save=True)


if __name__ == '__main__':
    main()
