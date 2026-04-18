import re

import unicodedata


def stats_seats(booking):
    list_seats, total_amount = [], 0
    if booking:
        for b in booking.values():
            list_seats.append(b)
            total_amount += float(b.get('price', 0))
    return {
        'seats': list_seats,
        'total_amount': total_amount
    }


def format_api_response_fail(message, status='error'):
    return {
        "status": status,
        "message": message
    }


def slugify(text):
    # Loại bỏ dấu tiếng Việt và dấu câu
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    # Xóa ký tự đặc biệt và viết thường
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    # Gắn kết các từ bằng dấu gạch ngang
    text = re.sub(r'[-\s]+', '-', text)
    return text


def get_vn_weekday(d):
    weekdays = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
    return weekdays[d.weekday()]
