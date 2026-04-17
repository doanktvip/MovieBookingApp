from wtforms import Form, StringField
from movieapp.admin import CKTextAreaWidget


# TEST: CKTextAreaWidget
def test_ck_text_area_widget_coverage():
    # Tạo một form thật sử dụng chính widget của bạn để test
    class DummyForm(Form):
        desc = StringField('Description', widget=CKTextAreaWidget())

    form = DummyForm()

    # Nhánh 1: Trường hợp KHÔNG truyền class
    html_no_class = form.desc()
    assert 'class="ckeditor"' in html_no_class

    # Nhánh 2: Trường hợp CÓ truyền class từ trước
    html_with_class = form.desc(class_="my-custom-class")
    assert 'class="my-custom-class ckeditor"' in html_with_class
