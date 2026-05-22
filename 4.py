import pymysql

try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        passwd='123456',
        db='student_class_db'
    )
    cursor = conn.cursor()

    # 1. 单条插入（只插入你表里有的字段：name, c_id, age）
    sql_single = "INSERT INTO students (name, c_id, age) VALUES ('赵六', 1, 22)"
    cursor.execute(sql_single)

    # 2. 批量插入
    students = [
        ('孙七', 2, 20),
        ('周八', 3, 23)
    ]
    sql_batch = "INSERT INTO students (name, c_id, age) VALUES (%s, %s, %s)"
    cursor.executemany(sql_batch, students)

    # 提交事务
    conn.commit()
    print("插入成功！")

except pymysql.Error as e:
    print("数据库错误：", e)
    conn.rollback()

finally:
    cursor.close()
    conn.close()