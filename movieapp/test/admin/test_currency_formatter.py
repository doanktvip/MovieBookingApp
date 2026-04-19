from movieapp.admin import currency_formatter


# TEST: currency_formatter
def test_currency_formatter_coverage():
    # Tạo một object giả lập Model trong Database
    class DummyModel:
        pass

    m = DummyModel()

    # Nhánh 1: Có giá trị
    m.price = 1500000
    result_truy_cap = currency_formatter(None, None, m, 'price')
    assert result_truy_cap == '1.500.000 VNĐ'

    # Nhánh 2: Giá trị rỗng (None)
    m.price = None
    result_rong = currency_formatter(None, None, m, 'price')
    assert result_rong == '0 VNĐ'

    #  Nhánh 3: Giá trị bằng 0
    m.price = 0
    result_khong = currency_formatter(None, None, m, 'price')
    assert result_khong == '0 VNĐ'
