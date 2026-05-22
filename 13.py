import pymysql
import time
from datetime import datetime, timedelta

# 图书管理核心类
class bookManager:
    # 初始化数据库连接
    def __init__(self):
        try:
            self.conn = pymysql.connect(
                host="localhost",
                user="root",
                password="123456",
                database="book_db2",
                charset="utf8mb4",
                autocommit=False
            )
            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            self.current_user = None
            print("数据库连接成功")
        except Exception as e:
            print("数据库连接失败：", e)

    # 日志记录工具
    def write_log(self, msg):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with open("book_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{now}] {msg}\n")

    # 数字输入校验
    def input_num_check(self, prompt):
        while True:
            num_str = input(prompt)
            if num_str.isdigit():
                return int(num_str)
            print("❌ 输入无效，请输入数字！")

    # ===================== 登录（已修复，无 role）=====================
    def login(self, username, password):
        sql = "SELECT * FROM user WHERE username=%s AND password=%s"
        self.cursor.execute(sql, (username, password))
        user = self.cursor.fetchone()
        if user:
            print(f"✅ 登录成功！欢迎，{username}")
            self.write_log(f"用户 {username} 登录系统")
            self.current_user = user
            return True
        else:
            print("❌ 用户名或密码错误！")
            return False

    # ===================== 1. 添加图书 =====================
    def add_book(self, book_id, name, auther, cla, sta):
        check_sql = "SELECT * FROM book WHERE book_id=%s"
        self.cursor.execute(check_sql, (book_id,))
        if self.cursor.fetchone():
            print("❌ 书号已存在，禁止重复添加！")
            return
        try:
            sql_book = "INSERT INTO book(book_id, name, auther, cla, sta) VALUES(%s,%s,%s,%s,%s)"
            self.cursor.execute(sql_book, (book_id, name, auther, cla, sta))
            self.conn.commit()
            print("✅ 添加成功")
            self.write_log(f"新增：书号{book_id} 书名{name}")
        except Exception as e:
            self.conn.rollback()
            print("❌ 添加失败！", e)

    # ===================== 2. 查看所有图书 =====================
    def show_all_book(self):
        sql = "SELECT * FROM book"
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        if not res:
            print("暂无图书数据！")
            return
        print("\n========== 所有图书信息 ==========")
        for item in res:
            print(f"书号：{item['book_id']} | 书名：{item['name']} | 作者：{item['auther']} | 分类：{item['cla']} | 状态：{item['sta']}")

    # ===================== 3. 按书号查询 =====================
    def search_book_by_id(self, book_id):
        sql = "SELECT * FROM book WHERE book_id = %s"
        self.cursor.execute(sql, (book_id,))
        res = self.cursor.fetchone()
        if res:
            print("\n========== 图书信息详情 ==========")
            print(f"书号：{res['book_id']}")
            print(f"书名：{res['name']}")
            print(f"作者：{res['auther']}")
            print(f"分类：{res['cla']}")
            print(f"状态：{res['sta']}")
        else:
            print("未查询到该图书信息！")

    # ===================== 4. 修改图书 =====================
    def update_book_info(self, book_id, new_name, new_auther, new_cla):
        try:
            sql = "UPDATE book SET name=%s, auther=%s, cla=%s WHERE book_id=%s"
            self.cursor.execute(sql, (new_name, new_auther, new_cla, book_id))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                print("✅ 修改成功")
                self.write_log(f"修改：书号{book_id}")
            else:
                print("❌ 未找到该书")
        except:
            self.conn.rollback()
            print("❌ 修改失败")

    # ===================== 5. 删除图书 =====================
    def delete_book(self, book_id):
        try:
            confirm = input("确定删除？(y/n)：")
            if confirm != "y":
                print("已取消")
                return
            sql = "DELETE FROM book WHERE book_id=%s"
            self.cursor.execute(sql, (book_id,))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                print("✅ 删除成功")
                self.write_log(f"删除：书号{book_id}")
            else:
                print("❌ 未找到")
        except:
            self.conn.rollback()
            print("❌ 删除失败")

    # ===================== 6. 借阅图书（已修复！可借阅 → 已借出）=====================
    def borrow_book(self, book_id):
        if not self.current_user:
            print("❌ 请先登录！")
            return
        user_id = self.current_user['id']

        # 最多借3本
        sql_cnt = "SELECT COUNT(*) AS cnt FROM borrower WHERE user_id=%s AND status='借阅中'"
        self.cursor.execute(sql_cnt, (user_id,))
        cnt = self.cursor.fetchone()['cnt']
        if cnt >= 3:
            print("❌ 最多借阅3本！")
            return

        try:
            sql = "SELECT sta FROM book WHERE book_id=%s"
            self.cursor.execute(sql, (book_id,))
            res = self.cursor.fetchone()
            if not res:
                print("❌ 图书不存在")
                return

            if res["sta"] == "可借阅":
                # 更新状态
                self.cursor.execute("UPDATE book SET sta='已借出' WHERE book_id=%s", (book_id,))
                # 记录借阅
                borrow_date = datetime.now().date()
                return_date = borrow_date + timedelta(days=7)
                sql_add = """INSERT INTO borrower(book_id, user_id, borrow_date, return_date, status)
                             VALUES(%s,%s,%s,%s,'借阅中')"""
                self.cursor.execute(sql_add, (book_id, user_id, borrow_date, return_date))
                self.conn.commit()
                print(f"✅ 借阅成功！应还日期：{return_date}")
                self.write_log(f"用户{self.current_user['username']} 借阅书号{book_id}")
            else:
                print("❌ 图书已借出，无法借阅")
        except:
            self.conn.rollback()
            print("❌ 借阅失败")

    # ===================== 7. 归还图书（已修复）=====================
    def back_book(self, book_id):
        if not self.current_user:
            print("❌ 请先登录！")
            return
        try:
            self.cursor.execute("SELECT sta FROM book WHERE book_id=%s", (book_id,))
            res = self.cursor.fetchone()
            if not res:
                print("❌ 图书不存在")
                return

            if res["sta"] == "已借出":
                self.cursor.execute("UPDATE book SET sta='可借阅' WHERE book_id=%s", (book_id,))
                self.cursor.execute("""UPDATE borrower SET status='已归还' 
                                      WHERE book_id=%s AND user_id=%s AND status='借阅中'""",
                                    (book_id, self.current_user['id']))
                self.conn.commit()
                print("✅ 归还成功")
                self.write_log(f"用户归还书号{book_id}")
            else:
                print("❌ 图书未借出")
        except:
            self.conn.rollback()
            print("❌ 归还失败")

    # ===================== 8. 我的借阅记录 =====================
    def show_my_borrow(self):
        if not self.current_user:
            print("❌ 请先登录！")
            return
        sql = """
        SELECT b.book_id, b.name, br.borrow_date, br.return_date, br.status
        FROM borrower br JOIN book b ON br.book_id = b.book_id
        WHERE br.user_id=%s
        """
        self.cursor.execute(sql, (self.current_user['id'],))
        records = self.cursor.fetchall()
        if not records:
            print("暂无借阅记录")
            return
        print("\n========== 我的借阅 ==========")
        for r in records:
            print(f"书号:{r['book_id']} 书名:{r['name']} 借:{r['borrow_date']} 应还:{r['return_date']} 状态:{r['status']}")

    # 关闭
    def close(self):
        self.cursor.close()
        self.conn.close()
        print("数据库已关闭")

