import sys
import requests
import platform
import os
import time
from colorama import Fore, Style, init
import concurrent.futures

# Khởi tạo màu sắc
init(autoreset=True)

# Biến toàn cục lưu trạng thái
redeemed_or_exhausted_codes = set()
last_log_time = {}  
user_claimed_history = {} 
limit_reached_users = set() 
last_amount = {} # Lưu số lượng lần check trước để so sánh

def clear_screen():
    os.system('cls' if platform.system() == "Windows" else 'clear')

def prints(r, g, b, text="text", end="\n"):
    print(f"\033[38;2;{r};{g};{b}m{text}\033[0m", end=end)

def banner():
    banner_text="""
    _  _                                                           
   FJ  L]    _    _    _    _        ____      ____     _ ___      
  J |__| L  J |  | L  J |  | L      F ___J.   F __ J   J '__ J     
  |  __  |  | |  | |  | |  | |     | |---LJ  | |--| |  | |__| |    
  F L__J J  F L__J J  F L__J J     F L___--. F L__J J  F L  J J    
 J__L  J__LJ\____,__L )-____  L   J\______/FJ\______/FJ__L  J__L   
 |__L  J__| J____,__FJ\______/F    J______F  J______F |__L  J__|   
                      J______F                                     
    """
    prints(32, 230, 151, banner_text)
    prints(247, 255, 97,"✨" + "═" * 45 + "✨")
    prints(32, 230, 151,"🌟 TOOL CANH CODE XWORLD PRO (SMART UPDATE) 🌟".center(45))
    prints(247, 255, 97,"═" * 47)
    prints(7, 205, 240,"ADMIN: HUYCONTOOL")
    prints(7, 205, 240,"MODIFIED BY: huy ")
    prints(247, 255, 97,"═" * 47)

def get_code_info(code):
    headers = {
        'accept': '*/*',
        'accept-language': 'vi,en;q=0.9',
        'content-type': 'application/json',
        'country-code': 'vn',
        'origin': 'https://xworld-app.com',
        'referer': 'https://xworld-app.com/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    }
    try:
        json_data = {
            'code': code,
            'os_ver': 'android',
            'platform': 'h5',
            'appname': 'app',
        }
        # Giảm timeout xuống 3s để check nhanh hơn
        response = requests.post('https://web3task.3games.io/v1/task/redcode/detail', headers=headers, json=json_data, timeout=3).json()

        if response.get('code') == 0 and response.get('message') == 'ok':
            data = response.get('data', {})
            admin_data = data.get('data', {}).get('admin', {})
            
            info = {
                'status': True,
                'total': data.get('user_cnt', 0),
                'used': data.get('progress', 0),
                'remaining': data.get('user_cnt', 0) - data.get('progress', 0),
                'currency': data.get('currency', 'UNK'),
                'value': admin_data.get('ad_show_value', 0),
                'name': admin_data.get('nick_name', 'Admin')
            }
            return info
        else:
            return {'status': False, 'message': response.get('message', 'Lỗi không xác định')}
    except Exception as e:
        return {'status': False, 'message': str(e)}

def nhap_code(userId, secretKey, code):
    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'origin': 'https://xworld.info',
        'referer': 'https://xworld.info/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'user-id': userId,
        'user-secret-key': secretKey,
    }
    try:
        json_data = {
            'code': code,
            'os_ver': 'android',
            'platform': 'h5',
            'appname': 'app',
        }
        response = requests.post('https://web3task.3games.io/v1/task/redcode/exchange', headers=headers, json=json_data, timeout=3).json()

        if response.get('code') == 0 and response.get('message') == 'ok':
            val = response['data'].get('value', 0)
            curr = response['data'].get('currency', '')
            return True, f"SUCCESS|{userId}|{val}|{curr}"
        else:
            msg = response.get('message', 'Unknown')
            if "đạt đến giới hạn" in msg.lower() or "limit" in msg.lower():
                return False, "LIMIT_REACHED"
            if "reward has been received" in msg.lower():
                return False, "CLAIMED"
            if "not exist" in msg.lower() or "finish" in msg.lower():
                return False, "EXHAUSTED"
            return False, msg
    except Exception as e:
        return False, str(e)

