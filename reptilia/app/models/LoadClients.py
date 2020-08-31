from pymysql import connect, cursors, err
from pexpect import pxssh, spawn
from multiprocessing import Process, Queue
from app.models.Campaign import Campaign
from pymongo import MongoClient
from app.models.BaseEntity import BaseEntity
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient

import datetime
import math
import pandas as pd
import json
import os
import logging
import requests
import sys

logger = logging.getLogger(__name__)

class LoadClients(BaseEntity):
    def __init__(self, client_data, list_id, charge_id, columns, channel_name, db, filename = None):
        super().__init__(db)

        env_multiprocess_name = 'INIT_MULTIPROCESS_LIMIT' if db == 'movistar' else 'MULTIPROCESS_LIMIT'
        self.columns = columns
        self.client_data = sorted(client_data, key = lambda item: item.get(self.columns.get('code')))
        self.filename = filename if filename else datetime.datetime.now().strftime('%Y%m%d_%H%M%S.csv')
        self.process = (int(len(client_data)/20) if len(client_data)/20 <= int(os.getenv(env_multiprocess_name, 100)) else int(os.getenv(env_multiprocess_name, 100))) if len(client_data) >= 40 else 1
        self.list_id = list_id
        self.charge_id = str(charge_id).zfill(4)
        self.channel_name = channel_name
        self.db = db
        # self.process = 1

        self.datafile_clients = {}
        self.process_ref = {}
        self.queue_ref = {}
        self.campaign_id = ''

        self.count_new_clients = 0
        self.count_new_products = 0
        self.count_duplicate_clients = 0
        self.count_out = 0
        self.msg = ''
        self.phone_numbers_pool = []

        self.__set_campaign_id()

        self.table_name_client = 'tbl_client_data'
        self.table_name_product = 'tbl_client_product'

    def __set_campaign_id(self):
        with Campaign() as campaign:
            camp = campaign.get_campaign_by_list(self.list_id)
            self.campaign_id = camp.get('campaign_id') if camp else 0

    def start(self):
        if self.process == 1:
            self.process_data(self.client_data)

        elif self.process > 1:
            count = self.process
            part = int(len(self.client_data)/self.process) + 1
            self.queue_ref[1] = Queue()
            self.process_ref[1] = Process(target=self.process_data, args=(self.client_data[:part],self.queue_ref[1],))
            self.process_ref[1].start()
            after = part

            while count > 2:
                before = after
                after = before + part
                self.queue_ref[count] = Queue()
                self.process_ref[count] = Process(target=self.process_data, args=(self.client_data[before:after],self.queue_ref[count],))
                self.process_ref[count].start()
                count -= 1

            self.queue_ref[2] = Queue()
            self.process_ref[2] = Process(target=self.process_data, args=(self.client_data[after:],self.queue_ref[2],))
            self.process_ref[2].start()

            for i in self.process_ref:
                self.process_ref.get(i).join()

                part = self.queue_ref.get(i).get()

                self.count_new_clients += part.get('count_clients')
                self.count_new_products += part.get('count_products')
                self.count_duplicate_clients += part.get('count_duplicates')
                self.count_out += part.get('count_out')
                self.msg += f'{"|" if self.msg else ""}{part.get("msg")}' if part.get('msg') not in self.msg.split('|') else ''

                phone_numbers = part.get('phone_numbers')

                for j in phone_numbers:
                    if j in self.datafile_clients:
                        self.datafile_clients[j] += phone_numbers.get(j)
                    else:
                        self.datafile_clients[j] = phone_numbers.get(j)

                self.process_ref.get(i).close()

        return {
            'msg': self.msg,
            'count_clients': self.count_new_clients,
            'count_products': self.count_new_products,
            'count_duplicates': self.count_duplicate_clients,
            'count_out': self.count_out,
            'process': self.process
        }

    def load_data(self):
        if self.channel_name == 'SMS':
            filename = datetime.datetime.now().strftime('%Y%m%d_%H%M%S.txt')
            with open(f'./{filename}', 'w') as f:
                for client_id in self.datafile_clients:
                    phone_numbers = list(dict.fromkeys(self.datafile_clients.get(client_id)))

                    phone_numbers = list(filter(lambda pn: pn not in self.phone_numbers_pool, phone_numbers))
                    self.phone_numbers_pool += phone_numbers

                    s = client_id

                    for number in phone_numbers:
                        s = f'{s}.{number}'

                    f.write(f'{s}\n')

            try:
                response = requests.post(f"{os.getenv('URL_SMS_API')}/init-messages", files={
                    'phones_file' : open(f'./{filename}', 'rb')
                }, data={
                    'db': self.db
                })

                logger.info(response.json())

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error(f'{e}:: {exc_type}, {exc_tb.tb_lineno}')

        else:
            if self.db == 'movistar':
                self.store_asterisk()
            else:
                with open(f'./docs/{self.filename}', 'w') as f:
                    for client_id in self.datafile_clients:
                        phone_numbers = list(dict.fromkeys(self.datafile_clients.get(client_id)))

                        s = f'"{client_id}","{len(phone_numbers)}","{self.campaign_id}"'

                        for number in phone_numbers:
                            s = f'{s},"{self.charge_id}{number}{client_id}"'

                        f.write(f'{s}\n')

                try:
                    ssh = SSHClient()
                    ssh.set_missing_host_key_policy(AutoAddPolicy())
                    ssh.connect(hostname='172.16.80.5', port='22', username='root', password='hdec')

                    scp = SCPClient(ssh.get_transport())
                    scp.put(f'./docs/{self.filename}', f'/var/grabaciones/base/{self.filename}')
                    scp.close()
                    
                    ssh = pxssh.pxssh()

                    ssh.login('172.16.80.11', 'root', 'vicidial', login_timeout = 200)
                    ssh.sendline(f'/usr/src/astguiclient/trunk/bin/VICIDIAL_IN_new_leads_file.pl --format=dccsv10  --forcelistid={self.list_id} --file-prefix-filter={self.filename} --ftp-pull --ftp-dir=base')
                    ssh.logout()

                except Exception as e:
                    logger.error(f'::load_data:: {e}')
                    self.msg = f'File {e}'

    def store_asterisk(self):
        data = [{'id': k, 'phones': list(dict.fromkeys(v))} for k, v in self.datafile_clients.items()]
        size = len(data)
        print(size)
        if size >= 5000:
        # if False:
            part = int((size/5)+1)
            after = part
            before = 0
            for i in range(1,6):
                if i == 1:
                    _list = data[:after]
                elif i == 5:
                    _list = data[before:]
                else:
                    _list = data[before:after]
                
                before = after
                after = before + part

                params = {
                    'host': os.getenv(f'CALLER_HOST_{i}'),
                    'user': os.getenv(f'CALLER_USER_{i}'),
                    'password': os.getenv(f'CALLER_PASSWORD_{i}'),
                    'db': os.getenv(f'CALLER_DB_{i}')
                }
                self.__marker_process(_list, params)
                print(f'Terminado para: {params}')

        else:
            self.__marker_process(data)

    def __store_data_caller(self, data: list, conn_params):
        try:
            conn = connect(
                host = os.getenv('CALLER_HOST_1'),
                user = os.getenv('CALLER_USER_1'),
                password = os.getenv('CALLER_PASSWORD_1'),
                db = os.getenv('CALLER_DB_1'),
                autocommit = True
            ) if conn_params is None else connect(**{**conn_params, **{'autocommit': True}})
            with conn.cursor() as cursor:
                for row in data:
                    client_id, account  = row.get('id').split('$$')
                    phone_numbers       = row.get('phones')

                    pn1 = f'{phone_numbers[0]}'
                    pn2 = f'{phone_numbers[1]}' if len(phone_numbers) > 1 else ''
                    pn3 = f'{phone_numbers[2]}' if len(phone_numbers) > 2 else ''

                    query = f"""
                            insert into list(entry_date,list_id,campaign_id, prefix_code, code, account_code, recycling,status,numbers_count,numbers_total,
                            Phone_number1,Phone_number2,Phone_number3, turn_calls) values(NOW(),{self.list_id}, '{self.campaign_id}',
                            {self.charge_id}, '{client_id}', '{account}','0','NEW', '0','{len(phone_numbers)}','{pn1}','{pn2}','{pn3}', '0')
                        """
                    cursor.execute(query)
                    row_id = cursor.lastrowid

                    for index, pn in enumerate(phone_numbers):
                        if index > 2:
                            query = f"""
                                        insert into list_alt_phones(lead_id, numbers_count, phone_number)
                                        values({row_id}, {index + 1}, '{pn}')
                                    """
                            cursor.execute(query)
                    # client_id     = row.get('id')
                    # phone_numbers = row.get('phones')

                    # pn1 = f'{self.charge_id}{phone_numbers[0]}{client_id}'
                    # pn2 = f'{self.charge_id}{phone_numbers[1]}{client_id}' if len(phone_numbers) > 1 else ''
                    # pn3 = f'{self.charge_id}{phone_numbers[2]}{client_id}' if len(phone_numbers) > 2 else ''

                    # now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # query = f"""
                    #         insert into list(entry_date,list_id,campaign_id,code,recycling,status,numbers_count,numbers_total,
                    #         Phone_number1,Phone_number2,Phone_number3, turn_calls) values('{now}',{self.list_id}, '{self.campaign_id}',
                    #         '{client_id}','0','NEW', '0','{len(phone_numbers)}','{pn1}','{pn2}','{pn3}', '0')
                    #     """
                    # cursor.execute(query)
                    # row_id = cursor.lastrowid

                    # for index, pn in enumerate(phone_numbers):
                    #     if index > 2:
                    #         query = f"""
                    #                     insert into list_alt_phones(lead_id, numbers_count, phone_number)
                    #                     values({row_id}, {index + 1}, '{self.charge_id}{pn}{client_id}')
                    #                 """
                    #         cursor.execute(query)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(f'{e}:: {exc_type}, {exc_tb.tb_lineno}')

    def __marker_process(self, data: list, conn_params=None):
        count = self.process
        part = int(len(data)/self.process) + 1
        _process = {}
        _process[1] = Process(target=self.__store_data_caller, args=(data[:part],conn_params,))
        _process[1].start()
        after = part

        while count > 2:
            before = after
            after = before + part
            _process[count] = Process(target=self.__store_data_caller, args=(data[before:after],conn_params,))
            _process[count].start()
            count -= 1

        _process[2] = Process(target=self.__store_data_caller, args=(data[after:],conn_params,))
        _process[2].start()

        for i in _process:
            _process.get(i).join()
            _process.get(i).close()
    
    def process_data(self, rows, queue = None):
        self.conn_params['autocommit'] = False
        try:
            conn = connect(**self.conn_params)
            for index, row in enumerate(rows):
                phone_numbers = []
                phone_field = ''.join([ (' ' if sub.isdigit() else sub) for sub in self.columns.get('phone')]).split()[0]

                for i in range(1, 51):
                    pn = row.get(f'{phone_field}{i}')

                    if pn is None:
                        if i == 1:
                            pn = row.get(f'{phone_field}')
                            pn2 = row.get('numero')
                            pn3 = row.get('numero_tmp')
                            if pn and pd.notna(pn) and isinstance(pn, (int, float)) and ((self.channel_name != 'SMS' and pn > 1000000) or (self.channel_name == 'SMS' and pn > 899999999)):
                                phone_numbers.append(str(int(pn)))
                            if pn2 and pd.notna(pn2)  and isinstance(pn2, (int, float)) and ((self.channel_name != 'SMS' and pn2 > 1000000) or (self.channel_name == 'SMS' and pn2 > 899999999)):
                                phone_numbers.append(str(int(pn2)))
                            if pn3 and pd.notna(pn3)  and isinstance(pn3, (int, float)) and ((self.channel_name != 'SMS' and pn3 > 1000000) or (self.channel_name == 'SMS' and pn3 > 899999999)):
                                phone_numbers.append(str(int(pn3)))

                        break

                    elif pd.notna(pn) and isinstance(pn, (int, float)) and ((self.channel_name != 'SMS' and pn > 1000000) or (self.channel_name == 'SMS' and pn > 899999999)):
                        phone_numbers.append(str(int(pn)))

                # tomorrow = (datetime.datetime.now() + datetime.timedelta(1)).strftime('%Y-%m-%d')
                phone_numbers = list(dict.fromkeys(phone_numbers))
                if phone_numbers:
                    name = row[self.columns.get('name')].strip().lower()
                    name = name.replace('?','ñ')
                    name = name.replace('#','ñ')
                    name = name.replace("'","")

                    product = row[self.columns.get('product')]
                    if not pd.notna(product): product = ''
                    product = str(product).strip().lower()
                    product = product.replace('S/.','')
                    product = product.replace('?','é')

                    c = row[self.columns.get('currency')].strip()
                    currency = 'pen' if c in ['S/', '1'] else ('usd' if c == '2' else c)
                    d = row[self.columns.get('date')]
                    pay_date = (datetime.datetime.now() - datetime.timedelta(d)).strftime('%Y-%m-%d') if isinstance(d, int) else d.strftime('%Y-%m-%d')

                    client = {
                        'client_id': row[self.columns.get('code')] if self.db == 'movistar' else row[self.columns.get('code')].zfill(15),
                        'phone_numbers': phone_numbers,
                        'name': name,
                        'amount': row[self.columns.get('amount')],
                        'currency': currency ,
                        'product': product,
                        'pay_date': pay_date
                    }

                    numero_asesor = row.get(self.columns.get('numero_asesor'))
                    if numero_asesor is not None and pd.notna(numero_asesor): client['numero_asesor'] = str(int(numero_asesor))
                    asesor = row.get(self.columns.get('asesor'))
                    if asesor is not None and pd.notna(asesor): client['asesor'] = asesor
                    genre = row.get(self.columns.get('genre'))
                    if genre is not None and pd.notna(genre): client['genre'] = genre
                    account = row.get(self.columns.get('account'))
                    if account is not None and pd.notna(account): client['account'] = account
                    # origen_code = row.get(self.columns.get('code'))
                    # if origen_code is not None and pd.notna(origen_code): client['origen_code'] = origen_code

                    conn.begin()
                    self.store_mysql(conn, **client)
                    conn.commit()
                else:
                    self.count_out += 1

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(f'::process_data:: {e}:: {exc_type}, {exc_tb.tb_lineno}')
            if 'conn' in locals(): conn.rollback()
            if isinstance(e, err.InternalError):
                if e.args[0] == 1292:
                    self.msg = 'MYSQL: Tipo de dato incorrecto.'
                else:
                    self.msg = f'INTERNAL: {e}'
            else:
                self.msg = f'OTHER: {e}'

        if queue:
            queue.put({
                'msg': self.msg,
                'phone_numbers': self.datafile_clients,
                'count_clients': self.count_new_clients,
                'count_products': self.count_new_products,
                'count_out': self.count_out,
                'count_duplicates': self.count_duplicate_clients
            })

        if 'conn' in locals(): conn.close()

    def store_mysql(self, conn, client_id, phone_numbers, name, product, amount, currency, pay_date, asesor=None, numero_asesor=None, genre=None, account = None):
        
        key = client_id if account is None else f"{client_id}$${account}"

        if key in self.datafile_clients:
            self.datafile_clients[key] += phone_numbers
        else:
            self.datafile_clients[key] = phone_numbers

        
        with conn.cursor(cursors.DictCursor) as cursor:
            account_field, account_condition, account_val = ('','','')
            if account is not None:
                account_field = 'account,'
                account_val = f"'{account}',"
                account_condition = f" and c.account = '{account}'"

            query = f"""select c.id, p.id product_id, p.phone_numbers,  case when p.product = '{product}' and p.amount = {round(amount, 2)} and p.currency = '{currency}'
                    then '1' else '0' end as same_product from {self.table_name_client} c left join {self.table_name_product} p
                    on c.id = p.client_data_id where c.client_id = '{client_id}' and c.campaign_id = '{self.campaign_id}' and
                    c.list_id = {self.list_id} {account_condition}"""

            cursor.execute(query)
            rows = cursor.fetchall()

            if rows:
                _pass = True

                for row in rows:
                    if row.get('same_product') == '1':
                        phones = json.loads(row.get('phone_numbers'))
                        phone_numbers += phones
                        phone_numbers = list(dict.fromkeys(phone_numbers))
                        query = f"""
                                    update {self.table_name_product} set phone_numbers = '{json.dumps(phone_numbers)}',
                                    total_numbers = {len(phone_numbers)}, updated_at = now()
                                    where id = {row.get('product_id')}
                                """
                        cursor.execute(query)
                        _pass = False
                        break

                if _pass:
                    query = f"""insert into {self.table_name_product}(product, amount, currency, pay_date, client_data_id, phone_numbers, total_numbers,
                                created_at, updated_at) values('{product}', {amount}, '{currency}', '{pay_date}', '{rows[0].get('id')}',
                                '{json.dumps(phone_numbers)}', {len(phone_numbers)}, now(), now())"""
                    cursor.execute(query)

                    self.count_new_products +=1

                    return True, f'Success add product! {client_id}'
            else:
                asesor_field, asesor_val, numero_asesor_field, numero_asesor_val, genre_field, genre_val = ('','','','','','')
                if asesor is not None:
                    asesor_field = 'asesor,'
                    asesor_val = f"'{asesor}',"
                if numero_asesor is not None:
                    numero_asesor_field = 'numero_asesor,'
                    numero_asesor_val = f"'{numero_asesor}',"
                if genre is not None:
                    genre_field = 'genre,'
                    genre_val = f"'{genre}',"

                query = f"""insert into {self.table_name_client}(client_id, name, list_id, campaign_id, {asesor_field} {numero_asesor_field} {genre_field} {account_field} created_at, updated_at)
                            values('{client_id}', '{name}', {self.list_id}, '{self.campaign_id}', {asesor_val} {numero_asesor_val} {genre_val} {account_val} now(), now())"""
                cursor.execute(query)

                client_data_id = cursor.lastrowid

                query = f"""insert into {self.table_name_product}(product, amount, currency, pay_date, client_data_id, phone_numbers, total_numbers,
                            created_at, updated_at)  values('{product}', {amount}, '{currency}', '{pay_date}', '{client_data_id}',
                            '{json.dumps(phone_numbers)}', {len(phone_numbers)}, now(), now())"""
                cursor.execute(query)

                self.count_new_clients +=1
                self.count_new_products +=1

                return True, f'Success! {client_id}'

            self.count_duplicate_clients +=1

            return False, f'Duplicado para el cliente {client_id}'


class LoadClientsV2(BaseEntity):
    def __init__(self, client_data, list_id, charge_id, columns, channel_name, db, filename = None):
        super().__init__(db)

        self.filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv"

        client_data.to_csv(self.filename, encoding='utf-8', index=False)
        self.conn_params['local_infile'] = True
        conn = connect(**self.conn_params)

        query = f"LOAD DATA LOCAL INFILE '{self.filename}' INTO TABLE _tmp_full_data FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n' IGNORE 1 LINES"

        with conn.cursor(cursors.DictCursor) as cursor:
            r = cursor.execute(query)
            print(r)

        # self.columns = columns
        # self.list_id = list_id
        # self.charge_id = str(charge_id).zfill(4)
        # self.channel_name = channel_name
        # self.db = db

        # self.campaign_id = ''

        # self.__set_campaign_id()

        # self.table_name_client = 'tbl_client_data_dev'
        # self.table_name_product = 'tbl_client_product_dev'

    def __set_campaign_id(self):
        with Campaign() as campaign:
            camp = campaign.get_campaign_by_list(self.list_id)
            self.campaign_id = camp.get('campaign_id') if camp else 0
        
