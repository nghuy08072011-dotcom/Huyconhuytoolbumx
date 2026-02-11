import subprocess
import sys
import importlib

def install_package(package):
    try:
        importlib.import_module(package)
    except ImportError:
        print(f"Đang cài đặt thư viện thiếu: {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_package('requests')
import requests
import json
import time
import random
import logging
import os
import threading
from datetime import datetime, timedelta

SLEEP_BETWEEN_GAMES = 3 
HISTORY_FILE = "history_log.txt"
CONFIG_FILE = "user_config.json"
REQUIRED_HISTORY_LEN = 2 

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("WinhashPro")

bot_running_flag = True 

def get_vn_time():
    return datetime.utcnow() + timedelta(hours=7)

def safe_float(value):
    try:
        if value is None: return 0.0
        return float(value)
    except:
        return 0.0

def append_history_file(issue_id, result_str, logic_note=""):
    try:
        timestamp = get_vn_time().strftime('%Y-%m-%d %H:%M:%S')
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} | Ván: {issue_id} | KQ: {result_str} | Note: {logic_note}\n")
    except Exception:
        pass

def load_user_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    return None

def save_user_config(user_id, secret_key):
    data = {"user_id": user_id, "user_secret_key": secret_key}
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Lỗi lưu file: {e}")

BET_TYPES = {
    'small': 'Nhỏ (3-9)',
    'big': 'Lớn (12-18)', 
    'draw': 'Hòa (10-11)'
}

BET_IDS = {
    'small': 70309, 
    'big': 71218, 
    'draw': 71011
}

