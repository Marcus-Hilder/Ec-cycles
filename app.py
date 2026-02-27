from flask import Flask, render_template,request, redirect, url_for, flash
import sqlite3
import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"
def time_gen():
    time_dict = {"":""}
    day_info = datetime.datetime.now()
    date = day_info.strftime("%x")
    time = day_info.strftime("%X")
    time_dict["Date"] = date
    time_dict["Time"] = time
    return time_dict
def get_db_conn():
    """setup connection to sql database"""
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
    """main home page loads curent jobs but plans to have the 
    curent day's jobs on it"""
    time = time_gen()
    # print(date2)
    conn = get_db_conn()
    sql = "SELECT jobs.* ,Customers.CustFName,Customers.CustLName FROM Jobs INNER JOIN Customers ON Customers.Cust_ID = Jobs.Cust_ID;"
    jobs = conn.execute(sql).fetchall()
    conn.close()
    return render_template("index.html", jobs=jobs, time=time)

@app.route('/newCust',methods=('POST','GET'))
def newCust():
    time = time_gen()

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
    return render_template("Newcust.html", time=time)

@app.route('/CustSearch', methods=['GET', 'POST'])
def CustSearch():
    time = time_gen()
    conn =  get_db_conn()
    search = request.args.get("search")

    if search:
        words = search.split()
        query = "SELECT * FROM Customers WHERE "
        conditons = []
        values = []

        for word in words:
            conditons.append("(custFName LIKE ? or CustLName LIKE ?)")
            values.append("%"+ word + "%")
            values.append("%"+ word + "%")
        query += " AND ".join(conditons)

        

        CustInfo = conn.execute(query, values).fetchall()
        
    else:
        CustInfo = conn.execute("SELECT * FROM Customers").fetchall()
    
    conn.close()
    return render_template("custSearch.html", CustInfo=CustInfo, time=time)

@app.route('/Cust/<int:id>', methods=['GET', 'POST'])
def CustInfo(id):
    time = time_gen()
    conn = get_db_conn()
    CustInfo = conn.execute('SELECT * FROM Customers WHERE Cust_ID = (?)',(id,)).fetchall()
    conn.close()
    if request.method == 'POST':
        CustFName = request.form['CustFName']
        CustLName = request.form['CustLName']
        CustPNumber = request.form['CustPNumber']
        CustEmail = request.form['CustEmail']
        CustDetails = request.form['CustDetails']
        conn = get_db_conn()
        conn.execute('UPDATE Customers SET CustFName = ?,CustLName = ?,CustPNumber = ?, CustEmail = ? , CustDetails = ? \
                      WHERE Cust_ID = ?',(CustFName,CustLName,CustPNumber,CustEmail,CustDetails,id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('CustInfo.html', CustInfo=CustInfo, time = time)
@app.route('/delete/<int:id>', methods=('POST',))
def delete_user(id):
    print(id)
    conn = get_db_conn()    
    conn.execute('DELETE FROM Customers WHERE cust_ID = (?)', (id,))
    conn.commit() 
    conn.close()
    flash('User deleted successfully!')
    return redirect(url_for('index'))

@app.route('/NewJobCard',methods=('POST','GET'))
def NewJobCard():
    time = time_gen()
    conn = get_db_conn()

    search = request.args.get('search', '')
    result = []
    if search:
        result = conn.execute(
            "SELECT * FROM Customers WHERE CustFName LIKE ?",
            ('%' + search + '%',)
        ).fetchall()
    if request.method == 'POST':
        Cust_ID = request.form['Cust_ID']
        BikeBrand = request.form['BikeBrand']
        BikeModel = request.form['BikeModel']
        JobDetails = request.form['JobDetails']
        conn.execute('INSERT INTO Jobs (Cust_ID,BikeBrand,BikeModel,JobDetails) VALUES (?,?,?,?)',(Cust_ID,BikeBrand,BikeModel,JobDetails))
        conn.commit()
        return redirect(url_for('index'))
   
    conn.close()
    return render_template("NewJobCard.html", result=result, search=search, time = time)
@app.route('/NewJobCard1',methods=('POST','GET'))
def NewJobCard1():
    time = time_gen()
    conn = get_db_conn()
    return render_template("NewjobCard1.html",time = time)
@app.route('/JobSearch',methods=('POST','GET'))
def JobSearch():
    time = time_gen()
    conn = get_db_conn()

    search = request.args.get("search", time = time)

    if search:
        words = search.split()
        query = "SELECT * FROM Customers WHERE "
        conditons = []
        values = []

        for word in words:
            conditons.append("(custFName LIKE ? or CustLName LIKE ?)")
            values.append("%"+ word + "%")
            values.append("%"+ word + "%")
        query += " AND ".join(conditons)
        JobInfo = conn.execute(query, values).fetchall()
        
    else:
        conn = get_db_conn()
        sql = "SELECT jobs.* ,Customers.CustFName,Customers.CustLName FROM Jobs INNER JOIN Customers ON Customers.Cust_ID = Jobs.Cust_ID;"
        JobInfo = conn.execute(sql).fetchall()
        conn.close()
    
    conn.close()
    return render_template("JobSearch.html", JobInfo=JobInfo, time = time)
@app.route('/ViewJobCard/<int:id>', methods=['GET', 'POST'] )
def ViewJobCard(id):
   time = time_gen()
   conn = get_db_conn()
   if request.method == 'POST':
        Cust_ID = request.form['Cust_ID']
        
        JobDetails = request.form['JobDetails']
        conn.execute('UPDATE Jobs SET JobDetails = ? WHERE Cust_ID = ? ',(JobDetails,Cust_ID))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
   sql = "SELECT jobs.* ,Customers.CustFName,Customers.CustLName FROM Jobs INNER JOIN Customers ON Customers.Cust_ID = Jobs.Cust_ID WHERE JobID=?;"
   JobInfo = conn.execute(sql,(id,)).fetchall()
   return render_template('viewjobcard.html', jobInfo=JobInfo, time=time)



if __name__ == '__main__':
    app.run(debug=True, port=5000)