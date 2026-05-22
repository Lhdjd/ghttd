import pymysql
import time
import csv
from datetime import datetime, timedelta
from dbutils.pooled_db import PooledDB

# ==============================================
# 工具类：数据库连接池
# ==============================================
class DBPool:
    __pool = None

    def __init__(self):
        if DBPool.__pool is None:
            DBPool.__pool = PooledDB(
                creator=pymysql,
                maxconnections=5,
                mincached=1,
                maxcached=2,
                host="localhost",
                user="root",
                password="123456",
                database="book_db3",
                charset="utf8mb4"
            )

    def get_conn(self):
        return self.__pool.connection()

# ==============================================
# 工具类：日志工具
# ==============================================
class LogUtil:
    @staticmethod
    def write(msg):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with open("book_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{now}] {msg}\n")

# ==============================================
# 工具类：输入校验工具
# ==============================================
class InputUtil:
    @staticmethod
    def number(tip):
        while True:
            val = input(tip).strip()
            if val.isdigit():
                return val
            print("❌ 必须输入数字，请重试")

    @staticmethod
    def confirm(tip):
        res = input(f"{tip}（y/n）：").strip().lower()
        return res == 'y'

# ==============================================
# 核心业务类：图书管理器
# ==============================================
class BookManager:
    def __init__(self):
        self.db_pool = DBPool()
        self.current_user = None
        self.current_role = None
        print("✅ 数据库连接池初始化成功")

    # 获取连接
    def get_conn(self):
        return self.db_pool.get_conn()

    # ==================== 登录 ====================
    def login(self, username, password):
        conn = self.get_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT * FROM user WHERE username=%s AND password=%s"
        cursor.execute(sql, (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            self.current_user = username
            self.current_role = user['role']
            LogUtil.write(f"用户 {username} 登录")
            return True
        return False

    # ==================== 管理员：修改密码 ====================
    def update_password(self):
        old = input("原密码：")
        new = input("新密码：")
        confirm = input("确认密码：")
        if new != confirm:
            print("❌ 两次密码不一致")
            return

        conn = self.get_conn()
        cursor = conn.cursor()
        sql = "UPDATE user SET password=%s WHERE username=%s AND password=%s"
        cursor.execute(sql, (new, self.current_user, old))
        if cursor.rowcount > 0:
            conn.commit()
            print("✅ 密码修改成功")
            LogUtil.write(f"{self.current_user} 修改密码")
        else:
            print("❌ 原密码错误")
        cursor.close()
        conn.close()

    # ==================== 超级管理员：新增管理员 ====================
    def add_admin(self):
        if self.current_role != 'super_admin':
            print("❌ 无权限")
            return
        username = input("用户名：")
        password = input("密码：")
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            sql = "INSERT INTO user(username,password,role) VALUES(%s,%s,'admin')"
            cursor.execute(sql, (username, password))
            conn.commit()
            print("✅ 管理员添加成功")
        except:
            print("❌ 用户名已存在")
        cursor.close()
        conn.close()

    # ==================== 图书：添加（唯一校验） ====================
    def add_book(self, book_id=None, name=None, auther=None, cla=None):
        if not book_id:
            book_id = InputUtil.number("图书编号：")
            name = input("书名：")
            auther = input("作者：")
            cla = input("分类：")

        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM book WHERE book_id=%s", (book_id,))
        if cursor.fetchone():
            print("❌ 图书编号已存在")
            cursor.close()
            conn.close()
            return False

        sql = "INSERT INTO book(book_id,name,auther,cla,sta) VALUES(%s,%s,%s,%s,'可借阅')"
        cursor.execute(sql, (book_id, name, auther, cla))
        conn.commit()
        LogUtil.write(f"新增图书 {book_id}")
        cursor.close()
        conn.close()
        return True

    # ==================== 批量导入图书 ====================
    def batch_import(self):
        path = input("请输入文件路径（books.csv 或 books.txt）：")
        success = 0
        fail = 0

        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) < 4:
                        fail +=1
                        continue
                    if self.add_book(row[0], row[1], row[2], row[3]):
                        success +=1
                    else:
                        fail +=1
            print(f"✅ 导入完成：成功{success}本，失败{fail}本")
        except Exception as e:
            print("❌ 文件读取失败", e)

    # ==================== 高级查询：模糊+分类+分页 ====================
    def search_advance(self):
        print("\n┌───── 高级查询 ─────┐")
        print("│ 1 书名模糊查询     │")
        print("│ 2 按分类筛选       │")
        print("│ 3 分页查询         │")
        print("└───────────────────┘")
        c = input("选择：")

        conn = self.get_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if c == '1':
            kw = input("关键词：")
            cursor.execute("SELECT * FROM book WHERE name LIKE %s", (f"%{kw}%",))
        elif c == '2':
            cate = input("分类：")
            cursor.execute("SELECT * FROM book WHERE cla=%s", (cate,))
        elif c == '3':
            page = int(InputUtil.number("页码："))
            page = page if page >0 else 1
            cursor.execute("SELECT * FROM book LIMIT 5 OFFSET %s", ((page-1)*5,))
        else:
            print("输入错误")
            return

        for r in cursor.fetchall():
            print(f"│ {r['book_id']} │ {r['name']} │ {r['cla']} │ {r['sta']} │")
        cursor.close()
        conn.close()

    # ==================== 借阅：限制3本 + 逾期判断 ====================
    def borrow_book(self):
        reader_id = InputUtil.number("读者ID：")
        book_id = InputUtil.number("图书ID：")

        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) cnt FROM borrow_record WHERE reader_id=%s AND status='借阅中'", (reader_id,))
        if cursor.fetchone()['cnt'] >=3:
            print("❌ 最多借阅3本")
            return

        cursor.execute("SELECT sta FROM book WHERE book_id=%s", (book_id,))
        book = cursor.fetchone()
        if not book or book['sta'] != '可借阅':
            print("❌ 不可借阅")
            return

        # 事务：修改状态 + 新增记录
        try:
            cursor.execute("UPDATE book SET sta='已借出' WHERE book_id=%s", (book_id,))
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO borrow_record(book_id,reader_id,borrow_date,status) VALUES(%s,%s,%s,'借阅中')",
                           (book_id, reader_id, now))
            conn.commit()
            print("✅ 借阅成功")
        except:
            conn.rollback()
            print("❌ 借阅失败")
        cursor.close()
        conn.close()

    # ==================== 归还：逾期提醒 ====================
    def return_book(self):
        book_id = InputUtil.number("图书ID：")
        conn = self.get_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM borrow_record WHERE book_id=%s AND status='借阅中'", (book_id,))
        rec = cursor.fetchone()
        if not rec:
            print("❌ 未借阅")
            return

        days = (datetime.now() - datetime.strptime(rec['borrow_date'], "%Y-%m-%d %H:%M:%S")).days
        if days >30:
            print("⚠️ 已逾期！")

        # 事务
        try:
            cursor.execute("UPDATE book SET sta='可借阅' WHERE book_id=%s", (book_id,))
            cursor.execute("UPDATE borrow_record SET status='已归还',return_date=NOW() WHERE id=%s", (rec['id'],))
            conn.commit()
            print("✅ 归还成功")
        except:
            conn.rollback()
        cursor.close()
        conn.close()

    # ==================== 数据统计 ====================
    def statistics(self):
        conn = self.get_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        print("\n┌──────── 数据统计 ────────┐")
        cursor.execute("SELECT COUNT(*) total FROM book")
        total = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) can FROM book WHERE sta='可借阅'")
        can = cursor.fetchone()['can']
        cursor.execute("SELECT COUNT(*) out FROM book WHERE sta='已借出'")
        out = cursor.fetchone()['out']

        print(f"│ 图书总数：{total}")
        print(f"│ 可借阅：{can}")
        print(f"│ 已借出：{out}")

        print("\n├─ 热门借阅 TOP3 ─┤")
        cursor.execute("""
            SELECT book_id,COUNT(*) cnt FROM borrow_record
            GROUP BY book_id ORDER BY cnt DESC LIMIT 3
        """)
        for r in cursor.fetchall():
            print(f"│ 图书{r['book_id']} 借阅{r['cnt']}次")
        print("└────────────────────┘")
        cursor.close()
        conn.close()

