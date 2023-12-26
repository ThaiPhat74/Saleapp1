from datetime import datetime

from app.models import Category, Product, UserRoleEnum
from app import app, db, dao
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_login import logout_user, current_user
from flask import redirect, request


class AuthenticatedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.ADMIN


class AuthenticatedUser(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class MyProductView(AuthenticatedAdmin):
    column_list = ['id', 'name', 'price', 'active']
    column_searchable_list = ['name']
    column_filters = ['name', 'price']
    column_editable_list = ['name', 'price']
    edit_modal = True


class MyCategoryView(AuthenticatedAdmin):
    column_list = ['id', 'name', 'products']




class LogoutView(AuthenticatedUser):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')


class StatsView(AuthenticatedUser):
    @expose('/')
    def index(self):
        kw = request.args.get('kw')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        year = request.args.get('year', datetime.now().year)
        return self.render('admin/stats.html',
                           month_stats=dao.product_month_stats(year=year),
                           stats=dao.product_stats(kw=kw,
                                                   from_date=from_date,
                                                   to_date=to_date))

class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):

        return self.render('admin/index.html'
                           ,stats = dao.category_stats())

admin = Admin(app=app, name='Quan tri he thong ban hang online',
                  template_mode='bootstrap4', index_view=(MyAdminIndex()))

admin.add_view(MyCategoryView(Category, db.session))
admin.add_view(MyProductView(Product, db.session))
admin.add_view(StatsView(name='Thống kê báo cáo'))
admin.add_view(LogoutView(name='Đăng xuất'))

