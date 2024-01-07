from sqlalchemy import func, extract

from app.models import Category, Product, User, Receipt, ReceiptDetails,Comment
from app import app, db
import hashlib
from flask_login import current_user


def get_categories():
    return Category.query.all()


def get_products(kw, cate_id, page=None):
    products = Product.query

    if kw:
        products = products.filter(Product.name.contains(kw))

    if cate_id:
        products = products.filter(Product.category_id.__eq__(cate_id))

    if page:
        page = int(page)
        page_size = app.config['PAGE_SIZE']
        start = (page - 1) * page_size

        return products.slice(start, start + page_size)

    return products.all()


def count_product():
    return Product.query.count()

def get_comment(product_id,page):
    page = int(page)
    page_size = app.config['COMMENT_SIZE']
    start = (page - 1) * page_size
    return Comment.query.filter(Comment.product_id.__eq__(product_id)).order_by(-Comment.id).slice(start,start + page_size).all()

def count_comment(product_id):
    return Comment.query.filter(Comment.product_id.__eq__(product_id)).count()



def get_user_by_id(user_id):
    return User.query.get(user_id)


def auth_user(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username),
                             User.password.__eq__(password)).first()


def add_receipt(cart):
    if cart:
        r = Receipt(user=current_user)
        db.session.add(r)

        for c in cart.values():
            d = ReceiptDetails(quantity=c['quantity'], price=c['price'], receipt=r, product_id=c['id'])
            db.session.add(d)

        try:
            db.session.commit()
        except:
            return False
        else:
            return True

    return False


def product_stats(kw=None,from_date=None,to_date=None):
    p = db.session.query(Product.id,Product.name,
                         func.sum(ReceiptDetails.quantity * ReceiptDetails.price))\
                        .join(ReceiptDetails,ReceiptDetails.product_id.__eq__(Product.id),isouter=True)\
                        .join(Receipt,ReceiptDetails.receipt_id.__eq__(Receipt.id),isouter=True)\
                        .group_by(Product.id,Product.name)
    if kw:
        p = p.filter(Product.name.contains(kw))
    if from_date:
        p = p.filter(Receipt.created_date.__ge__(from_date))
    if to_date:
        p = p.filter(Receipt.created_date.__le__(to_date))

    return p.all()


def product_month_stats(year):
    query = db.session.query(
        extract('month', Receipt.created_date).label('month'),
        func.sum(ReceiptDetails.quantity * ReceiptDetails.price).label('total_amount')
    )

    query = query.join(ReceiptDetails, ReceiptDetails.receipt_id == Receipt.id)
    query = query.filter(extract('year', Receipt.created_date) == year)
    query = query.group_by(extract('month', Receipt.created_date))
    query = query.order_by('month')
    results = query.all()

    return results

def category_stats():
    '''
        Select c.id,c.name,count(p.id)
        from category c left outer join product p on c.id = p.category_id
        group by c.id, c.name
    '''

    # return  Category.query.join(Product, Product.category_id.__eq__
    # (Category.id),isouter=True).add_column(func.count(Product.id)).group_by(Category.id,Category.name).all()

    return db.session.query(Category.id,Category.name,func.count(Product.id))\
        .join(Product, Category.id.__eq__(Product.category_id),isouter=True)\
        .group_by(Category.id,Category.name)

def get_product_by_id(product_id):
    return Product.query.get(product_id)

def add_user(name,username,password,**kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User( name=name.strip(), username=username.strip(), password=password,
                avatar = kwargs.get('avatar'))

    db.session.add(user)
    db.session.commit()

def add_comment(content,product_id):
    c = Comment(content=content,product_id=product_id,user=current_user)

    db.session.add(c)
    db.session.commit()

    return c


