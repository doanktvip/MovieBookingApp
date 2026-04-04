let countdownInterval = null;

document.addEventListener("DOMContentLoaded", function () {
    const timerContainer = document.getElementById('timer-container');

    let initialTime = parseInt(timerContainer.getAttribute('data-time-remaining')) || 0;

    if (initialTime > 0) {
        startHoldTimer(initialTime);
        renderUIFromExistingSelection();
    } else {
        document.querySelectorAll('.seat-check:checked').forEach(el => el.checked = false);
    }
});

function renderUIFromExistingSelection() {
    let selectedSeats = document.querySelectorAll('.seat-check:checked');
    let data = {
        seats: [],
        total_amount: 0
    };

    selectedSeats.forEach(seat => {
        let price = parseFloat(seat.getAttribute('data-price')) || 0;
        data.seats.push({
            "id": seat.value,
            "name": seat.getAttribute('data-seat-name'),
            "price": price
        });
        data.total_amount += price;
    });

    if (data.seats.length > 0) {
        renderBookingDetails(data);
    }
}

function startHoldTimer(initialSeconds) {
    let timeRemaining = initialSeconds;
    if (countdownInterval) clearInterval(countdownInterval);

    const timerContainer = document.getElementById('timer-container');
    const timerDisplay = document.getElementById('countdown-timer');

    if (timerContainer) {
        timerContainer.style.setProperty('display', 'block', 'important');
    }

    function updateDisplay() {
        if (timeRemaining <= 0) {
            handleExpiredSession();
            return;
        }

        let minutes = Math.floor(timeRemaining / 60);
        let seconds = timeRemaining % 60;
        if (timerDisplay) {
            timerDisplay.innerText = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        timeRemaining--;
    }
    updateDisplay();
    countdownInterval = setInterval(updateDisplay, 1000);
}

function updateBookingSummary(checkboxElement) {
    let selectedSeats = document.querySelectorAll('.seat-check:checked');

    // Chặn tối đa 8 ghế
    if (selectedSeats.length > 8) {
        showCustomAlert("Bạn chỉ được chọn tối đa 8 ghế!", "danger");
        if (checkboxElement) checkboxElement.checked = false;
        selectedSeats = document.querySelectorAll('.seat-check:checked');
    }

    let seatsDataToSend = [];
    selectedSeats.forEach(seat => {
        seatsDataToSend.push({
            "id": seat.value,
            "name": seat.getAttribute('data-seat-name'),
            "price": parseFloat(seat.getAttribute('data-price')) || 0
        });
    });

    fetch("/api/booking", {
        method: "POST",
        body: JSON.stringify({ "seats": seatsDataToSend }),
        headers: { "Content-Type": "application/json" }
    })
    .then(res => res.json())
    .then(data => {
        const timerContainer = document.getElementById('timer-container');

        if (data.expired) {
            handleExpiredSession();
            return;
        }

        if (data.time_remaining && data.time_remaining > 0) {
            if (timerContainer) timerContainer.style.display = 'block';
            startHoldTimer(data.time_remaining);
        } else {
            if (countdownInterval) clearInterval(countdownInterval);
            if (timerContainer) timerContainer.style.display = 'none';
        }

        renderBookingDetails(data);
    });
}

function renderBookingDetails(data) {
    const seatListDiv = document.getElementById('selected-seats-list');
    const detailsDiv = document.getElementById('booking-details');
    const seatCountSpan = document.getElementById('seat-count');
    const ticketPriceSpan = document.getElementById('ticket-price');
    const totalPriceSpan = document.getElementById('total-price');
    const btnCheckout = document.getElementById('btn-checkout');
    const hiddenTotalInput = document.getElementById('total_amount_hidden');

    if (data.seats && data.seats.length > 0) {
        let seatBlocksHtml = '';
        data.seats.forEach(seat => {
            seatBlocksHtml += `<div class="bg-danger text-white fw-bold rounded d-flex align-items-center justify-content-center seat-box" style="width:38px; height:38px; margin:2px;">${seat.name}</div>`;
        });

        seatListDiv.innerHTML = seatBlocksHtml;
        seatCountSpan.innerText = data.seats.length;
        const formattedTotal = new Intl.NumberFormat('vi-VN').format(data.total_amount) + ' đ';
        ticketPriceSpan.innerText = formattedTotal;
        totalPriceSpan.innerText = formattedTotal;

        if (hiddenTotalInput) hiddenTotalInput.value = data.total_amount;
        detailsDiv.classList.remove('d-none');
        btnCheckout.disabled = false;
        btnCheckout.classList.remove('opacity-50');
    } else {
        resetBookingUI();
    }
}

function resetBookingUI() {
    document.getElementById('selected-seats-list').innerHTML = '<span class="text-white-50">Chưa chọn ghế</span>';
    document.getElementById('booking-details').classList.add('d-none');
    document.getElementById('total-price').innerText = '0 đ';
    const btn = document.getElementById('btn-checkout');
    btn.disabled = true;
    btn.classList.add('opacity-50');
}

function handleExpiredSession() {
    if (countdownInterval) clearInterval(countdownInterval);
    const timerContainer = document.getElementById('timer-container');
    if (timerContainer) timerContainer.style.display = 'none';
    document.querySelectorAll('.seat-check').forEach(el => el.checked = false);
    resetBookingUI();

    showCustomAlert("Hết thời gian giữ ghế!", "danger");

    // Gọi API xóa và reload
    fetch("/api/clear-booking-session", { method: "POST" })
        .then(() => {
            setTimeout(() => {
                location.reload();
            }, 3000);
        });
}