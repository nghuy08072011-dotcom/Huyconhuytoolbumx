import hashlib
from collections import Counter
import statistics
import platform
from datetime import datetime
import requests
import random
import math
import json
import os
import time
import sys
from colorama import Fore, Style, init, Back

# Khởi tạo màu sắc
init(autoreset=True)

# --- CẤU HÌNH UI/UX ---
class Colors:
    RED = Fore.RED + Style.BRIGHT
    GREEN = Fore.GREEN + Style.BRIGHT
    YELLOW = Fore.YELLOW + Style.BRIGHT
    BLUE = Fore.BLUE + Style.BRIGHT
    CYAN = Fore.CYAN + Style.BRIGHT
    MAGENTA = Fore.MAGENTA + Style.BRIGHT
    WHITE = Fore.WHITE + Style.BRIGHT
    RESET = Style.RESET_ALL
    BG_RED = Back.RED + Fore.WHITE + Style.BRIGHT
    BG_GREEN = Back.GREEN + Fore.BLACK + Style.BRIGHT
    BG_BLUE = Back.BLUE + Fore.WHITE + Style.BRIGHT

NV = {
    1: 'Bậc thầy tấn công',
    2: 'Quyền sắt',
    3: 'Thợ lặn sâu',
    4: 'Cơn lốc sân cỏ',
    5: 'Hiệp sĩ phi nhanh',
    6: 'Vua home run'
}

# --- UI HELPER FUNCTIONS ---
def clear_screen():
    os.system('cls' if platform.system() == "Windows" else 'clear')

def print_timestamp(text, color=Colors.WHITE):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"{Colors.MAGENTA}[{now}] {color}{text}")

def banner_omega():
    clear_screen()
    logo = """
██╗  ██╗██╗   ██╗██╗   ██╗ ██████╗ ██████╗ ███╗   ██╗
██║  ██║██║   ██║╚██╗ ██╔╝██╔════╝██╔═══██╗████╗  ██║
███████║██║   ██║ ╚████╔╝ ██║     ██║   ██║██╔██╗ ██║
██╔══██║██║   ██║  ╚██╔╝  ██║     ██║   ██║██║╚██╗██║
██║  ██║╚██████╔╝   ██║   ╚██████╗╚██████╔╝██║ ╚████║
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
    """
    print(Colors.CYAN + logo)
    print(Colors.BG_BLUE + f" 🌌 HUYCON OMEGA CORE - QUANTUM PREDICTION V7 🌌 ".center(60))
    print(Colors.WHITE + "Admin: ".ljust(10) + Colors.GREEN + "HUYCONHUY")
    print(Colors.CYAN + "═" * 60)

