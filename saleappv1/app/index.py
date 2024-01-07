import math

import cloudinary
from flask import render_template, request, redirect, jsonify, session, url_for
import dao
import utils
from app import app, login, admin
from flask_login import login_user, logout_user, login_required, current_user


@app.route("/")
def index():
    kw = request.args.get('kw')
    cate_id = request.args.get('cate_id')
    page = request.args.get('page')

    prods = dao.get_products(kw, cate_id, page)

    num = dao.count_product()
    page_size = app.config['PAGE_SIZE']

    return render_template('index.html',
                           products=prods, pages=math.ceil(num/page_size))


@app.route("/products/<int:product_id>")
def product_detail(product_id):
    product = dao.get_product_by_id(product_id)
    page = int(request.args.get('page',1))
    comments = dao.get_comment(product_id=product_id,page=int(page))

    num = dao.count_comment(product_id=product_id)
    page_size = app.config['COMMENT_SIZE']

    return render_template('product_detail.html',comments=comments,
                           product=product,
                           pages=math.ceil(num/page_size))

@app.route('/admin/login', methods=['post'])
def login_admin():
    username = request.form.get('username')
    password = request.form.get('password')

    user = dao.auth_user(username=username, password=password)
    if user:
        login_user(user)

    return redirect('/admin')


@app.route("/cart")
def cart():
    return render_template('cart.html')


@app.route("/api/cart", methods=['post'])
def add_to_cart():
    data = request.json

    cart = session.get('cart')
    if cart is None:
        cart = {}

    id = str(data.get("id"))
    if id in cart:
        cart[id]['quantity'] += 1
    else:
        cart[id] = {
            "id": id,
            "name": data.get("name"),
            "price": data.get("price"),
            "quantity": 1
        }

    session['cart'] = cart

    """
        {
            "1": {
                "id": "1",
                "name": "...",
                "price": 123,
                "quantity": 2
            },  "2": {
                "id": "2",
                "name": "...",
                "price": 1234,
                "quantity": 1
            }
        }
    """

    return jsonify(utils.count_cart(cart))


@app.route("/api/cart/<product_id>", methods=['put'])
def update_cart(product_id):
    cart = session.get('cart')
    if cart and product_id in cart:
        quantity = request.json.get('quantity')
        cart[product_id]['quantity'] = int(quantity)

    session['cart'] = cart
    return jsonify(utils.count_cart(cart))


@app.route("/api/cart/<product_id>", methods=['delete'])
def delete_cart(product_id):
    cart = session.get('cart')
    if cart and product_id in cart:
        del cart[product_id]

    session['cart'] = cart
    return jsonify(utils.count_cart(cart))


@app.route("/api/pay", methods=['post'])
def pay():
    cart = session.get('cart')
    if dao.add_receipt(cart):
        del session['cart']
        return jsonify({'status': 200})

    return jsonify({'status': 500, 'err_msg': 'Something wrong!'})


@app.route('/login', methods=['get', 'post'])
def login_view():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user)

        next = request.args.get('next')
        if next:
            return redirect(next)

        return redirect("/")

    return render_template('login.html')


@app.context_processor
def common_responses():
    return {
        'categories': dao.get_categories(),
        'cart_stats': utils.count_cart(session.get('cart'))
    }


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id=user_id)

# dang nhap luc nao cung phai la post
@app.route('/user-login', methods=['GET', 'POST'])
def user_signin():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
            next = request.args.get('next', 'home')
            return redirect(url_for('index'))
        else:
            err_msg = 'Username hoac password khong chinh xac'
    return render_template('login.html', err_msg=err_msg)


@app.route('/user_logout', methods=['get'])
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))

@app.route('/register', methods=['get', 'post'])
def user_register():
    err_msg = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        avatar_path = None
        try:
            if (password.strip().__eq__(confirm.strip())):
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']
                dao.add_user(name=name, username=username,
                             password=password,
                             avatar=avatar_path)
                return redirect(url_for('user_signin'))
            else:
                err_msg = 'Mat khau khong khop!'
        except Exception as ex:
            err_msg = 'He thong co loi: ' + str(ex)
        # sau nay co cac truong hop loi cu the phai show ra dung loi

    return render_template('register.html', err_msg=err_msg)



@app.route('/api/comments',methods=['post'])
@login_required
def add_commnet():
    data = request.json
    content = data.get('content')
    product_id = data.get('product_id')

    try:
        c = dao.add_comment(content=content,product_id=product_id)
    except:
        return {'status': 404, 'err_msg': 'Chuong trinh dang bi loi'}
    return {'status': 201,'comment':{
        'id':c.id,
        'content':c.content,
        'created_date':c.created_date,
        'user':{
            'username': current_user.username,
            'avatar': current_user.avatar
        }
    }}




if __name__ == '__main__':
    app.run(debug=True)
