import json
import uuid
import requests
import hmac
import hashlib

# Cấu hình API Key
MOMO_ENDPOINT = "https://test-payment.momo.vn/v2/gateway/api/create"
PARTNER_CODE = "MOMO"
ACCESS_KEY = "F8BBA842ECF85"
SECRET_KEY = "K951B6PE1waDMi640xX08PD3vg6EkVlz"

def create_momo_payment(order_id, amount, order_info, redirect_url, ipn_url,expire_minutes):
    request_id = str(uuid.uuid4())
    request_type = "captureWallet"
    extra_data = "" # Có thể truyền thêm dữ liệu chuỗi tại đây
    amount_str = str(int(amount)) # MoMo yêu cầu số tiền là chuỗi (string) không có số thập phân

    # 1. Tạo chuỗi ký tự theo chuẩn MoMo yêu cầu
    raw_signature = f"accessKey={ACCESS_KEY}&amount={amount_str}&extraData={extra_data}&ipnUrl={ipn_url}&orderId={order_id}&orderInfo={order_info}&partnerCode={PARTNER_CODE}&redirectUrl={redirect_url}&requestId={request_id}&requestType={request_type}"

    # 2. Mã hóa chữ ký bằng HMAC SHA256
    h = hmac.new(bytes(SECRET_KEY, 'utf-8'), bytes(raw_signature, 'utf-8'), hashlib.sha256)
    signature = h.hexdigest()

    # 3. Gói dữ liệu gửi lên MoMo
    data = {
        'partnerCode': PARTNER_CODE,
        'partnerName': "DDN Cinema",
        'storeId': "MomoTestStore",
        'requestId': request_id,
        'amount': amount_str,
        'orderId': order_id,
        'orderInfo': order_info,
        'redirectUrl': redirect_url,
        'ipnUrl': ipn_url,
        'lang': "vi",
        'extraData': extra_data,
        'requestType': request_type,
        'signature': signature,
        'orderExpireTime': expire_minutes
    }

    # 4. Gửi Request và nhận kết quả
    response = requests.post(MOMO_ENDPOINT, json=data)
    return response.json()