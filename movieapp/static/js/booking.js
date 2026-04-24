let confirmedSeats = new Set();

document.addEventListener('DOMContentLoaded', function() {
    const initialChecked = document.querySelectorAll('.seat-check:checked');
    initialChecked.forEach(seat => confirmedSeats.add(seat.value));

    updateBookingSummary();
});

function updateBookingSummary(element) {
    const selectedSeats = document.querySelectorAll('.seat-check:checked');
    const prevTicketsCount = parseInt(document.getElementById('prev_tickets_count').value) || 0;
    const maxAllowed = 8 - prevTicketsCount;
    if (selectedSeats.length > maxAllowed) {
        if (maxAllowed === 0) {
            showCustomAlert("Bạn đã đặt tối đa 8 ghế cho suất chiếu này!");
        } else {
            showCustomAlert(`Bạn chỉ được chọn thêm tối đa ${maxAllowed} ghế!`);
        }

        if (element) element.checked = false;
        return updateBookingSummary();
    }
    let totalAmount = 0;
    let seatNames = [];

    if (element && !element.checked) {
        if (confirmedSeats.has(element.value)) {
            releaseSingleSeat(element.value);
            confirmedSeats.delete(element.value);
        }
    }

    selectedSeats.forEach(seat => {
        totalAmount += (parseFloat(seat.getAttribute('data-price')) || 0);
        seatNames.push(`<div class="bg-danger text-white fw-bold rounded d-flex align-items-center justify-content-center seat-box" style="width:38px; height:38px; margin:2px;">${seat.getAttribute('data-seat-name')}</div>`);
    });

    // Cập nhật giao diện
    document.getElementById('seat-count').innerText = selectedSeats.length;
    document.getElementById('total-price').innerText = new Intl.NumberFormat('vi-VN').format(totalAmount) + ' đ';
    document.getElementById('ticket-price').innerText = new Intl.NumberFormat('vi-VN').format(totalAmount) + ' đ';
    document.getElementById('total_amount_hidden').value = totalAmount;

    const btnBook = document.getElementById('btn-book-seats');
    if (selectedSeats.length > 0) {
        document.getElementById('selected-seats-list').innerHTML = seatNames.join('');
        document.getElementById('booking-details').classList.remove('d-none');
        btnBook.disabled = false;
        btnBook.classList.remove('opacity-50');
    } else {
        document.getElementById('selected-seats-list').innerHTML = '<span class="text-white-50">Chưa chọn ghế</span>';
        document.getElementById('booking-details').classList.add('d-none');
        btnBook.disabled = true;
        btnBook.classList.add('opacity-50');
    }
}

function handleBooking() {
    const selectedSeats = document.querySelectorAll('.seat-check:checked');
    const showtimeId = document.querySelector('input[name="showtime_id"]').value;

    if (selectedSeats.length === 0) return;

    let seatsDataToSend = Array.from(selectedSeats).map(seat => ({
        "id": seat.value,
        "name": seat.getAttribute('data-seat-name')
    }));

    const btnBook = document.getElementById('btn-book-seats');
    btnBook.disabled = true;
    btnBook.innerHTML = 'Đang xử lý...';

    fetch("/api/booking", {
        method: "POST",
        body: JSON.stringify({
            "showtime_id": showtimeId,
            "seats": seatsDataToSend
        }),
        headers: { "Content-Type": "application/json" }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            // SAU KHI ĐẶT THÀNH CÔNG: Cập nhật danh sách confirmedSeats
            selectedSeats.forEach(seat => confirmedSeats.add(seat.value));
            window.location.href = data.redirect_url;
            // Tùy chọn: Chuyển trang hoặc giữ lại tùy luồng của bạn
            document.querySelector('form').submit();
        } else {
            showCustomAlert(data.message);
            btnBook.disabled = false;
            btnBook.innerHTML = 'Đặt ghế';
            if (data.message.includes("người khác")) location.reload();
        }
    });
}

function releaseSingleSeat(seatId) {
    fetch("/api/release-seat", {
        method: "POST",
        body: JSON.stringify({ "seat_id": seatId }),
        headers: { "Content-Type": "application/json" }
    }).catch(err => console.error("Lỗi giải phóng ghế:", err));
}