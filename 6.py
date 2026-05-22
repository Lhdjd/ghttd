import pymysql

try:
    # 1. 连接数据库（先不指定库，因为库还没创建）
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="123456"
    )
    cursor = conn.cursor()

    # 2. 先创建数据库！解决第一个报错
    cursor.execute("CREATE DATABASE IF NOT EXISTS test_db")
    cursor.execute("USE test_db")  # 使用数据库

    # 3. 创建user表（严格按要求：枚举gender，默认男）
    create_sql = """
    CREATE TABLE IF NOT EXISTS user(
        id INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(30) NOT NULL,
        gender ENUM('男','女') DEFAULT '男',
        phone VARCHAR(20)
    )
    """
    cursor.execute(create_sql)
    print("表创建完成")

    # 4. 事务：连续插入5条数据
    conn.autocommit = False
    insert_data = [
        ("小明", "男", "13111111111"),
        ("小红", "女", "13222222222"),
        ("小华", "男", "13333333333"),
        ("小丽", "女", "13444444444"),
        ("小凯", "男", "13555555555")
    ]
    insert_sql = "INSERT INTO user(username,gender,phone) VALUES(%s,%s,%s)"
    cursor.executemany(insert_sql, insert_data)
    conn.commit()
    print("事务插入5条数据成功")

    # 5. 查询所有男性用户
    print("\n所有男性用户")
    cursor.execute("SELECT * FROM user WHERE gender='男'")
    for row in cursor.fetchall():
        print(row)

    # 6. 修改手机号
    cursor.execute("UPDATE user SET phone='13666666666' WHERE id=1")
    conn.commit()
    print("\n修改id=1手机号成功")

    # 7. 删除 id=3
    cursor.execute("DELETE FROM user WHERE id=3")
    conn.commit()
    print("删除id=3成功")

    # 8. 查看最终数据
    print("\最终全部数据 ")
    cursor.execute("SELECT * FROM user")
    for row in cursor.fetchall():
        print(row)

except pymysql.Error as e:
    print("数据库错误：", e)
    # 只有conn存在时才回滚
    if 'conn' in locals():
        conn.rollback()

finally:
    # 安全关闭
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()