from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text, Table, MetaData, select, engine, and_

app = Flask(__name__)
app.debug = True
app.secret_key = 'Budders23!'

# connection string is in the format mysql://Root:password@server/boatdb
connection = "mysql://root:Budders23!@localhost/finalfinal"
engine = create_engine(connection, echo=True)
conn = engine.connect()


def h(str):
    alph = "abcdefghijklmnopqrstuvwxyz"
    sum = 0
    for char in str:
        sum += alph.find(char) + 1
    return sum


@app.route('/')
def index():
    return render_template("index.html")


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
            if user[5] == 'Admin':
                acc = conn.execute(text("SELECT id FROM finalaccounts"))
                return redirect(url_for('admin', acc=acc))
            elif user[5] == 'Vendor':
                acc = conn.execute(text("SELECT id FROM finalaccounts"))
                return redirect(url_for('vendor', acc=acc))
            else:
                acc = conn.execute(text("SELECT id FROM finalaccounts"))
                return redirect(url_for('viewProducts', acc=acc))
    else:
        return render_template('index.html')


@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


@app.route('/admin')
def admin():
    query = text("SELECT * FROM finalproducts")
    result = conn.execute(query)
    products = []
    for row in result:
        products.append(row)
    return render_template('admin.html', products=products)


@app.route('/customer')
def customer():
    query = text("SELECT * FROM finalproducts")
    result = conn.execute(query)
    products = []
    for row in result:
        products.append(row)
    return render_template('customer.html', products=products)


@app.route('/vendor')
def vendor():
    session_id = session.get('id')
    query = text("SELECT * FROM finalproducts WHERE vendor_id = :session_id")
    result = conn.execute(query, {'session_id': session_id})
    products = []
    for row in result:
        products.append(row)
    return render_template('vendor.html', products=products)


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
    full_name = first_name+' '+last_name
    password = h(password)
    type = 'customer'

    query = text("INSERT INTO finalaccounts (id, username, password, email, full_name,"
                 " type)"
                 " VALUES (:id, :username, :password, :email, :full_name, :type"
                 " )")
    params = {"id": new_id, "username": username, "password": password, "email": email, "full_name": full_name,
              "type": type}
    conn.execute(query, params)
    conn.commit()

    return render_template('index.html')


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

    query = text("INSERT INTO finalproducts (id, vendor_id, title, description, image, customizations,"
                 " price)"
                 " VALUES (:id, :vendor_id, :description, :customizations, :image,"
                 " :price)")
    params = {"id": new_id, "vendor_id": vendor_id, "title": title, "description": description,
              "price": price, "image": image, "customizations": customizations}
    conn.execute(query, params)
    conn.commit()

    return url_for('admin')


@app.route('/vendor_add_product', methods=['POST'])
def add_product():
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

    query = text("INSERT INTO finalproducts (id, vendor_id, title, description, image, customizations,"
                 " price)"
                 " VALUES (:id, :vendor_id, :description, :customizations, :image,"
                 " :price)")
    params = {"id": new_id, "vendor_id": vendor_id, "title": title, "description": description,
              "price": price, "image": image, "customizations": customizations}
    conn.execute(query, params)
    conn.commit()

    return url_for('vendor')


if __name__ == '__main__':
    app.run(debug=True)