# ==============================================
# 主程序：ASCII 美化菜单
# ==============================================
def main():
    bm = BookManager()
    print("┌──────────────────────────┐")
    print("│    图书管理系统 v3.0      │")
    print("└──────────────────────────┘")

    for _ in range(3):
        u = input("用户名：")
        p = input("密码：")
        if bm.login(u,p):
            break
    else:
        print("❌ 登录失败")
        return

    while True:
        print("\n┌────────── 主菜单 ──────────┐")
        print("│ 1 新增图书   2 查看全部     │")
        print("│ 3 高级查询   4 修改图书     │")
        print("│ 5 删除图书   6 借阅图书     │")
        print("│ 7 归还图书   8 批量导入     │")
        print("│ 9 统计报表   0 退出系统     │")
        print("│ A 修改密码   B 管理管理员   │")
        print("└────────────────────────────┘")

        choice = input("请选择：").strip()
        if choice == "1": bm.add_book()
        elif choice == "3": bm.search_advance()
        elif choice == "6": bm.borrow_book()
        elif choice == "7": bm.return_book()
        elif choice == "8": bm.batch_import()
        elif choice == "9": bm.statistics()
        elif choice == "A": bm.update_password()
        elif choice == "B": bm.add_admin()
        elif choice == "0":
            print("👋 退出系统")
            break

if __name__ == "__main__":
    main()