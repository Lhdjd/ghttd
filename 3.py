import pymysql
try:
    # 1. 连接数据库
    conn = pymysql.connect(
        host='localhost',
        user='root',
        passwd='123456',
        db='A'
    )
    cursor = conn.cursor()

    # ---------------- 插入数据（只插表里有的字段！）----------------
    # 正确字段：emp_name, salary, dept_id
    sql_single = "INSERT INTO employees (emp_name, salary, dept_id) VALUES ('钱九', 18000, 1)"
    cursor.execute(sql_single)
    conn.commit()  # 必须提交
    print(f"插入成功，影响行数：{cursor.rowcount}")

    # ---------------- 查询 8000~10000 ----------------
    sql = "SELECT * FROM employees WHERE salary >= 8000 AND salary <= 10000;"
    cursor.execute(sql)
    result = cursor.fetchall()

    print("\n薪水 8000~10000 的员工：")
    for row in result:
        print(row)

except pymysql.Error as e:
    print("数据库操作失败：", e)

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()