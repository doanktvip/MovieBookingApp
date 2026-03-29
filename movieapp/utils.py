def stats_seats(booking):
    list_seats, total_amount = [], 0
    if booking:
        for b in booking.values():
            list_seats.append(b)
            total_amount += float(b.get('price', 0)) + float(b.get('surcharge', 0))
    return {
        'seats': list_seats,
        'total_amount': total_amount
    }
