import pymysql
class DBHelper:
    def __init__(self, host, user, pwd, db):
        self.conn = pymysql.connect(host=host,user=user,password=pwd,database=db,charset='utf8')
        self.cursor = self.conn.cursor()
    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.cursor.fetchall()
    def execute(self, sql, params=None):
        try:
            self.cursor.execute(sql, params or ())
            self.conn.commit()
        except pymysql.Error as e:
            self.conn.rollback();
            raise e

    def close(self):
        self.cursor.close()
        self.conn.close()
# 1. 创建工具对象
db = DBHelper("localhost", "root", "123456", "test_db")

# 2. 查询
data = db.query("SELECT * FROM user")
print(data)

# 3. 增删改
db.execute("INSERT INTO user(username) VALUES('测试')")

# 4. 关闭
db.close()