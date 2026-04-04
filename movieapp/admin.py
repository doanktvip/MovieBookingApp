from flask import redirect, url_for, request, jsonify
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from markupsafe import Markup
from wtforms import StringField, TextAreaField, FileField
from wtforms.widgets import TextArea
from movieapp import app, db, dao
from movieapp.models import (
    User, UserRole, Genre, Movie, Room, Seat, SeatType,
    MovieFormat, Showtime, ShowtimeSeat, Booking, Ticket, Cinema, Province
)


@app.route('/api/add_province_quick', methods=['POST'])
def add_province_quick():
    data = request.get_json()
    name = data.get('name', '')

    if not name.strip():
        return jsonify({'message': 'Tên không được để trống'}), 400

    try:
        province = dao.get_or_create_province(name)

        if province:
            return jsonify({
                'id': province.id,
                'name': province.name
            })

    except Exception as e:
        return jsonify({'message': str(e)}), 500


class MapPreviewWidget(object):
    def __call__(self, field, **kwargs):
        # field.id thường là 'map_url' trong Flask-Admin
        return Markup(f"""
            <input id="{field.id}" name="{field.name}" type="text" value="{field.data or ''}" class="form-control" readonly placeholder="URL sẽ tự động xuất hiện tại đây...">
            <div class="mt-2">
                <button type="button" class="btn btn-sm btn-warning" onclick="previewMap()">
                    <i class="fa fa-search-plus"></i> Kiểm tra vị trí này
                </button>
            </div>

            <script>
                (function() {{
                    // Lấy các phần tử dựa trên ID mặc định của Flask-Admin
                    var nameInput = document.getElementById('name');
                    var addrInput = document.getElementById('address');
                    var urlInput = document.getElementById('{field.id}');

                    function generateUrl() {{
                        var name = nameInput.value.trim();
                        var address = addrInput.value.trim();

                        if (name && address) {{
                            // Tạo chuỗi tìm kiếm và mã hóa URL
                            var query = encodeURIComponent(name + " " + address);
                            var finalUrl = "https://www.google.com/maps/search/?api=1&query=" + query;

                            // Đẩy giá trị vào ô Xác nhận bản đồ
                            urlInput.value = finalUrl;
                        }} else {{
                            urlInput.value = "";
                        }}
                    }}

                    // Lắng nghe sự kiện gõ phím trên cả 2 ô
                    if (nameInput) nameInput.addEventListener('input', generateUrl);
                    if (addrInput) addrInput.addEventListener('input', generateUrl);
                }})();

                function previewMap() {{
                    var url = document.getElementById('{field.id}').value;
                    if (!url) {{
                        alert('Vui lòng nhập Tên Rạp và Địa chỉ để tạo link trước!');
                        return;
                    }}
                    window.open(url, '_blank');
                }}
            </script>
        """)


class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


def currency_formatter(view, context, model, name):
    value = getattr(model, name)
    if value:
        return f"{int(value):,} VNĐ".replace(',', '.')
    return '0 VNĐ'


class AdminAuthMixin:
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))


class BaseModelView(AdminAuthMixin, ModelView):
    # Nổi cái modal lên thay vì chuyển trang
    edit_modal = True
    # Ẩn các cột hệ thống mặc định khỏi bảng hiển thị
    column_exclude_list = ['created_at', 'updated_at']


class ProvinceView(BaseModelView):
    column_searchable_list = ['name']
    form_columns = ['name', 'cinemas']
    column_labels = {'name': 'Tỉnh/Thành phố', 'cinemas': 'Các rạp'}


