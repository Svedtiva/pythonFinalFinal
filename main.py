from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text, Table, MetaData, select, engine, and_

app = Flask(__name__)
app.debug = True
app.secret_key = 'Budders23!'

# connection string is in the format mysql://Root:password@server/boatdb
connection = "mysql://root:Budders23!@localhost/finalfinal"
engine = create_engine(connection, echo=True)
conn = engine.connect()

# Universal


def h(str):
    alph = "abcdefghijklmnopqrstuvwxyz"
    sum = 0
    for char in str:
        sum += alph.find(char) + 1
    return sum


@app.route('/in')
def re():
    return render_template('index.html')


@app.route('/')
def index():
    query = text("SELECT * FROM finalproducts")
    result = conn.execute(query)
    products = []
    for row in result:
        products.append(row)
    return render_template('customer.html', products=products)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == 'RK123' or password == 'Cars!':
            password = password
        else:
            password = h(password)
        query = text("SELECT * FROM finalaccounts WHERE username = :username AND password = :password")
        params = {"username": username, "password": password}
        result = conn.execute(query, params)
        user = result.fetchone()
        if user is None:
            return render_template('index.html')
        else:
            session['id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[3]
            session['full_name'] = user[4]
            session['type'] = user[5]
            session['logged_in'] = True
            if user[5] == 'Admin':
                acc = conn.execute(text("SELECT id FROM finalaccounts"))
                return redirect(url_for('admin', acc=acc))
            elif user[5] == 'Vendor':
                acc = conn.execute(text("SELECT id FROM finalaccounts"))
                return redirect(url_for('vendor', acc=acc))
            else:
                acc = conn.execute(text("SELECT id FROM finalaccounts"))
                return redirect(url_for('customer', acc=acc))
    else:
        return render_template('index.html')


@app.route('/register', methods=['GET'])
def register():
        return render_template('register.html')


@app.route('/add_account', methods=['POST'])
def add_account():
    max_id_query = text("SELECT MAX(id) FROM finalaccounts")
    max_id = conn.execute(max_id_query).fetchone()[0]
    new_id = max_id + 1 if max_id is not None else 1

    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    full_name = first_name + ' ' + last_name
    password = h(password)
    type = 'customer'
    user = conn.execute(text("SELECT * FROM finalaccounts WHERE email=:email"), {'email': email}).fetchone()
    if user is not None:
        flash("An account with this email already exists.")
        return redirect(url_for('register'))
    else:
        query = text("INSERT INTO finalaccounts (id, username, password, email, full_name,"" type)"
                     " VALUES (:id, :username, :password, :email, :full_name, :type"" )")
        params = {"id": new_id, "username": username, "password": password, "email": email, "full_name": full_name,
                  "type": type}
        conn.execute(query, params)
        conn.commit()

    return render_template('index.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



# Admin
@app.route('/admin')
def admin():
    query = text("SELECT * FROM finalproducts")
    result = conn.execute(query)
    products = []
    for row in result:
        products.append(row)
    return render_template('admin.html', products=products)


@app.route('/add_product', methods=['POST'])
def add_product():
    max_id_query = text("SELECT MAX(item_id) FROM finalproducts")
    max_id = conn.execute(max_id_query).fetchone()[0]
    new_id = max_id + 1 if max_id is not None else 1

    vendor_id = request.form['vendor_id']
    title = request.form['title']
    description = request.form['description']
    price = request.form['price']
    image = request.form['image']
    customizations = request.form['customizations']
    stock = request.form['stock']

    query = text("INSERT INTO finalproducts (item_id, vendor_id, title, description, image, customizations,"
                 " price, stock)"
                 " VALUES (:item_id, :vendor_id, :title, :description, :customizations, :image,"
                 " :price, :stock)")
    params = {"item_id": new_id, "vendor_id": vendor_id, "title": title, "description": description,
              "price": price, "image": image, "customizations": customizations, 'stock': stock}
    conn.execute(query, params)
    conn.commit()

    return url_for('admin')


@app.route('/admin_delete_product/<int:item_id>', methods=['POST'])
def admin_delete_product(item_id):
    query = text("DELETE FROM finalproducts WHERE item_id = :item_id")
    conn.execute(query, {"item_id": item_id})
    conn.commit()
    return redirect(url_for('admin'))


@app.route('/admin_edit_product/<int:item_id>', methods=['GET', 'POST'])
def admin_edit_product(item_id):
    if request.method == 'POST':
        vendor_id = request.form['vendor_id']
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        image = request.form['image']
        customizations = request.form['customizations']
        stock = request.form['stock']
        query = text("UPDATE finalproducts SET vendor_id=:vendor_id, title=:title, description=:description, price=:price, image=:image, customizations=:customizations, stock=:stock WHERE item_id=:item_id")
        params = {"vendor_id": vendor_id, "title": title, "description": description, "price": price, "image": image, "customizations": customizations, "stock": stock, "item_id": item_id}
        conn.execute(query, params)
        conn.commit()
        flash("Product updated successfully.")
        return redirect(url_for('admin'))
    else:
        query = text("SELECT * FROM finalproducts WHERE item_id=:item_id")
        params = {"item_id": item_id}
        result = conn.execute(query, params)
        product = result.fetchone()
        if product is None:
            flash("Product not found.")
            return redirect(url_for('admin'))
        else:
            return render_template('edit_product.html', product=product)



# Vendor


@app.route('/vendor')
def vendor():
    session_id = session.get('id')
    query = text("SELECT * FROM finalproducts WHERE vendor_id = :session_id")
    result = conn.execute(query, {'session_id': session_id})
    products = []
    for row in result:
        products.append(row)
    return render_template('vendor.html', products=products)


@app.route('/vendor_add_product', methods=['POST'])
def vendor_add_product():
    max_id_query = text("SELECT MAX(item_id) FROM finalproducts")
    max_id = conn.execute(max_id_query).fetchone()[0]
    new_id = max_id + 1 if max_id is not None else 1

    vendor_id = session.id
    title = request.form['title']
    description = request.form['description']
    price = request.form['price']
    image = request.form['image']
    customizations = request.form['customizations']
    stock = request.form['stock']

    query = text("INSERT INTO finalproducts (item_id, vendor_id, title, description, image, customizations,"
                 " price, stock)"
                 " VALUES (:item_id, :vendor_id, :description, :customizations, :image,"
                 " :price, :stock)")
    params = {"item_id": new_id, "vendor_id": vendor_id, "title": title, "description": description,
              "price": price, "image": image, "customizations": customizations, 'stock': stock}
    conn.execute(query, params)
    conn.commit()

    return url_for('vendor')


@app.route('/vendor_edit_product/<int:item_id>', methods=['GET', 'POST'])
def vendor_edit_product(item_id):
    if request.method == 'POST':
        vendor_id = request.form['vendor_id']
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        image = request.form['image']
        customizations = request.form['customizations']
        stock = request.form['stock']
        query = text("UPDATE finalproducts SET vendor_id=:vendor_id, title=:title, description=:description, price=:price, image=:image, customizations=:customizations, stock=:stock WHERE item_id=:item_id")
        params = {"vendor_id": vendor_id, "title": title, "description": description, "price": price, "image": image, "customizations": customizations, "stock": stock, "item_id": item_id}
        conn.execute(query, params)
        conn.commit()
        flash("Product updated successfully.")
        return redirect(url_for('admin'))
    else:
        query = text("SELECT * FROM finalproducts WHERE item_id=:item_id")
        params = {"item_id": item_id}
        result = conn.execute(query, params)
        product = result.fetchone()
        if product is None:
            flash("Product not found.")
            return redirect(url_for('admin'))
        else:
            return render_template('edit_product.html', product=product)



# Customer
@app.route('/customer')
def customer():
    query = text("SELECT * FROM finalproducts")
    result = conn.execute(query)
    products = []
    for row in result:
        products.append(row)
    return render_template('customer.html', products=products)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_id = request.form['item_id']
    vendor_id = request.form['vendor_id']
    purchaser_id = session.get('id')
    cart_id = f""
    status = "open"

    query = text(
        "INSERT INTO finalcart (cart_id, item_id, vendor_id, purchaser_id, status)"
        " VALUES (:cart_id, :item_id, :vendor_id, :purchaser_id, :status)")
    params = {"cart_id": cart_id, "item_id": item_id, "vendor_id": vendor_id, "purchaser_id": purchaser_id,
              "status": status}
    conn.execute(query, params)
    conn.commit()

    flash("Item added to cart successfully!")
    return redirect(url_for('customer'))


@app.route('/accinfo')
def accinfo():
    return render_template('accinfo.html')


if __name__ == '__main__':
    app.run(debug=True)
