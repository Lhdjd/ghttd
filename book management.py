import pymysql
import time

# 学生管理核心类
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
            print("数据库连接成功")
        except Exception as e:
            print("数据库连接失败：", e)

    # 关闭连接
    def close(self):
        self.cursor.close()
        self.conn.close()
        print("数据库连接已关闭")

    # 日志记录工具
    def write_log(self, msg):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with open("book_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{now}] {msg}\n")

    # 登录验证功能
    def login(self, username, password):
        sql = "SELECT * FROM user WHERE username=%s AND password=%s"
        self.cursor.execute(sql, (username, password))
        user = self.cursor.fetchone()
        if user:
            print(f"登录成功！欢迎，{username}")
            self.write_log(f"用户 {username} 登录系统")
            return True
        else:
            print("用户名或密码错误！")
            return False

    # 1. 插入
    def add_book(self, book_id, name, auther, cla, sta):
        try:
            sql_book = "INSERT INTO book(book_id, name, auther, cla, sta) VALUES(%s,%s,%s,%s,%s)"
            self.cursor.execute(sql_book, (book_id, name, auther, cla, sta))
            self.conn.commit()
            print("添加成功")
            self.write_log(f"新增：书号{book_id} 书名{name}")

        except Exception as e:
            self.conn.rollback()
            print("添加失败！错误原因：", e)

    # 2. 查看所有图书信息
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

    # 3. 按书号查询图书
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


    # 4. 修改基础信息
    def update_book_info(self, book_id, new_name, new_auther, new_cla):
        try:
            sql = "UPDATE book SET name=%s, auther=%s, cla=%s WHERE book_id=%s"
            self.cursor.execute(sql, (new_name, new_auther, new_cla, book_id))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("基础信息修改成功")
                self.write_log(f"修改基础信息：书号{book_id}")
            else:
                print("未找到该书")
        except Exception as e:
            self.conn.rollback()
            print("修改失败")


    # 5. 删除图书信息
    def delete_book(self, book_id):
        try:
            # 只需删除学生表数据，成绩表会自动级联删除
            sql = "DELETE FROM book WHERE book_id=%s"
            self.cursor.execute(sql, book_id)
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("信息及对应成绩已全部删除")
                self.write_log(f"删除数据：学号{book_id}")
            else:
                print("未找到该学生")
        except:
            self.conn.rollback()
            print("删除失败")

    # 6. 图书借阅
    def borrow_book(self, book_id):
        try:
            sql = "SELECT sta FROM book WHERE book_id=%s"
            self.cursor.execute(sql, (book_id,))
            res = self.cursor.fetchone()
            if not res:
                print("未查询到该图书")
                return
            if res["sta"] == "可借阅":
                up_sql = "UPDATE book SET sta='已借出' WHERE book_id=%s"
                self.cursor.execute(up_sql, (book_id,))
                self.conn.commit()
                print("借阅成功")
                self.write_log(f"书号{book_id}完成借阅")
            else:
                print("图书已借出，无法借阅")
        except:
            self.conn.rollback()
            print("借阅失败")

    # 7. 图书归还
    def back_book(self, book_id):
        try:
            sql = "SELECT sta FROM book WHERE book_id=%s"
            self.cursor.execute(sql, (book_id,))
            res = self.cursor.fetchone()
            if not res:
                print("未查询到该图书")
                return
            if res["sta"] == "已借出":
                up_sql = "UPDATE book SET sta='可借阅' WHERE book_id=%s"
                self.cursor.execute(up_sql, (book_id,))
                self.conn.commit()
                print("归还成功")
                self.write_log(f"书号{book_id}完成归还")
            else:
                print("图书未借出，无需归还")
        except:
            self.conn.rollback()
            print("归还失败")



    # 关闭数据库连接
    def close(self):
        self.cursor.close()
        self.conn.close()
        print("数据库连接已关闭")


def main():
    bm = bookManager()

    print("===== 图书信息管理系统 登录 =====")
    login_success = False
    for _ in range(3):
        username = input("请输入用户名：")
        password = input("请输入密码：")
        if bm.login(username, password):
            login_success = True
            break
    if not login_success:
        print("登录失败次数过多，系统退出！")
        bm.close()
        return

    while True:
        print("\n======= 图书管理系统 =======")
        print("1. 添加图书")
        print("2. 查看所有图书")
        print("3. 按书号查询图书")
        print("4. 修改图书信息")
        print("5. 删除学生（含成绩）")
        print("0. 退出系统")

        choice = input("请输入功能编号：")

        if choice == "1":
            bid = input("请输入图书书号：")
            name = input("请输入图书书名：")
            aut = input("请输入作者：")
            c = input("请输入分类：")
            stu = input("请输入状态：")
            bm.add_book(bid, name, aut, c, stu)

        elif choice == "2":
            bm.show_all_book()

        elif choice == "3":
            sid = input("请输入图书书号：")
            bm.search_book_by_id(sid)

        elif choice == "4":
            book_id = input("请输入要修改的书号：")
            new_name = input("请输入新书名：")
            new_auther = input("请输入新作者：")
            new_cla = input("请输入新分类：")
            bm.update_book_info(book_id, new_name, new_auther, new_cla)

        elif choice == "5":
            book_id = input("请输入要删除的书号：")
            bm.delete_book(book_id)

        elif choice == "6":
            book_id = input("请输入借阅书号：")
            bm.borrow_book(book_id)

        elif choice == "7":
            book_id = input("请输入归还书号：")
            bm.back_book(book_id)

        elif choice == "0":
            print("系统退出！")
            bm.write_log("用户退出系统")
            bm.close()
            break

        else:
            print("输入无效，请输入 0-7 的数字！")

if __name__ == "__main__":
    main()