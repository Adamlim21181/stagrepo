from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# Configure the MySQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqldb://STAGNASTICS:gyM!2025_Score$NZ@STAGNASTICS.mysql.pythonanywhere-services.com/STAGNASTICS$stagdata"

# Set pool_recycle to prevent connection timeouts
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280}

# Initialize the database
db = SQLAlchemy(app)

# Home route to display all items
@app.route('/')
def index():
    # Use raw SQL to fetch all items
    result = db.session.execute(text("SELECT * FROM items"))
    items = result.fetchall()  # Fetch all results from the query
    return render_template('index.html', items=items)

# Route to add an item
@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        if name:  # Check if name is provided
            # Use raw SQL to insert a new item
            query = text("INSERT INTO items (name, description) VALUES (:name, :description)")
            db.session.execute(query, {"name": name, "description": description})
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('add_item.html')

# Route to edit an item
@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    # Fetch the item to be edited
    result = db.session.execute(text("SELECT * FROM items WHERE id = :id"), {"id": item_id})
    item = result.fetchone()

    if not item:
        return "Item not found", 404

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        # Update the item using raw SQL
        query = text("UPDATE items SET name = :name, description = :description WHERE id = :id")
        db.session.execute(query, {"name": name, "description": description, "id": item_id})
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_item.html', item=item)

# Route to delete an item
@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    # Delete the item using raw SQL
    query = text("DELETE FROM items WHERE id = :id")
    db.session.execute(query, {"id": item_id})
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)