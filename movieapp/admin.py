from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from movieapp import app, db
from movieapp.models import Movie, User, Room


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')


admin = Admin(app=app, name='Hệ Thống Đặt Vé', index_view=MyAdminIndexView())
admin.add_view(ModelView(Movie, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Room, db.session))