class CinemaView(BaseModelView):
    create_template = 'admin/cinema_create_custom.html'
    edit_template = 'admin/cinema_create_custom.html'
    # Cấu hình tạo Phòng ngay trong Rạp (Inline Model)
    inline_models = [
        (Room, dict(
            form_columns=['id', 'name', 'capacity'],
            column_labels={
                'name': 'Tên phòng chiếu',
                'capacity': 'Sức chứa (số ghế)'
            }
        ))
    ]
    # Cấu hình danh sách hiển thị
    column_list = ['name', 'address', 'map_url', 'hotline', 'province']
    column_searchable_list = ['name', 'address']
    # Cấu hình Form nhập liệu
    form_columns = ['name', 'address', 'map_url', 'hotline', 'province']
    # Việt hóa nhãn (Dùng chữ thuần để bộ lọc Filter không bị lỗi hiển thị mã code)
    column_labels = {
        'name': 'Tên Rạp',
        'address': 'Địa chỉ',
        'hotline': 'Số điện thoại',
        'map_url': 'Bản đồ',
        'province': 'Tỉnh / Thành phố',
        'rooms': 'Phòng chiếu'
    }
    # Cấu hình chi tiết cho từng trường trong Form
    form_overrides = {
        'map_url': StringField
    }

    form_args = {
        'map_url': {
            'widget': MapPreviewWidget(),
            'label': 'Xác nhận bản đồ'
        },
        'province': {
            'label': Markup(
                'Tỉnh / Thành phố '
                '<button type="button" class="btn btn-xs btn-success" style="margin-left:5px" onclick="showAddProvince()">'
                '<i class="fa fa-plus"></i> Thêm nhanh</button>'
            )
        }
    }

    def _format_map_url(view, context, model, name):
        if not model.map_url:
            return ''
        html = f'<a href="{model.map_url}" target="_blank" class="btn btn-sm btn-outline-info"><i class="fa fa-map-marker"></i> Xem</a>'
        return Markup(html)

    column_formatters = {
        'map_url': _format_map_url
    }

    def on_model_change(self, form, model, is_created):
        if model.name and model.address:
            query = f"{model.name} {model.address}"
            model.map_url = f"https://www.google.com/maps/search/?api=1&query={query.replace(' ', '+')}"


class RoomView(BaseModelView):
    column_searchable_list = ['name']
    column_editable_list = ['name']
    column_list = ['name', 'capacity', 'cinema']
    form_columns = ['name', 'capacity', 'cinema']
    column_labels = {'name': 'Tên phòng', 'capacity': 'Sức chứa', 'cinema': 'Thuộc Rạp'}


class SeatTypeView(BaseModelView):
    column_labels = {'name': 'Loại ghế', 'surcharge': 'Phụ thu'}
    form_columns = ['name', 'surcharge']
    column_formatters = {
        'surcharge': currency_formatter
    }
    column_editable_list = ['surcharge']

    def after_model_change(self, form, model, is_created):
        if not is_created:
            success = dao.update_future_showtime_seats_price(model.id, model.surcharge)
            if not success:
                pass


class SeatView(BaseModelView):
    column_list = ['seat_number', 'row', 'col', 'seat_type', 'room']
    form_columns = ['seat_number', 'row', 'col', 'seat_type', 'room']
    column_labels = {
        'room': 'Phòng chiếu', 'seat_number': 'Số ghế',
        'row': 'Hàng', 'col': 'Cột', 'seat_type': 'Loại ghế'
    }


class GenreView(BaseModelView):
    column_searchable_list = ['name']
    form_columns = ['name', 'movies']
    column_labels = {'name': 'Tên thể loại', 'movies': 'Danh sách phim'}


class MovieFormatView(BaseModelView):
    column_labels = {'name': 'Định dạng (2D, 3D...)', 'showtimes': 'Những suất chiếu'}
    form_columns = ['name', 'showtimes']


class MovieView(BaseModelView):
    edit_modal = False
    column_searchable_list = ['name']
    column_filters = ['release_date', 'is_active', 'rate']

    # 1. Ẩn trường image (dạng text gốc), showtimes, và các trường tự động
    form_excluded_columns = ['showtimes', 'created_at', 'updated_at', 'image', 'rate']
    column_exclude_list = ['description', 'created_at', 'updated_at']

    # 2. Thêm một trường File ảo để người dùng chọn ảnh
    form_extra_fields = {
        'upload_image': FileField('Chọn ảnh Poster')
    }

    column_labels = {
        'name': 'Tên phim', 'duration': 'Thời lượng (phút)',
        'release_date': 'Ngày khởi chiếu', 'rate': 'Đánh giá', 'image': 'Ảnh',
        'limited_age': 'Giới hạn tuổi', 'is_active': 'Đang chiếu', 'genres': 'Thể loại',
        'upload_image': 'Tải ảnh lên'
    }

    column_formatters = {
        'image': lambda view, context, model, name: Markup(
            f'<img src="{model.image}" style="width: 80px; object-fit: cover; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" alt="Poster">'
        ) if model.image else Markup('<span class="text-muted">Chưa có ảnh</span>')
    }

    extra_js = ['https://cdnjs.cloudflare.com/ajax/libs/ckeditor/4.21.0/ckeditor.js']
    form_overrides = {
        'description': CKTextAreaField
    }

    def on_model_change(self, form, model, is_created):
        upload_field = getattr(form, 'upload_image', None)

        if upload_field and upload_field.data:
            image_file = upload_field.data
            image_url = dao.upload_image(image_file, folder_name="movies")

            if image_url:
                model.image = image_url


