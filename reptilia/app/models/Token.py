from pymysql import cursors
from app.models.BaseRept import BaseRept

class Token(BaseRept):
    def __init__(self, conn_params = None):
        super().__init__(conn_params)

    def insert(self, jti, token, user_id):
        with self.conn.cursor() as cursor:
            query = f"insert into tbl_token(jti, token, user_id) values('{jti}', '{token}', {user_id})"
            cursor.execute(query)

    def remove(self, jti):
        with self.conn.cursor() as cursor:
            query = f"delete from tbl_token where jti = '{jti}'"
            cursor.execute(query)

    def token_exist(self, jti):
        with self.conn.cursor() as cursor:
            query = f"select * from tbl_token where jti = '{jti}'"
            cursor.execute(query)
            if cursor.fetchone():
                return True

        return False

    def get_all(self):
        with self.conn.cursor(cursors.DictCursor) as cursor:
            query = f"select * from tbl_token"
            cursor.execute(query)
            return cursor.fetchall()

    def by_jti(self, jti):
        with self.conn.cursor(cursors.DictCursor) as cursor:
            query = f"select user_id from tbl_token where jti = '{jti}'"
            cursor.execute(query)
            return cursor.fetchone()
