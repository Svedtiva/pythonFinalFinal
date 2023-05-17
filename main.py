from datetime import datetime

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
                 " VALUES (:item_id, :vendor_id, :title, :description, :image, :customizations, "
                 " :price, :stock)")
    params = {"item_id": new_id, "vendor_id": vendor_id, "title": title, "description": description,
              "price": price, "image": image, "customizations": customizations, 'stock': stock}
    conn.execute(query, params)
    conn.commit()

    return redirect(url_for('admin'))


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


@app.route('/add_to_cart', methods=['POST', 'GET'])
def add_to_cart():
    if request.method == 'POST':
        query = text("SELECT * FROM finalproducts")
        resul = conn.execute(query)
        products = []
        for row in resul:
            products.append(row)
        max_id_query = text("SELECT MAX(cart_id) AS max_id FROM finalcarts")
        result = conn.execute(max_id_query).fetchone()
        max_id = result[0] if result[0] is not None else 1

        max_id = int(max_id)
        new_id = max_id + 1

        cart_id = new_id

        item_id = request.form['id']
        image = request.form['image']
        price = request.form['price']
        amount = request.form['amount']
        shopper_id = session['id']
        status = 'open'

        open_cart_query = text("SELECT cart_id FROM finalcarts WHERE shopper_id = :shopper_id AND status = 'open'")
        open_cart_result = conn.execute(open_cart_query, {"shopper_id": shopper_id}).fetchone()
        if open_cart_result:
            cart_id = open_cart_result[0]

            existing_item_query = text("SELECT * FROM finalcarts WHERE cart_id = :cart_id AND item_id = :item_id")
            existing_item_result = conn.execute(existing_item_query,
                                                {"cart_id": cart_id, "item_id": item_id}).fetchone()
            if existing_item_result:
                existing_amount = int(existing_item_result[4])
                new_amount = existing_amount + int(amount)

                update_query = text("UPDATE finalcarts SET amount = :new_amount "
                                    "WHERE cart_id = :cart_id AND item_id = :item_id")
                update_params = {
                    "new_amount": new_amount,
                    "cart_id": cart_id,
                    "item_id": item_id
                }
                conn.execute(update_query, update_params)
                conn.commit()
            else:
                query = text("INSERT INTO finalcarts (cart_id, item_id, image, price, amount, shopper_id, status) "
                             "VALUES (:cart_id, :item_id, :image, :price, :amount, :shopper_id, :status)")
                params = {
                    "cart_id": cart_id,
                    "item_id": item_id,
                    'image': image,
                    "price": price,
                    "amount": amount,
                    "shopper_id": shopper_id,
                    "status": status
                }
                conn.execute(query, params)
                conn.commit()
        else:
            query = text("INSERT INTO finalcarts (cart_id, item_id, image, price, amount, shopper_id, status) "
                         "VALUES (:cart_id, :item_id, :image, :price, :amount, :shopper_id, :status)")
            params = {
                "cart_id": cart_id,
                "item_id": item_id,
                'image': image,
                "price": price,
                "amount": amount,
                "shopper_id": shopper_id,
                "status": status
            }
            conn.execute(query, params)
            conn.commit()
        return redirect(url_for('customer'))


@app.route('/accinfo')
def accinfo():
    if 'id' in session:
        cart_query = text("SELECT * FROM finalcarts WHERE shopper_id = :shopper_id")
        cart_items = conn.execute(cart_query, {"shopper_id": session['id']}).fetchall()

        total = 0

        for cart_item in cart_items:
            price = float(cart_item[3])
            amount = int(cart_item[4])
            item_total = price * amount
            total += item_total
        shopper_id = session['id']
        query = text("SELECT * FROM finalcarts WHERE shopper_id = :shopper_id AND status = 'closed'")
        params = {"shopper_id": shopper_id}
        result = conn.execute(query, params)
        confirmed_orders = result.fetchall()
        return render_template('accinfo.html', orders=confirmed_orders[:1], total=total, cart_items=cart_items)


