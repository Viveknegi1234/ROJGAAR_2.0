from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
from flask import jsonify
app = Flask(__name__)

app.config['SECRET_KEY'] = "rojgaar-secret"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.context_processor
def inject_notifications():

    if "user_id" not in session:
        return dict(notifications=0)

    count = Application.query.filter_by(
        status="pending"
    ).count()

    return dict(notifications=count)

@app.context_processor
def inject_user():

    if "user_id" in session:
        user = User.query.get(session["user_id"])
        return dict(user=user)

    return dict(user=None)

# =============================
# DATABASE MODELS
# =============================

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)

    password = db.Column(db.String(200))

    user_type = db.Column(db.String(20))

    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Worker(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    skills = db.Column(db.String(200))
    experience = db.Column(db.Integer)
    daily_wage = db.Column(db.Integer)

    rating = db.Column(db.Float, default=4.5)


class Job(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    employer_id = db.Column(db.Integer)

    title = db.Column(db.String(200))
    description = db.Column(db.Text)

    wage = db.Column(db.Integer)

    category = db.Column(db.String(100))

    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Application(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(db.Integer)
    worker_id = db.Column(db.Integer)

    status = db.Column(db.String(20), default="pending")

    applied_at = db.Column(db.DateTime, default=datetime.utcnow)




class Message(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(db.Integer)
    receiver_id = db.Column(db.Integer)

    message = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Review(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    employer_id = db.Column(db.Integer)
    worker_id = db.Column(db.Integer)

    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# =============================
# LOGIN REQUIRED
# =============================

def login_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return wrapper


# =============================
# ROUTES
# =============================

@app.route("/")
def index():
    return render_template("index.html")


# =============================
# SIGNUP
# =============================

@app.route("/signup", methods=["GET","POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        user_type = request.form["user_type"]

        hashed = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password=hashed,
            user_type=user_type
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created")

        return redirect(url_for("login"))

    return render_template("signup.html")


# =============================
# LOGIN
# =============================

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User not found")
            return redirect(url_for("login"))

        if not check_password_hash(user.password, password):
            flash("Wrong password")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        session["user_type"] = user.user_type
        session["user_name"] = user.name

        return redirect(url_for("dashboard"))

    return render_template("login.html")

# =============================
# LOGOUT
# =============================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("index"))

# =============================
# FIND WORKERS PAGE
# =============================

@app.route("/find-workers")
@login_required
def find_workers_page():

    return render_template("find_workers.html")

# =============================
# MESSAGES PAGE
# =============================

@app.route("/messages")
@login_required
def messages_page():

    msgs = Message.query.filter(
        (Message.sender_id == session["user_id"]) |
        (Message.receiver_id == session["user_id"])
    ).order_by(Message.created_at.desc()).all()

    return render_template("messages.html", messages=msgs)
# =============================
# FIND JOBS PAGE
# =============================

@app.route("/find-jobs")
@login_required
def find_jobs_page():

    return render_template("find_jobs.html")


@app.route("/worker_dashboard")
def worker_dashboard():

    jobs = [
        {
            "title": "Fix Kitchen Sink",
            "location": "Delhi",
            "pay": "₹500"
        },
        {
            "title": "Electrical Wiring Repair",
            "location": "Noida",
            "pay": "₹700"
        },
        {
            "title": "Paint Living Room",
            "location": "Gurgaon",
            "pay": "₹1200"
        },
        {
            "title": "Install Ceiling Fan",
            "location": "Faridabad",
            "pay": "₹400"
        }
    ]

    return render_template("worker_dashboard.html", jobs=jobs)

# =============================
# DASHBOARD
# =============================

@app.route("/dashboard")
@login_required
def dashboard():

    if session["user_type"] == "employer":
        return render_template("employer_dashboard.html")

    return render_template("worker_dashboard.html")


# =============================
# POST JOB
# =============================

@app.route("/post-job")
@login_required
def post_job_page():

    if session["user_type"] != "employer":
        return redirect(url_for("dashboard"))

    return render_template("post_job.html")


@app.route("/api/post_job", methods=["POST"])
@login_required
def post_job():

    data = request.json

    job = Job(

        employer_id=session["user_id"],

        title=data["title"],
        description=data["description"],
        wage=data["wage"],
        category=data["category"],

        lat=data.get("lat"),
        lng=data.get("lng")
    )

    db.session.add(job)
    db.session.commit()

    return jsonify({"success":True})


# =============================
# JOBS API
# =============================



@app.route("/api/jobs")
def api_jobs():

    jobs = [
        {
            "title": "Fix Kitchen Sink",
            "description": "Need plumber for kitchen sink repair",
            "wage": 500
        },
        {
            "title": "Electrical Wiring Repair",
            "description": "House wiring issue needs fixing",
            "wage": 700
        },
        {
            "title": "Paint Living Room",
            "description": "Need painter for 1 room",
            "wage": 1200
        },
        {
            "title": "Gardner for feilds",
            "description": "Gardner for 2 days",
            "wage": 500 
        },
        {
            "title": "chef",
            "description": "chefs for making lunch",
            "wage": 900
        },
          ]

    return jsonify(jobs)


# =============================
# APPLY JOB
# =============================

@app.route("/apply/<job_id>")
@login_required
def apply(job_id):

    application = Application(

        job_id=job_id,
        worker_id=session["user_id"]
    )

    db.session.add(application)
    db.session.commit()

    flash("Applied successfully")

    return redirect("/dashboard")

# =============================
# WORKER PROFILE
# =============================

@app.route("/worker-profile")
@login_required
def worker_profile():

    user = User.query.get(session["user_id"])
    worker = Worker.query.filter_by(user_id=user.id).first()

    return render_template("worker_profile.html", user=user, worker=worker)


# =============================
# EMPLOYER PROFILE
# =============================

@app.route("/employer-profile")
@login_required
def employer_profile():

    user = User.query.get(session["user_id"])

    return render_template("employer_profile.html", user=user)

# =============================
# FIND WORKERS
# =============================

@app.route("/api/workers")
def api_workers():
    workers = [
        {
            "name": "Ramesh",
            "skills": "Plumber",
            "lat": 28.6139,
            "lng": 77.2090
        },
        {
            "name": "Suresh",
            "skills": "Electrician",
            "lat": 28.6200,
            "lng": 77.2150
        },
        {
            "name": "Amit",
            "skills": "Carpenter",
            "lat": 28.6050,
            "lng": 77.2000
        },
        {
            "name": "Rahul",
            "skills": "Painter",
            "lat": 28.6300,
            "lng": 77.2200
        }
    ]

    return workers


 ##  job application route

@app.route("/apply-job/<int:job_id>")
@login_required
def apply_job(job_id):

    if session["user_type"] != "worker":
        flash("Only workers can apply")
        return redirect("/dashboard")

    existing = Application.query.filter_by(
        job_id=job_id,
        worker_id=session["user_id"]
    ).first()

    if existing:
        flash("Already applied")
        return redirect("/dashboard")

    application = Application(
        job_id=job_id,
        worker_id=session["user_id"]
    )

    db.session.add(application)
    db.session.commit()

    flash("Application sent")

    return redirect("/dashboard")


## accept reject worker

@app.route("/application/<int:id>/<action>")
@login_required
def manage_application(id, action):

    app_obj = Application.query.get(id)

    if action == "accept":
        app_obj.status = "accepted"

    elif action == "reject":
        app_obj.status = "rejected"

    db.session.commit()

    return redirect("/dashboard")

# =============================
# MAP
# =============================

@app.route("/map")
@login_required
def map_page():

    role = session.get("user_type")

    return render_template("map.html", role=role)


## messages system

@app.route("/send-message", methods=["POST"])
@login_required
def send_message():

    receiver = request.form["receiver_id"]
    message = request.form["message"]

    msg = Message(

        sender_id=session["user_id"],
        receiver_id=receiver,
        message=message

    )

    db.session.add(msg)
    db.session.commit()

    return redirect("/messages")


## worker rating system

@app.route("/rate-worker", methods=["POST"])
@login_required
def rate_worker():

    worker_id = request.form["worker_id"]
    rating = request.form["rating"]
    comment = request.form["comment"]

    review = Review(

        employer_id=session["user_id"],
        worker_id=worker_id,
        rating=rating,
        comment=comment

    )

    db.session.add(review)
    db.session.commit()

    flash("Review submitted")

    return redirect("/dashboard")

# =============================
# RUN SERVER
# =============================

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)