def load_data_comfirm_codexw():
    user_ids = []
    user_secretkeys = []
    try:
        if os.path.exists('data_xw_confirm_code.txt'):
            print(Fore.YELLOW + 'Phát hiện file dữ liệu cũ (data_xw_confirm_code.txt).')
            x = input(Fore.YELLOW + 'Bạn có muốn sử dụng lại không? (y/n): ' + Style.RESET_ALL).lower()
            if x == 'y':
                with open('data_xw_confirm_code.txt', 'r', encoding='utf-8') as f:
                    for line in f:
                        if '|' in line:
                            parts = line.strip().split('|')
                            if len(parts) >= 2:
                                user_ids.append(parts[0])
                                user_secretkeys.append(parts[1])
                if user_ids:
                    prints(0, 255, 0, f'✅ Đã load thành công {len(user_ids)} tài khoản.')
                    return user_ids, user_secretkeys
        
        print(Fore.CYAN + "--- NHẬP TÀI KHOẢN MỚI ---")
        try:
            num = int(input('Nhập số lượng tài khoản: '))
        except: num = 0
            
        for i in range(num):
            print(f"Nhập link Vua thoát hiểm của tài khoản {i+1}: ", end="")
            link = input().strip()
            try:
                uid = link.split('?userId=')[1].split('&')[0]
                key = link.split('secretKey=')[1].split('&')[0]
                user_ids.append(uid)
                user_secretkeys.append(key)
            except:
                print(Fore.RED + "Link lỗi, bỏ qua.")
        
        if user_ids:
            with open('data_xw_confirm_code.txt', 'w', encoding='utf-8') as f:
                for i in range(len(user_ids)):
                    f.write(f'{user_ids[i]}|{user_secretkeys[i]}\n')
            prints(0, 255, 0, '✅ Đã lưu dữ liệu vào file.')
            
        return user_ids, user_secretkeys
    except Exception as e:
        print(Fore.RED + f"Lỗi nhập liệu: {e}")
        sys.exit()