# --- CORE LOGIC: HUYCON_OMEGA_CORE ---
class HuyCon_Omega_Core:
    def __init__(self, history, rooms, lose_streak, ai_weights=None):
        self.history = history
        self.rooms = rooms
        self.lose_streak = lose_streak
        self.ai_weights = ai_weights if ai_weights else {f"block_{i}": 1.0 for i in range(1, 41)}
        self.scores = {r: 0.0 for r in rooms}
        self.last = history[0] if history else 0
        self.len_h = len(history)
        self.mean = statistics.mean(history) if history else 3.5
        self.stdev = statistics.stdev(history) if len(history) > 1 else 1.0
        self.mod_base = 6 

    def apply_weight(self, block_id, score_dict):
        w = self.ai_weights.get(f"block_{block_id}", 1.0)
        for r in self.rooms:
            self.scores[r] += (score_dict.get(r, 0) * w)

    def run_4000_logics(self):
        # KHỐI 1-10: TOÁN HỌC
        self._exec_block(1, self._run_block_01_frequency)
        self._exec_block(2, self._run_block_02_gap)
        self._exec_block(3, self._run_block_03_modulo)
        self._exec_block(4, self._run_block_04_geometry)
        self._exec_block(5, self._run_block_05_primes)
        self._exec_block(6, self._run_block_06_fibonacci)
        self._exec_block(7, self._run_block_07_vectors)
        self._exec_block(8, self._run_block_08_symmetry)
        self._exec_block(9, self._run_block_09_golden_ratio)
        self._exec_block(10, self._run_block_10_matrix)
        # KHỐI 11-20: XÁC SUẤT
        self._exec_block(11, self._run_block_11_poisson)
        self._exec_block(12, self._run_block_12_gaussian)
        self._exec_block(13, self._run_block_13_binomial)
        self._exec_block(14, self._run_block_14_bayesian)
        self._exec_block(15, self._run_block_15_markov)
        self._exec_block(16, self._run_block_16_variance)
        self._exec_block(17, self._run_block_17_standard_error)
        self._exec_block(18, self._run_block_18_correlation)
        self._exec_block(19, self._run_block_19_monte_carlo)
        self._exec_block(20, self._run_block_20_entropy_info)
        # KHỐI 21-30: VẬT LÝ
        self._exec_block(21, self._run_block_21_gravity)
        self._exec_block(22, self._run_block_22_magnetism)
        self._exec_block(23, self._run_block_23_velocity)
        self._exec_block(24, self._run_block_24_acceleration)
        self._exec_block(25, self._run_block_25_oscillation)
        self._exec_block(26, self._run_block_26_waves)
        self._exec_block(27, self._run_block_27_optics)
        self._exec_block(28, self._run_block_28_quantum_spin)
        self._exec_block(29, self._run_block_29_string_theory)
        self._exec_block(30, self._run_block_30_relativity)
        # KHỐI 31-40: AI & CHAOS
        self._exec_block(31, self._run_block_31_hash_chaos)
        self._exec_block(32, self._run_block_32_neural_weights)
        self._exec_block(33, self._run_block_33_genetic_cross)
        self._exec_block(34, self._run_block_34_genetic_mut)
        self._exec_block(35, self._run_block_35_game_theory)
        self._exec_block(36, self._run_block_36_pattern_match)
        self._exec_block(37, self._run_block_37_linear_reg)
        self._exec_block(38, self._run_block_38_polynomial)
        self._exec_block(39, self._run_block_39_fractals)
        self._exec_block(40, self._run_block_40_final_consensus)
        return self.scores

    def _exec_block(self, block_id, func):
        temp_scores = {r: 0.0 for r in self.rooms}
        original_scores = self.scores.copy()
        self.scores = temp_scores
        func()
        w = self.ai_weights.get(f"block_{block_id}", 1.0)
        for r in self.rooms:
            original_scores[r] += (temp_scores[r] * w)
        self.scores = original_scores

    # --- CÁC HÀM XỬ LÝ (GIỮ NGUYÊN) ---
    def _run_block_01_frequency(self):
        for i in range(1, 51):
            w = i * 10
            for r in self.rooms: self.scores[r] -= (self.history.count(r) * w)
    def _run_block_02_gap(self):
        for i in range(1, 51):
            target_gap = i % 10
            for r in self.rooms:
                if r not in self.history[:target_gap]: self.scores[r] += (i * 5)
    def _run_block_03_modulo(self):
        for i in range(1, 51):
            mod_val = (i % 5) + 2
            for r in self.rooms:
                if (r % mod_val) == (self.last % mod_val): self.scores[r] -= (i * 8)
    def _run_block_04_geometry(self):
        for i in range(1, 51):
            for r in self.rooms:
                if abs(r - self.last) == 3: self.scores[r] -= (i * 15)
    def _run_block_05_primes(self):
        primes = [2,3,5]
        for i in range(1, 51):
            for r in self.rooms:
                if r in primes: self.scores[r] += (i * 2)
                else: self.scores[r] -= (i * 2)
    def _run_block_06_fibonacci(self):
        fib = [1, 1, 2, 3, 5, 8]
        for i in range(1, 51):
            step = fib[i % 6]
            bad = (self.last + step - 1) % self.mod_base + 1
            for r in self.rooms:
                if r == bad: self.scores[r] -= (i * 10)
    def _run_block_07_vectors(self):
        for i in range(1, 51):
            vec = self.last - (self.history[1] if len(self.history)>1 else 0)
            pred = (self.last + vec) % self.mod_base + 1
            for r in self.rooms:
                if r == pred: self.scores[r] -= (i * 5)
    def _run_block_08_symmetry(self):
        for i in range(1, 51):
            axis = (self.last + i) % self.mod_base + 1
            for r in self.rooms:
                if r == axis: self.scores[r] -= (i * 3)
    def _run_block_09_golden_ratio(self):
        phi = 1.618
        for i in range(1, 51):
            target = int((self.last * phi * i)) % self.mod_base + 1
            for r in self.rooms:
                if abs(r - target) < 1: self.scores[r] -= (i * 4)
    def _run_block_10_matrix(self):
        for i in range(1, 51):
            trans = (self.last * i + 7) % self.mod_base + 1
            for r in self.rooms:
                if r == trans: self.scores[r] -= (i * 2)
    def _run_block_11_poisson(self):
        for i in range(1, 51):
            lamda = 1 + (i/20)
            for r in self.rooms:
                k = self.history.count(r)
                p = (lamda**k * math.exp(-lamda))/math.factorial(k)
                if p < 0.1: self.scores[r] += (i*5)
    def _run_block_12_gaussian(self):
        for i in range(1, 51):
            thresh = 1 + (i/50)
            for r in self.rooms:
                if self.stdev == 0: continue
                z = (r - self.mean)/self.stdev
                if abs(z) > thresh: self.scores[r] -= (i*3)
    def _run_block_13_binomial(self):
        for i in range(1, 51):
            for r in self.rooms:
                if (r%2) == (self.last%2): self.scores[r] -= (i*2)
    def _run_block_14_bayesian(self):
        for i in range(1, 51):
            for r in self.rooms: self.scores[r] += (random.random() * i)
    def _run_block_15_markov(self):
        for i in range(1, 51):
            if len(self.history) > 2 and self.history[0] == self.history[1]:
                for r in self.rooms:
                     if r == self.history[0]: self.scores[r] -= (i * 20)
    def _run_block_16_variance(self):
        for i in range(1, 51):
            for r in self.rooms:
                if abs(r - self.mean) > 2: self.scores[r] += (i * 2)
    def _run_block_17_standard_error(self):
         for i in range(1, 51):
            for r in self.rooms: self.scores[r] += i
    def _run_block_18_correlation(self):
         for i in range(1, 51):
            lag = (i % 3) + 1
            if len(self.history) > lag:
                lag_val = self.history[lag]
                for r in self.rooms:
                    if r == lag_val: self.scores[r] -= (i * 4)
    def _run_block_19_monte_carlo(self):
        seed = int(time.time())
        for i in range(1, 51):
            random.seed(seed + i)
            sim = random.randint(1, 6)
            for r in self.rooms:
                if r == sim: self.scores[r] += 100
    def _run_block_20_entropy_info(self):
        for i in range(1, 51):
            for r in self.rooms:
                prob = self.history.count(r) / 10.0
                if prob > 0: self.scores[r] -= (prob * i * 10)
    def _run_block_21_gravity(self):
        for i in range(1, 51):
            g = i * 10
            for r in self.rooms:
                d = abs(r - self.last) or 0.1
                self.scores[r] -= (g / (d**2))
    def _run_block_22_magnetism(self):
        for i in range(1, 51):
            for r in self.rooms:
                if (r%2) == (self.last%2): self.scores[r] -= (i*5)
    def _run_block_23_velocity(self):
        for i in range(1, 51):
            for r in self.rooms:
                if r > 3: self.scores[r] += i
    def _run_block_24_acceleration(self):
        for i in range(1, 51):
            for r in self.rooms:
                if r < 3: self.scores[r] += (i*2)
    def _run_block_25_oscillation(self):
        for i in range(1, 51):
            phase = math.sin(i)
            for r in self.rooms:
                if phase > 0: self.scores[r] += (i*2)
    def _run_block_26_waves(self):
        for i in range(1, 51):
            wave = math.cos(i)
            for r in self.rooms:
                if wave < 0: self.scores[r] -= (i*2)
    def _run_block_27_optics(self):
        for i in range(1, 51):
            mirror = 7 - self.last
            for r in self.rooms:
                if r == mirror: self.scores[r] -= (i*3)
    def _run_block_28_quantum_spin(self):
        for i in range(1, 51):
            spin = 1 if i % 2 == 0 else -1
            for r in self.rooms:
                self.scores[r] += (spin * i)
    def _run_block_29_string_theory(self):
        for i in range(1, 51):
            vibe = i % 6 + 1
            for r in self.rooms:
                if r == vibe: self.scores[r] -= (i*2)
    def _run_block_30_relativity(self):
        for i in range(1, 51):
            for r in self.rooms:
                if r == self.last: self.scores[r] -= i
    def _run_block_31_hash_chaos(self):
        for i in range(1, 51):
            h = hashlib.md5(f"{i}-{self.last}".encode()).hexdigest()
            val = int(h, 16) % 6 + 1
            for r in self.rooms:
                if r == val: self.scores[r] += (i*2)
    def _run_block_32_neural_weights(self):
        for i in range(1, 51):
            w = math.tanh(i/50)
            for r in self.rooms:
                if r != self.last: self.scores[r] += (w * 100)
    def _run_block_33_genetic_cross(self):
        for i in range(1, 51):
            child = (self.last + i) % 6 + 1
            for r in self.rooms:
                if r == child: self.scores[r] += (i*3)
    def _run_block_34_genetic_mut(self):
        for i in range(1, 51):
            mut = (self.last ^ i) % 6 + 1
            for r in self.rooms:
                if r == mut: self.scores[r] -= (i*4)
    def _run_block_35_game_theory(self):
        for i in range(1, 51):
            for r in self.rooms:
                if self.lose_streak > 3: self.scores[r] += i
                else: self.scores[r] -= i
    def _run_block_36_pattern_match(self):
         for i in range(1, 51):
             if len(self.history) > 2:
                 pat = self.history[0] + self.history[1]
                 if pat > 7:
                     for r in self.rooms: self.scores[r] -= i
    def _run_block_37_linear_reg(self):
        for i in range(1, 51):
            slope = i / 10
            pred = int((self.last + slope)) % 6 + 1
            for r in self.rooms:
                if abs(r - pred) < 1: self.scores[r] -= (i*5)
    def _run_block_38_polynomial(self):
        for i in range(1, 51):
            poly = (i**2) % 6 + 1
            for r in self.rooms:
                if r == poly: self.scores[r] += i
    def _run_block_39_fractals(self):
        for i in range(1, 51):
            c = complex(i/100, self.last/6)
            if abs(c) < 2:
                for r in self.rooms: self.scores[r] += i
    def _run_block_40_final_consensus(self):
        for i in range(1, 51):
            bias = 1 if i > 25 else -1
            for r in self.rooms:
                self.scores[r] += (bias * 10)

