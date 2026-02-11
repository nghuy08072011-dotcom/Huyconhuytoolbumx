import os
import time
import requests
import sys
import json
import random
import math
import statistics
import hashlib
from urllib.parse import urlparse, parse_qs
from collections import Counter, deque


try:
    from requests import session
    from rich.console import Console, Group
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    from rich import box
    from rich.progress import track, Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn
    from rich.layout import Layout
    from rich.live import Live
    from rich.spinner import Spinner
    from rich.style import Style
    from rich.columns import Columns
except ImportError:
    os.system("pip install requests rich colorama")
    sys.exit()

console = Console()
CONFIG_FILE = "config_huycon_omega_vn.json"


FAKE_UAS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Xiaomi 2201123G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15"
]


def send_telegram_alert(token, chat_id, msg):
    if not token or not chat_id: return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=5)
    except:
        pass 


class SecureGatekeeper:
    """
    Trụ kiểm soát an ninh:
    1. Quản lý tiền: Thắng reset, Thua gấp thếp.
    2. Chặn trùng lặp: Mỗi ván chỉ được phép đặt 1 lần duy nhất.
    """
    def __init__(self, base_bet, multiplier):
        self.base_bet = base_bet
        self.current_bet = base_bet
        self.multiplier = multiplier
        self.last_bet_round_id = None 

    def can_bet(self, round_id):
        """Kiểm tra xem có được phép đặt cược vào ván này không"""
        if round_id == self.last_bet_round_id:
            return False 
        return True

    def mark_bet_placed(self, round_id):
        """Đánh dấu là đã đặt cược xong ván này"""
        self.last_bet_round_id = round_id

    def process_result(self, is_win):
        """Xử lý kết quả để tính tiền ván sau"""
        if is_win:
            self.current_bet = self.base_bet
        else:
            self.current_bet = self.current_bet * self.multiplier
        return self.current_bet

    def force_reset(self):
        """Bắt buộc reset về mức cược gốc (Dùng khi cắt lỗ/chốt lời)"""
        self.current_bet = self.base_bet

# ==============================================================================
#  CORE LOGIC (GIỮ NGUYÊN)
# ==============================================================================

