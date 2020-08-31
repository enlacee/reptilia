from pymysql import connect, cursors
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import create_access_token, get_jwt_identity

from app.models.BaseRept import BaseRept

class User(BaseRept):
    def __init__(self, conn_params = None):
        super().__init__(conn_params)

    def register_user(self, username, password, role_id):
        if self.validate_credentials(username, password):
            with self.conn.cursor() as cursor:
                query = f"insert into tbl_user values(null, '{username}', '{sha256.hash(password)}', {role_id})"
                cursor.execute(query)
                return True
        return False

    def login_user(self, username, password):
        if self.validate_credentials(username, password):
            with self.conn.cursor(cursors.DictCursor) as cursor:
                query = f"select * from tbl_user where username = '{username}'"
                cursor.execute(query)
                user = cursor.fetchone()

                if user and sha256.verify(password, user.get('password')):
                    access_token = create_access_token(identity = username)
                    return True, access_token, user.get('id')

        return False, None, None

    def validate_credentials(self, username, password):
        rules = {
            'min_lenght': 4,
        }
        if len(username) >= rules.get('min_lenght') and len(password) >= rules.get('min_lenght'):
            return True

        return False

    def get_roles(self):
        with self.conn.cursor(cursors.DictCursor) as cursor:
            query = f"select * from tbl_role"
            cursor.execute(query)
            return cursor.fetchall()

    def get_users(self):
        with self.conn.cursor(cursors.DictCursor) as cursor:
            query = f"select * from tbl_user u inner join tbl_role r on u.role_id = r.id"
            cursor.execute(query)
            return cursor.fetchall()