# --- SYSTEM FUNCTIONS ---
def load_data_cdtd():
    if os.path.exists('data-xw-cdtd.txt'):
        print(Colors.YELLOW + 'DATA FOUND! ' + Colors.WHITE + 'Sử dụng data cũ? (y/n): ', end='')
        if input().lower() == 'y':
            with open('data-xw-cdtd.txt', 'r', encoding='utf-8') as f:
                return json.load(f)
    print(Colors.CYAN + '📋 Paste Link Login:', end=' ')
    link = input()
    try:
        user_id = link.split('&')[0].split('?userId=')[1]
        user_secretkey = link.split('&')[1].split('secretKey=')[1]
        json_data = {'user-id': user_id, 'user-secret-key': user_secretkey}
        with open('data-xw-cdtd.txt', 'w+', encoding='utf-8') as f: json.dump(json_data, f)
        return json_data
    except:
        print(Colors.RED + "Link sai!"); return load_data_cdtd()

def get_history(s, headers):
    try:
        resp = s.get('https://api.sprintrun.win/sprint/recent_10_issues', headers=headers).json()
        history = [int(i['result'][0]) for i in resp['data']['recent_10']]
        current_issue = int(resp['data']['recent_10'][0]['issue_id'])
        return history, current_issue
    except: return [], 0

