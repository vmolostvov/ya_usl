import sqlite3

conn = sqlite3.connect('names_yausl.db')

cur = conn.cursor()
# cur.execute("""CREATE TABLE FIO(Name TEXT, Name2 TEXT)""")
#
# name1 = 'Misha'
# name2 = 'vasya'
# cur.execute("INSERT INTO FIO VALUES (?, ?)", (name1, name1))
# conn.commit()

def is_in_base(self, name1):
    cur = self.conn.cusor()
    cur.execute("SELECT Name FROM Names")
    names = cur.fetchall()
    for name in names:
        if name == name1:
            return 'y'
    cur.execute("INSERT INTO Names VALUES ?", name1)
    self.conn.commit()
    return 'no'

def del_from_db():
#     # login1 = 'sdfsdfsdfsd@mail.ru'
    with conn:
        c = conn.cursor()
        # result = "DELETE FROM payments_info"  # чистим запись в бд
        # c.execute(result)
        # res = "SELECT Password FROM ivi_account_data WHERE Login=?"
        # cur.execute(res, [(login1)])
        # res1 = cur.fetchone()[0]
        # print(res1)
        # c.execute("UPDATE ivi_account_data SET persons=6")
        # c.execute("DELETE FROM kp_account_data WHERE Password='yRtMsbK3874'")
        # res = "UPDATE {}_account_data SET persons = 0 WHERE Login=?".format('kp')
        # c.execute(res, [('FvhZ8588')])
        conn.commit()
        c.execute("SELECT * FROM FIO")
        names = list(map(lambda x: x[0], c.description))
        print(names)
        rows = c.fetchall()
        for row in rows:
            print(row)

del_from_db()