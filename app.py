from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import text

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

    @property
    def formatted_date(self):
        """Return a human-friendly date string for templates.

        Examples:
        - Today • 2:43 PM
        - Yesterday • 9:12 AM
        - Mar 04, 2025 • 2:43 PM
        """
        if not self.date:
            return ''
        now = datetime.utcnow()
        try:
            dt = self.date
        except Exception:
            return str(self.date)

        # compare dates in UTC (assumes stored in UTC or naive)
        # Use portable %I (12-hour) and strip leading zero for nicer display.
        time_str = dt.strftime('%I:%M %p').lstrip('0')
        if dt.date() == now.date():
            return f"Today • {time_str}"
        if dt.date() == (now.date() - timedelta(days=1)):
            return f"Yesterday • {time_str}"

        # e.g., Mar 4, 2025 • 2:43 PM (strip zero-padded day)
        formatted = dt.strftime('%b %d, %Y • %I:%M %p').replace(' 0', ' ')
        return formatted

@app.route("/", methods=["GET"])
def home():
    # support searching via ?q=... on GET
    search_q = request.args.get('q', type=str)

    # choose query set depending on search
    if search_q:
        # filter by title or description (contains -> LIKE '%q%')
        allTodo = Todo.query.filter((Todo.title.contains(search_q)) | (Todo.desc.contains(search_q))).order_by(Todo.sno).all()
    else:
        allTodo = Todo.query.order_by(Todo.sno).all()

    total = Todo.query.count()
    completed = Todo.query.filter_by(completed=True).count()
    pending = total - completed

    return render_template("index.html", allTodo=allTodo, total=total, completed=completed, pending=pending, search_q=search_q)


@app.route('/add', methods=["GET","POST"])
def add():
    # New page for creating todos
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        if title and desc:
            todo = Todo(title=title, desc=desc)
            db.session.add(todo)
            db.session.commit()
            return redirect('/')
        # If missing data, just fall through to re-render the form (could add an error message later)
    return render_template('add.html')

@app.route("/update/<int:sno>", methods=["GET","POST"])
def update(sno):
    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["desc"]
        todo = Todo.query.filter_by(sno=sno).first()
        todo.title=title
        todo.desc=desc
        db.session.commit()  
        return redirect("/")
      
    todo = Todo.query.filter_by(sno=sno).first()
    return render_template("update.html", todo=todo)

@app.route("/delete/<int:sno>")
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")


@app.route('/complete/<int:sno>')
def complete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if todo:
        todo.completed = not bool(todo.completed)
        db.session.commit()
    return redirect('/')


@app.route('/about')
def about():
    return render_template('about.html')

with app.app_context():
    # Ensure table exists and add missing column if necessary (SQLite friendly)
    db.create_all()
    try:
        res = db.session.execute(text("PRAGMA table_info('todo')")).all()
        cols = [r[1] for r in res]
        if 'completed' not in cols:
            db.session.execute(text("ALTER TABLE todo ADD COLUMN completed BOOLEAN DEFAULT 0"))
            db.session.commit()
    except Exception:
        # If the DB or PRAGMA isn't available, skip migration step.
        pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