def bet_cdtd(s, headers, ki, kq, Coin, amount):
    try:
        data = {'issue_id': ki, 'bet_group': 'not_winner', 'asset_type': Coin, 'athlete_id': kq, 'bet_amount': amount}
        resp = s.post('https://api.sprintrun.win/sprint/bet', headers=headers, json=data).json()
        return resp.get('code') == 0
    except: return False

def user_asset(s, headers):
    try:
        data = {'user_id': int(headers['user-id']), 'source': 'home'}
        resp = s.post('https://wallet.3games.io/api/wallet/user_asset', headers=headers, json=data).json()
        return resp['data']['user_asset']
    except: return {'USDT': 0, 'WORLD': 0, 'BUILD': 0}

def print_matrix(scores, chosen_one):
    print(Colors.CYAN + "╔════════════════════════════════════════════╗")
    print(Colors.CYAN + "║      HUYCON OMEGA CORE - SCORING MATRIX    ║")
    print(Colors.CYAN + "╠════════╤════════════════════════╤══════════╣")
    print(Colors.CYAN + "║   NV   │   ĐIỂM SỐ (LOGIC W)    │ ĐÁNH GIÁ ║")
    print(Colors.CYAN + "╠════════╪════════════════════════╪══════════╣")
    
    min_s = min(scores.values())
    sorted_s = sorted(scores.items(), key=lambda item: item[1])
    
    for char_id, score in sorted_s:
        color = Colors.WHITE
        status = "Risk"
        if char_id == chosen_one:
            color = Colors.GREEN
            status = "SAFE/BET"
        elif score == max(scores.values()):
            color = Colors.RED
            status = "WINNER?"
            
        char_name = NV[char_id]
        print(f"║ {color}{str(char_id).center(6)}{Colors.CYAN} │ {color}{f'{score:.1f}'.center(22)}{Colors.CYAN} │ {color}{status.center(8)}{Colors.CYAN} ║")
    print(Colors.CYAN + "╚════════╧════════════════════════╧══════════╝")