class WinhashBot:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = None
        self.user_secret_key = None
        self.headers = {}
        
        self.asset = 'BUILD'
        
        self.base_amount = 10.0
        self.current_bet_amount = 10.0
        self.logic_mode = 1
        self.fixed_bet_side = 'small'
        
        self.multiplier = 1.0
        self.max_games = 0
        self.stop_loss_limit = 0.0
        self.take_profit_limit = 0.0
        
        self.stats = {
            'win': 0,
            'lose': 0,
            'total_games': 0,
            'start_balance': 0.0,
            'current_balance': 0.0
        }
        
        self.history_data = [] 

    def send_msg(self, text):
        try:
            clean_text = text.replace('`', '').replace('**', '').replace('*', '')
            print(f"\n{clean_text}") 
        except Exception as e:
            print(f"Lỗi in thông báo: {e}")

    def setup_headers(self):
        self.headers = {
            'accept': '*/*',
            'country-code': 'vn',
            'origin': 'https://winhash.io',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'user-id': self.user_id,
            'user-login': 'login_v2',
            'user-secret-key': self.user_secret_key,
            'xb-language': 'vi-VN',
            'cache-control': 'no-cache', 
            'pragma': 'no-cache'
        }

    def get_balance(self, max_retries=5):
        for i in range(max_retries):
            try:
                current_time = int(time.time() * 1000)
                random_salt = random.randint(1, 99999)
                params = {
                    'is_cwallet': '1', 
                    'is_mission_setting': 'true', 
                    'version': '', 
                    'time': str(current_time),
                    '_': str(random_salt)
                }
                header_copy = self.headers.copy()
                header_copy['cache-control'] = 'no-store'
                
                response = self.session.get('https://user.3games.io/user/regist', params=params, headers=header_copy, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('code') == 200:
                        cwallet = data.get('data', {}).get('cwallet', {})
                        if cwallet:
                            build_bal = safe_float(cwallet.get('ctoken_contribute', 0))
                            return {'BUILD': build_bal}
            except Exception:
                time.sleep(1)
        return {'BUILD': 0.0}

    def get_hourly_issue_list(self):
        try:
            params = {'ts': int(time.time()), 'r': random.random()}
            response = self.session.get('https://api.winhash.net/lucky_game/hourly_issue_list', params=params, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    return data.get('data', [])
        except Exception:
            pass 
        return []

    def sync_initial_history(self):
        self.send_msg("⏳ Đang đồng bộ dữ liệu lịch sử...")
        issue_list = self.get_hourly_issue_list()
        count_added = 0
        if issue_list:
            sorted_issues = sorted(issue_list, key=lambda x: x['issue_id'])
            for issue in sorted_issues:
                issue_id = issue.get('issue_id')
                lucky_codes = issue.get('lucky_codes', [])
                if lucky_codes and len(lucky_codes) == 3:
                    total = sum(lucky_codes)
                    res_side = self.get_result_side(total)
                    if not any(x['issue'] == issue_id for x in self.history_data):
                        self.history_data.append({'issue': issue_id, 'result': res_side})
                        count_added += 1
        
        if len(self.history_data) > 30:
            self.history_data = self.history_data[-30:]
            
        self.send_msg(f"✅ Đã đồng bộ {count_added} ván mới. Tổng data phân tích: {len(self.history_data)}")

    def find_current_issue_id(self):
        issue_list = self.get_hourly_issue_list()
        if not issue_list: return None
        current_time = int(time.time())
        
        max_issue_id = 0
        for issue in issue_list:
            iid = issue.get('issue_id', 0)
            if iid > max_issue_id:
                max_issue_id = iid
        
        if max_issue_id > 0:
            return max_issue_id + 1
        return None

    def place_bet_api(self, issue_id, bet_type, amount):
        try:
            item_id = BET_IDS.get(bet_type)
            if not item_id: return False, "Loại cược lỗi"
            
            amt_str = f"{amount:.2f}" if isinstance(amount, float) else str(amount)
            
            payload = {
                "game_id": 1,
                "issue_id": issue_id,
                "items": [{"id": item_id, "amount": amt_str, "asset": self.asset}]
            }
            headers_bet = self.headers.copy()
            headers_bet['request-ts'] = str(int(time.time()))
            
            
            response = self.session.post('https://api.winhash.net/lucky_game/v2/create_order', headers=headers_bet, json=payload, timeout=10)
            data = response.json()
            
            if data.get('code') == 0: 
                return True, "OK"
            else: 
                return False, f"Server trả lỗi: {data.get('msg', 'Unknown Error')}"
        except Exception as e:
            return False, str(e)

    def wait_for_result(self, issue_id):
        start_wait = time.time()
        timeout_seconds = 70 
        while time.time() - start_wait < timeout_seconds:
            try:
                issue_list = self.get_hourly_issue_list()
                if issue_list:
                    for issue in issue_list:
                        if issue.get('issue_id') == issue_id:
                            lucky_codes = issue.get('lucky_codes', [])
                            if lucky_codes and len(lucky_codes) == 3:
                                total = sum(lucky_codes)
                                return total, lucky_codes
            except Exception:
                pass
            time.sleep(2)
        return None, None

    def get_result_side(self, total_score):
        if 3 <= total_score <= 9: return 'small'
        if 12 <= total_score <= 18: return 'big'
        return 'draw'

    def check_win_lose(self, total_score, bets_placed):
        actual_outcome = self.get_result_side(total_score)
        is_win = False
        for bet in bets_placed:
            if bet == actual_outcome:
                is_win = True
        return is_win, actual_outcome

    def analyze_flexible_logic(self):
        if not self.history_data: return 'small'
        
        recent = self.history_data[-20:]
        results = [x['result'] for x in recent]
        if not results: return 'small'
        last_res = results[-1]
        
        streak_count = 0
        for i in range(len(results)-1, -1, -1):
            if results[i] == last_res: streak_count += 1
            else: break
            
        if streak_count >= 4 and last_res in ['small', 'big']: 
            return 'small' if last_res == 'big' else 'big'

        if len(results) >= 3:
            r1, r2, r3 = results[-3], results[-2], results[-1]
            if r1 != r2 and r2 != r3: 
                return 'small' if r3 == 'big' else 'big'

        return last_res if last_res != 'draw' else 'small'

    def select_bets(self):
        if self.logic_mode == 3:
            return [self.fixed_bet_side]
        
        prediction = self.analyze_flexible_logic()
        
        if prediction == 'draw': prediction = 'small'
        
        if self.logic_mode == 1:
            return [prediction, 'draw'] 
        elif self.logic_mode == 2:
            return [prediction]
        return ['small']

    def run_process(self):
        global bot_running_flag
        
        if not self.user_id or not self.user_secret_key:
            self.send_msg("❌ Chưa có User ID/Secret.")
            bot_running_flag = False
            return

        self.setup_headers()
        
        bal = self.get_balance(max_retries=3)
        current_build = bal.get('BUILD', 0.0)
        self.stats['start_balance'] = current_build
        
        msg_start = (
            f"🚀 BẮT ĐẦU CHẠY TOOL\n"
            f"💰 Số dư đầu: `{current_build:.2f}` BUILD\n"
            f"💵 Cược gốc: `{self.base_amount}`\n"
            f"✖️ Nhân vốn: `{self.multiplier}`\n"
            f"🧠 Chế độ: `{self.logic_mode}`\n"
            f"--------------------------------"
        )
        self.send_msg(msg_start)
        
        self.sync_initial_history()
        self.current_bet_amount = self.base_amount

        last_issue_processed = None

        while bot_running_flag:
            try:
                new_bal = self.get_balance(max_retries=1)
                real_current_bal = new_bal.get('BUILD', 0)
                curr_profit = real_current_bal - self.stats['start_balance']
                
                if self.max_games > 0 and self.stats['total_games'] >= self.max_games:
                    self.send_msg(f"🛑 Đã dừng: Đủ {self.max_games} ván.")
                    break
                if self.take_profit_limit > 0 and curr_profit >= self.take_profit_limit:
                    self.send_msg(f"🎉 CHỐT LỜI: +{curr_profit:.2f} BUILD")
                    break
                if self.stop_loss_limit > 0 and curr_profit <= -self.stop_loss_limit:
                    self.send_msg(f"⚠️ CẮT LỖ: -{abs(curr_profit):.2f} BUILD")
                    break

                curr_issue = self.find_current_issue_id()
                if not curr_issue:
                    self.send_msg("⚠️ Không lấy được phiên mới, thử lại...")
                    time.sleep(2)
                    continue
                
                if curr_issue == last_issue_processed:
                    time.sleep(SLEEP_BETWEEN_GAMES)
                    continue

                if len(self.history_data) < REQUIRED_HISTORY_LEN:
                    self.sync_initial_history()
                    if len(self.history_data) == 0:
                        self.send_msg(f"⚠️ Chưa có dữ liệu lịch sử nào, chờ ván {curr_issue}...")
                        total, codes = self.wait_for_result(curr_issue)
                        if total is not None:
                            res = self.get_result_side(total)
                            self.history_data.append({'issue': curr_issue, 'result': res})
                        last_issue_processed = curr_issue
                        continue

                target_bets = self.select_bets()
                bet_names = [BET_TYPES.get(x, x) for x in target_bets]
                
                self.send_msg(f"🆔 {curr_issue}\n👉 Dự đoán: `{', '.join(bet_names)}`\n💵 Vào tiền: `{self.current_bet_amount}`")
                
                placed_ok = False
                msg_err = ""
                for b_type in target_bets:
                    ok, msg = self.place_bet_api(curr_issue, b_type, self.current_bet_amount)
                    if ok: 
                        placed_ok = True
                    else:
                        msg_err = msg
                
                if not placed_ok:
                    self.send_msg(f"❌ Lỗi đặt cược: {msg_err}")
                    if "balance" in str(msg_err).lower() or "insufficient" in str(msg_err).lower():
                        self.send_msg("🛑 Số dư không đủ, dừng tool.")
                        break
                    last_issue_processed = curr_issue
                    continue
                
                last_issue_processed = curr_issue
                self.send_msg("⏳ Đang đợi kết quả mở thưởng...")
                total_score, lucky_codes = self.wait_for_result(curr_issue)
                
                if total_score is not None:
                    is_win, result_side = self.check_win_lose(total_score, target_bets)
                    
                    self.history_data.append({'issue': curr_issue, 'result': result_side})
                    if len(self.history_data) > 60: self.history_data.pop(0)
                    
                    self.stats['total_games'] += 1
                    
                    if is_win:
                        self.stats['win'] += 1
                        result_icon = "✅ WIN"
                        self.current_bet_amount = self.base_amount
                    else:
                        self.stats['lose'] += 1
                        result_icon = "❌ LOSS"
                        self.current_bet_amount = round(self.current_bet_amount * self.multiplier, 2)

                    bal_now = self.get_balance(max_retries=2)
                    real_bal = bal_now.get('BUILD', 0)
                    profit = real_bal - self.stats['start_balance']
                    
                    res_msg = (
                        f"{result_icon} KẾT QUẢ: {total_score} ({BET_TYPES.get(result_side)})\n"
                        f"📊 Thắng/Thua: {self.stats['win']}/{self.stats['lose']}\n"
                        f"💰 Lãi: `{profit:+.2f}` | Dư: `{real_bal:.2f}`"
                    )
                    self.send_msg(res_msg)
                else:
                    self.send_msg("⚠️ Không lấy được kết quả (Time out).")

            except Exception as e:
                self.send_msg(f"⚠️ Lỗi hệ thống: {e}")
                time.sleep(5)
            except KeyboardInterrupt:
                break
        
        bot_running_flag = False
        self.send_msg("🛑 ĐÃ DỪNG HỆ THỐNG")


if __name__ == "__main__":
    print("========================================")
    print("      WINHASH LOTTO TOOL (huyconhuy-TOOL)     ")
    print("========================================")
    
    my_bot = WinhashBot()

    saved_config = load_user_config()
    has_config = False
    
    if saved_config:
        print(f"✅ Tìm thấy cấu hình cũ: UserID {saved_config.get('user_id')}")
        use_old = input("Bạn có muốn dùng lại không? (y/n): ").strip().lower()
        if use_old == 'y':
            my_bot.user_id = saved_config['user_id']
            my_bot.user_secret_key = saved_config['user_secret_key']
            has_config = True
    
    if not has_config:
        print("\nCÀI ĐẶT TÀI KHOẢN")
        link_input = input("Nhập Link (chứa userId & secretKey): ").strip()
        try:
            if 'userId=' in link_input and 'secretKey=' in link_input:
                u_id = link_input.split('userId=')[1].split('&')[0]
                s_key = link_input.split('secretKey=')[1].split('&')[0]
                save_user_config(u_id, s_key)
                my_bot.user_id = u_id
                my_bot.user_secret_key = s_key
                print("✅ Đã lưu cấu hình!")
            else:
                print("❌ Link không hợp lệ! Vui lòng khởi động lại.")
                sys.exit()
        except Exception as e:
            print(f"❌ Lỗi xử lý link: {e}")
            sys.exit()

    print("\nCẤU HÌNH CƯỢC")
    try:
        base_amt = input("Nhập tiền cược gốc (Mặc định 10): ").strip()
        my_bot.base_amount = float(base_amt) if base_amt else 10.0
        
        multi = input("Nhập hệ số nhân khi thua (Mặc định 1.0): ").strip()
        my_bot.multiplier = float(multi) if multi else 1.0
        
        print("Chọn chế độ:")
        print("1: cược 2 cửa")
        print("2: cược 1 cửa")
        print("3: Cố định (Chỉ đánh 1 cửa)")
        mode_inp = input("Nhập số 1, 2 hoặc 3 (Mặc định 1): ").strip()
        my_bot.logic_mode = int(mode_inp) if mode_inp else 1
        
        if my_bot.logic_mode == 3:
            side = input("Nhập cửa cố định (small/big/draw): ").strip().lower()
            if side in ['small', 'big', 'draw']:
                my_bot.fixed_bet_side = side
            else:
                print("Sai tên cửa, về mặc định 'small'")
                my_bot.fixed_bet_side = 'small'
                
        my_bot.current_bet_amount = my_bot.base_amount
        
    except ValueError:
        print("❌ Nhập sai định dạng số! Dùng mặc định.")
    
    print("\n🚀 Đang khởi động... Nhấn Ctrl+C để dừng.")
    try:
        my_bot.run_process()
    except KeyboardInterrupt:
        print("\n🛑 Đã tắt tool.")
