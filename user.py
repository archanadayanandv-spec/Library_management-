
import re
from book import Book 
from db import cur, conn

pattern = r'^[9876]\d{9}$'
class User(Book):
    def __init__(self, cur, conn):
        super().__init__(cur, conn) 
        
    def validate_phone(self,ph):
        return re.match(pattern,ph) 
    
    def register(self,name,ph): 
        if not self.validate_phone(ph):
            return "Invalid phone number"
        
        self.cur.execute("""select * from library_user 
                         where user_name=%s and ph_no=%s""",(name,ph))
        
        if self.cur.fetchone():
            return "User Already Exits..."
        self.cur.execute(""" insert into library_user (user_name,ph_no)
                         values (%s,%s)""",(name,ph)) 
        self.conn.commit()
        return "Register successfully..."
    
    def login(self,name,ph):
        if not self.validate_phone(ph):
            return "Invalid phone number" 
        self.cur.execute (""" select * from library_user 
                          where user_name=%s and ph_no=%s""",(name,ph)) 
        return self.cur.fetchone()
    
    def borrow(self,name,ph,book_name,qty):
        self.cur.execute(""" select book_id,quantity from book
                         where book_name = %s""",(book_name,))
        book = self.cur.fetchone() 
        
        self.cur.execute(""" SELECT user_id, number_of_books
                        FROM library_user WHERE user_name=%s AND ph_no=%s
                        """, (name, ph))
        user = self.cur.fetchone() 
        
        if not book:
            return "Book not found..."
        
        book_id, book_qty = book
        user_id,user_books = user  

        if book_qty < qty:
            return "Not enough books available"

        if user_books + qty > 3:
            return "Max 3 books allowed"  
        
        self.cur.execute(""" UPDATE book SET quantity = quantity - %s
                        WHERE book_id = %s """, (qty,book_id)) 
        
        self.cur.execute(""" UPDATE library_user SET number_of_books = number_of_books + %s
            WHERE user_id = %s """, (qty, user_id))

        self.cur.execute(""" INSERT INTO transaction
            (issued_date, books_to_return, user_id, book_id)
            VALUES (CURRENT_DATE, %s, %s, %s) """, (qty, user_id, book_id))
        self.conn.commit()
        return "Book Borrowed Successfully " 
    
    def return_book(self, name, ph, book_name, qty):

        self.cur.execute("""
            SELECT book_id FROM book
            WHERE book_name=%s
        """, (book_name,))
        book = self.cur.fetchone()

        self.cur.execute("""
            SELECT user_id, number_of_books FROM library_user
            WHERE user_name=%s AND ph_no=%s
        """, (name, ph))
        user = self.cur.fetchone()

        if not book or not user:
            return "User or Book not found " 
            
        book_id = book[0]
        user_id, user_books = user

        if qty > user_books:
            return "Invalid return "

        self.cur.execute("""
            UPDATE book SET quantity = quantity + %s
            WHERE book_id = %s
        """, (qty, book_id))

        self.cur.execute("""
            UPDATE library_user
            SET number_of_books = number_of_books - %s
            WHERE user_id = %s
        """, (qty, user_id)) 
        
        self.cur.execute("""
            SELECT books_to_return FROM transaction
            WHERE user_id=%s AND book_id=%s AND return_date IS NULL
        """, (user_id, book_id))

        trans = self.cur.fetchone()

        if not trans:
            return "No active transaction "

        remaining = trans[0] - qty

        if remaining == 0:
            self.cur.execute("""
                UPDATE transaction
                SET return_date = CURRENT_DATE, books_to_return = 0
                WHERE user_id=%s AND book_id=%s AND return_date IS NULL
            """, (user_id, book_id))
        else:
            self.cur.execute("""
                UPDATE transaction
                SET books_to_return = %s
                WHERE user_id=%s AND book_id=%s AND return_date IS NULL
            """, (remaining, user_id, book_id))

        self.conn.commit()

        return "Book Returned" 
    
    def get_user_history(self, name, ph):
        self.cur.execute("""
            SELECT b.book_name, t.issued_date, t.return_date, t.books_to_return
            FROM transaction t
            JOIN book b ON t.book_id = b.book_id
            JOIN library_user u ON t.user_id = u.user_id
            WHERE u.user_name=%s AND u.ph_no=%s
        """, (name, ph))

        return self.cur.fetchall()



        

    
 
        

        

        
        

        
        
        