from pymysql import cursors
from app.models.BaseVici import BaseVici

class RemoteAgents(BaseVici):
    def __init__(self, conn_params = None):
        super().__init__(conn_params)
    
    def get_all(self):
        with self.conn.cursor(cursors.DictCursor) as _cursor:
            query = "select * from vicidial_remote_agents"
            _cursor.execute(query)
            return _cursor.fetchall()
    
    def update_lines(self, _id, lines):
        with self.conn.cursor(cursors.DictCursor) as _cursor:
            query = f"update vicidial_remote_agents set number_of_lines = {lines} where remote_agent_id = {_id}"
            _cursor.execute(query)