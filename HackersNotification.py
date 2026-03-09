from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# for loading environment variables
import os
from dotenv import load_dotenv

# for date handling
import datetime

# for scheduling
import schedule
import time

# for sending email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# for credentials management
import json
import tkinter as tk
from tkinter import messagebox

CONFIG_FILE = 'config.json'

def get_credentials():
    # 1. 기존 설정 파일 로드 시도
    required_keys = ['HACKERSID', 'HACKERSPW', 'GMAIL', 'GMAILPW', 'USER1MAIL']
    existing_data = {}
    
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
                # 모든 필수 정보가 있다면 바로 반환 (자동화 유지)
                if all(existing_data.get(k) for k in required_keys):
                    return existing_data
            except json.JSONDecodeError:
                pass

    # 2. 정보가 부족하거나 파일이 없으면 GUI 실행
    result = {}

    def save_and_exit():
        vals = {
            'HACKERSID': entry_h_id.get().strip(),
            'HACKERSPW': entry_h_pw.get().strip(),
            'GMAIL': entry_gmail.get().strip(),
            'GMAILPW': entry_gmail_pw.get().strip(),
            'USER1MAIL': entry_user_mail.get().strip()
        }
        
        if all(vals.values()):
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(vals, f, ensure_ascii=False, indent=4)
            result.update(vals)
            root.destroy()
        else:
            messagebox.showwarning("입력 오류", "모든 항목을 정확히 입력해주세요.")

    root = tk.Tk()
    root.title("해커스 알림 설정")
    root.geometry("350x480")
    
    # 입력창 생성을 돕는 함수
    def create_entry(label_text, key, is_password=False):
        tk.Label(root, text=label_text).pack(pady=(5, 0))
        entry = tk.Entry(root, width=30, show="*" if is_password else None)
        # 기존 데이터가 있으면 채워넣기
        if existing_data.get(key):
            entry.insert(0, existing_data[key])
        entry.pack(pady=2)
        return entry

    tk.Label(root, text="[해커스 계정 정보]", font=('Arial', 10, 'bold')).pack(pady=(15, 5))
    entry_h_id = create_entry("아이디:", "HACKERSID")
    entry_h_pw = create_entry("비밀번호:", "HACKERSPW", True)

    tk.Label(root, text="[이메일 알림 설정]", font=('Arial', 10, 'bold')).pack(pady=(20, 5))
    entry_gmail = create_entry("보낼 Gmail 주소:", "GMAIL")
    entry_gmail_pw = create_entry("Gmail 앱 비밀번호 (16자리):", "GMAILPW", True)
    entry_user_mail = create_entry("알림 받을 이메일 주소:", "USER1MAIL")

    tk.Button(root, text="설정 저장 및 시작", command=save_and_exit, bg='#4CAF50', fg='white', width=20, height=2).pack(pady=25)

    root.mainloop()
    return result if result else None

HACKERS_ENDPOINT = 'https://champ.hackers.com/?r=champstudy&c=mypage/my_lec/my_lec_refund&sub=refund_class_view&odri_id=1499326525'

options = webdriver.ChromeOptions()  
options.add_argument('--headless')  # 창을 띄우지 않고 실행
options.add_argument('--disable-gpu')  # GPU 사용 안함
options.add_argument("lang=ko_KR")
options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
driver = webdriver.Chrome(options=options)

driver.get(HACKERS_ENDPOINT)

# 모든 설정 정보 가져오기
creds = get_credentials()

if not creds:
    print("설정 정보가 입력되지 않아 종료합니다.")
    driver.quit()
    exit()

driver.find_element(By.NAME, 'login_id').send_keys(creds['HACKERSID'])
driver.find_element(By.NAME, 'password').send_keys(creds['HACKERSPW'])
driver.find_element(By.CLASS_NAME, 'btn-com').click()

wait = WebDriverWait(driver, 10)
login_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div[3]/div[2]/div[2]/table/caption')))
#로그인 완료


#로그인 후 오늘 날짜 달력 찾기
today = datetime.datetime.now()

today_callendar = driver.find_elements(By.CLASS_NAME, 'date')
parent_element = today_callendar[today.day-1].find_element(By.XPATH, '..')
icon_elements = parent_element.find_elements(By.TAG_NAME, 'span')


header = f'[해커스 알림] {today.month}월 {today.day}일 해커스 학습 알림'
body =  f'환급받는 그날까지!\n오늘은 {today.month}월 {today.day}일 입니다. 아직 해커스 학습을 완료하지 않았습니다. 해커스 달력 아이콘을 확인하여 주세요.\n{HACKERS_ENDPOINT}\n환급받는 그날까지 화이팅!'
if len(icon_elements) == 1:
    # 1. 메일 객체 생성
    msg = MIMEMultipart()
    msg['Subject'] = header
    msg['From'] = creds['GMAIL']
    msg['To'] = creds['USER1MAIL']

    # 2. 본문 설정
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # 3. 메일 전송
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(creds['GMAIL'], creds['GMAILPW'])
            server.send_message(msg)
        print("메일 전송 완료!")
    except Exception as e:
        print(f"오류 발생: {e}")

driver.quit()

