from flask import Flask, render_template,request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

def get_db_conn():
    conn = sqlite3.connect('JobCards.db')
    conn.row_factory = sqlite3.Row
    
    return conn
    
def init_db():
    conn = get_db_conn()
    with app.open_resource('schema.sql') as f:
        conn.executescript(f.read().decode('utf8'))
    conn.close()

@app.route('/')
def index():
    conn = get_db_conn()
    sql = "SELECT * FROM  Customers"
    Customers = conn.execute(sql).fetchall()
    conn.close()
    return render_template("index.html",Customers=Customers)

@app.route('/newCust',methods=('POST','GET'))
def newCust():
    if request.method == 'POST':
        CustFName = request.form['CustFName']
        CustLName = request.form['CustLName']
        CustDetails = request.form['CustDetails']

        if not CustFName or not CustLName:
            flash('all feilds required')
        else:
            conn = get_db_conn()
            conn.execute('INSERT INTO Customers (CustFName,CustLName,CustDetails) VALUES (?,?,?)',(CustFName,CustLName,CustDetails))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template("Newcust.html")

@app.route('/CustSearch', methods=['GET', 'POST'])
def CustSearch():
    conn = get_db_conn()

    if request.method == 'POST':
        search = request.form['Search']
        result = conn.execute(
            "SELECT * FROM Customers WHERE CustFname LIKE ?",('%' + search + '%',)).fetchall()
    else:
        result = conn.execute("SELECT * FROM Customers").fetchall()

    conn.close()
    return render_template('custSearch.html', result=result)

@app.route('/Cust/<int:id>', methods=['GET', 'POST'])
def CustInfo(id):
    print(id)
    conn = get_db_conn()
    result = conn.execute('SELECT * FROM Customers WHERE Cust_ID = (?)',(id,)).fetchall()
    conn.close
    print(result)
    if request.method == 'POST':
        CustFName = request.form['CustFName']
        CustLName = request.form['CustLName']
        CustPNumber = request.form['CustPNumber']
        CustEmail = request.form['CustEmail']
        CustDetails = request.form['CustDetails']
        conn = get_db_conn()
        conn.execute('UPDATE Customers SET CustFName = ?,CustLName = ?,CustPNumber = ?, CustEmail = ? , CustDetails = ?  WHERE Cust_ID = ?',(CustFName,CustLName,CustPNumber,CustEmail,CustDetails,id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        return render_template('CustInfo.html', result=result)

    
@app.route('/delete/<int:id>', methods=('POST',))
def delete_user(id):
    print(id)
    conn = get_db_conn()
    conn.execute('DELETE FROM Customers WHERE cust_ID = (?)', (id,))
    conn.commit() 
    conn.close()
    flash('User deleted successfully!')
    return redirect(url_for('index'))
@app.route('/NewJob',methods=('POST','GET'))
def newjob():
    return render_template("newjob.html")
        


if __name__ == '__main__':
    app.run(debug=True, port=5000)