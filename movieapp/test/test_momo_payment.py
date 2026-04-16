import pytest
import requests
from movieapp.momo_payment import create_momo_payment

def test_create_momo_payment_success(mocker):
    # Tạo đối tượng(Mocker) giả để gọi requests.post của momopayment
    mock_post = mocker.patch('movieapp.momo_payment.requests.post')

    #Kết qua trả về sau khi requests.post thành công
    mock_response = mocker.Mock()
    #Thiết lập giá trị giả để lấy dlieu lên
    mock_response.json.return_value = {
        "partnerCode": "MOMO",
        "orderId": "DDN-999",
        "payUrl": "https://test-payment.momo.vn/qr/example",
        "resultCode": 0,
        "message": "Successful."
    }
    mock_post.return_value = mock_response
    #Gọi hàm thực thi
    result = create_momo_payment(
        order_id="DDN-999",
        amount=200000,
        order_info="Test thanh toán",
        redirect_url="http://localhost/return",
        ipn_url="http://localhost/ipn",
        expire_minutes=15
    )
    assert result['resultCode'] == 0
    assert result['orderId'] == "DDN-999"
    assert "payUrl" in result

    # Kiểm tra xem dữ liệu gửi lên MoMo có đúng định dạng không
    # Lấy tham số json được truyền vào requests.post
    sent_json = mock_post.call_args.kwargs['json']
    assert sent_json['amount'] == "200000"
    assert sent_json['orderExpireTime'] == 15

def test_create_momo_payment_api_error(mocker):
    mock_post = mocker.patch('movieapp.momo_payment.requests.post')

    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "resultCode": 9000,
        "message": "Giao dịch đã tồn tại"
    }
    mock_post.return_value = mock_response
    result = create_momo_payment("DUP_ID", 1000, "Info", "url", "url", 5)
    assert result['resultCode'] == 9000
    assert "Giao dịch đã tồn tại" in result['message']



