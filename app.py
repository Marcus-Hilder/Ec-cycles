from flask import Flask, render_template,request, redirect, url_for, flash

import sqlite3
import datetime
import calendar

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
    conn = get_db_conn()
    templates = conn.execute("SELECT * FROM JobTemplates").fetchall()
    
    if request.method == 'POST':
        Cust_ID = request.form['Cust_ID']
        BikeBrand = request.form['BikeBrand']
        BikeModel = request.form['BikeModel']
        JobDetails = request.form['JobDetails']
        DueDate = request.form['Date']
        conn.execute('INSERT INTO Jobs (Cust_ID,BikeBrand,BikeModel,JobDetails,DueDate) VALUES (?,?,?,?,?)',(Cust_ID,BikeBrand,BikeModel,JobDetails,DueDate))
        conn.commit()
        return redirect(url_for('index'))
    return render_template("NewjobCard.html",time = time, search = search, result = result, templates = templates)

@app.route('/JobTemplates', methods=['GET', 'POST'])
def job_templates():
    time = time_gen()
    conn = get_db_conn()
    
    if request.method == 'POST':
        name = request.form['TemplateName']
        text = request.form['TemplateText']
        if name and text:
            conn.execute("INSERT INTO JobTemplates (TemplateName, TemplateText) VALUES (?, ?)", (name, text))
            conn.commit()
    
    templates = conn.execute("SELECT * FROM JobTemplates").fetchall()
    conn.close()
    
    return render_template('job_templates.html', templates=templates, time=time)

@app.route('/JobSearch',methods=('POST','GET'))
def JobSearch():
    time = time_gen()
    conn = get_db_conn()

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
        DueDate = request.form['DueDate']
        JobDetails = request.form['JobDetails']
        print(DueDate)
        conn.execute('UPDATE Jobs SET JobDetails = ?, DueDate = ?  WHERE JobID = ? ',(JobDetails,DueDate,id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
   sql = "SELECT jobs.* ,Customers.CustFName,Customers.CustLName FROM Jobs INNER JOIN Customers ON Customers.Cust_ID = Jobs.Cust_ID WHERE JobID=?;"
   JobInfo = conn.execute(sql,(id,)).fetchall()
   return render_template('viewjobcard.html', jobInfo=JobInfo, time=time)
@app.route('/calendar', methods=['GET'])
def calendar_view():
    time = time_gen()

    # Get year/month from URL params or default to today
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    today_dt = datetime.datetime.now()

    if not year or not month:
        year = today_dt.year
        month = today_dt.month

    # Highlight today only if viewing current month
    today = today_dt.day if year == today_dt.year and month == today_dt.month else None

    cal = calendar.monthcalendar(year, month)

    # Fetch jobs for this month
    conn = get_db_conn()
    cursor = conn.execute("""
        SELECT jobs.*, Customers.CustFName, Customers.CustLName
        FROM Jobs
        INNER JOIN Customers ON Customers.Cust_ID = Jobs.Cust_ID
        WHERE strftime('%Y', DueDate) = ? AND strftime('%m', DueDate) = ?
    """, (str(year), f"{month:02d}"))
    jobs = cursor.fetchall()
    conn.close()

    # Convert jobs into dictionary {day_number: [jobs]}, only 2nd line of JobDetails
    job_dict = {}
    for job in jobs:
        job_day = int(job["DueDate"].split("-")[2])
        lines = job["JobDetails"].splitlines()
        second_line = lines[1] if len(lines) > 1 else ""  # second line only

        job_copy = dict(job)
        job_copy["JobDetails"] = second_line

        if job_day not in job_dict:
            job_dict[job_day] = []
        job_dict[job_day].append(job_copy)

    # Previous/next month
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year += 1

    return render_template(
        "calendar.html",
        calendar=cal,
        year=year,
        month=month,
        today=today,
        jobs=job_dict,
        time=time,
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year
    )
@app.route('/calendar/<int:year>/<int:month>/<int:day>')
def jobs_by_day(year, month, day):
    time = time_gen()
    conn = get_db_conn()
    cursor = conn.execute("""
        SELECT jobs.*, Customers.CustFName, Customers.CustLName
        FROM Jobs
        INNER JOIN Customers ON Customers.Cust_ID = Jobs.Cust_ID
        WHERE DueDate = ?
    """, (f"{year}-{month:02d}-{day:02d}",))
    jobs = cursor.fetchall()
    conn.close()

    return render_template('jobs_by_day.html', jobs=jobs, year=year, month=month, day=day, time=time)


if __name__ == '__main__':
    app.run(debug=True, port=5000)