from pymysql import cursors
from app.models.BaseEntity import BaseEntity

class Report(BaseEntity):
    def __init__(self, db, date):
        super().__init__(db)
        self.date = date
        self.date_from = f'{self.date} 00:00:00'
        self.date_to = f'{self.date} 23:59:59'
    
    def called_clients(self):
        with self.conn.cursor(cursors.DictCursor) as _cursor:
            query = f"""select * from tbl_client_data c inner join tbl_client_report r
                        on c.id = r.client_data_id where r.created_at between '{self.date_from}' and '{self.date_to}' group by c.id"""
            _cursor.execute(query)
            return _cursor.fetchall()
    
    def contacted_clients(self):
        with self.conn.cursor(cursors.DictCursor) as _cursor:
            query = f"""select * from tbl_client_data c inner join tbl_client_report r on c.id = r.client_data_id
                        where r.created_at between '{self.date_from}' and '{self.date_to}' and dialog_is_client <> '' group by c.id"""
            _cursor.execute(query)
            return _cursor.fetchall()
    
    def get_all(self, limit = 0):
        limit = f'limit {limit}' if limit else ''
        with self.conn.cursor(cursors.DictCursor) as _cursor:
            query = f"select id from tbl_client_report where created_at between '{self.date_from}' and '{self.date_to}' order by id desc {limit}"
            _cursor.execute(query)
            return _cursor.fetchall()
    
    def wrong_number(self):
        with self.conn.cursor(cursors.DictCursor) as _cursor:
            query = f"""select r.* from tbl_client_data c inner join tbl_client_report r on c.id = r.client_data_id
                        where r.created_at between '{self.date_from}' and '{self.date_to}' and dialog_call_again = '3'  group by r.phone_number"""
            _cursor.execute(query)
            return _cursor.fetchall()
    
    def all_clients(self):
        with self.conn.cursor(cursors.DictCursor) as _cursor:
            query = f"select id from tbl_client_data where created_at between '{self.date_from}' and '{self.date_to}'"
            _cursor.execute(query)
            return _cursor.fetchall()