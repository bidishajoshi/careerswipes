import pymysql

try:
    # Connect to MySQL server without selecting a database
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password=''
    )
    
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS careerswipe;")
        print("Database 'careerswipe' verified/created successfully.")
        
    connection.commit()
    connection.close()
except Exception as e:
    print(f"Error creating database: {e}")