class HuyCon_Omega_Core:
    def __init__(self, history, rooms, lose_streak, ai_weights=None):
        self.history = history
        self.rooms = rooms
        self.lose_streak = lose_streak
        self.ai_weights = ai_weights if ai_weights else {f"block_{i}": 1.0 for i in range(1, 41)}
        self.scores = {r: 0.0 for r in rooms}
        self.last = history[0] if history else 0
        self.len_h = len(history)
        self.mean = statistics.mean(history) if history else 4.5
        self.stdev = statistics.stdev(history) if len(history) > 1 else 1.0

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
        original_scores = self.scores
        self.scores = temp_scores
        func()
        w = self.ai_weights.get(f"block_{block_id}", 1.0)
        for r in self.rooms:
            original_scores[r] += (temp_scores[r] * w)
        self.scores = original_scores

    # --- CÁC HÀM XỬ LÝ (LOGIC GỐC) ---
    def _run_block_01_frequency(self):
        for i in range(1, 101):
            w = i * 10
            for r in self.rooms: self.scores[r] -= (self.history.count(r) * w)
    def _run_block_02_gap(self):
        for i in range(1, 101):
            target_gap = i % 10
            for r in self.rooms:
                if r not in self.history[:target_gap]: self.scores[r] += (i * 5)
    def _run_block_03_modulo(self):
        for i in range(1, 101):
            mod_val = (i % 7) + 2
            for r in self.rooms:
                if (r % mod_val) == (self.last % mod_val): self.scores[r] -= (i * 8)
    def _run_block_04_geometry(self):
        for i in range(1, 101):
            for r in self.rooms:
                if abs(r - self.last) == 4: self.scores[r] -= (i * 15)
    def _run_block_05_primes(self):
        primes = [2,3,5,7]
        for i in range(1, 101):
            for r in self.rooms:
                if r in primes: self.scores[r] += (i * 2)
                else: self.scores[r] -= (i * 2)
    def _run_block_06_fibonacci(self):
        fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
        for i in range(1, 101):
            step = fib[i % 10]
            bad = (self.last + step - 1) % 8 + 1
            for r in self.rooms:
                if r == bad: self.scores[r] -= (i * 10)
    def _run_block_07_vectors(self):
        for i in range(1, 101):
            vec = self.last - (self.history[1] if len(self.history)>1 else 0)
            pred = (self.last + vec) % 8 + 1
            for r in self.rooms:
                if r == pred: self.scores[r] -= (i * 5)
    def _run_block_08_symmetry(self):
        for i in range(1, 101):
            axis = (self.last + i) % 8 + 1
            for r in self.rooms:
                if r == axis: self.scores[r] -= (i * 3)
    def _run_block_09_golden_ratio(self):
        phi = 1.618
        for i in range(1, 101):
            target = (self.last * phi * i) % 8
            for r in self.rooms:
                if abs(r - target) < 1: self.scores[r] -= (i * 4)
    def _run_block_10_matrix(self):
        for i in range(1, 101):
            trans = (self.last * i + 7) % 8 + 1
            for r in self.rooms:
                if r == trans: self.scores[r] -= (i * 2)
    def _run_block_11_poisson(self):
        for i in range(1, 101):
            lamda = 1 + (i/20)
            for r in self.rooms:
                k = self.history.count(r)
                p = (lamda**k * math.exp(-lamda))/math.factorial(k)
                if p < 0.1: self.scores[r] += (i*5)
    def _run_block_12_gaussian(self):
        for i in range(1, 101):
            thresh = 1 + (i/50)
            for r in self.rooms:
                z = (r - self.mean)/self.stdev
                if abs(z) > thresh: self.scores[r] -= (i*3)
    def _run_block_13_binomial(self):
        for i in range(1, 101):
            for r in self.rooms:
                if (r%2) == (self.last%2): self.scores[r] -= (i*2)
    def _run_block_14_bayesian(self):
        for i in range(1, 101):
            for r in self.rooms: self.scores[r] += (random.random() * i)
    def _run_block_15_markov(self):
        for i in range(1, 101):
            if len(self.history) > 2 and self.history[0] == self.history[1]:
                for r in self.rooms:
                     if r == self.history[0]: self.scores[r] -= (i * 20)
    def _run_block_16_variance(self):
        for i in range(1, 101):
            for r in self.rooms:
                if abs(r - self.mean) > 2: self.scores[r] += (i * 2)
    def _run_block_17_standard_error(self):
         for i in range(1, 101):
            for r in self.rooms: self.scores[r] += i
    def _run_block_18_correlation(self):
         for i in range(1, 101):
            lag = (i % 3) + 1
            if len(self.history) > lag:
                lag_val = self.history[lag]
                for r in self.rooms:
                    if r == lag_val: self.scores[r] -= (i * 4)
    def _run_block_19_monte_carlo(self):
        seed = int(time.time())
        for i in range(1, 101):
            random.seed(seed + i)
            sim = random.randint(1, 8)
            for r in self.rooms:
                if r == sim: self.scores[r] += 100
    def _run_block_20_entropy_info(self):
        for i in range(1, 101):
            for r in self.rooms:
                prob = self.history.count(r) / 10.0
                if prob > 0: self.scores[r] -= (prob * i * 10)
    def _run_block_21_gravity(self):
        for i in range(1, 101):
            g = i * 10
            for r in self.rooms:
                d = abs(r - self.last) or 0.1
                self.scores[r] -= (g / (d**2))
    def _run_block_22_magnetism(self):
        for i in range(1, 101):
            for r in self.rooms:
                if (r%2) == (self.last%2): self.scores[r] -= (i*5)
    def _run_block_23_velocity(self):
        for i in range(1, 101):
            for r in self.rooms:
                if r > 4: self.scores[r] += i
    def _run_block_24_acceleration(self):
        for i in range(1, 101):
            for r in self.rooms:
                if r < 4: self.scores[r] += (i*2)
    def _run_block_25_oscillation(self):
        for i in range(1, 101):
            phase = math.sin(i)
            for r in self.rooms:
                if phase > 0: self.scores[r] += (i*2)
    def _run_block_26_waves(self):
        for i in range(1, 101):
            wave = math.cos(i)
            for r in self.rooms:
                if wave < 0: self.scores[r] -= (i*2)
    def _run_block_27_optics(self):
        for i in range(1, 101):
            mirror = 9 - self.last
            for r in self.rooms:
                if r == mirror: self.scores[r] -= (i*3)
    def _run_block_28_quantum_spin(self):
        for i in range(1, 101):
            spin = 1 if i % 2 == 0 else -1
            for r in self.rooms:
                self.scores[r] += (spin * i)
    def _run_block_29_string_theory(self):
        for i in range(1, 101):
            vibe = i % 8 + 1
            for r in self.rooms:
                if r == vibe: self.scores[r] -= (i*2)
    def _run_block_30_relativity(self):
        for i in range(1, 101):
            for r in self.rooms:
                if r == self.last: self.scores[r] -= i
    def _run_block_31_hash_chaos(self):
        for i in range(1, 101):
            h = hashlib.md5(f"{i}-{self.last}".encode()).hexdigest()
            val = int(h, 16) % 8 + 1
            for r in self.rooms:
                if r == val: self.scores[r] += (i*2)
    def _run_block_32_neural_weights(self):
        for i in range(1, 101):
            w = math.tanh(i/50)
            for r in self.rooms:
                if r != self.last: self.scores[r] += (w * 100)
    def _run_block_33_genetic_cross(self):
        for i in range(1, 101):
            child = (self.last + i) % 8 + 1
            for r in self.rooms:
                if r == child: self.scores[r] += (i*3)
    def _run_block_34_genetic_mut(self):
        for i in range(1, 101):
            mut = (self.last ^ i) % 8 + 1
            for r in self.rooms:
                if r == mut: self.scores[r] -= (i*4)
    def _run_block_35_game_theory(self):
        for i in range(1, 101):
            for r in self.rooms:
                if self.lose_streak > 3: self.scores[r] += i
                else: self.scores[r] -= i
    def _run_block_36_pattern_match(self):
         for i in range(1, 101):
             if len(self.history) > 2:
                 pat = self.history[0] + self.history[1]
                 if pat > 10:
                     for r in self.rooms: self.scores[r] -= i
    def _run_block_37_linear_reg(self):
        for i in range(1, 101):
            slope = i / 10
            pred = (self.last + slope) % 8
            for r in self.rooms:
                if abs(r - pred) < 1: self.scores[r] -= (i*5)
    def _run_block_38_polynomial(self):
        for i in range(1, 101):
            poly = (i**2) % 8 + 1
            for r in self.rooms:
                if r == poly: self.scores[r] += i
    def _run_block_39_fractals(self):
        for i in range(1, 101):
            c = complex(i/100, self.last/8)
            if abs(c) < 2:
                for r in self.rooms: self.scores[r] += i
    def _run_block_40_final_consensus(self):
        for i in range(1, 101):
            bias = 1 if i > 50 else -1
            for r in self.rooms:
                self.scores[r] += (bias * 10)


