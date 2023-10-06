#!/usr/bin/python3

from os import get_terminal_size as gts, system
from time import sleep as sl

from modules.mastermind import setting
from modules.mastermind import maxdis
from modules.mastermind import warna

banner = f'''{warna[1]}########### 5.22-B ##########
#                           #
# made with hand by ipin    #
#---------------------------#{warna[0]}
# masih beta & kacau        #
# seperti negeri ini        #
#                           #
#############################
'''

def cli():
    system('clear')
    for _ in banner:
        print(_, end='', flush=1)
        sl(0.003)

    print(
        f'{warna[1]}1. {warna[0]}ganti toko\n\
        \r{warna[1]}2. {warna[0]}tambah akun\n\
        \r{warna[1]}3. {warna[0]}apus akun\n\
        \r{warna[1]}m. {warna[0]}maxdis\n\
        \r{warna[1]}0. {warna[0]}keluar'
    )
    cmd = input(f'{warna[1]}[{warna[0]}maxdis{warna[1]}]{warna[2]}:-) {warna[0]}')

    if cmd == '0':
        exit()
    elif cmd == '1':
        setting.toko()
    elif cmd == '2' or cmd == '3':
        setting.akun('tambah' if cmd == '2' else 'apus')
    elif cmd == 'm':
        maxdis.start()
    
    cli()

cli()