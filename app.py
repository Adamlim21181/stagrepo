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

# Define the Item model
class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

# Home route to display all items
@app.route('/')
def index():
    # Use the text() function to declare a textual SQL query
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
            new_item = Item(name=name, description=description)
            db.session.add(new_item)
            db.session.commit()
            db.session.remove()  # Remove session after commit
            return redirect(url_for('index'))
    return render_template('add_item.html')

# Route to edit an item
@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        db.session.commit()
        db.session.remove()  # Remove session after commit
        return redirect(url_for('index'))
    return render_template('edit_item.html', item=item)

# Route to delete an item
@app.route('/delete/<int:item_id>', methods=['POST'])  # Change method to POST for deletion
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    db.session.remove()  # Remove session after commit
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
