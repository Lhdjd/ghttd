import pymysql
import time

# 学生管理核心类
class StudentManager:
    # 初始化数据库连接
    def __init__(self):
        try:
            self.conn = pymysql.connect(
                host="localhost",
                user="root",          # 改为自己的MySQL账号
                password="123456",    # 改为自己的MySQL密码
                database="student_db",
                charset="utf8mb4",
                autocommit=False
            )
            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            print("数据库连接成功（双表模式）")
        except Exception as e:
            print("数据库连接失败：", e)

    # 日志记录工具
    def write_log(self, msg):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with open("student_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{now}] {msg}\n")

    # ---------------------- 新增：登录验证功能 ----------------------
    def login(self, username, password):
        """从数据库验证账号密码"""
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

    # 1. 添加学生信息 + 录入成绩（双表同时插入）
    def add_student(self, stu_id, name, age, major, chinese, math, english):
        try:
            # 先插入学生基础信息
            sql_stu = "INSERT INTO student(stu_id, name, age, major) VALUES(%s,%s,%s,%s)"
            self.cursor.execute(sql_stu, (stu_id, name, age, major))

            # 再插入对应成绩数据
            sql_score = "INSERT INTO student_score(stu_id, chinese, math, english) VALUES(%s,%s,%s,%s)"
            self.cursor.execute(sql_score, (stu_id, chinese, math, english))

            self.conn.commit()
            print("学生信息及成绩添加成功")
            self.write_log(f"新增学生：学号{stu_id} 姓名{name} 并录入成绩")
        except Exception as e:
            self.conn.rollback()
            print("添加失败！学号重复或数据格式错误")

    # 2. 查看所有学生（联查双表，展示完整信息+成绩）
    def show_all_student(self):
        # 双表联查，通过学号关联
        sql = """
        SELECT s.stu_id, s.name, s.age, s.major, sc.chinese, sc.math, sc.english
        FROM student s
        LEFT JOIN student_score sc ON s.stu_id = sc.stu_id
        """
        self.cursor.execute(sql)
        res = self.cursor.fetchall()

        if not res:
            print("暂无学生数据！")
            return

        print("\n========== 学生完整信息及成绩列表 ==========")
        for item in res:
            total = item["chinese"] + item["math"] + item["english"]
            avg = total / 3
            print(f"学号：{item['stu_id']} | 姓名：{item['name']} | 年龄：{item['age']} | 专业：{item['major']}")
            print(f"语文：{item['chinese']} | 数学：{item['math']} | 英语：{item['english']} | 总分：{total} | 平均分：{avg:.1f}")
            print("-" * 90)

    # 3. 按学号精准查询学生成绩及信息
    def search_score_by_id(self, stu_id):
        sql = """
        SELECT s.stu_id, s.name, s.age, s.major, sc.chinese, sc.math, sc.english
        FROM student s
        LEFT JOIN student_score sc ON s.stu_id = sc.stu_id
        WHERE s.stu_id = %s
        """
        self.cursor.execute(sql, stu_id)
        res = self.cursor.fetchone()

        if res:
            print("\n========== 学生成绩详情 ==========")
            print(f"学号：{res['stu_id']}")
            print(f"姓名：{res['name']}")
            print(f"年龄：{res['age']}")
            print(f"专业：{res['major']}")
            print(f"语文成绩：{res['chinese']}")
            print(f"数学成绩：{res['math']}")
            print(f"英语成绩：{res['english']}")
            total = res["chinese"] + res["math"] + res["english"]
            avg = total / 3
            print(f"总成绩：{total} 分 | 平均成绩：{avg:.1f} 分")
        else:
            print("未查询到该学生信息！")

    # 4. 修改学生基础信息（仅修改学生表）
    def update_student_info(self, stu_id, new_age, new_major):
        try:
            sql = "UPDATE student SET age=%s, major=%s WHERE stu_id=%s"
            self.cursor.execute(sql, (new_age, new_major, stu_id))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("学生基础信息修改成功")
                self.write_log(f"修改学生基础信息：学号{stu_id}")
            else:
                print("未找到该学生")
        except:
            self.conn.rollback()
            print("修改失败")

    # 5. 单独修改学生成绩（仅修改成绩表）
    def update_student_score(self, stu_id, c, m, e):
        try:
            sql = "UPDATE student_score SET chinese=%s, math=%s, english=%s WHERE stu_id=%s"
            self.cursor.execute(sql, (c, m, e, stu_id))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("学生成绩修改成功")
                self.write_log(f"修改学生成绩：学号{stu_id}")
            else:
                print("未找到该学生成绩数据")
        except:
            self.conn.rollback()
            print("成绩修改失败")

    # 6. 删除学生信息（外键级联删除，成绩自动删除）
    def delete_student(self, stu_id):
        try:
            # 只需删除学生表数据，成绩表会自动级联删除
            sql = "DELETE FROM student WHERE stu_id=%s"
            self.cursor.execute(sql, stu_id)
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("学生信息及对应成绩已全部删除")
                self.write_log(f"删除学生数据：学号{stu_id}")
            else:
                print("未找到该学生")
        except:
            self.conn.rollback()
            print("删除失败")

    # 关闭数据库连接
    def close(self):
        self.cursor.close()
        self.conn.close()
        print("数据库连接已关闭")

# 主菜单函数
def main():
    sm = StudentManager()

    # ---------------------- 新增：登录流程 ----------------------
    print("===== 学生信息管理系统 登录 =====")
    login_success = False
    # 最多允许尝试3次登录
    for _ in range(3):
        username = input("请输入用户名：")
        password = input("请输入密码：")
        if sm.login(username, password):
            login_success = True
            break
    if not login_success:
        print("登录失败次数过多，系统退出！")
        sm.close()
        return

    # 登录成功后才进入主菜单
    while True:
        print("\n======= 学生信息成绩管理系统【双表版】=======")
        print("1. 添加学生（含成绩录入）")
        print("2. 查看所有学生完整信息")
        print("3. 按学号查询学生成绩")
        print("4. 修改学生基础信息")
        print("5. 修改学生成绩信息")
        print("6. 删除学生（含成绩）")
        print("0. 退出系统")
        print("==========================================")

        choice = input("请输入功能编号：")

        if choice == "1":
            sid = input("请输入学生学号：")
            name = input("请输入学生姓名：")
            age = input("请输入学生年龄：")
            major = input("请输入所学专业：")
            c = input("请输入语文成绩：")
            m = input("请输入数学成绩：")
            e = input("请输入英语成绩：")
            sm.add_student(sid, name, age, major, c, m, e)

        elif choice == "2":
            sm.show_all_student()

        elif choice == "3":
            sid = input("请输入查询学号：")
            sm.search_score_by_id(sid)

        elif choice == "4":
            sid = input("请输入要修改的学号：")
            age = input("请输入新年龄：")
            major = input("请输入新专业：")
            sm.update_student_info(sid, age, major)

        elif choice == "5":
            sid = input("请输入要修改成绩的学号：")
            c = input("请输入新语文成绩：")
            m = input("请输入新数学成绩：")
            e = input("请输入新英语成绩：")
            sm.update_student_score(sid, c, m, e)

        elif choice == "6":
            sid = input("请输入要删除的学号：")
            sm.delete_student(sid)

        elif choice == "0":
            sm.close()
            print("系统退出成功，再见！")
            break

        else:
            print("输入无效，请输入 0-6 的数字！")

if __name__ == "__main__":
    main()