import sqlite3, json
from flask import Flask, render_template, request, url_for, redirect, abort, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a random secret key'
DATABASE = 'database.db'
global_data = {'order_by': 'created'}

def get_contacts(order_by):
    query = 'SELECT * FROM contacts ORDER BY ' + order_by
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        contacts = cursor.fetchall()
    return contacts

def get_contact(contact_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contacts WHERE id = ?',
                 (contact_id,))
        contact = cursor.fetchone()
    return contact

def add_contact(firstname, lastname, emails_json):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO contacts (firstname, lastname, emails) VALUES (?,?,?)',
                     (firstname, lastname, (emails_json)))
        conn.commit()

def update_contact(firstname, lastname, emails_json, id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE contacts SET firstname = ?, lastname = ?, emails = ? WHERE id = ?',
                         (firstname, lastname, (emails_json), id))
        conn.commit()

def delete_contact(contact_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
        conn.commit()

def delete_one_email(contact_id, emails_json):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE contacts SET emails = ? WHERE id = ?',
                     (emails_json, contact_id))

@app.route('/')
def index():
    contacts = get_contacts(global_data["order_by"])
    return render_template('base.html', contacts=contacts)

@app.route('/add', methods=['GET', 'POST'])
def add():
    contacts = get_contacts(global_data["order_by"])
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        
        emails_json = json.dumps([])
        add_contact(firstname, lastname, emails_json)
        contacts = get_contacts(global_data["order_by"])
        return redirect(url_for('add'))

    return render_template('write.html', contact=None, contacts=contacts, emails=None)

@app.route('/<int:id>/update/', methods=['GET', 'POST'])
def edit_contact(id):
    contacts = get_contacts(global_data["order_by"])
    contact = get_contact(id)
    current_emails = json.loads(contact[4]) if contact and contact[4] else []
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        new_email = request.form['email']
        if not current_emails:
            current_emails = []
        if new_email:
            current_emails.append(new_email)

        emails_json = json.dumps(current_emails)

        update_contact(firstname, lastname, emails_json, contact[0])
        contacts = get_contacts(global_data["order_by"])
        contact = get_contact(id)
        return render_template('write.html', contact=contact, contacts=contacts, emails=current_emails)

    return render_template('write.html', contact=contact, contacts=contacts, emails=current_emails)

@app.route('/<int:id>/delete/', methods=['GET'])
def delete(id):
    delete_contact(id)
    return redirect(url_for('index'))

@app.route('/delete_email/<int:contact_id>/<int:email_index>', methods=['GET'])
def delete_email(contact_id, email_index):
    contact = get_contact(contact_id)
    current_emails = json.loads(contact[4]) if contact else []
    
    if current_emails and 0 <= email_index < len(current_emails):
        current_emails.pop(email_index)
        emails_json = json.dumps(current_emails)
        delete_one_email(contact_id, emails_json)
        
    return redirect(url_for('edit_contact', id=contact[0]))

@app.route('/sort/', methods=['GET'])
def sort_contacts():
    if global_data["order_by"] == 'created':
        global_data["order_by"] = 'firstname'
    else:
        global_data["order_by"] = 'created'
    return redirect(url_for('index'))
