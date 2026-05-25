import psycopg2 

conn = psycopg2.connect(
    host = 'localhost',
    database = 'Library_Management',
    user = 'postgres',
    password = 'root' 
    
) 
cur = conn.cursor()   
conn.commit()
