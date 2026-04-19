from flask import Flask, render_template, url_for, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "DBMS"

# Configure Database
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "12345"
app.config['MYSQL_DB'] = "jobportal3"



mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def login():
    find = 0
    if request.method == 'POST':
        # Retrieve login form entries
        loginDetails = request.form
        email = loginDetails['email']
        password = loginDetails['password']
        cur = mysql.connection.cursor()
        # Use parameterized query to avoid SQL injection
        find = cur.execute("SELECT * FROM jobseeker WHERE email = %s AND password = %s", (email, password))
        details = cur.fetchall()
        cur.close()
        # If record found, log in the user and redirect to home page
        if find != 0:
            user = details[0][0]
            session["user"] = user
            print(f"Logged in user id: {user}")
            return redirect('/home')
    # If already logged in, redirect or show the login page with find=0
    if "user" in session:
        return redirect(url_for("home"))
    return render_template('login.html', find=find)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Retrieve entries from the signup form
        userDetails = request.form
        fname = userDetails['fname']
        lname = userDetails['lname']
        phone_num = userDetails['phone_num']
        address = userDetails['address']
        email = userDetails['email']
        password = userDetails['password']
        cpassword = userDetails['cpassword']
        # Check if both passwords match
        if password == cpassword:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO jobseeker(first_name, last_name, phone_number, address, email, password) VALUES (%s, %s, %s, %s, %s, %s)",
                (fname, lname, phone_num, address, email, password)
            )
            mysql.connection.commit()
            cur.close()
            return redirect('/')
        else:
            return redirect('signup')
    return render_template('signup.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if "user" in session:
        user = session["user"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM jobseeker WHERE jobseeker_id = %s", (user,))
        userdet = cur.fetchall()
        cur.close()
        if userdet:
            name = userdet[0][1]  # Adjust the index if needed
            return render_template('home.html', name=name)
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if "user" in session:
        user = session['user']
        cur = mysql.connection.cursor()
        # Get applied jobs
        cur.execute("""
            SELECT job.job_title, job.job_type, company.name, company.location, 
                   job.job_salary, job.job_id 
            FROM job 
            INNER JOIN company ON job.company_id = company.company_id 
            WHERE job.job_id IN (
                SELECT job_id FROM apply WHERE jobseeker_id = %s
            )
            """, (user,))
        applied_jobs = cur.fetchall()
        
        # Get profile details
        cur.execute("SELECT * FROM profile WHERE jobseeker_id = %s", (user,))
        profile_details = cur.fetchall()
        profile_details = profile_details[-1] if profile_details else None
        
        # Get resume details
        cur.execute("SELECT * FROM resume WHERE jobseeker_id = %s", (user,))
        resume_details = cur.fetchall()
        resume_details = resume_details[-1] if resume_details else None

        cur.close()
        return render_template('profile.html', applied_jobs=applied_jobs,
                               profile_details=profile_details, resume_details=resume_details)
    return redirect(url_for('login'))

@app.route('/manageprofile', methods=['GET', 'POST'])
def manageprofile():
    if "user" in session:
        user = session['user']
        cur = mysql.connection.cursor()
        # Get current profile data for the user
        cur.execute("SELECT * FROM profile WHERE jobseeker_id = %s", (user,))
        profile_data = cur.fetchall()
        
        if request.method == 'POST':
            profile = request.form
            college = profile['college']
            dept = profile['dept']
            education = profile['education']
            
            # Handle resume file upload safely
            resume_file = request.files.get('resume')
            filename = resume_file.filename if resume_file else ''
            
            # Refresh profile existence query
            cur.execute("SELECT * FROM profile WHERE jobseeker_id = %s", (user,))
            exist = cur.fetchone()  # Use fetchone since existence check is needed

            if exist:
                # Update existing profile
                cur.execute("UPDATE profile SET college = %s, department = %s, education = %s WHERE jobseeker_id = %s", 
                            (college, dept, education, user))
                mysql.connection.commit()
            else:
                # Insert new profile record
                cur.execute("INSERT INTO profile(college, department, education, jobseeker_id) VALUES (%s, %s, %s, %s)", 
                            (college, dept, education, user))
                mysql.connection.commit()
            
            # Handle resume entry
            cur.execute("SELECT * FROM resume WHERE jobseeker_id = %s", (user,))
            res = cur.fetchone()

            if res:
                cur.execute("UPDATE resume SET filename = %s WHERE jobseeker_id = %s", (filename, user))
                mysql.connection.commit()
            else:
                cur.execute("INSERT INTO resume(filename, jobseeker_id) VALUES (%s, %s)", (filename, user))
                mysql.connection.commit()
            
            cur.close()
            return redirect(url_for('profile'))
        
        cur.close()
        # Use conditional expression: if profile_data is empty, pass None
        return render_template('manageprofile.html', profile_data=profile_data[-1] if profile_data else None)
    return redirect(url_for('login'))

@app.route('/jobs', methods=['GET', 'POST'])
def jobs():
    if "user" in session:
        cur = mysql.connection.cursor()
        if request.method == 'POST':
            searchjob = request.form
            keyword = searchjob.get('keyword', '')
            location = searchjob.get('location', '')
            # Construct query based on available search criteria
            if keyword and not location:
                query = """
                    SELECT job.job_title, job.job_type, company.name, company.location, 
                           job.job_salary, job.job_description, job.job_id 
                    FROM job 
                    INNER JOIN company ON job.company_id = company.company_id 
                    WHERE job.job_title LIKE %s OR job.job_type LIKE %s OR job.job_description LIKE %s
                """
                like_keyword = f"%{keyword}%"
                count_search = cur.execute(query, (like_keyword, like_keyword, like_keyword))
            elif location and not keyword:
                query = """
                    SELECT job.job_title, job.job_type, company.name, company.location, 
                           job.job_salary, job.job_description, job.job_id 
                    FROM job 
                    INNER JOIN company ON job.company_id = company.company_id 
                    WHERE company.location LIKE %s
                """
                like_location = f"%{location}%"
                count_search = cur.execute(query, (like_location,))
            elif location and keyword:
                query = """
                    SELECT job.job_title, job.job_type, company.name, company.location, 
                           job.job_salary, job.job_description, job.job_id 
                    FROM job 
                    INNER JOIN company ON job.company_id = company.company_id 
                    WHERE ((job.job_title LIKE %s) OR (job.job_type LIKE %s) OR (job.job_description LIKE %s))
                      AND company.location LIKE %s
                """
                like_keyword = f"%{keyword}%"
                like_location = f"%{location}%"
                count_search = cur.execute(query, (like_keyword, like_keyword, like_keyword, like_location))
            else:
                count_search = 0

            jobsearch = cur.fetchall()
            cur.close()
            return render_template('jobsearch.html', jobsearch=jobsearch)

        # Display all jobs if not a POST request
        query_all_jobs = """
            SELECT job.job_title, job.job_type, company.name, company.location, 
                   job.job_salary, job.job_description, job.job_id 
            FROM job 
            INNER JOIN company ON job.company_id = company.company_id
        """
        count_jobs = cur.execute(query_all_jobs)
        if count_jobs > 0:
            alljobs = cur.fetchall()
            cur.close()
            return render_template('jobs.html', alljobs=alljobs)
        cur.close()
    return redirect(url_for('login'))

@app.route('/jobsearch')
def jobsearch():
    if "user" in session:
        return render_template('jobsearch.html')
    return redirect(url_for('login'))

@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if "user" in session:
        user = session['user']
        if request.method == 'POST':
            apply_form = request.form
            jobid = apply_form['j_id']
            cur = mysql.connection.cursor()
            # Check if the user has already applied for the job
            applied = cur.execute("SELECT * FROM apply WHERE jobseeker_id = %s AND job_id = %s", (user, jobid))
            if applied == 0:
                cur.execute("INSERT INTO apply(jobseeker_id, job_id) VALUES (%s, %s)", (user, jobid))
                mysql.connection.commit()
            cur.close()
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/interviews')
def interviews():
    if "user" in session:
        user = session['user']
        cur = mysql.connection.cursor()
        # Retrieve interviews for the jobs the user has applied for
        check_apply = cur.execute("""
            SELECT * 
            FROM apply 
            INNER JOIN interview ON (apply.jobseeker_id = interview.jobseeker_id AND apply.job_id = interview.job_id)
            WHERE interview.jobseeker_id = %s
            """, (user,))
        if check_apply > 0:
            query = """
                SELECT interview.jobseeker_id, job.job_title, company.name, interview.date, interview.time 
                FROM job 
                INNER JOIN company ON job.company_id = company.company_id 
                INNER JOIN interview ON interview.job_id = job.job_id 
                WHERE interview.jobseeker_id = %s 
                  AND interview.job_id IN (
                      SELECT apply.job_id FROM apply 
                      INNER JOIN interview ON (apply.jobseeker_id = interview.jobseeker_id AND apply.job_id = interview.job_id) 
                      WHERE interview.jobseeker_id = %s
                  )
            """
            interview_count = cur.execute(query, (user, user))
            schedule = cur.fetchall() if interview_count > 0 else None
        else:
            schedule = None
        cur.close()
        return render_template('interview.html', schedule=schedule)
    return redirect(url_for('login'))

@app.route('/results')
def results():
    if "user" in session:
        user = session['user']
        cur = mysql.connection.cursor()
        # Check if results exist for the applied jobs
        chk_apply = cur.execute("""
            SELECT * 
            FROM apply 
            INNER JOIN result ON (apply.jobseeker_id = result.jobseeker_id AND apply.job_id = result.job_id)
            WHERE result.jobseeker_id = %s
            """, (user,))
        if chk_apply > 0:
            query = """
                SELECT result.jobseeker_id, job.job_title, company.name, company.location, result.status 
                FROM job 
                INNER JOIN company ON job.company_id = company.company_id 
                INNER JOIN result ON result.job_id = job.job_id 
                WHERE result.jobseeker_id = %s 
                  AND result.job_id IN (
                      SELECT apply.job_id FROM apply 
                      INNER JOIN result ON (apply.jobseeker_id = result.jobseeker_id AND apply.job_id = result.job_id) 
                      WHERE result.jobseeker_id = %s
                  )
            """
            r = cur.execute(query, (user, user))
            res = cur.fetchall() if r > 0 else None
        else:
            res = None
        cur.close()
        return render_template('results.html', res=res)
    return redirect(url_for('login'))

@app.route('/account')
def account():
    if "user" in session:
        user = session["user"]
        cur = mysql.connection.cursor()
        # Get jobseeker details
        cur.execute("SELECT * FROM jobseeker WHERE jobseeker_id = %s", (user,))
        acc = cur.fetchall()
        # Count applied jobs
        a = cur.execute("SELECT COUNT(job_id) FROM apply WHERE jobseeker_id = %s GROUP BY jobseeker_id", (user,))
        apply_count = cur.fetchall()[0][0] if a > 0 else 0
        # Count results declared
        r = cur.execute("SELECT COUNT(job_id) FROM result WHERE jobseeker_id = %s GROUP BY jobseeker_id", (user,))
        res_count = cur.fetchall()[0][0] if r > 0 else 0
        # Count interviews scheduled
        i = cur.execute("SELECT COUNT(job_id) FROM interview WHERE jobseeker_id = %s GROUP BY jobseeker_id", (user,))
        interview_count = cur.fetchall()[0][0] if i > 0 else 0
        cur.close()
        return render_template('account.html', acc=acc, apply=apply_count, res=res_count, interview=interview_count)
    return redirect(url_for("login"))

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