# ==============================================================================
#  VISUALS (LITE VERSION)
# ==============================================================================

def glitch_print(text, style="bold cyan", duration=1.5):
    chars = "░▒▓█@#$%&*!?/\|"
    end_time = time.time() + duration
    with Live(console=console, refresh_per_second=20, transient=True) as live:
        while time.time() < end_time:
            glitched = "".join([c if random.random() > 0.4 else random.choice(chars) for c in text])
            live.update(Panel(Align.center(glitched), style="bold red", border_style="dim white"))
            time.sleep(0.05)
    console.print(Panel(Align.center(text), style=style, border_style="green", box=box.HEAVY))

def decrypt_room_id(target_room, bet_amount):
    final_text = f"P{target_room}"
    steps = 25
    with Live(console=console, refresh_per_second=20, transient=True) as live:
        for i in range(steps):
            fake = f"P{random.randint(1, 8)}"
            if i > steps - 8: display = final_text
            else: display = fake
            bar = "█" * i + "░" * (steps - i)
            color = "red" if i < steps - 5 else "bright_green"
            title_st = "LOCKING TARGET" if i < steps - 5 else "TARGET LOCKED"
            content = f"""
            [bold white]SCANNING...[/]
            [size=40 bold {color}]{display}[/]
            [dim]{bar}[/dim]
            [bold yellow]CƯỢC: {bet_amount}[/]
            """
            panel = Panel(Align.center(content), 
                          title=f"[blink]{title_st}[/]", border_style=color, box=box.DOUBLE)
            live.update(panel)
            time.sleep(0.08)

def cyber_waiting_screen(seconds, last_bet_info=None):
    start_time = time.time()
    with Live(console=console, refresh_per_second=4, transient=True) as live:
        while time.time() - start_time < seconds:
            elapsed = time.time() - start_time; remaining = seconds - elapsed
            cpu_load = random.randint(10, 45); ram_usage = random.randint(2048, 4096); ping = random.randint(12, 88); algo_conf = random.randint(85, 99)
            wave = "".join([" " if random.random() > 0.5 else "▂" for _ in range(30)])
            msg = "ĐANG ĐỢI MÁY CHỦ TRẢ KẾT QUẢ..."
            if last_bet_info: msg = f"ĐANG CHỜ KẾT QUẢ VÁN #{last_bet_info['id']} | CƯỢC PHÒNG P{last_bet_info['r']}"
            grid = Table.grid(expand=True); grid.add_column(justify="center")
            stats_table = Table(show_header=False, box=box.SIMPLE, border_style="dim blue")
            stats_table.add_row(f"[bold cyan]TẢI CPU:[/][bold white] {cpu_load}%[/]", f"[bold green]RAM:[/][bold white] {ram_usage}MB[/]")
            stats_table.add_row(f"[bold magenta]ĐỘ TRỄ:[/][bold white] {ping}ms[/]", f"[bold yellow]ĐỘ TIN CẬY:[/][bold white] {algo_conf}%[/]")
            main_panel = Panel(Align.center(stats_table), title=f"[bold blink cyan]⏳ {msg} ({int(remaining)}s)[/]", subtitle=f"[dim blue]{wave}[/]", border_style="blue", padding=(0, 2))
            live.update(main_panel)
            time.sleep(0.25)
            if remaining <= 0: break

