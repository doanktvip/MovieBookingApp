// ==========================================
// 1. HÀM TẠO THÔNG BÁO JAVASCRIPT (GLOBAL)
// ==========================================
function showCustomAlert(message, category = 'danger') {
    const container = document.getElementById('js-alert-container');
    if (!container) return;

    let iconHtml = category === 'success'
        ? '<i class="bi bi-check-circle-fill me-2 fs-5 text-success"></i>'
        : '<i class="bi bi-exclamation-circle-fill me-2 fs-5 text-danger"></i>';

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${category} alert-dismissible fade show d-flex align-items-center shadow-lg mb-2`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${iconHtml}
        <div class="fw-bold">${message}</div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    container.prepend(alertDiv);

    // Tự động đóng thông báo do JS tạo ra sau 3 giây
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 150);
    }, 3000);
}
// ==========================================
// HÀM GỌI API ĐĂNG NHẬP
// ==========================================
function loginUser(username, password, nextUrl = '/') {
    fetch("/api/login", {
        method: "post",
        body: JSON.stringify({
            "username": username,
            "password": password
        }),
        headers: {
            "Content-Type": "application/json"
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            addPendingAlert(data.message, 'success')

            window.location.href = nextUrl;
        } else {
            showCustomAlert(data.message, "danger");
        }
    })
    .catch(error => {
        console.error('Lỗi khi gọi API:', error);
        showCustomAlert("Lỗi kết nối đến máy chủ. Vui lòng thử lại!", "danger");
    });
}

// ==========================================
// HÀM GỌI API ĐĂNG KÝ (VÀ TỰ ĐỘNG ĐĂNG NHẬP)
// ==========================================
function registerUser(username, email, password, confirm_password) {
    fetch("/api/register", {
        method: "post",
        body: JSON.stringify({
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": confirm_password
        }),
        headers: {
            "Content-Type": "application/json"
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            showCustomAlert(data.message, 'success');
            const loginTabBtn = document.getElementById('tab-login');
            if (loginTabBtn) {
                const tab = new bootstrap.Tab(loginTabBtn);
                tab.show();
            }
        } else {
            showCustomAlert(data.message, "danger");
        }
    })
    .catch(error => {
        console.error('Lỗi khi gọi API:', error);
        showCustomAlert("Lỗi kết nối đến máy chủ. Vui lòng thử lại!", "danger");
    });
}

function addPendingAlert(message, type = 'success') {
    let alerts = JSON.parse(sessionStorage.getItem('pendingAlerts') || "[]");
    alerts.push({ message: message, type: type });
    sessionStorage.setItem('pendingAlerts', JSON.stringify(alerts));
}

// ==========================================
// 2. XỬ LÝ SỰ KIỆN KHI TRANG VỪA LOAD XONG
// ==========================================
document.addEventListener("DOMContentLoaded", function() {
    
    // --- A. Tự động đóng thông báo của Flask (Flash messages) sau 3 giây ---
    // Chỉ lấy những thông báo có sẵn khi vừa load trang để không đóng nhầm thông báo của JS
    let serverAlerts = document.querySelectorAll('.alert:not(#timer-container)');
    if (serverAlerts.length > 0) {
        setTimeout(function() {
            serverAlerts.forEach(function(alertNode) {
                // Kiểm tra xem alert đã bị người dùng bấm x tắt trước đó chưa
                if (document.body.contains(alertNode)) {
                    let bsAlert = new bootstrap.Alert(alertNode);
                    bsAlert.close();
                }
            });
        }, 3000);
    }

    // Thông báo hiển thị ở đây
    const pendingAlerts = JSON.parse(sessionStorage.getItem('pendingAlerts') || "[]");

    if (pendingAlerts.length > 0) {
        pendingAlerts.forEach((alert, index) => {
            setTimeout(() => {
                showCustomAlert(alert.message, alert.type);
            }, index * 100);
        });

        sessionStorage.removeItem('pendingAlerts');
    }
});