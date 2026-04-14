// --- BOOKING.JS ---

// 1. Hàm tính toán và cập nhật giao diện (Không gọi API)
function updateBookingSummary() {
    const selectedSeats = document.querySelectorAll('.seat-check:checked');
    let totalAmount = 0;
    let seatNames = [];

    // Chặn ngay lập tức nếu chọn quá 8 ghế
    if (selectedSeats.length > 8) {
        showCustomAlert("Bạn chỉ được chọn tối đa 8 ghế cho mỗi suất chiếu!");
        event.target.checked = false; // Tự động bỏ tick ghế vừa bấm
        return updateBookingSummary(); // Tính toán lại
    }

    selectedSeats.forEach(seat => {
        totalAmount += (parseFloat(seat.getAttribute('data-price')) || 0);
        seatNames.push(`<div class="bg-danger text-white fw-bold rounded d-flex align-items-center justify-content-center seat-box" style="width:38px; height:38px; margin:2px;">${seat.getAttribute('data-seat-name')}</div>`);
    });

    // Cập nhật các con số trên màn hình
    document.getElementById('seat-count').innerText = selectedSeats.length;
    document.getElementById('ticket-price').innerText = new Intl.NumberFormat('vi-VN').format(totalAmount) + ' đ';
    document.getElementById('total-price').innerText = new Intl.NumberFormat('vi-VN').format(totalAmount) + ' đ';
    document.getElementById('total_amount_hidden').value = totalAmount;

    // Bật/tắt nút Đặt ghế
    const btnBook = document.getElementById('btn-book-seats');
    const detailsDiv = document.getElementById('booking-details');
    const seatListDiv = document.getElementById('selected-seats-list');

    if (selectedSeats.length > 0) {
        seatListDiv.innerHTML = seatNames.join('');
        detailsDiv.classList.remove('d-none');
        btnBook.disabled = false;
        btnBook.classList.remove('opacity-50');
    } else {
        seatListDiv.innerHTML = '<span class="text-white-50">Chưa chọn ghế</span>';
        detailsDiv.classList.add('d-none');
        btnBook.disabled = true;
        btnBook.classList.add('opacity-50');
    }
}

// 2. Hàm DUY NHẤT gọi API khi nhấn nút Đặt ghế
function handleBooking() {
    const selectedSeats = document.querySelectorAll('.seat-check:checked');
    const showtimeId = document.querySelector('input[name="showtime_id"]').value;

    if (selectedSeats.length === 0) {
        showCustomAlert("Vui lòng chọn ít nhất 1 ghế!");
        return;
    }

    // Thu thập ID các ghế đã chọn
    let seatsDataToSend = Array.from(selectedSeats).map(seat => ({
        "id": seat.value,
        "name": seat.getAttribute('data-seat-name')
    }));

    // Khóa nút để tránh bấm 2 lần
    const btnBook = document.getElementById('btn-book-seats');
    btnBook.disabled = true;
    btnBook.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Đang xử lý...';

    // Gửi dữ liệu lên Backend kiểm tra ràng buộc
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
        if (data.status === "error") {
            // Hiển thị lỗi từ backend (Ví dụ: ghế đã bị mua, quá 8 ghế, phim đã chiếu)
            addPendingAlert(data.message,'danger');

            // Khôi phục lại nút bấm
            btnBook.disabled = false;
            btnBook.innerHTML = 'Đặt ghế';

            // Nếu lỗi do ghế bị người khác lấy mất, tự động tải lại trang để cập nhật bản đồ ghế
            if (data.message.includes("người khác")) {
                location.reload();
            }
        } else {
            // Nếu qua được hết ràng buộc Backend -> Tự động submit form để sang trang Thanh toán
            document.querySelector('form').submit();
        }
    })
    .catch(err => {
        console.error(err);
        showCustomAlert("Lỗi kết nối máy chủ, vui lòng thử lại!");
        btnBook.disabled = false;
        btnBook.innerHTML = 'Đặt ghế';
    });
}