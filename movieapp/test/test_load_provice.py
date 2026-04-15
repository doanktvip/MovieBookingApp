import pytest
from movieapp.dao import load_provinces
from movieapp.test.test_base import test_session, test_app, sample_basic_setup


def test_load_provinces_success(sample_basic_setup):
    """Kiểm tra tải danh sách tỉnh từ Tầng 1"""
    result = load_provinces()

    # Kiểm tra số lượng (p_hcm, p_hn)
    assert len(result) == 2

    result_names = [p.name for p in result]
    # Phải dùng đúng chuỗi ký tự trong test_base.py
    assert "TP.HCM" in result_names
    assert "Hà Nội" in result_names


def test_load_provinces_empty(test_app):
    """Kiểm tra khi DB trống"""
    result = load_provinces()
    assert len(result) == 0
