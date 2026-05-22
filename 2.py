import pymysql

# 完整正确代码
try:
    # 连接数据库
    conn = pymysql.connect(
        host='localhost',
        user='root',
        passwd='123456',  # 你的密码
        db='W'  # 数据库名
    )

    cursor = conn.cursor()

    # 执行查询
    cursor.execute("SELECT * FROM orders")
    print(cursor.fetchall())  # 打印所有数据

except pymysql.Error as e:
    # 捕获错误并打印
    print("数据库操作失败：", e)

finally:
    # 无论是否出错，都关闭连接
    cursor.close()
    conn.close()