def main():
    clear_screen()
    banner()
    
    user_ids, user_secretkeys = load_data_comfirm_codexw()
    if not user_ids:
        print(Fore.RED + "Không có tài khoản nào. Thoát."); return
    
    for uid in user_ids:
        if uid not in user_claimed_history:
            user_claimed_history[uid] = set()

    print("\n" + Fore.CYAN + "--- CẤU HÌNH CANH CODE ---")
    codes = []
    while True:
        try:
            sl = int(input(Fore.YELLOW + "Nhập số lượng code muốn canh: " + Style.RESET_ALL))
            break
        except: print("Nhập số nguyên!")

    print(Fore.MAGENTA + "\nĐang kiểm tra thông tin code (Check giá trị)... Vui lòng đợi.")
    print("-" * 50)
    
    valid_codes = []
    
    for i in range(sl):
        c = input(f"Nhập code thứ {i+1}: ").strip()
        if not c: continue
        
        info = get_code_info(c)
        if info['status']:
            prints(0, 255, 255, f"🔰 CODE: {c}")
            prints(0, 255, 0,   f"   💰 Giá trị: {info['value']} {info['currency']}")
            prints(255, 165, 0, f"   📊 Tiến độ: {info['used']}/{info['total']} (Còn {info['remaining']})")
            valid_codes.append(c)
            last_log_time[c] = 0
            last_amount[c] = info['remaining']
        else:
            print(Fore.RED + f"❌ Code '{c}' lỗi hoặc không tồn tại: {info['message']}")
            
    if not valid_codes:
        print(Fore.RED + "Không có code nào hợp lệ để canh. Thoát."); return

    print("-" * 50)
    print(Fore.WHITE + "Ví dụ: Code có 300 lượt. Muốn nhập khi còn 10 lượt -> Gõ 10")
    try:
        threshold = int(input(Fore.YELLOW + "Nhập ngưỡng số lượt còn lại để bắt đầu cướp: " + Style.RESET_ALL))
    except: threshold = 5

    clear_screen()
    banner()
    prints(32, 230, 151, f"🔥 ĐANG CANH {len(valid_codes)} CODE VỚI {len(user_ids)} TÀI KHOẢN 🔥".center(50))
    print(Fore.WHITE + "(Tool sẽ tự động điều chỉnh tốc độ check dựa trên số lượng code còn lại)")
    prints(247, 255, 97,"═" * 47)
    
    # Dòng in đè tránh spam
    sys.stdout.write(Fore.CYAN + "⏳ Đang khởi tạo tiến trình canh code...\r") 

    while True:
        if len(limit_reached_users) >= len(user_ids):
            print()
            prints(255, 0, 0, "❌ TẤT CẢ TÀI KHOẢN ĐỀU ĐÃ ĐẠT GIỚI HẠN NHẬP CODE TRONG NGÀY. DỪNG TOOL.")
            break

        if not valid_codes:
            print()
            print(Fore.RED + "Tất cả code đã hết hoặc xong. Dừng tool."); break

        # Tính toán delay động dựa trên tình trạng code
        min_sleep_time = 5.0 # Mặc định check chậm
        critical_code_info = "" # Text hiển thị code quan trọng nhất

        for code in list(valid_codes): 
            eligible_users_indices = []
            for idx, uid in enumerate(user_ids):
                if uid not in limit_reached_users and code not in user_claimed_history[uid]:
                    eligible_users_indices.append(idx)
            
            # Nếu tài khoản đã nhập hết code này rồi thì bỏ qua
            if not eligible_users_indices:
                active_users_count = len(user_ids) - len(limit_reached_users)
                if active_users_count > 0:
                    claimed_count = sum(1 for uid in user_ids if uid not in limit_reached_users and code in user_claimed_history[uid])
                    if claimed_count == active_users_count:
                        print()
                        prints(0, 255, 0, f"✅ Tất cả tài khoản đã xong code '{code}'. Ngừng canh code này.")
                        valid_codes.remove(code)
                continue

            info = get_code_info(code)
            
            if not info['status']:
                continue
            
            remaining = info['remaining']
            curr_time = time.time()
            time_str = time.strftime("%H:%M:%S")

            # --- LOGIC HIỂN THỊ THÔNG MINH ---
            # Chỉ in LOG DÒNG MỚI nếu:
            # 1. Đã quá 60s chưa báo cáo
            # 2. Hoặc số lượng giảm đột biến (có người đang nhập)
            # 3. Hoặc số lượng còn rất ít (nguy cấp)
            
            should_print_log = False
            if (curr_time - last_log_time.get(code, 0) > 60): 
                should_print_log = True
            elif remaining < last_amount.get(code, remaining) and remaining <= threshold + 50:
                 # Nếu số lượng giảm và đang gần ngưỡng -> In ngay để biết
                should_print_log = True
            
            # Cập nhật số lượng cũ
            last_amount[code] = remaining

            if should_print_log:
                print() # Xuống dòng để không đè lên dòng trạng thái
                color = (0, 255, 0) if remaining > threshold + 10 else (255, 165, 0)
                prints(color[0], color[1], color[2], 
                       f"[{time_str}] {code} | Còn: {remaining}/{info['total']} | Val: {info['value']} {info['currency']}")
                last_log_time[code] = curr_time
            
            # Cập nhật dòng trạng thái (in đè - không spam)
            # Lấy code có số lượng ít nhất để hiển thị ưu tiên
            status_color = Fore.GREEN if remaining > threshold + 20 else Fore.YELLOW
            if remaining <= threshold + 5: status_color = Fore.RED
            
            critical_code_info = f"{status_color}[{time_str}] Checking {code}: {remaining} left...{Style.RESET_ALL}"
            sys.stdout.write(f"\r{critical_code_info}".ljust(60))
            sys.stdout.flush()

            # --- LOGIC TẤN CÔNG ---
            if remaining <= threshold and remaining > 0:
                print() # Xuống dòng
                prints(255, 0, 0, f"🚀 [{time_str}] CODE '{code}' CÒN {remaining} LƯỢT! TẤN CÔNG !!!")
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=len(eligible_users_indices)) as executor:
                    futures = {
                        executor.submit(nhap_code, user_ids[i], user_secretkeys[i], code): user_ids[i] 
                        for i in eligible_users_indices
                    }
                    
                    for future in concurrent.futures.as_completed(futures):
                        uid = futures[future]
                        try:
                            success, msg = future.result()
                            if success:
                                _, u, v, c = msg.split('|')
                                prints(0, 255, 255, f"✅ [{u}] Nhập thành công! +{v} {c}")
                                user_claimed_history[u].add(code)
                            else:
                                if msg == "CLAIMED":
                                    prints(100, 100, 100, f"⚠️ [{uid}] Đã nhập trước đó.")
                                    user_claimed_history[uid].add(code) 
                                elif msg == "LIMIT_REACHED":
                                    prints(255, 0, 0, f"❌ [{uid}] Đạt giới hạn ngày! Ngừng dùng acc này.")
                                    limit_reached_users.add(uid)
                                elif msg == "EXHAUSTED":
                                    prints(255, 0, 0, f"❌ [{uid}] Code hết lượt.")
                                else:
                                    prints(255, 0, 0, f"❌ [{uid}] Lỗi: {msg}")
                        except Exception as e:
                            print(f"Lỗi luồng: {e}")

                final_check = get_code_info(code)
                if final_check['status'] and final_check['remaining'] <= 0:
                    prints(255, 0, 0, f"💀 Code '{code}' đã hết sạch. Xóa khỏi list.")
                    valid_codes.remove(code)
                
            elif remaining <= 0:
                print()
                prints(255, 0, 0, f"💀 Code '{code}' đã hết lượt (0). Xóa khỏi danh sách.")
                if code in valid_codes: valid_codes.remove(code)
            
            # --- LOGIC ĐIỀU CHỈNH TỐC ĐỘ (SMART DELAY) ---
            # Nếu code còn ít lượt -> giảm thời gian ngủ để check nhanh hơn
            if remaining < threshold + 30:
                current_sleep = 0.5 # Rất nhanh
            elif remaining < 100:
                current_sleep = 1.5 # Trung bình
            elif remaining < 500:
                current_sleep = 3.0 # Chậm
            else:
                current_sleep = 10.0 # Rất chậm để tiết kiệm tài nguyên
            
            if current_sleep < min_sleep_time:
                min_sleep_time = current_sleep

        # Ngủ theo thời gian ngắn nhất cần thiết của code quan trọng nhất
        time.sleep(min_sleep_time) 

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nĐã dừng tool.")