# --- NEW: PROFIT/LOSS TABLE ---
def print_financial_report(initial, current, coin):
    profit = current - initial
    percent = (profit / initial) * 100 if initial > 0 else 0
    
    color = Colors.GREEN if profit >= 0 else Colors.RED
    status = "LÃI (PROFIT)" if profit >= 0 else "LỖ (LOSS)"
    
    print(Colors.YELLOW + "╔════════════════════════════════════════════╗")
    print(Colors.YELLOW + "║           BÁO CÁO TÀI CHÍNH (P/L)          ║")
    print(Colors.YELLOW + "╠══════════════════════╤═════════════════════╣")
    # Định dạng chuỗi fixed width để khung không bị lệch
    print(f"║ {Colors.WHITE}Vốn Ban Đầu          {Colors.YELLOW}│ {Colors.CYAN}{f'{initial:.2f} {coin}'.center(19)} {Colors.YELLOW}║")
    print(f"║ {Colors.WHITE}Số Dư Hiện Tại       {Colors.YELLOW}│ {Colors.CYAN}{f'{current:.2f} {coin}'.center(19)} {Colors.YELLOW}║")
    print(Colors.YELLOW + "╠══════════════════════╪═════════════════════╣")
    print(f"║ {Colors.WHITE}Lợi Nhuận Ròng       {Colors.YELLOW}│ {color}{f'{profit:+.2f} {coin}'.center(19)} {Colors.YELLOW}║")
    print(f"║ {Colors.WHITE}Tỉ Suất (%)          {Colors.YELLOW}│ {color}{f'{percent:+.2f} %'.center(19)} {Colors.YELLOW}║")
    print(f"║ {Colors.WHITE}Trạng Thái           {Colors.YELLOW}│ {color}{status.center(19)} {Colors.YELLOW}║")
    print(Colors.YELLOW + "╚══════════════════════╧═════════════════════╝")

