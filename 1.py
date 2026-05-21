import pymysql
try:
    conn=pymysql.connect(host='localhost',user='root',passwd='123456',db='W')
    print("连接成功")
except pymysql.Error as e:
    print(f"Error:{e}")
