from pymysql import cursors
from app.models.Campaign import Campaign
from app.models.Entity import Entity
from app.models.BaseRept import BaseRept

class Charge(BaseRept):
    def __init__(self, conn_params = None):
        super().__init__(conn_params)
    
    def add_charge(self, list_id, carrier_id, iterations, seconds_between_iterations, entity_prefix, channel_id):
        with Campaign() as campaign:
            camp = campaign.get_campaign_by_list(list_id)
            campaign_id = camp.get('campaign_id') if camp else 0

        with Entity() as ent:
            entity = ent.by_prefix(entity_prefix)
            entity_id = entity.get('id')

        with self.conn.cursor(cursors.DictCursor) as cursor:
            query = f"""select * from tbl_charge where list_id = {list_id} and carrier_id = {carrier_id}
                        and campaign_id = '{campaign_id}' and entity_id = {entity_id} and channel_id = {channel_id}"""
            cursor.execute(query)
            row = cursor.fetchone()
            if not row:
                query = f"""insert into tbl_charge(campaign_id, list_id, iterations, seconds_between_iterations, carrier_id,
                            entity_id, channel_id, created_at, updated_at) values('{campaign_id}', {list_id}, {iterations},
                            {seconds_between_iterations}, {carrier_id}, {entity_id}, {channel_id}, now(), now())"""
                cursor.execute(query)

                return cursor.lastrowid
            else:
                return row.get('id')

        return 0
    
    def get_all(self):
        with self.conn.cursor(cursors.DictCursor) as cursor:
            query = """select ch.id as charge_id, ch.*, e.name as entity_name, c.name as carrier_name from tbl_charge ch
                        inner join tbl_entity e on ch.entity_id = e.id inner join tbl_carrier c on ch.carrier_id = c.id
                    """
            cursor.execute(query)
            charges = cursor.fetchall()
            charges = list(map(lambda charge: {**charge, 'created_at': charge.get('created_at').strftime('%Y/%m/%d %H:%M:%S'), 'updated_at': charge.get('updated_at').strftime('%Y/%m/%d %H:%M:%S')}, charges))
            return charges
    
    def update(self, charge_id, carrier_id):
        with self.conn.cursor(cursors.DictCursor) as cursor:
            query = f"update tbl_charge set carrier_id = {carrier_id}, updated_at = now() where id = {charge_id}"
            cursor.execute(query)