# --- MAIN LOOP ---
def main_omega():
    s = requests.Session()
    banner_omega()
    data = load_data_cdtd()
    headers = {
        'user-id': data['user-id'], 'user-secret-key': data['user-secret-key'],
        'user-agent': 'Mozilla/5.0 (Linux; Android 10)', 'origin': 'https://xworld.info'
    }

    # Setup Tiền & Cược
    asset = user_asset(s, headers)
    print(Colors.YELLOW + f"Ví: {asset['USDT']} USDT | {asset['BUILD']} BUILD | {asset['WORLD']} WORLD")
    print(Colors.CYAN + "Chọn tiền cược (1.USDT 2.BUILD 3.WORLD): ", end='')
    c = input()
    Coin = 'USDT' if c=='1' else 'BUILD' if c=='2' else 'WORLD'
    
    try:
        base_bet = float(input(Colors.GREEN + f"Nhập mức cược gốc ({Coin}): "))
        he_so = float(input(Colors.RED + "Nhập hệ số gấp thếp (VD: 2): "))
    except: print(Colors.RED + "Lỗi nhập liệu!"); return

    # SNAPSHOT VỐN BAN ĐẦU
    initial_balance = asset[Coin]
    current_bet = base_bet
    lose_streak = 0
    last_processed_issue = 0

    while True:
        try:
            # 1. Lấy dữ liệu & Phân tích
            history, current_issue = get_history(s, headers)
            next_issue = current_issue + 1
            
            # Cập nhật số dư realtime để tính P/L
            current_asset = user_asset(s, headers)
            current_balance = current_asset[Coin]
            
            if len(history) < 5:
                print(Colors.YELLOW + "Đang thu thập dữ liệu...", end='\r'); time.sleep(2); continue

            # 2. Xử lý Logic Omega Core
            if next_issue > last_processed_issue:
                # Hiển thị bảng P/L TRƯỚC khi vào ván mới
                clear_screen()
                banner_omega()
                print_financial_report(initial_balance, current_balance, Coin)
                
                print_timestamp(f"🚀 Kích hoạt Omega Core v7 cho kì #{next_issue}...", Colors.MAGENTA)
                
                core = HuyCon_Omega_Core(history, [1,2,3,4,5,6], lose_streak)
                scores = core.run_4000_logics()
                
                sorted_chars = sorted(scores.items(), key=lambda item: item[1])
                chosen_one = sorted_chars[0][0] # Min Score
                
                if chosen_one == history[0]:
                    print(Colors.YELLOW + "⚠️ Detect: Người này vừa thắng, đổi sang phương án an toàn 2.")
                    chosen_one = sorted_chars[1][0]

                print_matrix(scores, chosen_one)
                
                # 3. Đặt cược
                print(Colors.YELLOW + f"➤ Đang vào tiền: {current_bet} {Coin} cho cửa: {NV[chosen_one]} (Not Win)")
                if bet_cdtd(s, headers, next_issue, chosen_one, Coin, current_bet):
                    print(Colors.GREEN + "✅ Đặt cược thành công! Đang đợi kết quả...")
                    last_processed_issue = next_issue
                    
                    # 4. Đợi kết quả & Xử lý Gấp thếp
                    while True:
                        check_h, check_iss = get_history(s, headers)
                        if check_iss == next_issue: # Đã có kết quả
                            winner = check_h[0]
                            print_timestamp(f"🔔 Kết quả: {NV[winner]} về nhất!", Colors.BLUE)
                            
                            if winner == chosen_one: # MÌNH THUA
                                print(Colors.BG_RED + f" ❌ THUA RỒI! Kích hoạt gấp thếp x{he_so} ❌ ")
                                current_bet *= he_so
                                lose_streak += 1
                            else: # MÌNH THẮNG
                                print(Colors.BG_GREEN + " ✨ CHIẾN THẮNG! Reset mức cược ✨ ")
                                current_bet = base_bet
                                lose_streak = 0
                            
                            time.sleep(3)
                            break
                        sys.stdout.write(Colors.CYAN + "."); sys.stdout.flush(); time.sleep(2)
                else:
                    print(Colors.RED + "❌ Lỗi đặt cược (Hết tiền/Mạng lag). Thử lại sau 5s...")
                    time.sleep(5)
            else:
                print(Colors.WHITE + f"Đang đợi kì mới... #{current_issue}", end='\r')
                time.sleep(2)

        except Exception as e:
            print(Colors.RED + f"Lỗi hệ thống: {e}"); time.sleep(5)

if __name__ == "__main__":
    main_omega()
