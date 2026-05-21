import pymysql

try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        passwd='123456',
        db='company1'
    )
    cursor = conn.cursor()

    sql = "UPDATE employees SET salary = %s WHERE name = %s"
    params = (20000, '张三')

    sql = "DELETE FROM employees WHERE name = %s"
    params = ('钱九',)
    cursor.execute(sql, params)
    conn.commit()
    print(f"更新成功，影响行数：{cursor.rowcount}")


except pymysql.Error as e:
    print("数据库错误：", e)
    conn.rollback()

finally:
    cursor.close()
    conn.close()