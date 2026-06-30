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
def get_jobs_for_month(year, month):
    conn = get_db_conn()

    cursor = conn.execute("""
        SELECT Jobs.*, Customers.CustFName, Customers.CustLName
        FROM Jobs
        INNER JOIN Customers
            ON Customers.Cust_ID = Jobs.Cust_ID
        WHERE strftime('%Y', DueDate)=?
          AND strftime('%m', DueDate)=?
    """, (str(year), f"{month:02d}"))

    jobs = cursor.fetchall()
    conn.close()

    job_dict = {}

    for job in jobs:
        job_day = int(job["DueDate"].split("-")[2])

        lines = job["JobDetails"].splitlines()
        second_line = lines[1] if len(lines) > 1 else ""

        job_copy = dict(job)
        job_copy["JobDetails"] = second_line

        job_dict.setdefault(job_day, []).append(job_copy)

    return job_dict
def get_jobs_for_dates(start_date, end_date):
    conn = get_db_conn()
    cursor = conn.execute("""
        SELECT Jobs.*, Customers.CustFName, Customers.CustLName
        FROM Jobs
        INNER JOIN Customers ON Customers.Cust_ID = Jobs.Cust_ID
        WHERE DueDate BETWEEN ? AND ?
    """, (start_date.isoformat(), end_date.isoformat()))

    jobs = cursor.fetchall()
    conn.close()

    job_dict = {}
    for job in jobs:
        job_date = datetime.datetime.strptime(job["DueDate"], "%Y-%m-%d").date()

        lines = job["JobDetails"].splitlines()
        second_line = lines[1] if len(lines) > 1 else ""

        job_copy = dict(job)
        job_copy["JobDetails"] = second_line

        job_dict.setdefault(job_date, []).append(job_copy)

    return job_dict
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
        Status = request.form.get('Status', 'Not Started')
        conn.execute(
            'INSERT INTO Jobs (Cust_ID,BikeBrand,BikeModel,JobDetails,DueDate,Status) VALUES (?,?,?,?,?,?)',
            (Cust_ID, BikeBrand, BikeModel, JobDetails, DueDate, Status)
        )
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
        Status = request.form.get('Status', 'Not Started')
        conn.execute(
            'UPDATE Jobs SET JobDetails = ?, DueDate = ?, Status = ? WHERE JobID = ?',
            (JobDetails, DueDate, Status, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
   sql = "SELECT jobs.* ,Customers.CustFName,Customers.CustLName FROM Jobs INNER JOIN Customers ON Customers.Cust_ID = Jobs.Cust_ID WHERE JobID=?;"
   JobInfo = conn.execute(sql,(id,)).fetchall()
   return render_template('viewjobcard.html', jobInfo=JobInfo, time=time)

@app.route("/calendar")
def calendar_view():

    time = time_gen()
    page_title = "EC Cycles | Calendar"

    today_dt = datetime.datetime.now()

    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    if not year:
        year = today_dt.year

    if not month:
        month = today_dt.month

    today = today_dt.day if (
        year == today_dt.year and month == today_dt.month
    ) else 0

    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    prev_month = 12 if month == 1 else month - 1
    prev_year = year - 1 if month == 1 else year

    next_month = 1 if month == 12 else month + 1
    next_year = year + 1 if month == 12 else year

    jobs = get_jobs_for_month(year, month)

    return render_template(
        "calendar.html",
        time=time,
        page_title=page_title,

        cal=cal,
        jobs=jobs,

        today=today,

        year=year,
        month=month,
        month_name=month_name,

        prev_month=prev_month,
        prev_year=prev_year,

        next_month=next_month,
        next_year=next_year,

        week=0
    )

@app.route("/calendar/week")
def timetable():

    time = time_gen()
    page_title = "EC Cycles | Calendar"

    today_dt = datetime.datetime.now()
    today_date = today_dt.date()

    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    week = request.args.get("week", type=int)
    today_param = request.args.get("today", type=int)

    if not year:
        year = today_dt.year
    if not month:
        month = today_dt.month

    cal_obj = calendar.Calendar(firstweekday=0)
    cal = cal_obj.monthdatescalendar(year, month)
    month_name = calendar.month_name[month]

    prev_month = 12 if month == 1 else month - 1
    prev_year = year - 1 if month == 1 else year

    next_month = 1 if month == 12 else month + 1
    next_year = year + 1 if month == 12 else year

    month_back = cal_obj.monthdatescalendar(prev_year, prev_month)
    month_forward = cal_obj.monthdatescalendar(next_year, next_month)

    prev_week_count = len(month_back) - 1

    if week is None:
        week = 0
        if year == today_dt.year and month == today_dt.month:
            for i, w in enumerate(cal):
                if today_date in w:
                    week = i
                    break

    week = max(0, min(week, len(cal) - 1))  # keep week index in range
    cal_week = cal[week]

    if today_param:
        today = next((d for d in cal_week if d.day == today_param), cal_week[0])
    elif today_date in cal_week:
        today = today_date
    else:
        today = cal_week[0]

    jobs = get_jobs_for_dates(cal_week[0], cal_week[-1])

    return render_template(
        "calendarWeek.html",
        time=time,
        page_title=page_title,
        cal=cal,
        cal_week=cal_week,
        jobs=jobs,
        today=today,
        year=year,
        month=month,
        month_name=month_name,
        week=week,
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year,
        prev_week_count=prev_week_count,
        month_back=month_back,
        month_forward=month_forward,
    )

@app.route('/calendar/<int:year>/<int:month>/<int:day>')
def jobs_by_day(year, month, day):
    time = time_gen()
    page_title = "EC Cycles | Calendar"

    current_date = datetime.date(year, month, day)
    today_date = datetime.date.today()

    prev_date = current_date - datetime.timedelta(days=1)
    next_date = current_date + datetime.timedelta(days=1)

    jobs_dict = get_jobs_for_dates(current_date, current_date)
    jobs = jobs_dict.get(current_date, [])

    day_name = current_date.strftime("%A")
    date_label = f"{current_date.day} {current_date.strftime('%B %Y')}"

    return render_template(
        'jobs_by_day.html',
        time=time,
        page_title=page_title,

        jobs=jobs,
        current_date=current_date,
        is_today=(current_date == today_date),

        day_name=day_name,
        date_label=date_label,

        year=year,
        month=month,
        day=day,

        prev_date=prev_date,
        next_date=next_date,
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)