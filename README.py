# Huyconhuytoolbumx
import base64
import json
import os
import platform
import random
import re
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from time import sleep
import subprocess

# --- CẤU HÌNH MÀU SẮC RỰC RỠ ---
def get_random_neon():
    # Trả về các màu neon rực rỡ ngẫu nhiên
    neons = [
        (255, 0, 255),   # Magenta
        (0, 255, 255),   # Cyan
        (0, 255, 127),   # Spring Green
        (255, 255, 0),   # Yellow
        (255, 20, 147),  # Deep Pink
        (138, 43, 226),  # Blue Violet
        (255, 69, 0)     # Orange Red
    ]
    return random.choice(neons)

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    import requests
except ImportError:
    print('__Đang cài đặt các thư viện cần thiết, vui lòng chờ...__')
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "colorama"])
    print('__Cài đặt hoàn tất, vui lòng chạy lại Tool__')
    sys.exit()

proxy_list = []
proxy_rotator = None
# ĐỔI TÊN FILE THEO YÊU CẦU
JOB_HISTORY_FILE = 'HUY_job_history.json'
COOKIE_JOB_LIMIT = 50
CONSECUTIVE_FAILURE_LIMIT = 4

def load_job_history():
    try:
        with open(JOB_HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_job_history(history):
    with open(JOB_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

def has_job_been_done(history, user_id, buff_id):
    return buff_id in history.get(str(user_id), [])

def record_job_done(history, user_id, buff_id):
    user_id_str = str(user_id)
    if user_id_str not in history:
        history[user_id_str] = []
    if buff_id not in history[user_id_str]:
        history[user_id_str].append(buff_id)

class ProxyRotator:
    def __init__(self, proxies: list):
        self.proxies = proxies[:] if proxies else []
        self.i = 0

    def has_proxy(self):
        return bool(self.proxies)

    def current(self):
        if not self.proxies:
            return None
        return self.proxies[self.i % len(self.proxies)]

    def rotate(self):
        if not self.proxies:
            return None
        self.i = (self.i + 1) % len(self.proxies)
        return self.current()

def to_requests_proxies(proxy_str):
    if not proxy_str:
        return None
    p = proxy_str.strip().split(':')
    if len(p) == 4:
        try:
            host, port, user, past = p
            int(port)
        except ValueError:
            user, past, host, port = p
        return {
            'http':  f'http://{user}:{past}@{host}:{port}',
            'https': f'http://{user}:{past}@{host}:{port}',
        }
    if len(p) == 2:
        host, port = p
        return {
            'http':  f'http://{host}:{port}',
            'https': f'http://{host}:{port}',
        }
    return None

def check_proxy_fast(proxy_str):
    try:
        _sess = requests.Session()
        r = _sess.get(
            'http://www.google.com/generate_204',
            proxies=to_requests_proxies(proxy_str),
            timeout=6
        )
        return r.status_code in (204, 200)
    except Exception:
        return False

def get_proxy_info(proxy_str):
    try:
        _sess = requests.Session()
        r = _sess.get(
            'https://api64.ipify.org',
            proxies=to_requests_proxies(proxy_str),
            timeout=10
        )
        if r.status_code == 200:
            return r.text.strip()
    except:
        try:
            _sess = requests.Session()
            r = _sess.get(
                'http://api.ipify.org',
                proxies=to_requests_proxies(proxy_str),
                timeout=10
            )
            if r.status_code == 200:
                return r.text.strip()
        except:
            pass
    return "Unknown"

def check_proxy(proxy):
    session = requests.Session()
    try:
        response = session.post('https://kiemtraip.vn/check-proxy',
            data={'option': 'checkCountry', 'changeTimeout': '5000',
                  'changeUrl': 'http://www.google.com', 'proxies': str(proxy)},
            timeout=10).text
        if '<span class="text-success copy">' in response:
            ip = response.split('<span class="text-success copy">')[1].split()[0].split('</span>')[0]
            return {'status': "success", 'ip': ip}
        else:
            return {'status': "error", 'ip': None}
    except:
        return {'status': "error", 'ip': None}

def add_proxy():
    i = 1
    proxy_list = []
    prints(255, 20, 147, "Nhập Proxy Theo Dạng: username:password:host:port hoặc host:port:username:password")
    prints(0, 255, 255, "Nhấn Enter để bỏ qua và tiếp tục không dùng proxy.")
    while True:
        proxy = input(f'{Fore.LIGHTMAGENTA_EX}Nhập Proxy Số {i}: {Style.RESET_ALL}').strip()
        if proxy == '':
            if i == 1:
                return []
            break
        try:
            check = check_proxy(proxy)
            if check['status'] == "success":
                i += 1
                prints(0,255,0,f'Proxy Hoạt Động: {check["ip"]}')
                proxy_list.append(proxy)
            else:
                prints(255,0,0,'Proxy Die! Vui Lòng Nhập Lại !!!')
        except Exception as e:
            prints(255,0,0,f'Lỗi Kiểm Tra Proxy: {str(e)}')
    return proxy_list

def rotate_proxy():
    global proxy_rotator
    if not proxy_rotator or not proxy_rotator.has_proxy():
        return None

    tried = 0
    prints(255, 215, 0,'🔄 Đang tìm proxy live...')
    while tried < len(proxy_rotator.proxies):
        new_proxy = proxy_rotator.rotate()
        prints(255, 165, 0,f'🔍 Kiểm tra proxy: {new_proxy}')
        if check_proxy_fast(new_proxy):
            proxy_ip = get_proxy_info(new_proxy)
            prints(0,255,127,f'✅ Proxy live: {new_proxy} (IP: {proxy_ip})')
            return new_proxy
        else:
            prints(255,69,0,f'❌ Proxy die: {new_proxy}')
        tried += 1

    prints(255,0,0,'❌ Không tìm thấy proxy live nào!')
    return None

def clear_screen():
    os.system('cls' if platform.system() == "Windows" else 'clear')

# --- BANNER HUYCON MỚI ---
def banner():
    banner_text = r"""
██╗  ██╗██╗   ██╗██╗   ██╗ ██████╗ ██████╗ ███╗   ██╗
██║  ██║██║   ██║╚██╗ ██╔╝██╔════╝██╔═══██╗████╗  ██║
███████║██║   ██║ ╚████╔╝ ██║     ██║   ██║██╔██╗ ██║
██╔══██║██║   ██║  ╚██╔╝  ██║     ██║   ██║██║╚██╗██║
██║  ██║╚██████╔╝   ██║   ╚██████╗╚██████╔╝██║ ╚████║
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
                      HUYCON
"""
    # Bảng màu cầu vồng rực rỡ hơn
    colors = [
        (255, 0, 0),    # Red
        (255, 127, 0),  # Orange
        (255, 255, 0),  # Yellow
        (127, 255, 0),  # Chartreuse
        (0, 255, 0),    # Green
        (0, 255, 127),  # Spring Green
        (0, 255, 255),  # Cyan
        (0, 127, 255),  # Azure
        (0, 0, 255),    # Blue
        (127, 0, 255),  # Violet
        (255, 0, 255),  # Magenta
        (255, 0, 127)   # Rose
    ]

    color_index = 0
    for line in banner_text.split('\n'):
        for char in line:
            if char != ' ':
                r, g, b = colors[color_index % len(colors)]
                prints(r, g, b, char, end='')
                color_index += 1
            else:
                print(' ', end='')
        print() # Xuống dòng

    # Kẻ chân trang banner rực rỡ
    print()
    for i in range(60):
        r, g, b = colors[i % len(colors)]
        prints(r, g, b, "═", end='')
    print()

def decode_base64(encoded_str):
    decoded_bytes = base64.b64decode(encoded_str)
    decoded_str = decoded_bytes.decode('utf-8')
    return decoded_str

def encode_to_base64(_data):
    byte_representation = _data.encode('utf-8')
    base64_bytes = base64.b64encode(byte_representation)
    base64_string = base64_bytes.decode('utf-8')
    return base64_string

def prints(*args, **kwargs):
    r, g, b = 255, 255, 255
    text = "text"
    end = "\n"

    if len(args) == 1:
        text = args[0]
    elif len(args) >= 3:
        r, g, b = args[0], args[1], args[2]
        if len(args) >= 4:
            text = args[3]
    if "text" in kwargs:
        text = kwargs["text"]
    if "end" in kwargs:
        end = kwargs["end"]

    print(f"\033[38;2;{r};{g};{b}m{text}\033[0m", end=end)

def facebook_info(cookie: str, proxy: str = None, timeout: int = 15):
    try:
        session = requests.Session()

        if proxy:
            session.proxies = to_requests_proxies(proxy)

        session_id = str(uuid.uuid4())
        fb_dtsg = ""
        jazoest = ""
        lsd = ""
        name = ""
        user_id = cookie.split("c_user=")[1].split(";")[0]

        headers = {
            "authority": "www.facebook.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "vi",
            "sec-ch-prefers-color-scheme": "light",
            "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/106.0.0.0 Safari/537.36",
            "viewport-width": "1366",
            "Cookie": cookie
        }

        url = session.get(f"https://www.facebook.com/{user_id}", headers=headers, timeout=timeout).url
        response = session.get(url, headers=headers, timeout=timeout).text

        fb_token = re.findall(r'\["DTSGInitialData",\[\],\{"token":"(.*?)"\}', response)
        if fb_token:
            fb_dtsg = fb_token[0]

        jazo = re.findall(r'jazoest=(.*?)\"', response)
        if jazo:
            jazoest = jazo[0]

        lsd_match = re.findall(r'"LSD",\[\],\{"token":"(.*?)"\}', response)
        if lsd_match:
            lsd = lsd_match[0]

        get = session.get("https://www.facebook.com/me", headers=headers, timeout=timeout).url
        url = "https://www.facebook.com/" + get.split("%2F")[-2] + "/" if "next=" in get else get
        response = session.get(url, headers=headers, params={"locale": "vi_VN"}, timeout=timeout)

        data_split = response.text.split('"CurrentUserInitialData",[],{')
        json_data_raw = "{" + data_split[1].split("},")[0] + "}"
        parsed_data = json.loads(json_data_raw)

        user_id = parsed_data.get("USER_ID", "0")
        name = parsed_data.get("NAME", "")

        if user_id == "0" and name == "":
            print("[!] Cookie is invalid or expired.")
            return {'success': False}
        elif "828281030927956" in response.text:
            print("[!] Account is under a 956 checkpoint.")
            return {'success': False}
        elif "1501092823525282" in response.text:
            print("[!] Account is under a 282 checkpoint.")
            return {'success': False}
        elif "601051028565049" in response.text:
            print("[!] Account action is blocked (spam).")
            return {'success': False}

        json_data = {
            'success': True,
            'user_id': user_id,
            'fb_dtsg': fb_dtsg,
            'jazoest': jazoest,
            'lsd': lsd,
            'name': name,
            'session': session,
            'session_id': session_id,
            'cookie': cookie,
            'headers': headers
        }
        return json_data

    except Exception as e:
        print(f"[Facebook.info] Error: {e}")
        return {'success': False}

def get_post_id(session,cookie,link):
    prints(0, 255, 255, f'Đang lấy post id', end='\r')
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'dpr': '1',
        'priority': 'u=0, i',
        'sec-ch-prefers-color-scheme': 'light',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'cookie': cookie,
    }
    try:
        response = session.get(link, headers=headers, timeout=15).text
        response= re.sub(r"\\", "", response)

        page_id=''
        post_id=''
        stories_id=''
        permalink_id=''
        try:
            if '"post_id":"' in str(response):
                permalink_id=re.findall('"post_id":".*?"',response)[0].split(':"')[1].split('"')[0]
                prints(255, 105, 180, f'permalink_id là: {permalink_id[:20]}      ',end='\r')
        except:
            pass
        try:
            if 'posts' in str(response):
                post_id=response.split('posts')[1].split('"')[0]
                post_id=post_id.replace("/", "")
                post_id = re.sub(r"\\", "", post_id)
                prints(255, 105, 180, f'Post id là: {post_id[:20]}        ',end='\r')
        except:
            pass
        try:
            if 'storiesTrayType' in response and not '"profile_type_name_for_content":"PAGE"' in response:
                stories_id=re.findall('"card_id":".*?"',response)[0].split('":"')[1].split('"')[0]
                prints(255, 105, 180, f'stories_id là: {stories_id[:20]}      ',end='\r')
        except:
            pass
        try:
            if '"page_id"' in response:
                page_id=re.findall('"page_id":".*?"',response)[0].split('id":"')[1].split('"')[0]
                prints(255, 105, 180, f'page_id là: {page_id[:20]}         ',end='\r')
        except:
            pass
        return {'success':True,'post_id':post_id,'permalink_id':permalink_id,'stories_id':stories_id,'page_id':page_id}
    except Exception as e:
        print(Fore.RED+f'Lỗi khi lấy ID post: {e}')
        return {'success':False}

def _parse_graphql_response(response):
    try:
        response_json = response.json()
        if 'errors' in response_json:
            error = response_json['errors'][0]
            error_msg = error.get('message', '').lower()

            if 'login required' in error_msg or 'session has expired' in error_msg:
                return {'status': 'cookie_dead', 'message': 'Cookie đã hết hạn hoặc không hợp lệ.'}

            if 'automated' in error_msg or 'tự động' in error_msg:
                 return {'status': 'cookie_dead', 'message': f'Hành vi tự động bị phát hiện: {error.get("message", "Không rõ")}'}

            if 'temporarily blocked' in error_msg or 'spam' in error_msg:
                 return {'status': 'action_failed', 'message': 'Hành động bị chặn vì spam.'}
            if 'permission' in error_msg:
                return {'status': 'action_failed', 'message': 'Không có quyền thực hiện hành động này.'}

            return {'status': 'action_failed', 'message': f"Lỗi từ Facebook: {error.get('message', 'Không rõ')}"}

        if 'data' in response_json and response_json.get('data'):
            if any(v is None for v in response_json['data'].values()):
                 return {'status': 'action_failed', 'message': 'Phản hồi thành công nhưng dữ liệu trả về không hợp lệ.'}
            return {'status': 'success', 'data': response_json['data']}

        return {'status': 'action_failed', 'message': 'Phản hồi không chứa dữ liệu hợp lệ.'}
    except json.JSONDecodeError:
        return {'status': 'action_failed', 'message': 'Lỗi giải mã phản hồi từ Facebook.'}
    except Exception as e:
        return {'status': 'action_failed', 'message': f'Lỗi không xác định khi phân tích phản hồi: {e}'}


def react_post_perm(data,object_id,type_react, proxy=None):
    prints(255, 0, 255, f'Đang thả {type_react} vào {object_id[:20]}        ',end='\r')
    headers = {
        'accept': '*/*', 'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'content-type': 'application/x-www-form-urlencoded', 'origin': 'https://www.facebook.com',
        'priority': 'u=1, i', 'referer': 'https://www.facebook.com/'+str(object_id),
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'x-fb-friendly-name': 'CometUFIFeedbackReactMutation', 'x-fb-lsd': data['lsd'], 'cookie': data['cookie'],
    }
    react_list = {"LIKE": "1635855486666999","LOVE": "1678524932434102","CARE": "613557422527858","HAHA": "115940658764963","WOW": "478547315650144","SAD": "908563459236466","ANGRY": "444813342392137"}
    json_data = {
        'av': str(data['user_id']), '__user': str(data['user_id']), 'fb_dtsg': data['fb_dtsg'],
        'jazoest': str(data['jazoest']), 'lsd': str(data['lsd']), 'fb_api_caller_class': 'RelayModern',
        'fb_api_req_friendly_name': 'CometUFIFeedbackReactMutation',
        'variables': '{"input":{"attribution_id_v2":"CometSinglePostDialogRoot.react,comet.post.single_dialog,via_cold_start,'+str(int(time.time()*1000))+',893597,,,","feedback_id":"'+encode_to_base64(str('feedback:'+object_id))+'","feedback_reaction_id":"'+str(react_list.get(type_react.upper()))+'","feedback_source":"OBJECT","is_tracking_encrypted":true,"tracking":["AZWEqXNx7ELYfHNA7b4CrfdPexzmIf2rUloFtOZ9zOxrcEuXq9Nr8cAdc1kP5DWdKx-DdpkffT5hoGfKYfh0Jm8VlJztxP7elRZBQe5FqkP58YxifFUwdqGzQnJPfhGupHYBjoq5I5zRHXPrEeuJk6lZPblpsrYQTO1aDBDb8UcDpW8F82ROTRSaXpL-T0gnE3GyKCzqqN0x99CSBp1lCZQj8291oXhMoeESvV__sBVqPWiELtFIWvZFioWhqpoAe_Em15uPs4EZgWgQmQ-LfgOMAOUG0TOb6wDVO75_PyQ4b8uTdDWVSEbMPTCglXWn5PJzqqN4iQzyEKVe8sk708ldiDug7SlNS7Bx0LknC7p_ihIfVQqWLQpLYK6h4JWZle-ugySqzonCzb6ay09yrsvupxPUGp-EDKhjyEURONdtNuP-Fl3Oi1emIy61-rqISLQc-jp3vzvnIIk7r_oA1MKT065zyX-syapAs-4xnA_12Un5wQAgwu5sP9UmJ8ycf4h1xBPGDmC4ZkaMWR_moqpx1k2Wy4IbdcHNMvGbkkqu12sgHWWznxVfZzrzonXKLPBVW9Y3tlQImU9KBheHGL_ADG_8D-zj2S9JG2y7OnxiZNVAUb1yGrVVrJFnsWNPISRJJMZEKiYXgTaHVbZBX6CdCrA7gO25-fFBvVfxp2Do3M_YKDc5TtqBeiZgPCKogeTkSQt1B67Kq7FTpBYJ05uEWLpHpk1jYLH8ppQQpSEasmmKKYj9dg7PqbHPMUkeyBtL69_HkdxtVhDgkNzh1JerLPokIkdGkUv0RALcahWQK4nR8RRU2IAFMQEp-FsNk_VKs_mTnZQmlmSnzPDymkbGLc0S1hIlm9FdBTQ59--zU4cJdOGnECzfZq4B5YKxqxs0ijrcY6T-AOn4_UuwioY"],"session_id":"'+data['session_id']+'","actor_id":"'+str(data['user_id'])+'","client_mutation_id":"1"},"useDefaultActor":false,"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider":false}',
        'server_timestamps': 'true', 'doc_id': '24034997962776771',
    }
    try:
        if proxy:
            data['session'].proxies = to_requests_proxies(proxy)
        response = data['session'].post('https://www.facebook.com/api/graphql/', headers=headers, data=json_data, timeout=15)
        response.raise_for_status()
        return _parse_graphql_response(response)
    except requests.exceptions.RequestException as e:
        return {'status': 'action_failed', 'message': f'Lỗi kết nối: {e}'}

def react_post_defaul(data,object_id,type_react, proxy=None):
    prints(255, 0, 255, f'Đang thả {type_react} vào {object_id[:20]}        ',end='\r')
    react_list = {"LIKE": "1635855486666999","LOVE": "1678524932434102","CARE": "613557422527858","HAHA": "115940658764963","WOW": "478547315650144","SAD": "908563459236466","ANGRY": "444813342392137"}
    headers = {
        'accept': '*/*', 'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'content-type': 'application/x-www-form-urlencoded', 'origin': 'https://www.facebook.com',
        'priority': 'u=1, i', 'referer': 'https://www.facebook.com/'+str(object_id),
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'x-fb-friendly-name': 'CometUFIFeedbackReactMutation', 'x-fb-lsd': data['lsd'], 'cookie': data['cookie'],
    }
    json_data = {
        'av': str(data['user_id']), '__user': str(data['user_id']), 'fb_dtsg': data['fb_dtsg'],
        'jazoest': data['jazoest'], 'lsd': data['lsd'], 'fb_api_caller_class': 'RelayModern',
        'fb_api_req_friendly_name': 'CometUFIFeedbackReactMutation',
        'variables': '{"input":{"attribution_id_v2":"CometSinglePostDialogRoot.react,comet.post.single_dialog,via_cold_start,'+str(int(time.time()*1000))+',912367,,,","feedback_id":"'+encode_to_base64(str('feedback:'+object_id))+'","feedback_reaction_id":"'+str(react_list.get(type_react.upper()))+'","feedback_source":"OBJECT","is_tracking_encrypted":true,"tracking":["AZWEqXNx7ELYfHNA7b4CrfdPexzmIf2rUloFtOZ9zOxrcEuXq9Nr8cAdc1kP5DWdKx-DdpkffT5hoGfKYfh0Jm8VlJztxP7elRZBQe5FqkP58YxifFUwdqGzQnJPfhGupHYBjoq5I5zRHXPrEeuJk6lZPblpsrYQTO1aDBDb8UcDpW8F82ROTRSaXpL-T0gnE3GyKCzqqN0x99CSBp1lCZQj8291oXhMoeESvV__sBVqPWiELtFIWvZFioWhqpoAe_Em15uPs4EZgWgQmQ-LfgOMAOUG0TOb6wDVO75_PyQ4b8uTdDWVSEbMPTCglXWn5PJzqqN4iQzyEKVe8sk708ldiDug7SlNS7Bx0LknC7p_ihIfVQqWLQpLYK6h4JWZle-ugySqzonCzb6ay09yrsvupxPUGp-EDKhjyEURONdtNuP-Fl3Oi1emIy61-rqISLQc-jp3vzvnIIk7r_oA1MKT065zyX-syapAs-4xnA_12Un5wQAgwu5sP9UmJ8ycf4h1xBPGDmC4ZkaMWR_moqpx1k2Wy4IbdcHNMvGbkkqu12sgHWWznxVfZzrzonXKLPBVW9Y3tlQImU9KBheHGL_ADG_8D-zj2S9JG2y7OnxiZNVAUb1yGrVVrJFnsWNPISRJJMZEKiYXgTaHVbZBX6CdCrA7gO25-fFBvVfxp2Do3M_YKDc5TtqBeiZgPCKogeTkSQt1B67Kq7FTpBYJ05uEWLpHpk1jYLH8ppQQpSEasmmKKYj9dg7PqbHPMUkeyBtL69_HkdxtVhDgkNzh1JerLPokIkdGkUv0RALcahWQK4nR8RRU2IAFMQEp-FsNk_VKs_mTnZQmlmSnzPDymkbGLc0S1hIlm9FdBTQ59--zU4cJdOGnECzfZq4B5YKxqxs0ijrcY6T-AOn4_UuwioY"],"session_id":"'+str(data['session_id'])+'","actor_id":"'+data['user_id']+'","client_mutation_id":"1"},"useDefaultActor":false,"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider":false}',
        'server_timestamps': 'true', 'doc_id': '24034997962776771',
    }
    try:
        if proxy:
            data['session'].proxies = to_requests_proxies(proxy)
        response = data['session'].post('https://www.facebook.com/api/graphql/', headers=headers, data=json_data, timeout=15)
        response.raise_for_status()
        return _parse_graphql_response(response)
    except requests.exceptions.RequestException as e:
        return {'status': 'action_failed', 'message': f'Lỗi kết nối: {e}'}

def react_stories(data,object_id, proxy=None):
    prints(255, 0, 255, f'Đang tim story {object_id[:20]}       ',end='\r')
    headers = {
        'accept': '*/*', 'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'content-type': 'application/x-www-form-urlencoded', 'origin': 'https://www.facebook.com',
        'priority': 'u=1, i', 'referer': 'https://www.facebook.com/',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'x-fb-friendly-name': 'useStoriesSendReplyMutation', 'x-fb-lsd': data['lsd'], 'cookie': data['cookie']
    }
    json_data = {
        'av': str(data['user_id']), '__user': str(data['user_id']), 'fb_dtsg': data['fb_dtsg'],
        'jazoest': str(data['jazoest']), 'lsd': data['lsd'], 'fb_api_caller_class': 'RelayModern',
        'fb_api_req_friendly_name': 'useStoriesSendReplyMutation',
        'variables': '{"input":{"attribution_id_v2":"StoriesCometSuspenseRoot.react,comet.stories.viewer,via_cold_start,'+str(int(time.time()*1000))+',33592,,,","lightweight_reaction_actions":{"offsets":[0],"reaction":"❤️"},"message":"❤️","story_id":"'+str(object_id)+'","story_reply_type":"LIGHT_WEIGHT","actor_id":"'+str(data['user_id'])+'","client_mutation_id":"2"}}',
        'server_timestamps': 'true', 'doc_id': '9697491553691692',
    }
    try:
        if proxy:
            data['session'].proxies = to_requests_proxies(proxy)
        response = data['session'].post('https://www.facebook.com/api/graphql/',  headers=headers, data=json_data, timeout=15)
        response.raise_for_status()
        return _parse_graphql_response(response)
    except requests.exceptions.RequestException as e:
        return {'status': 'action_failed', 'message': f'Lỗi kết nối: {e}'}

def react_post(data,link,type_react, proxy=None):
    res_object_id=get_post_id(data['session'],data['cookie'],link)
    if not res_object_id.get('success'):
        return {'status': 'action_failed', 'message': 'Không thể lấy ID bài viết.'}

    if res_object_id.get('stories_id'):
        return react_stories(data,res_object_id['stories_id'], proxy)
    elif res_object_id.get('permalink_id'):
        return react_post_perm(data,res_object_id['permalink_id'],type_react, proxy)
    elif res_object_id.get('post_id'):
        return react_post_defaul(data,res_object_id['post_id'],type_react, proxy)

    return {'status': 'action_failed', 'message': 'Không tìm thấy đối tượng hợp lệ để tương tác.'}

def wallet(authorization):
    headers = {
        'User-Agent': 'Dart/3.3 (dart:io)', 'Content-Type': 'application/json',
        'lang': 'en', 'version': '37', 'origin': 'app', 'authorization': authorization,
    }
    try:
        response = requests.get('https://api-v2.bumx.vn/api/business/wallet', headers=headers, timeout=10).json()
        return response.get('data', {}).get('balance', 'N/A')
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    except json.JSONDecodeError:
        return "Error decoding server response"

def load(session,authorization,job):
    prints(255, 255, 0, f'Đang mở nhiệm vụ...',end='\r')
    headers = {
        'User-Agent': 'Dart/3.3 (dart:io)', 'Content-Type': 'application/json',
        'lang': 'en', 'version': '37', 'origin': 'app', 'authorization': authorization,
    }
    json_data = {'buff_id': job['buff_id']}
    try:
        response = session.post('https://api-v2.bumx.vn/api/buff/load-mission', headers=headers, json=json_data, timeout=10).json()
        return response
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        prints(255,0,0,f'Lỗi khi tải thông tin NV')
        return None

def get_job(session, authorization, type_job=None):
    if type_job:
        prints(0, 255, 255, f'Đang lấy nhiệm vụ loại {type_job}...',end='\r')
    else:
        prints(0, 255, 255, f'Đang lấy tất cả nhiệm vụ...',end='\r')

    headers = {
        'User-Agent': 'Dart/3.3 (dart:io)', 'lang': 'en', 'version': '37',
        'origin': 'app', 'authorization': authorization,
    }
    params = {'is_from_mobile': 'true'}

    if type_job:
        params['type'] = type_job

    try:
        response = session.get('https://api-v2.bumx.vn/api/buff/mission', params=params, headers=headers, timeout=10)
        response.raise_for_status()
        response_json = response.json()
    except requests.exceptions.RequestException:
        prints(255,0,0,f'Lỗi khi lấy NV')
        return []
    except json.JSONDecodeError:
        prints(255,0,0,f'Lỗi giải mã JSON khi lấy NV.')
        return []

    job_count = response_json.get('count', 0)
    if type_job:
        prints(Fore.LIGHTMAGENTA_EX+f"Đã tìm thấy {job_count} NV loại {type_job}",end='\r')
    else:
        prints(Fore.LIGHTMAGENTA_EX+f"Đã tìm thấy {job_count} NV (tổng)",end='\r')

    JOB=[]
    for i in response_json.get('data', []):
        json_job={
            "_id":i['_id'], "buff_id":i['buff_id'], "type":i['type'], "name":i['name'],
            "status":i['status'], "object_id":i['object_id'], "business_id":i['business_id'],
            "mission_id":i['mission_id'], "create_date":i['create_date'], "note":i['note'],
            "require":i['require'],
        }
        JOB.insert(0,json_job)
    return JOB

def reload(session, authorization, type_job, retries=3):
    prints(255, 255, 0, f'Đang tải danh sách nhiệm vụ {type_job}...', end='\r')
    if retries == 0:
        prints(255, 0, 0, f'Tải danh sách NV {type_job} thất bại. Bỏ qua.')
        return
    headers = {
        'User-Agent': 'Dart/3.3 (dart:io)', 'Content-Type': 'application/json',
        'lang': 'en', 'version': '37', 'origin': 'app', 'authorization': authorization,
    }
    json_data = {'type': type_job}
    try:
        response = session.post('https://api-v2.bumx.vn/api/buff/get-new-mission', headers=headers, json=json_data, timeout=10).json()
    except Exception:
        prints(255, 0, 0, f'Lỗi khi tải lại NV. Thử lại trong 2s...')
        time.sleep(2)
        return reload(session, authorization, type_job, retries - 1)

def submit(session,authorization,job,reslamjob,res_load):
    prints(0, 255, 127, f'Đang nhấn hoàn thành nhiệm vụ',end='\r')
    headers = {
        'User-Agent': 'Dart/3.3 (dart:io)', 'Content-Type': 'application/json',
        'lang': 'en', 'version': '37', 'origin': 'app', 'authorization': authorization,
    }
    json_data = {
        'buff_id': job['buff_id'], 'comment': None, 'comment_id': None, 'code_submit': None,
        'attachments': [], 'link_share': '', 'code': '', 'is_from_mobile': True,
        'type': job['type'], 'sub_id': None, 'data': None,
    }
    if job['type']=='like_facebook':
        json_data['comment'] = 'tt nha'

    try:
        response = session.post('https://api-v2.bumx.vn/api/buff/submit-mission', headers=headers, json=json_data, timeout=10).json()
        if response.get('success') == True:
            message = response.get('message', '')
            _xu = '0'
            sonvdalam = '0'
            try:
                _xu = message.split('cộng ')[1].split(',')[0]
                sonvdalam = message.split('làm: ')[1]
            except IndexError:
                pass
            return [True,_xu,sonvdalam]
        return [False,'0','0']
    except Exception:
        prints(255,0,0,f'Lỗi khi submit')
        return [False,'0','0']

def report(session, authorization, job, retries=3):
    prints(255, 69, 0, f'Đang báo lỗi...', end='\r')
    if retries == 0:
        prints(255, 0, 0, f'Báo lỗi thất bại sau nhiều lần thử. Bỏ qua...')
        return
    headers = {
        'User-Agent': 'Dart/3.3 (dart:io)', 'Content-Type': 'application/json',
        'lang': 'en', 'version': '37', 'origin': 'app', 'authorization': authorization,
    }
    json_data = {'buff_id': job['buff_id']}
    try:
        response = session.post('https://api-v2.bumx.vn/api/buff/report-buff', headers=headers, json=json_data, timeout=10).json()
        prints(255, 140, 0, 'Đã báo lỗi thành công và bỏ qua NV.')
    except Exception:
        prints(255, 140, 0, f'Báo lỗi không thành công, thử lại... ({retries-1} lần còn lại)')
        time.sleep(2)
        return report(session, authorization, job, retries - 1)

def lam_job(data, jobs, type_job_doing, current_proxy=None):
    prints(255, 255, 0, f'Đang làm NV...', end='\r')
    link = 'https://www.facebook.com/' + jobs['object_id']

    result = {'status': 'action_failed', 'message': 'Hành động không xác định'}

    if type_job_doing == 'like_facebook':
        react_type = 'LIKE'
        icon = jobs.get('icon', '').lower()
        if 'love' in icon or 'thuongthuong' in icon: react_type = 'LOVE'
        elif 'care' in icon: react_type = 'CARE'
        elif 'wow' in icon: react_type = 'WOW'
        elif 'sad' in icon: react_type = 'SAD'
        elif 'angry' in icon: react_type = 'ANGRY'
        elif 'haha' in icon: react_type = 'HAHA'

        react_result = react_post(data, link, react_type.upper(), current_proxy)
        if react_result['status'] == 'success':
            prints(0, 255, 255, f'Đã thả {react_type}, chờ 10 giây...')
            time.sleep(10)
        return react_result

    return result

def countdown(seconds):
    seconds = int(seconds)
    if seconds < 1: return
    for i in range(seconds, 0, -1):
        r1, g1, b1 = get_random_neon()
        r2, g2, b2 = get_random_neon()
        prints(r1, g1, b1, '[', end='')
        prints(0, 255, 127, "HUYCON", end='')
        prints(r1, g1, b1, ']', end='')
        prints(255, 255, 255, '[', end='')
        prints(255, 215, 0, "WAIT", end='')
        prints(255, 255, 255, ']', end='')
        prints(255, 20, 147, ' ➤ ', end='')
        prints(r2, g2, b2, f"⏳ {i}s...", end='\r')
        time.sleep(1)
    print(' ' * 50, end='\r')

def add_account_fb(session,authorization,user_id):
    headers = {
        'Content-Type': 'application/json', 'lang': 'en', 'version': '37',
        'origin': 'app', 'authorization': authorization,
    }
    json_data = {'link': f'https://www.facebook.com/profile.php?id={str(user_id)}'}
    try:
        response = session.post('https://api-v2.bumx.vn/api/account-facebook/connect-link', headers=headers, json=json_data, timeout=10).json()
        prints(0, 255, 255, f"Khai báo tài khoản FB: {response.get('message', 'No message')}")
    except Exception as e:
        prints(255,0,0,f"Lỗi khai báo tài khoản FB: {e}")

def rgb(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

def print_state(status_job,_xu,jobdalam,dahoanthanh,tongcanhoanthanh,type_job, name_acc, bumx_acc_num):
    hanoi_tz = timezone(timedelta(hours=7))
    now = datetime.now(hanoi_tz).strftime("%H:%M:%S")
    type_NV = {'like_facebook':'CAMXUC'}

    status_color = rgb(57, 255, 20,status_job.upper()) if status_job.lower()=='complete' else rgb(255,255,0,status_job.upper())

    # Màu sắc rực rỡ hơn cho từng thành phần
    print(f"[{rgb(255, 20, 147, f'BUMX-{bumx_acc_num}')}]"
          f"[{rgb(0, 255, 255, name_acc)}]"
          f"[{rgb(255, 255, 0, now)}]"
          f"[{rgb(255, 165, 0, dahoanthanh)}/{rgb(255, 165, 0, tongcanhoanthanh)}]"
          f"[{rgb(138, 43, 226, type_NV.get(type_job, 'UNKNOWN'))}]"
          f"[{status_color}]"
          f"[{rgb(0, 255, 0, '+'+_xu.strip())}]"
          f"[{rgb(255, 105, 180, 'Done:'+jobdalam.strip())}]")

def switch_facebook_account(cookie, authorization, bumx_session, proxy=None):
    prints(0, 255, 255, "\n--- Chuyển đổi tài khoản Facebook ---")
    data = facebook_info(cookie, proxy)
    if not data or not data.get('success'):
        prints(255, 0, 0, 'Cookie không hợp lệ. Bỏ qua tài khoản này.')
        return None

    prints(50, 205, 50, f"Đang sử dụng tài khoản: {data['name']} ({data['user_id']})")
    add_account_fb(bumx_session, authorization, data['user_id'])
    return data

def main_bumx_free():
    global proxy_list, proxy_rotator

    banner()

    proxy_list = []
    proxy_rotator = None

    # ĐỔI TÊN FILE PROXY
    if os.path.exists('HUY-proxy-vip.json'):
        prints(66, 245, 245,'Phát hiện file proxy đã lưu.')
        x=input(Fore.LIGHTMAGENTA_EX+'Bạn có muốn dùng lại proxy đã lưu không? (y/n): ')
        if x.lower()=='y':
            try:
                with open('HUY-proxy-vip.json', 'r') as f:
                    proxy_list = json.load(f)
                proxy_rotator = ProxyRotator(proxy_list)
                prints(0,255,0,f'Đã tải {len(proxy_list)} proxy từ file.')
            except:
                prints(255,0,0,'Lỗi đọc file proxy, sẽ nhập mới.')
                proxy_list = add_proxy()
                proxy_rotator = ProxyRotator(proxy_list)
                if proxy_list:
                    with open('HUY-proxy-vip.json', 'w') as f:
                        json.dump(proxy_list, f)
        else:
            proxy_list = add_proxy()
            proxy_rotator = ProxyRotator(proxy_list)
            if proxy_list:
                with open('HUY-proxy-vip.json', 'w') as f:
                    json.dump(proxy_list, f)
    else:
        prints(66, 245, 245,'Chưa có file proxy, sẽ nhập mới.')
        proxy_list = add_proxy()
        proxy_rotator = ProxyRotator(proxy_list)
        if proxy_list:
            with open('HUY-proxy-vip.json', 'w') as f:
                json.dump(proxy_list, f)

    num_bumx_accounts = int(input(Fore.LIGHTCYAN_EX + 'Nhập số lượng tài khoản Bumx muốn chạy: '))
    authorizations_list = []
    for i in range(num_bumx_accounts):
        # ĐỔI TÊN FILE AUTH
        auth_file = f'HUY-auth-bumx-{i+1}.txt'
        authorization = ''
        if os.path.exists(auth_file):
            x = input(Fore.LIGHTYELLOW_EX + f'Bạn có muốn dùng lại authorization Bumx đã lưu trong file {auth_file} không (y/n): ').lower()
            if x == 'y':
                with open(auth_file, 'r', encoding='utf-8') as f:
                    authorization = f.read().strip()
            else:
                authorization = input(Fore.LIGHTWHITE_EX + f'Nhập authorization Bumx thứ {i+1} của Bạn: ').strip()
                with open(auth_file, 'w', encoding='utf-8') as f:
                    f.write(authorization)
                prints(5, 255, 0, f'Đã lưu authorization vào {auth_file}')
        else:
            authorization = input(Fore.LIGHTWHITE_EX + f'Nhập authorization Bumx thứ {i+1} của Bạn: ').strip()
            with open(auth_file, 'w', encoding='utf-8') as f:
                f.write(authorization)
            prints(5, 255, 0, f'Đã lưu authorization vào {auth_file}')
        if authorization:
            authorizations_list.append(authorization)

    if not authorizations_list:
        prints(255,0,0, "Không có authorization Bumx nào được nhập. Dừng tool.")
        sys.exit(1)

    bumx_switch_threshold = int(input(Fore.LIGHTCYAN_EX + 'Sau bao nhiêu nhiệm vụ thì đổi tài khoản Bumx: '))

    bumx_session = requests.Session()

    num_cookies = int(input(Fore.LIGHTCYAN_EX + 'Nhập số lượng cookie Facebook muốn chạy: '))
    cookies_list = []
    for i in range(num_cookies):
        # ĐỔI TÊN FILE COOKIE
        cookie_file = f'HUY-cookie-fb-bumx-{i+1}.txt'
        cookie = ''
        if os.path.exists(cookie_file):
            x = input(Fore.LIGHTYELLOW_EX + f'Bạn có muốn dùng lại cookie FB đã lưu trong file {cookie_file} không (y/n): ').lower()
            if x == 'y':
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    cookie = f.read().strip()
            else:
                cookie = input(Fore.LIGHTCYAN_EX + f'Nhập cookie FB thứ {i+1} của Bạn: ').strip()
                with open(cookie_file, 'w', encoding='utf-8') as f:
                    f.write(cookie)
                prints(5, 255, 0, f'Đã lưu cookie vào {cookie_file}')
        else:
            cookie = input(Fore.LIGHTCYAN_EX + f'Nhập cookie FB thứ {i+1} của Bạn: ').strip()
            with open(cookie_file, 'w', encoding='utf-8') as f:
                f.write(cookie)
            prints(5, 255, 0, f'Đã lưu cookie vào {cookie_file}')
        if cookie:
            cookies_list.append(cookie)

    if not cookies_list:
        prints(255,0,0, "Không có cookie nào được nhập. Dừng tool.")
        sys.exit(1)

    prints(255, 215, 0, f"Cơ chế đổi cookie FB: sau {COOKIE_JOB_LIMIT} jobs hoặc {CONSECUTIVE_FAILURE_LIMIT} lỗi liên tiếp.")

    list_type_job = ['like_facebook']
    prints(0, 255, 127, "Đã cấu hình tool chỉ chạy nhiệm vụ 'Thả cảm xúc' (like_facebook).")

    SO_NV=int(input(Fore.LIGHTMAGENTA_EX + 'Làm bao nhiêu NV thì dừng: '))
    total_completed_tasks=0
    demsk=0

    job_history = load_job_history()

    current_cookie_index = 0
    tasks_on_current_cookie = 0
    consecutive_failures = 0
    valid_cookies = []

    current_auth_index = 0
    tasks_on_current_auth = 0
    authorization = authorizations_list[current_auth_index]
    prints(50, 205, 50, f'Bắt đầu với tài khoản Bumx-1. Số dư: {wallet(authorization)}')

    current_proxy = proxy_rotator.current() if proxy_rotator else None

    if current_proxy and not check_proxy_fast(current_proxy):
        prints(255,255,0,'❌ Proxy ban đầu bị lỗi, đang tìm proxy khác...')
        current_proxy = rotate_proxy()

    if current_proxy:
        proxy_ip = get_proxy_info(current_proxy)
        prints(0,255,255,f'🔗 Đang sử dụng proxy để kiểm tra cookie: {current_proxy}')
        prints(0,255,255,f'🌐 IP public: {proxy_ip}')
    else:
        prints(255,255,0,'⚠️  Không sử dụng proxy')

    for ck in cookies_list:
        info = facebook_info(ck, current_proxy)
        if info and info.get('success'):
            valid_cookies.append(ck)
        else:
            prints(255, 165, 0, f"Cookie ...{ck[-20:]} không hợp lệ, sẽ được bỏ qua.")

    if not valid_cookies:
        prints(255,0,0,"Không có cookie nào hợp lệ. Vui lòng kiểm tra lại.")
        sys.exit(1)

    data = switch_facebook_account(valid_cookies[current_cookie_index], authorization, bumx_session, current_proxy)
    if not data:
        prints(255,0,0,"Cookie đầu tiên không hợp lệ. Không thể bắt đầu.")
        sys.exit(1)

    clear_screen()
    banner()

    all_available_jobs = []

    while total_completed_tasks < SO_NV:
        try:
            if current_proxy and not check_proxy_fast(current_proxy):
                prints(255,0,255,'❌ Proxy hiện tại chết, đang xoay sang proxy khác...')
                current_proxy = rotate_proxy()
                if current_proxy:
                    proxy_ip = get_proxy_info(current_proxy)
                    prints(0,255,255,f'✅ Đã chuyển sang proxy mới: {current_proxy} (IP: {proxy_ip})')
                else:
                    prints(255,0,0,'❌ Không còn proxy live, tiếp tục không proxy.')
                    current_proxy = None

            if tasks_on_current_auth >= bumx_switch_threshold and len(authorizations_list) > 1:
                current_auth_index = (current_auth_index + 1) % len(authorizations_list)
                authorization = authorizations_list[current_auth_index]
                tasks_on_current_auth = 0
                prints(0, 255, 255, f"\n--- Chuyển đổi sang tài khoản Bumx thứ {current_auth_index + 1} ---")
                prints(5,255,0,f'Số dư tài khoản mới: {wallet(authorization)}')
                add_account_fb(bumx_session, authorization, data['user_id'])

            if (tasks_on_current_cookie >= COOKIE_JOB_LIMIT or consecutive_failures >= CONSECUTIVE_FAILURE_LIMIT) and len(valid_cookies) > 1:
                if tasks_on_current_cookie >= COOKIE_JOB_LIMIT:
                    prints(255, 255, 0, f"Đã đạt giới hạn {COOKIE_JOB_LIMIT} jobs. Chuyển đổi cookie...")
                if consecutive_failures >= CONSECUTIVE_FAILURE_LIMIT:
                    prints(255, 0, 0, f"Đã đạt giới hạn {CONSECUTIVE_FAILURE_LIMIT} lỗi liên tiếp. Chuyển đổi cookie...")

                current_cookie_index = (current_cookie_index + 1) % len(valid_cookies)
                new_data = switch_facebook_account(valid_cookies[current_cookie_index], authorization, bumx_session, current_proxy)

                if new_data:
                    data = new_data
                    tasks_on_current_cookie = 0
                    consecutive_failures = 0
                else:
                    prints(255, 0, 0, f"Lỗi với cookie thứ {current_cookie_index+1}, loại bỏ khỏi danh sách chạy lần này.")
                    valid_cookies.pop(current_cookie_index)
                    if not valid_cookies:
                        prints(255,0,0,"Tất cả cookie đều lỗi. Dừng tool.")

                        if all_available_jobs:
                            prints(255, 165, 0, f"Đang báo lỗi {len(all_available_jobs)} nhiệm vụ còn lại do hết cookie...")
                            for remaining_job in all_available_jobs:
                                report(bumx_session, authorization, remaining_job)
                                time.sleep(0.5)

                        break
                    current_cookie_index = current_cookie_index % len(valid_cookies)
                    data = switch_facebook_account(valid_cookies[current_cookie_index], authorization, bumx_session, current_proxy)
                    tasks_on_current_cookie = 0
                    consecutive_failures = 0

            if not all_available_jobs:
                prints(0, 255, 255, "\n--- Danh sách nhiệm vụ trống, đang tải danh sách mới ---")
                for type_job in list_type_job:
                    reload(bumx_session, authorization, type_job)
                    time.sleep(2)
                    new_jobs = get_job(bumx_session, authorization, type_job)
                    if new_jobs:
                        prints(0, 255, 0, f"Đã tìm thấy {len(new_jobs)} nhiệm vụ loại {type_job}.")
                        all_available_jobs.extend(new_jobs)
                    else:
                        prints(255, 215, 0, f"Không có nhiệm vụ mới cho loại {type_job}.")

                if not all_available_jobs:
                    prints(255, 0, 0, "Không tìm thấy bất kỳ nhiệm vụ nào. Chờ 60 giây trước khi thử lại...")
                    countdown(60)
                    continue
            job = all_available_jobs.pop(0)

            if has_job_been_done(job_history, data['user_id'], job['buff_id']):
                prints(128, 128, 128, f"Nhiệm vụ {job['buff_id']} đã được làm bởi tài khoản này, báo lỗi và bỏ qua.")
                report(bumx_session, authorization, job)
                demsk += 1
                continue

            try:
                res_load = load(bumx_session, authorization, job)
                time.sleep(random.randint(2, 4))

                if not (res_load and res_load.get('success')):
                    raise Exception("Load nhiệm vụ thất bại")

                job_result = lam_job(data, res_load, job['type'], current_proxy)

                if job_result['status'] == 'success':
                    res_submit = submit(bumx_session, authorization, job, job_result.get('payload'), res_load)
                    if res_submit[0]:
                        total_completed_tasks += 1
                        tasks_on_current_cookie += 1
                        tasks_on_current_auth += 1
                        consecutive_failures = 0

                        record_job_done(job_history, data['user_id'], job['buff_id'])
                        save_job_history(job_history)

                        print_state('complete', res_submit[1], res_submit[2], total_completed_tasks, SO_NV, job['type'], data['name'], current_auth_index + 1)

                        post_submit_delay = random.randint(5, 15)
                        countdown(post_submit_delay)
                    else:
                        raise Exception("Submit nhiệm vụ thất bại")

                elif job_result['status'] == 'cookie_dead':
                    prints(255, 0, 0, f"COOKIE DIE: {job_result.get('message', '')}. Báo lỗi và buộc chuyển cookie.")
                    report(bumx_session, authorization, job)
                    demsk += 1
                    consecutive_failures = CONSECUTIVE_FAILURE_LIMIT
                else:
                    prints(255, 165, 0, f"Hành động thất bại ({job_result['status']}): {job_result.get('message', '')}")

                    report(bumx_session, authorization, job)
                    demsk += 1
                    consecutive_failures += 1
                    time.sleep(3)

            except Exception as e:
                prints(255, 165, 0, f"NV lỗi, báo cáo và bỏ qua: {e}")
                report(bumx_session, authorization, job)
                demsk += 1
                consecutive_failures += 1
                time.sleep(4)

        except KeyboardInterrupt:
            prints(255,255,0, "\nĐã dừng bởi người dùng.")

            if all_available_jobs:
                prints(255, 165, 0, f"Đang báo lỗi {len(all_available_jobs)} nhiệm vụ còn lại do người dùng dừng...")
                for remaining_job in all_available_jobs:
                    report(bumx_session, authorization, remaining_job)
                    time.sleep(0.5)

            break
        except Exception as e:
            prints(255,0,0,f'Lỗi vòng lặp chính: {e}')
            time.sleep(10)

    prints(0,255,0,f'\n--- HOÀN THÀNH ---')
    prints(0,255,127,f'Số nhiệm vụ đã hoàn thành: {total_completed_tasks}')
    prints(255,69,0,f'Số nhiệm vụ đã bỏ qua/lỗi: {demsk}')
    prints(0,255,255,f'Tổng: {demsk+total_completed_tasks}')


if __name__ == "__main__":
    try:
        print(f"\nBắt đầu chạy tool chính...")
        time.sleep(2)
        main_bumx_free()
    except Exception as e:
        print(f"\nTool đang bị lỗi, xin chờ...")
        # ĐỔI TÊN FILE LOG
        with open("HUY_error_log.txt", "a", encoding='utf-8') as f:
            f.write(f"{datetime.now()}: {str(e)}\n")
        time.sleep(3)
        sys.exit()
