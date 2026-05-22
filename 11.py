import pymysql
import time
from datetime import datetime, timedelta


# 学生管理核心类
class bookManager:
    # 初始化数据库连接
    def __init__(self):
        try:
            self.conn = pymysql.connect(
                host="localhost",
                user="root",
                password="123456",
                database="book_dbm",
                charset="utf8mb4",
                autocommit=False
            )
            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            # 保存当前登录用户信息
            self.current_user = None
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

    # 工具方法：输入非数字校验
    def input_num_check(self, prompt):
        while True:
            num_str = input(prompt)
            if num_str.isdigit():
                return int(num_str)
            print(" 输入无效，请输入数字！")

    # --------------------------
    # 登录/注册/分级权限
    # --------------------------
    # 登录验证功能（带角色信息）
    def login(self, username, password):
        sql = """
            SELECT u.*, r.role_name 
            FROM `user` u 
            JOIN `role` r ON u.role_id = r.id 
            WHERE u.username=%s AND u.password=%s
        """
        self.cursor.execute(sql, (username, password))
        user = self.cursor.fetchone()
        if user:
            print(f"✅ 登录成功！欢迎，{username}（角色：{user['role_name']}）")
            self.write_log(f"用户 {username} 登录系统，角色：{user['role_name']}")
            self.current_user = user
            return True
        else:
            print("❌ 用户名或密码错误！")
            return False

    # 注册学生账号
    def register(self, username, password):
        # 检查用户名是否重复
        check_sql = "SELECT * FROM `user` WHERE username=%s"
        self.cursor.execute(check_sql, (username,))
        if self.cursor.fetchone():
            print("❌ 用户名已存在！")
            return False

        # 获取学生角色ID
        role_sql = "SELECT id FROM `role` WHERE role_name='student'"
        self.cursor.execute(role_sql)
        student_role_id = self.cursor.fetchone()['id']

        try:
            insert_sql = "INSERT INTO `user` (username, password, role_id) VALUES(%s, %s, %s)"
            self.cursor.execute(insert_sql, (username, password, student_role_id))
            self.conn.commit()
            print("✅ 注册成功！请登录")
            self.write_log(f"新用户注册：{username}（学生角色）")
            return True
        except Exception as e:
            self.conn.rollback()
            print("❌ 注册失败：", e)
            return False

    # --------------------------
    # 图书管理功能（带编号唯一校验）
    # --------------------------
    # 1. 插入（管理员专属，带编号唯一校验）
    def add_book(self, book_id, name, auther, cla, sta):
        # 权限校验：仅管理员可添加图书
        if self.current_user['role_name'] != 'admin':
            print("❌ 权限不足，仅管理员可添加图书！")
            return

        # 校验图书编号唯一
        check_sql = "SELECT * FROM book WHERE book_id=%s"
        self.cursor.execute(check_sql, (book_id,))
        if self.cursor.fetchone():
            print("❌ 图书编号已存在，禁止重复添加！")
            return

        try:
            sql_book = "INSERT INTO book(book_id, name, auther, cla, sta) VALUES(%s,%s,%s,%s,%s)"
            self.cursor.execute(sql_book, (book_id, name, auther, cla, sta))
            self.conn.commit()
            print("✅ 添加成功")
            self.write_log(f"新增：书号{book_id} 书名{name}")

        except Exception as e:
            self.conn.rollback()
            print("❌ 添加失败！错误原因：", e)

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
            print(
                f"书号：{item['book_id']} | 书名：{item['name']} | 作者：{item['auther']} | 分类：{item['cla']} | 状态：{item['sta']}")

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

    # 4. 修改基础信息（管理员专属）
    def update_book_info(self, book_id, new_name, new_auther, new_cla):
        if self.current_user['role_name'] != 'admin':
            print("❌ 权限不足，仅管理员可修改图书信息！")
            return

        try:
            sql = "UPDATE book SET name=%s, auther=%s, cla=%s WHERE book_id=%s"
            self.cursor.execute(sql, (new_name, new_auther, new_cla, book_id))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("✅ 基础信息修改成功")
                self.write_log(f"修改基础信息：书号{book_id}")
            else:
                print("❌ 未找到该书")
        except Exception as e:
            self.conn.rollback()
            print("❌ 修改失败：", e)

    # 5. 删除图书信息（管理员专属）
    def delete_book(self, book_id):
        if self.current_user['role_name'] != 'admin':
            print("❌ 权限不足，仅管理员可删除图书！")
            return

        try:
            confirm = input("确定删除此图书？(y/n)：")
            if confirm != "y":
                print("已取消删除")
                return
            sql = "DELETE FROM book WHERE book_id=%s"
            self.cursor.execute(sql, (book_id,))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("图书信息已删除")
                self.write_log(f"删除数据：书号{book_id}")
            else:
                print("未找到该图书")
        except Exception as e:
            self.conn.rollback()
            print("删除失败：", e)

    # --------------------------
    # 借阅管理增强（记录借阅人/日期，最多借3本，可借7天）
    # --------------------------
    # 6. 图书借阅
    def borrow_book(self, book_id):
        if not self.current_user:
            print("请先登录！")
            return
        user_id = self.current_user['id']

        # 1. 检查用户已借阅数量（最多3本）
        borrow_count_sql = "SELECT COUNT(*) as cnt FROM borrower WHERE user_id=%s AND status='借阅中'"
        self.cursor.execute(borrow_count_sql, (user_id,))
        borrow_cnt = self.cursor.fetchone()['cnt']
        if borrow_cnt >= 3:
            print("你已借阅3本图书，无法再借阅！")
            return

        # 2. 检查图书状态
        sql = "SELECT sta FROM book WHERE book_id=%s"
        self.cursor.execute(sql, (book_id,))
        res = self.cursor.fetchone()
        if not res:
            print(" 未查询到该图书")
            return
        if res["sta"] != "可借阅":
            print("图书已借出，无法借阅")
            return

        # 3. 记录借阅信息（可借7天）
        borrow_date = datetime.now().date()
        return_date = borrow_date + timedelta(days=7)

        try:
            # 更新图书状态
            up_sql = "UPDATE book SET sta='已借出' WHERE book_id=%s"
            self.cursor.execute(up_sql, (book_id,))
            # 插入借阅记录
            insert_sql = """
                INSERT INTO borrower(book_id, user_id, borrow_date, return_date, status)
                VALUES(%s, %s, %s, %s, '借阅中')
            """
            self.cursor.execute(insert_sql, (book_id, user_id, borrow_date, return_date))
            self.conn.commit()
            print(f"借阅成功！应还日期：{return_date}")
            self.write_log(f"用户{self.current_user['username']} 书号{book_id}完成借阅，应还日期{return_date}")
        except Exception as e:
            self.conn.rollback()
            print("借阅失败：", e)

    # 7. 图书归还
    def back_book(self, book_id):
        if not self.current_user:
            print("请先登录！")
            return
        user_id = self.current_user['id']

        # 1. 检查图书状态
        sql = "SELECT sta FROM book WHERE book_id=%s"
        self.cursor.execute(sql, (book_id,))
        res = self.cursor.fetchone()
        if not res:
            print("未查询到该图书")
            return
        if res["sta"] != "已借出":
            print("图书未借出，无需归还")
            return

        # 2. 检查是否为当前用户借阅
        borrow_sql = """
            SELECT * FROM borrower 
            WHERE book_id=%s AND user_id=%s AND status='借阅中'
        """
        self.cursor.execute(borrow_sql, (book_id, user_id))
        borrow_record = self.cursor.fetchone()
        if not borrow_record:
            print("你没有借阅该图书！")
            return

        # 3. 更新状态
        try:
            # 更新图书状态
            up_book_sql = "UPDATE book SET sta='可借阅' WHERE book_id=%s"
            self.cursor.execute(up_book_sql, (book_id,))
            # 更新借阅记录
            up_borrow_sql = """
                UPDATE borrower 
                SET actual_return_date=%s, status='已归还' 
                WHERE id=%s
            """
            actual_return_date = datetime.now().date()
            self.cursor.execute(up_borrow_sql, (actual_return_date, borrow_record['id']))
            self.conn.commit()
            print("归还成功！")
            self.write_log(f"用户{self.current_user['username']} 书号{book_id}完成归还")
        except Exception as e:
            self.conn.rollback()
            print("归还失败：", e)

    # 查看我的借阅记录
    def show_my_borrow(self):
        if not self.current_user:
            print("请先登录！")
            return
        user_id = self.current_user['id']

        sql = """
            SELECT b.book_id, b.name, br.borrow_date, br.return_date, br.status
            FROM borrower br
            JOIN book b ON br.book_id = b.book_id
            WHERE br.user_id=%s
        """
        self.cursor.execute(sql, (user_id,))
        records = self.cursor.fetchall()
        if not records:
            print("你暂无借阅记录！")
            return
        print("\n========== 我的借阅记录 ==========")
        for r in records:
            print(
                f"书号：{r['book_id']} | 书名：{r['name']} | 借阅日期：{r['borrow_date']} | 应还日期：{r['return_date']} | 状态：{r['status']}")

    # 关闭数据库连接
    def close(self):
        self.cursor.close()
        self.conn.close()
        print("数据库连接已关闭")


def main():
    bm = bookManager()

    print("===== 图书信息管理系统 =====")
    print("1. 登录")
    print("2. 注册（学生账号）")
    choice = input("请选择操作：")
    if choice == "2":
        username = input("请输入用户名：")
        password = input("请输入密码：")
        bm.register(username, password)
        return
    elif choice != "1":
        print("输入无效，系统退出！")
        bm.close()
        return

    # 登录流程
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

    # 主菜单
    while True:
        print("\n======= 图书管理系统 =======")
        print("1. 添加图书（仅管理员）")
        print("2. 查看所有图书")
        print("3. 按书号查询图书")
        print("4. 修改图书信息（仅管理员）")
        print("5. 删除图书（仅管理员）")
        print("6. 借阅图书")
        print("7. 归还图书")
        print("8. 查看我的借阅记录")
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

        elif choice == "8":
            bm.show_my_borrow()

        elif choice == "0":
            print("系统退出！")
            bm.write_log("用户退出系统")
            bm.close()
            break

        else:
            print("输入无效，请输入 0-8 的数字！")


if __name__ == "__main__":
    main()