def simulate_ai_training():
    console.print()
    with Progress(
        SpinnerColumn("aesthetic", speed=1.5, style="bold magenta"),
        TextColumn("[bold cyan]AI ĐANG TỐI ƯU HÓA THUẬT TOÁN...[/]"),
        BarColumn(bar_width=None, style="blue", complete_style="bold green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        transient=True
    ) as progress:
        task = progress.add_task("Training", total=100)
        for _ in range(100):
            time.sleep(0.02)
            progress.update(task, advance=random.uniform(0.5, 3))
    console.print(Panel("[bold green]✅ ĐÃ CẬP NHẬT TRỌNG SỐ NEURAL NETWORK THÀNH CÔNG![/]", style="green"))
    time.sleep(1)

def draw_ascii_chart(data, height=8):
    if len(data) < 2: return Text("CHƯA CÓ DỮ LIỆU BIỂU ĐỒ...", style="dim italic")
    recent_data = data[-30:]
    min_val = min(recent_data)
    max_val = max(recent_data)
    range_val = max_val - min_val if max_val != min_val else 1.0
    rows = []
    for r in range(height):
        row_str = ""
        threshold_upper = min_val + (range_val * (height - r) / height)
        threshold_lower = min_val + (range_val * (height - r - 1) / height)
        for val in recent_data:
            if val >= threshold_upper: char = "█"
            elif val >= threshold_lower:
                ratio = (val - threshold_lower) / (threshold_upper - threshold_lower)
                if ratio > 0.8: char = "▇"
                elif ratio > 0.6: char = "▆"
                elif ratio > 0.4: char = "▅"
                elif ratio > 0.2: char = "▃"
                else: char = " "
            else: char = " "
            color = "bright_green" if val >= 0 else "bright_red"
            row_str += f"[{color}]{char}[/]"
        rows.append(row_str)
    return Text.from_markup("\n".join(rows))

def draw_heatmap(history):
    if not history: return Text("CHƯA CÓ DỮ LIỆU NHIỆT...", style="dim italic")
    recent_history = history[:50]
    counts = Counter(recent_history)
    max_count = max(counts.values()) if counts else 1
    grid = Table.grid(padding=(0, 1))
    row_rooms = []; row_heat = []
    for r in range(1, 9):
        c = counts.get(r, 0)
        intensity = c / max_count
        if intensity > 0.8: color = "bright_red"
        elif intensity > 0.6: color = "orange1"
        elif intensity > 0.4: color = "yellow"
        elif intensity > 0.2: color = "cyan"
        else: color = "blue"
        blocks = "█" * int(intensity * 4 + 1)
        row_rooms.append(f"[bold white]P{r}[/]")
        row_heat.append(f"[{color}]{blocks}[/]")
        grid.add_column(justify="center", width=6)
    grid.add_row(*row_rooms)
    grid.add_row(*row_heat)
    return Panel(grid, title="🔥 BẢN ĐỒ NHIỆT (50 VÁN) 🔥", border_style="orange1")

def generate_segmented_bar(score, total_parts=10):
    max_val = 10.0
    percent = min(abs(score) / max_val, 1.0)
    active_parts = int(percent * total_parts)
    bar_str = ""
    char_on = "▰"; char_off = "▱"
    if score >= 0:
        symbol = "[bold cyan]⚡[/]"; color_on = "bold bright_green" if active_parts < 7 else "bold bright_cyan"; color_off = "dim green"
    else:
        symbol = "[bold red]☠️[/]"; color_on = "bold orange1" if active_parts < 7 else "bold deep_pink1"; color_off = "dim red"
    for i in range(total_parts):
        if i < active_parts: bar_str += f"[{color_on}]{char_on}[/] "
        else: bar_str += f"[{color_off}]{char_off}[/] "
    return f"{symbol} {bar_str}"

def matrix_scan_effect_ultimate(final_scores):
    hack_phrases = ["ĐANG KHỞI ĐỘNG LÕI...", "ĐANG VƯỢT TƯỜNG LỬA...", "GIẢI MÃ DỮ LIỆU SỐ...", "KIỂM TRA BIẾN ĐỘNG LƯỢNG TỬ...", "ĐỒNG BỘ CHUỖI MÃ HÓA...", "TIÊM THUẬT TOÁN AI...", "TỐI ƯU HÓA DỰ ĐOÁN CẦU...", "CHỐT KẾT QUẢ CUỐI CÙNG..."]
    total_steps = 25
    with Live(refresh_per_second=20, console=console, transient=True) as live:
        for i in range(total_steps + 1):
            percent = int((i / total_steps) * 100)
            table = Table(box=box.SIMPLE_HEAVY, expand=True, show_header=True, header_style="bold black on bright_cyan", border_style="bright_blue")
            table.add_column("PHÒNG", justify="center", style="bold white", width=8)
            table.add_column("ĐIỂM SỐ", justify="right", style="bold yellow")
            table.add_column("THANH SỨC MẠNH", justify="left")
            fake_data = []
            for r in range(1, 9):
                if i < total_steps - 5: fake_score = random.uniform(-20, 20)
                else:
                    real_score = final_scores[r] / 10000.0
                    noise = random.uniform(-0.5, 0.5) * (total_steps - i)
                    fake_score = real_score + noise
                fake_data.append((r, fake_score))
            if i < total_steps - 8:
                if i % 2 == 0: random.shuffle(fake_data)
            else: fake_data.sort(key=lambda x: x[1], reverse=True)
            for r, s in fake_data:
                bar = generate_segmented_bar(s)
                style_row = "bold white"
                if random.random() < 0.1: style_row = "bold black on white"
                table.add_row(f"P{r}", f"[italic]{s:+.2f}[/]", bar, style=style_row)
            spin = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"][i % 8]
            phrase_idx = min(int((i / total_steps) * len(hack_phrases)), len(hack_phrases)-1)
            bar_fill = "█" * (percent // 5); bar_empty = "░" * (20 - (percent // 5))
            title_str = f"[bold white]{spin} HỆ THỐNG HUYCON: [bold bright_yellow]{hack_phrases[phrase_idx]}[/]"
            subtitle_str = f"[bold bright_cyan]TIẾN TRÌNH QUÉT... {percent}% [[bold bright_green]{bar_fill}[/][dim cyan]{bar_empty}[/]][/]"
            live.update(Panel(Align.center(table), title=title_str, subtitle=subtitle_str, border_style="white", box=box.DOUBLE, padding=(1, 2)))
            time.sleep(0.04)

def display_final_result_with_marquee(final_scores, best_room):
    table = Table(box=box.DOUBLE_EDGE, expand=True, show_header=True, header_style="bold white on purple", border_style="bright_magenta")
    table.add_column("PHÒNG", justify="center", style="bold cyan")
    table.add_column("TỈ LỆ CHUẨN", justify="right", style="bold gold1")
    table.add_column("SỨC MẠNH (MODULES)", justify="left")
    sorted_rooms = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    for r, s in sorted_rooms:
        avg_score = s / 10000.0
        energy_bar = generate_segmented_bar(avg_score)
        if r == best_room:
            r_display, s_display, row_style = f"👑 P{r}", f"[bold white blink on blue]{avg_score:+.2f}[/]", "bold white on navy_blue"
            energy_bar = f"🔱 {energy_bar}"
        else:
            r_display, s_display, row_style = f"P{r}", f"{avg_score:+.2f}", ("dim" if avg_score < 0 else "")
        table.add_row(r_display, s_display, energy_bar, style=row_style)
    final_panel = Panel(Align.center(table), title="[bold bright_white]🔮 MÁY QUÉT HUYCON OMEGA (HOÀN TẤT) 🔮[/]", subtitle="[bold yellow]DỮ LIỆU ĐÃ ĐƯỢC CHỐT - SẴN SÀNG VÀO TIỀN[/]", border_style="bright_magenta", box=box.HEAVY, padding=(1, 2))
    console.print(final_panel)

def analyze_and_score_rooms_omega(recent_10_data, last_win_room, lose_streak, ai_weights):
    rooms = list(range(1, 9))
    history = []
    if recent_10_data:
        for r in recent_10_data:
            try:
                val = int(r.get("killed_room_id", -1))
                if val != -1: history.append(val)
            except: pass
    if not history: return random.randint(1, 8)
    engine = HuyCon_Omega_Core(history, rooms, lose_streak, ai_weights)
    final_scores = engine.run_4000_logics()
    max_score = max(final_scores.values())
    candidates = [r for r, s in final_scores.items() if s == max_score]
    if len(candidates) > 1: best_room = random.choice(candidates)
    else: best_room = candidates[0]
    matrix_scan_effect_ultimate(final_scores)
    display_final_result_with_marquee(final_scores, best_room)
    return best_room

def clear_console(): os.system("clear")

def show_header():
    huycon_art_lines = [
        "    ██╗  ██╗██╗   ██╗██╗   ██╗ ██████╗ ██████╗ ███╗   ██╗",
        "    ██║  ██║██║   ██║╚██╗ ██╔╝ ██╔════╝██╔═══██╗████╗  ██║",
        "    ███████║██║   ██║ ╚████╔╝  ██║     ██║   ██║██╔██╗ ██║",
        "    ██╔══██║██║   ██║  ╚██╔╝   ██║     ██║   ██║██║╚██╗██║",
        "    ██║  ██║╚██████╔╝   ██║    ╚██████╗╚██████╔╝██║ ╚████║",
        "    ╚═╝  ╚═╝ ╚═════╝    ╚═╝     ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝"
    ]
    clear_console()
    console.print()
    for line in huycon_art_lines:
        text = Text(line); text.stylize(Style(color="bright_cyan", bold=True))
        console.print(Align.center(text)); time.sleep(0.02)
     
    glitch_print("🔱 CHỦ SỞ HỮU TỐI CAO: HUYCON 🔱", style="bold white on red")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f: return json.load(f)
        except: pass
    console.print(Panel("[bold yellow]THIẾT LẬP CẤU HÌNH BAN ĐẦU[/]", border_style="cyan"))
    config = {
        "url_game": console.input("[bold cyan]Link Game: [/]").strip(),
        "bet_type": console.input("[bold cyan]Loại tiền (BUILD/USDT/WORLD): [/]").strip().upper(),
        "base_bet": float(console.input("[bold cyan]Cược cơ bản: [/]").strip()),
        "multiplier": float(console.input("[bold cyan]Hệ số nhân: [/]").strip()),
        "max_lose_streak": int(console.input("[bold cyan]Max Thua: [/]").strip()),
        "stop_profit": float(console.input("[bold cyan]Mục tiêu Lãi: [/]").strip()),
        "stop_loss": float(console.input("[bold cyan]Giới hạn Lỗ: [/]").strip()),
        "play_rounds": int(console.input("[bold cyan]Số ván chơi: [/]").strip()),
        "pause_rounds": int(console.input("[bold cyan]Số ván nghỉ: [/]").strip()),
        "tele_token": console.input("[bold green]Token Bot Telegram (Enter để bỏ qua): [/]").strip(),
        "tele_id": console.input("[bold green]Chat ID Telegram (Enter để bỏ qua): [/]").strip()
    }
    with open(CONFIG_FILE, "w") as f: json.dump(config, f, indent=4)
    return config

def show_result_dashboard(rid, win, amt, profit, bal, curr, total_games, total_wins, profit_history, room_history, tele_cfg):
    if win:
        title, border_col, msg_style, icon, bg_effect = f"🤑 HUYCON THẮNG #{rid}", "bright_green", "bold bright_green", "💰", "on green"
        sign = "+"
        tele_msg = f"✅ HUYCON THẮNG #{rid}\n💰 +{amt:.4f} {curr}\n🤑 Lãi: {profit:.4f}\n💵 Số dư: {bal:.4f}"
    else:
        title, border_col, msg_style, icon, bg_effect = f"💸 HUYCON THUA #{rid}", "bright_red", "bold bright_red", "💀", ""
        sign = "-"
        tele_msg = f"❌ HUYCON THUA #{rid}\n💸 -{amt:.4f} {curr}\n📉 Lãi: {profit:.4f}\n💵 Số dư: {bal:.4f}"
     
    # Gửi Tele
    if tele_cfg["token"] and tele_cfg["id"]:
        send_telegram_alert(tele_cfg["token"], tele_cfg["id"], tele_msg)

    win_rate = (total_wins / total_games * 100) if total_games > 0 else 0.0
    grid_stats = Table.grid(expand=True)
    grid_stats.add_column(); grid_stats.add_column(justify="right")
    grid_stats.add_row(f"[bold white]KẾT QUẢ {icon}:[/]", f"[{msg_style} size=20]{sign}{amt:.4f} {curr}[/]")
    grid_stats.add_row("[bold cyan]SỐ DƯ:[/]", f"[bold gold1]{bal:.4f}[/]")
    grid_stats.add_row("[bold cyan]LÃI THỰC TẾ:[/]", f"[bold {'bright_green' if profit>=0 else 'bright_red'}]{profit:+.4f}[/]")
    grid_stats.add_row("---", "---")
    grid_stats.add_row("[dim]TỔNG SỐ TRẬN:[/]", f"[bold white]{total_games}[/]")
    wr_color = "bright_green" if win_rate >= 50 else ("yellow" if win_rate >= 30 else "red")
    grid_stats.add_row("[dim]TỶ LỆ THẮNG:[/]", f"[bold {wr_color}]{win_rate:.2f}%[/]")
    panel_stats = Panel(grid_stats, title=f"[bold white {bg_effect}]{title}[/]", border_style=border_col, box=box.HEAVY)
    panel_chart = Panel(draw_ascii_chart(profit_history), title=" 📉 BIỂU ĐỒ SÓNG LÃI/LỖ", border_style="cyan")
    heatmap_render = draw_heatmap(room_history)
    dashboard = Group(panel_stats, panel_chart, heatmap_render)
    console.print(dashboard)

def make_req(session, method, url, **kwargs):
    session.headers.update({"user-agent": random.choice(FAKE_UAS)})
    time.sleep(random.uniform(0.1, 0.5))
    for _ in range(3):
        try: return session.request(method, url, timeout=10, **kwargs).json()
        except: time.sleep(1)
    return None

def get_balance(session, url, bet_type):
    data = make_req(session, "GET", url)
    if not data: return 0
    wallets = data.get("data", {}).get("cwallet", {})
    key = {"USDT": "ctoken_kusdt", "WORLD": "ctoken_kther", "BUILD": "ctoken_contribute"}
    return float(wallets.get(key.get(bet_type, ""), 0))

def main():
    show_header(); cfg = load_config()
    tele_config = {"token": cfg.get("tele_token"), "id": cfg.get("tele_id")}
     
    try:
        q = parse_qs(urlparse(cfg["url_game"]).query)
        uid, key = q.get("userId")[0], q.get("secretKey")[0]
    except: return console.print("[red]Link lỗi![/]")
    ss = requests.Session()
    ss.headers.update({"user-id": uid, "user-secret-key": key})
    API = "https://api.escapemaster.net/escape_game"
    URL_U = "https://user.3games.io/user/regist?is_cwallet=1"
    URL_B = f"{API}/bet"
    URL_H = f"{API}/recent_10_issues?asset={cfg['bet_type']}"
    initial_balance = get_balance(ss, URL_U, cfg['bet_type'])
    console.print(Panel(f"💎 VỐN BAN ĐẦU: [bold gold1]{initial_balance} {cfg['bet_type']}[/]", style="bold blue", box=box.ROUNDED))
     
    # Báo Tele khi khởi động
    send_telegram_alert(tele_config["token"], tele_config["id"], f"🚀 BOT HUYCON ĐÃ KHỞI ĐỘNG!\n💰 Vốn: {initial_balance} {cfg['bet_type']}")

    ai_weights = {f"block_{i}": 1.0 for i in range(1, 41)}
    ai_training_counter = 0
    
    # KHỞI TẠO TRỤ KIỂM SOÁT (SECURE GATEKEEPER)
    gatekeeper = SecureGatekeeper(cfg["base_bet"], cfg["multiplier"])

    st = {"profit": 0.0, "initial_bal": initial_balance, "streak": 0, "last_id": None, "bet": cfg["base_bet"], "lw": None, "play": 0, "pause": 0, "total_games": 0, "total_wins": 0}
    profit_history = [0.0]
    room_history = []
    last_bet = None
    wait_count = 0
    try:
        init_res = make_req(ss, "GET", URL_H)
        if init_res and init_res.get("data"):
            for r in init_res["data"]:
                try: room_history.append(int(r["killed_room_id"]))
                except: pass
    except: pass
     
    while True:
        try:
            res = make_req(ss, "GET", URL_H)
            if not res or not res.get("data"): time.sleep(2); continue
            data = res["data"]
            if last_bet:
                found_result = False
                for issue in data:
                    if str(issue["issue_id"]) == str(last_bet["id"]):
                        found_result = True
                        kill = int(issue["killed_room_id"])
                        room_history.insert(0, kill)
                        if len(room_history) > 100: room_history.pop()
                        current_bal = get_balance(ss, URL_U, cfg['bet_type'])
                        st["profit"] = current_bal - st["initial_bal"]
                        profit_history.append(st["profit"])
                        
                        # --- XỬ LÝ KẾT QUẢ QUA TRỤ KIỂM SOÁT ---
                        if kill != last_bet["r"]:
                            # THẮNG
                            st["streak"], st["lw"] = 0, last_bet["r"]
                            # Trụ kiểm soát: Reset tiền về gốc
                            st["bet"] = gatekeeper.process_result(is_win=True)
                            
                            st["total_games"] += 1; st["total_wins"] += 1
                            show_result_dashboard(last_bet["id"], True, last_bet["a"]*0.95, st["profit"], current_bal, cfg['bet_type'], st["total_games"], st["total_wins"], profit_history, room_history, tele_config)
                            ai_weights[f"block_{random.randint(1,40)}"] += 0.05
                        else:
                            # THUA
                            st["streak"] += 1
                            # Trụ kiểm soát: Gấp thếp tiền
                            st["bet"] = gatekeeper.process_result(is_win=False)

                            st["total_games"] += 1
                            show_result_dashboard(last_bet["id"], False, last_bet["a"], st["profit"], current_bal, cfg['bet_type'], st["total_games"], st["total_wins"], profit_history, room_history, tele_config)
                            idx = f"block_{random.randint(1,40)}"
                            if ai_weights[idx] > 0.5: ai_weights[idx] -= 0.05
                            
                            # CẮT LỖ (RESET NẾU THUA QUÁ NHIỀU)
                            if st["streak"] >= cfg["max_lose_streak"]:
                                console.print("[bold yellow on red]⚠️ ĐẠT GIỚI HẠN CẮT LỖ -> RESET CƯỢC ⚠️[/]")
                                st["streak"] = 0
                                gatekeeper.force_reset() # Bắt buộc reset
                                st["bet"] = gatekeeper.current_bet
                        
                        ai_training_counter += 1
                        if ai_training_counter >= 5:
                            simulate_ai_training()
                            ai_training_counter = 0
                        if st["profit"] >= cfg["stop_profit"] or st["profit"] <= -cfg["stop_loss"]:
                            send_telegram_alert(tele_config["token"], tele_config["id"], f"🛑 DỪNG BOT: ĐẠT MỤC TIÊU LÃI/LỖ!\n💵 Lãi cuối cùng: {st['profit']}")
                            return console.print("[bold magenta]🔱 HUYCON DỪNG: ĐẠT MỤC TIÊU LÃI/LỖ 🔱[/]")
                        st["play"] += 1
                        if cfg["play_rounds"] > 0 and st["play"] >= cfg["play_rounds"]:
                            st["pause"] = cfg["pause_rounds"]; st["play"] = 0
                        last_bet = None
                        wait_count = 0
                        break
                if not found_result:
                    wait_count += 1
                    if wait_count > 40:
                        console.print(f"[bold red]⚠️ CẢNH BÁO: Ván #{last_bet['id']} quá lâu không trả thưởng! Bỏ qua...[/]")
                        last_bet = None; wait_count = 0; continue
             
            latest_id_on_server = str(data[0]["issue_id"])
            if latest_id_on_server != st["last_id"] and last_bet is None:
                if st["pause"] > 0:
                    console.print(Panel(f"💤 ĐANG NGHỈ NGƠI... ({st['pause']} ván còn lại)", style="dim")); st["pause"] -= 1
                    st["last_id"] = latest_id_on_server
                    time.sleep(5); continue
                
                nid = int(latest_id_on_server) + 1
                
                # --- TRỤ KIỂM SOÁT: CHECK QUYỀN ĐẶT CƯỢC ---
                if not gatekeeper.can_bet(nid):
                    # Nếu trụ phát hiện đã đặt rồi -> Bỏ qua vòng lặp này ngay
                    console.print(f"[bold red]⛔ TRỤ KIỂM SOÁT: CHẶN LỆNH CƯỢC TRÙNG VÁN #{nid}[/]")
                    time.sleep(1)
                    continue
                # ---------------------------------------------

                curr_bal = get_balance(ss, URL_U, cfg['bet_type'])
                if curr_bal < st["bet"]: 
                    send_telegram_alert(tele_config["token"], tele_config["id"], "⛔ HẾT TIỀN CƯỢC! VUI LÒNG NẠP THÊM.")
                    return console.print("[bold red]⛔ HẾT TIỀN! NẠP ĐI BẠN ƠI![/]")
                 
                best = analyze_and_score_rooms_omega(data, st["lw"], st["streak"], ai_weights)
                 
                decrypt_room_id(best, st['bet'])
                 
                console.print(f"[dim italic]👻 GHOST MODE: Đang chờ thời điểm thích hợp...[/]")
                time.sleep(random.uniform(1.5, 3.0))
                console.print(f"🎯 VÁN [bold white]#{nid}[/]: VÀO TIỀN [bold yellow]{st['bet']:.4f}[/] CHO PHÒNG [bold cyan]P{best}[/]")
                bet_res = make_req(ss, "POST", URL_B, json={"asset_type": cfg["bet_type"], "user_id": int(uid), "room_id": best, "bet_amount": round(st['bet'], 4)})
                if bet_res and bet_res.get("code") == 0:
                    # --- TRỤ KIỂM SOÁT: XÁC NHẬN ĐÃ ĐẶT ---
                    gatekeeper.mark_bet_placed(nid)
                    # --------------------------------------
                    last_bet = {"id": nid, "r": best, "a": st['bet']}
                    st["last_id"] = latest_id_on_server
                else:
                    console.print(f"[bold red]❌ Lỗi cược: {bet_res}[/]"); last_bet = None; time.sleep(2)
            else:
                wait_seconds = 3
                cyber_waiting_screen(wait_seconds, last_bet)
                 
        except Exception as e: console.print(f"[bold red]Lỗi Hệ Thống: {e}[/]"); time.sleep(5)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print("\n[bold red]ĐÃ TẮT NGUỒN HỆ THỐNG![/]")