@app.route('/viewchats')
def viewchats():
    user_id = session.get('id')

    query = text("SELECT c.chat_id, c.sender_id, c.recipient_id, c.text, a.username AS sender_username "
                 "FROM finalchats c "
                 "INNER JOIN finalaccounts a ON c.sender_id = a.id "
                 "WHERE c.sender_id = :user_id OR c.recipient_id = :user_id")
    params = {"user_id": user_id}
    result = conn.execute(query, params)
    messages = []
    for row in result:
        messages.append(row)
    return render_template('chats.html', messages=messages)


@app.route('/send_message', methods=['POST'])
def send_message():
    sender_id = session.get('id')
    recipient_id = request.form['recipient_id']
    message_text = request.form['text']
    chat_id = f"chat_{sender_id}_{recipient_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    query = text(
        "INSERT INTO finalchats (chat_id, sender_id, recipient_id, text)"
        " VALUES (:chat_id, :sender_id, :recipient_id, :text)")
    params = {"chat_id": chat_id, "sender_id": sender_id, "recipient_id": recipient_id, "text": message_text}
    conn.execute(query, params)
    conn.commit()

    flash("Message sent successfully!")
    return redirect(url_for('viewchats'))


@app.route('/view_cart')
def view_cart():
    if 'id' in session:
        shopper_id = session['id']

        cart_query = text("SELECT * FROM finalcarts WHERE shopper_id = :shopper_id AND status = 'open'")
        cart_items = conn.execute(cart_query, {"shopper_id": shopper_id}).fetchall()

        cart_query = text("SELECT cart_id FROM finalcarts WHERE shopper_id = :shopper_id AND status = 'open'")
        cart_result = conn.execute(cart_query, {"shopper_id": shopper_id}).fetchone()
        cart_id = cart_result[0] if cart_result else None

        return render_template('cart.html', cart_items=cart_items, cart_id=cart_id)


@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    if 'id' in session:
        shopper_id = session['id']

        remove_query = text("DELETE FROM finalcarts WHERE item_id = :item_id AND shopper_id = :shopper_id")
        conn.execute(remove_query, {"item_id": item_id, "shopper_id": shopper_id})
        conn.commit()

        return redirect(url_for('view_cart'))


@app.route('/submit_order/<int:cart_id>', methods=['POST'])
def submit_order(cart_id):
    cart_query = text("SELECT * FROM finalcarts WHERE cart_id = :cart_id")
    cart_items = conn.execute(cart_query, {"cart_id": cart_id}).fetchall()

    total = 0

    for cart_item in cart_items:
        price = float(cart_item[3])
        amount = int(cart_item[4])
        item_total = price * amount
        total += item_total

    query = text("UPDATE finalcarts SET status = 'closed' WHERE cart_id = :cart_id")
    conn.execute(query, {"cart_id": cart_id})
    conn.commit()

    flash("Order submitted successfully.")

    return render_template('ordersummary.html', total=total, cart_items=cart_items)


@app.route('/submit_review/<int:cart_id>', methods=['POST'])
def submit_review(cart_id):
    def get_cart_items(cart_id):
        cart_query = text("SELECT * FROM finalcarts WHERE cart_id = :cart_id")
        cart_items = conn.execute(cart_query, {"cart_id": cart_id}).fetchall()
        return cart_items

    cart_items = get_cart_items(cart_id)

    for cart_item in cart_items:
        review_id = cart_item.cart_item_id
        item_id = cart_item.item_id
        rating = int(request.form.get(f'rating{review_id}'))
        review_text = request.form.get(f'review{review_id}')

        query = text("INSERT INTO final_reviews (item_id, review_id, rating, text) VALUES (:item_id, :review_id, :rating, :text)")
        conn.execute(query, {"item_id": item_id, "review_id": review_id, "rating": rating, "text": review_text})
        conn.commit()

    flash("Reviews submitted successfully.")
    return redirect(url_for('customer'))



if __name__ == '__main__':
    app.run(debug=True)
