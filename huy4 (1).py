# -*- coding: utf-8 -*-
import requests, json, os, sys, hashlib
from sys import platform
from datetime import datetime, timedelta
from time import sleep

LINK_LAY_KEY = "liên hệ số 0326111431 để lấy key free " 
SECRET_CODE = "0807" 

den = '\x1b[1;90m'
luc = '\x1b[1;32m' 
trang = '\x1b[1;37m'
red = '\x1b[1;31m'
vang = '\x1b[1;33m'
tim = '\x1b[1;35m'
lamd = '\x1b[1;34m'
lam = '\x1b[1;36m'
reset = '\x1b[0m'

try:
    from pystyle import Add, Center, Anime, Colors, Colorate, Write, System
except:
    os.system('pip install pystyle requests colorama beautifulsoup4 selenium mechanize webdriver_manager')
    from pystyle import Add, Center, Anime, Colors, Colorate, Write, System

def clear():
    if platform[0:3] == 'lin':
        os.system('clear')
    else:
        os.system('cls')

def get_ip_public():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        data = response.json()
        return data['ip']
    except:
        return "Unknown"

def get_today_date_vn():
    now_utc = datetime.utcnow()
    now_vn = now_utc + timedelta(hours=7)
    return now_vn.strftime("%d%m%Y")

def generate_key(ip_address):
    date_key = get_today_date_vn()
    raw_str = f"{ip_address}|{date_key}|{SECRET_CODE}"
    md5_hash = hashlib.md5(raw_str.encode()).hexdigest()
    key_final = md5_hash[:8].upper()
    return key_final

banners = f"""
##     ## ##     ## ##    ##     ######   #######  ##    ##    
##     ## ##     ##  ##  ##     ##    ## ##     ## ###   ##    
##     ## ##     ##   ####      ##       ##     ## ####  ##    
######### ##     ##    ##       ##       ##     ## ## ## ##    
##     ## ##     ##    ##       ##       ##     ## ##  ####    
##     ## ##     ##    ##       ##    ## ##     ## ##   ###    
##     ##  #######     ##        ######   #######  ##    ##    
                                                   
=========================================================================
"""

def show_banner():
    clear()
    print(Colorate.Horizontal(Colors.green_to_white, Center.XCenter(banners)))

def login_system():
    show_banner()
    print(f"{luc}[!] Đang lấy dữ liệu IP máy...{reset}")
    ip = get_ip_public()
    
    if ip == "Unknown":
        print(f"{red}[X] Không thể lấy IP. Vui lòng kiểm tra kết nối mạng!{reset}")
        sys.exit()

    true_key = generate_key(ip)
    
    print(f"{luc}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print(f"{luc}┃ {trang}IP Của Bạn: {vang}{ip}{' ' * (35 - len(ip))} {luc}┃")
    print(f"{luc}┃ {trang}Trạng Thái: {red}Chưa Nhập Key{' ' * 24} {luc}┃")
    print(f"{luc}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
    print(f"\n{luc}[=>] Link Lấy Key Hôm Nay: {trang}{LINK_LAY_KEY}")
    print(f"{den}--------------------------------------------------{reset}")
    
    while True:
        user_key = input(f"{luc}root@huy:~# {trang}Nhập Key: {vang}").strip()
        
        if user_key == true_key:
            print(f"\n{luc} [✔] Key Chính Xác! Đang vào tool...{reset}")
            sleep(1)
            break
        elif user_key == "keyvip": 
             print(f"\n{luc} [✔] Chào Admin! Đang vào tool...{reset}")
             sleep(1)
             break
        else:
            print(f"{red} [X] Key Sai! Vui lòng kiểm tra lại IP hoặc Link.{reset}")
            print(f"{den} (Gợi ý: Key hôm nay cho IP {ip} bắt đầu bằng {true_key[:2]}...){reset}\n")

def main_menu():
    show_banner()
    print(f"{luc}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print(f"{luc}┃ {trang}USER: {vang}{os.getlogin()} {luc}| {trang}IP: {vang}{get_ip_public()} {luc}┃")
    print(f"{luc}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")

    print(f"\n{luc} [+] CHỌN TOOL {reset}")
    print(Colorate.Horizontal(Colors.green_to_white, "[01] TOOL VUA THOÁT HIỂM VIP "))
    print(Colorate.Horizontal(Colors.green_to_white, "[02] TOOL VUA TỐC ĐỘ VIP"))
    print(Colorate.Horizontal(Colors.green_to_white, "[03] TOOL CANH CODE "))
    print(Colorate.Horizontal(Colors.green_to_white, "[04] TOOL LOTO "))
    print(Colorate.Horizontal(Colors.green_to_white, "[05] có cái đầu buồi"))
    
print(Colorate.Horizontal(Colors.green_to_white, "[06] có cái đầu buồi"))

print(Colorate.Horizontal(Colors.green_to_white, "[07] có cái đầu buồi "))

login_system()

while True:
    main_menu()
    chon = input(f'\n{luc}root@huytool:~# {trang}Chọn chức năng: {vang}')

    try:
        link_map = {
            "1": "https://raw.githubusercontent.com/nghuy08072011-dotcom/Huyconhuytoolbumx/refs/heads/main/2%20(2).py",
            "2": "https://raw.githubusercontent.com/nghuy08072011-dotcom/Huyconhuytoolbumx/refs/heads/main/1vtd%20(1).py",
            "3": "https://raw.githubusercontent.com/nghuy08072011-dotcom/Huyconhuytoolbumx/refs/heads/main/1code%20(3).py",
            "4": "https://raw.githubusercontent.com/nghuy08072011-dotcom/Huyconhuytoolbumx/refs/heads/main/lotto1.py",
            "5": "",
            "6": "",
            "7": "",
        }

        if chon == "0" or chon == "00":
            print(f"{red}👋 Kết thúc phiên làm việc. Tạm biệt!{reset}")
            break

        if chon in link_map:
            url = link_map[chon]
            print(f"{luc}[PLEASE WAIT] Đang tải dữ liệu tool...{reset}")
            code = requests.get(url).text
            exec(code, globals())
            input(f"\n{vang}Nhấn Enter để quay lại menu chính...{reset}")
        else:
            print(f"{red}❌ Lựa chọn không hợp lệ, vui lòng nhập lại!{reset}")
            sleep(1)

    except Exception as e:
        print(f"{red}Lỗi khi thực thi file: {e}{reset}")
        input(f"{vang}Nhấn Enter để tiếp tục...{reset}")
