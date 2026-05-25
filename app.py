from flask import Flask, render_template, request, redirect, session
from book import Book 
from user import User
from db import cur, conn
 
app = Flask(__name__)
app.secret_key = "secret123"   # ✅ needed for session
 
# ✅ CREATE OBJECT HERE
obj = User(cur, conn)
 
@app.route('/')
def index():
    return render_template("home.html")   # ✅ FIXED 

@app.route("/librarian-login", methods=["GET", "POST"])
def librarian_login():
    if request.method == "POST":
        name = request.form["name"].title()
        password = request.form["password"]

        if obj.librarian_login_web(name, password):
            session["admin"] = name  
            return redirect("/admin_dashboard")
        return render_template("librarian_login.html", message="Invalid Credentials")
    return render_template("librarian_login.html") 

@app.route("/admin_dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/")

    books = obj.get_books()

    return render_template("admin_dashboard.html", books=books) 

@app.route("/add-qty/<int:book_id>", methods=["POST"])
def add_qty(book_id):

    qty = int(request.form["qty"])

    obj.add_quantity(book_id, qty)

    return redirect("/admin_dashboard")

@app.route("/delete/<int:book_id>")
def delete_book(book_id):

    obj.delete_book(book_id)

    return redirect("/admin_dashboard")


@app.route("/add_new", methods=["GET","POST"])
def add_new():

    if request.method == "POST":

        book_id = int(request.form["id"])
        book_name = request.form["name"].title()
        author = request.form["author"].title()
        qty = int(request.form["qty"])

        msg = obj.add_new_book(book_id, book_name, author, qty)

        return render_template("add_new.html", message=msg) 

    return render_template("add_new.html")

@app.route("/admin-history")
def admin_history():

    if "admin" not in session:
        return redirect("/librarian-login")

    data = obj.get_transactions()

    return render_template("admin_history.html", data=data)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/") 

@app.route("/register", methods=["GET", "POST"])
def register():

    if "reg_attempts" not in session:
        session["reg_attempts"] = 3

    if request.method == "POST":

        name = request.form["name"]
        ph = request.form["phone"]

        msg = obj.register(name, ph)

        if "Invalid phone" in msg:
            session["reg_attempts"] -= 1

            if session["reg_attempts"] == 0:
                session.pop("reg_attempts")
                return redirect("/")

            return render_template("register.html",
                                   message=f"{msg} | {session['reg_attempts']} attempts left")

        session.pop("reg_attempts", None) 
        
        return redirect("/login")

    return render_template("register.html") 

@app.route("/login", methods=["GET", "POST"])
def login():

    if "login_attempts" not in session:
        session["login_attempts"] = 3

    if request.method == "POST":
        name = request.form["name"]
        ph = request.form["phone"]
        if not obj.validate_phone(ph):
            session["login_attempts"] -= 1

            if session["login_attempts"] == 0:
                session.clear()
                return redirect("/")
            return render_template("login.html",
                message=f"Invalid phone  | {session['login_attempts']} attempts left")
        if obj.login(name, ph):
            session["user"] = name
            session["ph"] = ph
            session.pop("login_attempts", None)
            return redirect("/dashboard")

        return render_template("login.html", message="Invalid credentials")

    return render_template("login.html")  


@app.route("/books")
def view_books():
    if "user" not in session:
        return redirect("/login")

    cur.execute("SELECT book_name, quantity FROM book")
    data = cur.fetchall()

    return render_template("user_books.html", data=data)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html") 

@app.route("/borrow", methods=["GET", "POST"])
def borrow():
    if request.method == "POST":
        book = request.form["book"].title()
        qty = int(request.form["qty"])

        msg = obj.borrow(session["user"], session["ph"], book, qty)

        return render_template("borrow.html", message=msg)

    return render_template("borrow.html") 

@app.route("/return-book", methods=["GET", "POST"])
def return_book():

    if request.method == "POST":
        book = request.form["book"].title()
        qty = int(request.form["qty"])
        msg = obj.return_book(session["user"], session["ph"], book, qty)

        return render_template("return_book.html", message=msg)

    return render_template("return_book.html") 

@app.route("/user-history")
def user_history():

    if "user" not in session:
        return redirect("/login")

    cur.execute("""
        SELECT b.book_name, t.issued_date, t.return_date, t.books_to_return
        FROM transaction t
        JOIN book b ON t.book_id = b.book_id
        JOIN library_user u ON t.user_id = u.user_id
        WHERE u.user_name=%s AND u.ph_no=%s
    """, (session["user"], session["ph"]))

    data = cur.fetchall()

    return render_template("history.html", data=data)




if __name__ == "__main__":
    app.run(debug=True)


    
        