# ===================== 主函数 =====================
def main():
    bm = bookManager()
    print("===== 图书管理系统 =====")
    login_success = False
    for _ in range(3):
        username = input("用户名：")
        pwd = input("密码：")
        if bm.login(username, pwd):
            login_success = True
            break
    if not login_success:
        print("登录失败，退出")
        bm.close()
        return

    while True:
        print("\n======= 菜单 =======")
        print("1.添加图书  2.查看全部  3.按书号查询")
        print("4.修改图书  5.删除图书  6.借阅图书")
        print("7.归还图书  8.我的借阅  0.退出")
        choice = input("请输入：")

        if choice == "1":
            bid = input("书号：")
            name = input("书名：")
            aut = input("作者：")
            cla = input("分类：")
            sta = "可借阅"
            bm.add_book(bid, name, aut, cla, sta)

        elif choice == "2":
            bm.show_all_book()
        elif choice == "3":
            bm.search_book_by_id(input("书号："))
        elif choice == "4":
            bm.update_book_info(input("书号："), input("新书名："), input("新作者："), input("新分类："))
        elif choice == "5":
            bm.delete_book(input("书号："))
        elif choice == "6":
            bm.borrow_book(input("借阅书号："))
        elif choice == "7":
            bm.back_book(input("归还书号："))
        elif choice == "8":
            bm.show_my_borrow()
        elif choice == "0":
            print("退出系统")
            bm.write_log(f"用户退出")
            bm.close()
            break
        else:
            print("输入无效")

if __name__ == "__main__":
    main()