class ShowtimeView(BaseModelView):
    column_list = ['movie', 'room', 'start_time', 'end_time', 'base_price', 'movie_format', 'translation']
    column_searchable_list = ['movie.name', 'room.name']
    column_filters = ['movie.name', 'room.name', 'start_time', 'movie_format.name', 'translation']
    column_default_sort = ('start_time', True)
    column_sortable_list = ['start_time', 'end_time', 'base_price']

    column_labels = {
        'movie': 'Phim',
        'room': 'Phòng chiếu',
        'start_time': 'Giờ bắt đầu',
        'end_time': 'Giờ kết thúc',
        'base_price': 'Giá vé gốc',
        'movie_format': 'Định dạng',
        'translation': 'Ngôn ngữ'
    }

    form_excluded_columns = ['bookings', 'showtime_seats', 'created_at', 'updated_at']

    column_formatters = {
        'start_time': lambda view, context, model, name: model.start_time.strftime(
            '%H:%M | %d/%m/%Y') if model.start_time else '',
        'end_time': lambda view, context, model, name: model.end_time.strftime(
            '%H:%M | %d/%m/%Y') if model.end_time else '',
        'base_price': lambda view, context, model, name: f"{int(model.base_price):,} VNĐ".replace(',',
                                                                                                  '.') if model.base_price else '0 VNĐ'
    }
    column_editable_list = ['base_price']


class BookingView(BaseModelView):
    can_create = False  # Admin không được tự tạo hóa đơn
    can_delete = False  # Không được xóa hóa đơn để đảm bảo đối soát tài chính
    column_searchable_list = ['transaction_id']
    column_filters = ['status', 'payment_method']
    column_labels = {
        'user': 'Khách hàng', 'showtime': 'Suất chiếu',
        'total_price': 'Tổng tiền', 'status': 'Trạng thái',
        'payment_method': 'Thanh toán', 'transaction_id': 'Mã giao dịch'
    }


class TicketView(BaseModelView):
    can_create = False
    can_delete = False
    can_edit = False
    column_filters = ['is_checked_in']
    column_labels = {
        'booking': 'Mã Hóa Đơn', 'showtime_seat': 'Ghế - Suất',
        'final_price': 'Giá vé', 'is_checked_in': 'Đã soát vé'
    }


class UserView(BaseModelView):
    can_create = False  # Khách tự đăng ký, hoặc làm thêm logic riêng cho việc tạo Admin
    column_exclude_list = ['password', 'created_at', 'updated_at']
    column_searchable_list = ['username', 'email']
    column_filters = ['role', 'active']
    column_labels = {'username': 'Tên User', 'email': 'Email', 'role': 'Vai trò', 'active': 'Đang hoạt động'}


class MyAdminIndexView(AdminAuthMixin, AdminIndexView):
    @expose('/')
    def index(self):
        # Truyền thống kê cơ bản ra trang chủ admin
        stats = {
            'users': User.query.count(),
            'movies': Movie.query.filter_by(is_active=True).count(),
            'bookings': Booking.query.count()
        }
        return self.render('admin/index.html', stats=stats)


admin = Admin(app=app, name='Hệ Thống Đặt Vé', index_view=MyAdminIndexView())
# CATEGORY: QUẢN LÝ RẠP & CƠ SỞ VẬT CHẤT
admin.add_view(ProvinceView(Province, db.session, name='Tỉnh/Thành', category='Cơ sở vật chất'))
admin.add_view(CinemaView(Cinema, db.session, name='Rạp chiếu', category='Cơ sở vật chất'))
admin.add_view(RoomView(Room, db.session, name='Phòng chiếu', category='Cơ sở vật chất'))
admin.add_view(SeatTypeView(SeatType, db.session, name='Loại ghế', category='Cơ sở vật chất'))
admin.add_view(SeatView(Seat, db.session, name='Sơ đồ ghế', category='Cơ sở vật chất'))

# CATEGORY: QUẢN LÝ PHIM & LỊCH CHIẾU
admin.add_view(GenreView(Genre, db.session, name='Thể loại', category='Phim & Lịch chiếu'))
admin.add_view(MovieFormatView(MovieFormat, db.session, name='Định dạng', category='Phim & Lịch chiếu'))
admin.add_view(MovieView(Movie, db.session, name='Danh sách phim', category='Phim & Lịch chiếu'))
admin.add_view(ShowtimeView(Showtime, db.session, name='Lịch chiếu', category='Phim & Lịch chiếu'))

# CATEGORY: GIAO DỊCH & DOANH THU
admin.add_view(BookingView(Booking, db.session, name='Hóa đơn', category='Giao dịch'))
admin.add_view(TicketView(Ticket, db.session, name='Danh sách vé', category='Giao dịch'))

# CATEGORY: TÀI KHOẢN
admin.add_view(UserView(User, db.session, name='Người dùng'))
