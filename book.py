from db import cur, conn   
class Book:

    def __init__(self, cur, conn):
        self.cur = cur
        self.conn = conn  
        
    def librarian_login_web(self, name, password):
        self.cur.execute("""
            SELECT * FROM librarian
            WHERE l_name=%s AND l_psw=%s
        """, (name, password))

        return self.cur.fetchone() is not None
    def get_books(self):
        self.cur.execute("select * from book") 
        return self.cur.fetchall() 
    
    def add_quantity(self,book_id,qty):
        self .cur.execute (""" update book set quantity = quantity +%s
                                where book_id = %s""",(qty,book_id))
        self.conn.commit() 
    def delete_book(self,book_id):
        self.cur.execute ("delete from book where book_id = %s",(book_id,)) 
        self.conn.commit()
    def add_new_book(self,book_id,book_name,author,qty):
        self.cur.execute("select book_name from book where book_name=%s",(book_name,)) 
        if self.cur.fetchone():
            return "Book already Exits..."
        self .cur.execute("""Insert into book (book_id,book_name,author,quantity)
                          values (%s,%s,%s,%s)""",(book_id,book_name,author,qty)) 
        self.conn.commit()
        return "Book added successfully..."
    def get_transactions(self):
        self.cur.execute("""select u.user_name,b.book_name,t.issued_date,t.return_date,t.books_to_return
                            from transaction t 
                            join library_user u on t.user_id = u.user_id
                            join book b on t.book_id = b.book_id """)  
        return self.cur.fetchall()
    
    