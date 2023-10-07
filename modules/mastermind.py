import requests
import sqlite3
from sqlite3 import Error
from json import loads, dumps
from base64 import b64encode
from datetime import datetime as dt
from os import get_terminal_size as gts

class MasterMind:
    def __init__(self):
        global warna
        # sqlite
        try:
            self.connect = sqlite3.connect('config/akun.db')
        except Error as e:
            print(e)

        self.sesi = requests.Session()
        self.host = 'api.alfastore.co.id'

    def req(self, method, path, data = {}):
        if data:
            data = dumps(data)

        if method == 'GET':
            inter = self.sesi.get
        elif method == 'POST':
            inter = self.sesi.post
        elif method == 'PUT':
            inter = self.sesi.put
        else:
            return 'idk'

        try:
            r = inter(
                f'https://{self.host}/{path}',
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; V2132A Build/PQ3A.190605.003)',
                    'Host': self.host,
                    'Connection': 'Keep-Alive'
                },
                data = data,
                verify = 'config/resign.pem'
            )

            if r.status_code != 200:
                return {'err': r.status_code}

            return r.json()
        except Exception as ex:
            return {'err': ex}

    def load_config(self):
        tmp = open('config/setting.json')
        config = tmp.read()
        tmp.close()
        return loads(config)

    def write_config(self, key, val):
        config = self.load_config()
        config[key] = val
        tmp = open('config/setting.json', 'w')
        tmp.write(dumps(config))
        tmp.close()

    def debug(self, clr, txt):
        d = warna[0]
        if clr == 'r':
            a, b, c = warna[1], warna[3], '!'
        elif clr == 'g':
            a, b, c = warna[2], warna[6], '*'
        elif clr == 'c':
            a, b, c = warna[4], warna[5], '?'
        
        print(f'\r{" "*gts().columns}', end='')
        print(f'\r{d}[{a}{c}{d}] {b}{txt}{d}', end='', flush=1)

    def check_store(self, kode):
        self.debug('g', 'check toko')
        r = self.req('GET', f'api/sis/master/status_toko/?storeId={kode}')
        if r.get('err'):
            return self.debug('r', f'error: {r["err"]}\n')

        self.debug('g', f'nama toko: {r["storeName"]}\n')

    def login(self, nik, pwd):
        config = self.load_config()
        versi, store_id = config['versi_maxdis'], config['store']
        self.debug('g', 'login bentar...')
        r = self.req('POST', f'api/mob/login/?appName=MaxDisplay&versi={versi}', {
            'timeTx': dt.now().strftime('%H:%M:%S'),
            'userId': nik,
            'storeId': store_id,
            'password': b64encode(pwd.encode()).decode(),
            'storeDate': dt.now().strftime('%d/%m/%Y')
        })

        if r.get('err'):
            self.debug('r', f'error: {r["err"]}\n')
            return ()

        return r['user']

class Maxdis(MasterMind):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()

    def list_rack(self, flag):
        r = self.req('GET', f'api/mob/tablet/maxdisplay/list_rack_md/?storeid={self.config["store"]}&osa={flag}&order={self.config["order_by"]}')
        if ada := r.get('data'): return ada
        return r

    def rak_detail(self, arak, flag):
        r = req('GET', f'api/mob/tablet/maxdisplay/show_per_rack/?storeid={self.config["store"]}&osa={flag}&rack={arak}')
        return r

    def konfirm(self, plu, arak, plano, qty):
        r = self.req('PUT', f'api/mob/tablet/maxdisplay/confirm/?storeid={self.config["store"]}&plu={plu}&rack={arak}&plano={plano}&qty={qty}')
        return 'failed' if r.get('err') else 'saved'

    def maxdis(self, x, y):
        while 1:
            self.debug('g', f'rak {x}\n')
            all_rak = self.list_rack(y)
            if type(all_rak) != list:
                if all_rak['err'] == 204:
                    self.debug('r', 'no data\n')
                    break
                continue

            for rak in all_rak:
                no, name, item, qty = rak['rack_no'], rak['rack_name'], rak['jum_item'], rak['jum_qty']
                detail = self.rak_detail(no, y)['data']
                print('*'*50)
                print(f'[{no}] {name} | item: {item} | qty: {qty}')
                print('+'*50)
                for det in detail:
                    plu, desc, oh, plano, qreq = int(det['lmd_plu']), det['lmd_descp'], det['lmd_on_hand'], det['lmd_planogram'], det['lmd_qty_req']
                    confirm = self.konfirm(plu, no, plano, qreq)
                    print(f'{plu} | {desc} | oh={oh} | {plano} | {qreq} | {confirm}')
                    print('-'*50)
                print()
    
    def start(self):
        cur = self.connect.cursor()
        flag = {
            'osa': 'F',
            'khusus': 'T'
        }

        cur.execute('SELECT nik, password FROM akun ORDER BY RANDOM() LIMIT 1')
        usr, pwd = cur.fetchone()
        akun = self.login(usr, pwd)
        if type(akun) != dict:
            return self.debug('r', 'idk error\n')

        self.debug('g', f'Nik/Nama: {akun["userId"]}/{akun["name"]}\n')
        
        for x, y in flag.items():
            self.maxdis(x, y)

class Setting(MasterMind):
    def toko(self):
        self.debug('c', 'kode toko: ')
        kode = input()
        if len(kode) == 0: return
        self.check_store(kode)
        self.debug('c', 'betul tidak? [y/n] ')
        confirm = input()
        if confirm.lower() == 'y':
            self.write_config('store', kode)
            self.debug('g', 'oke done\n')
        else:
            return

    def akun(self, action):
        cur = self.connect.cursor()
        if action == 'tambah':
            self.debug('c', 'nik: ')
            nik = input()
            self.debug('c', 'password: ')
            pwd = input()
            if len(nik) == 0 or len(pwd) == 0:
                return self.debug('r', 'hah kosong?\n')

            akun = self.login(nik, pwd)
            if len(akun) == 0: return

            query = 'INSERT INTO akun VALUES(?,?,?)'
            cur.execute(query, (nik, pwd, akun['name']))
            self.connect.commit()
            self.debug('g', 'done\n')

        elif action == 'apus':
            cur.execute('SELECT nik, nama FROM akun')
            rows = cur.fetchall()
            n = 0
            for row in rows:
                n += 1
                print(f'{n}. {row[1]}')
            
            print('*ketik 0 untuk keluar')

            self.debug('c', 'pilih: ')
            n = int(input())
            if n == 0:
                return
            
            choosen = rows[n-1]
            query = 'DELETE FROM akun WHERE nik = ?'
            cur.execute(query, (choosen[0],))
            self.connect.commit()

setting = Setting()
maxdis = Maxdis()
warna = tuple([chr(27)+'[1;0m'] + list(chr(27)+'[1;3'+str(x)+'m' for x in range(1,7)))