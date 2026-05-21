import pymysql

# ------------------- 1. 通用数据库操作基类 DBHelper -------------------
class DBHelper:
    def __init__(self, host, user, pwd, db):
        self.conn = pymysql.connect(
            host=host,
            user=user,
            password=pwd,
            database=db,
            charset='utf8'
        )
        self.cursor = self.conn.cursor()

    def query(self, sql, params=None):
        """查询操作（SELECT）"""
        self.cursor.execute(sql, params or ())
        return self.cursor.fetchall()

    def execute(self, sql, params=None):
        """增删改操作（INSERT/UPDATE/DELETE），带事务"""
        try:
            self.cursor.execute(sql, params or ())
            self.conn.commit()
        except pymysql.Error as e:
            self.conn.rollback()  # 出错回滚
            raise e

    def close(self):
        """关闭连接"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()

# ------------------- 2. 用户专用管理类 UserManager -------------------
class UserManager:
    # 构造方法：接收 DBHelper 实例作为依赖（题目要求）
    def __init__(self, db_helper):
        self.db = db_helper

    # ① 添加用户（对应题目 add_user()）
    def add_user(self, username, password, email):
        sql = "INSERT INTO user(username, password, email) VALUES(%s, %s, %s)"
        self.db.execute(sql, (username, password, email))
        print(f"✅ 用户 [{username}] 添加成功")

    # ② 根据ID查询用户（对应题目 get_user_by_id()）
    def get_user_by_id(self, user_id):
        sql = "SELECT * FROM user WHERE id = %s"
        result = self.db.query(sql, (user_id,))
        return result[0] if result else None  # 有结果返回第一条，无结果返回None

    # ③ 更新用户邮箱（对应题目 update_user_email()）
    def update_user_email(self, user_id, new_email):
        sql = "UPDATE user SET email = %s WHERE id = %s"
        self.db.execute(sql, (new_email, user_id))
        print(f"✅ 用户ID [{user_id}] 的邮箱更新为：{new_email}")

    # ④ 删除用户（对应题目 delete_user()）
    def delete_user(self, user_id):
        sql = "DELETE FROM user WHERE id = %s"
        self.db.execute(sql, (user_id,))
        print(f"✅ 用户ID [{user_id}] 删除成功")

# ------------------- 3. 初始化：建库 + 建表（保证无报错） -------------------
def init_database():
    # 先连接MySQL创建数据库
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="123456",  # 改成你的数据库密码
        charset='utf8'
    )
    cursor = conn.cursor()

    # 创建数据库（不存在才创建）
    cursor.execute("CREATE DATABASE IF NOT EXISTS test_db")
    cursor.execute("USE test_db")

    # 创建user表（包含题目需要的email字段）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(50) NOT NULL,
            email VARCHAR(50)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ 数据库 & user表初始化完成")

# ------------------- 4. 测试代码 -------------------
if __name__ == "__main__":
    # 1. 初始化数据库和表
    init_database()

    # 2. 创建DBHelper实例
    db = DBHelper("localhost", "root", "123456", "test_db")

    # 3. 创建UserManager实例（依赖注入DBHelper）
    user_manager = UserManager(db)

    # 4. 测试所有方法
    user_manager.add_user("张三", "123456", "zhangsan@example.com")  # 添加用户
    user = user_manager.get_user_by_id(1)  # 查询用户
    print("📌 查询到的用户信息：", user)

    user_manager.update_user_email(1, "zhangsan_new@example.com")  # 更新邮箱
    user_manager.delete_user(1)  # 删除用户

    # 5. 关闭连接
    db.close()