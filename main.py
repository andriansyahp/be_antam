from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from time import sleep
from urllib.parse import quote
from io import BytesIO
from typing import List, Optional
import json

import win32clipboard
from PIL import Image

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class People(BaseModel):
    nama: str
    number: str
    checkAll: bool
    
class PeopleList(BaseModel):
    data: List[People]
    segmen: str
    
@app.get("/")
def read_root():
    return {"Hello": "World"}

# @app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile = File(...)):
#     contents = file.file.read()
#     buffer = BytesIO(contents)
#     df = pd.read_excel(buffer)
#     buffer.close()
#     file.file.close()
#     # df = pd.read_excel(file.file, header=0)
    
#     options = Options()
#     options.add_experimental_option("excludeSwitches", ["enable-logging"])
#     options.add_argument("--profile-directory=Default")
#     driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
#     delay = 30
#     driver.get('https://web.whatsapp.com')
    
#     nama_number_dict = dict(zip(df['nama'].tolist(), df['no_telp'].tolist()))
#     for _, (nama, number) in enumerate(nama_number_dict.items()):
#         try:
#             message = "Hi" + " " + nama
#             number = "+" + str(number)
#             url = 'https://web.whatsapp.com/send?phone=' + str(number) + '&text=' + message
#             sent = False
#             for i in range(3):
#                 if not sent:
#                     driver.get(url)
#                     try:
#                         click_btn = WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='compose-btn-send']")))
#                     except Exception as e:
#                         print(f"\nFailed to send message to: {str(number)}, retry ({i+1}/3)")
#                         print("Make sure your phone and computer is connected to the internet.")
#                         print("If there is an alert, please dismiss it.")
#                     else:
#                         sleep(1)
#                         click_btn.click()
#                         sent=True
#                         sleep(3)
#         except Exception as e:
#             print('Failed to send message to ' + str(number) + str(e))
#         # print(k, v)
#     driver.close()
#     return {"filename": file.filename}

@app.post("/final/")
async def get_json_people_data(data: PeopleList):
    req = json.loads(data.json())
    req_dict = {key: [i[key] for i in req["data"]] for key in req["data"][0]}
    # print(req_dict)
    segmen = req["segmen"]
    
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--profile-directory=Default")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    delay = 30
    driver.get('https://web.whatsapp.com')
    
    # nama_number_dict = dict(zip(df['nama'].tolist(), df['no_telp'].tolist()))
    nama_number_dict = dict(zip(req_dict['nama'], req_dict['number']))
    for _, (nama, number) in enumerate(nama_number_dict.items()):
        try:
            message = "Hi" + " " + nama + ",\n"
            message = message + "\n \nKami ingin menawarkan produk " + segmen
            # number = "+" + str(number)
            number = str(number)
            url = 'https://web.whatsapp.com/send?phone=' + str(number) + '&text=' + message
            sent = False
            for i in range(3):
                if not sent:
                    driver.get(url)
                    try:
                        click_btn = WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='compose-btn-send']")))
                    except Exception as e:
                        print(f"\nFailed to send message to: {str(number)}, retry ({i+1}/3)")
                        print("Make sure your phone and computer is connected to the internet.")
                        print("If there is an alert, please dismiss it.")
                    else:
                        sleep(1)
                        click_btn.click()
                        sent=True
                        sleep(3)
        except Exception as e:
            print('Failed to send message to ' + str(number) + str(e))
        # print(k, v)
    driver.close()
    return data

def send_to_clipboard(clip_type, data):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(clip_type, data)
    win32clipboard.CloseClipboard()

@app.post("/send_img/")
async def send_image(file: UploadFile = File(...), img: UploadFile = File(None)):
    img_contents = img.file.read()
    img_buffer = BytesIO(img_contents)
    image = Image.open(img_buffer)
    
    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    img_data = output.getvalue()[14:]
    output.close()
    img_buffer.close()
    img.file.close()
    
    send_to_clipboard(win32clipboard.CF_DIB, img_data)
    
    file_contents = file.file.read()
    file_buffer = BytesIO(file_contents)
    raw_data = pd.read_csv(file_buffer, header=None)
    file_buffer.close()
    file.file.close()
    
    # looking for the header row
    for i, row in raw_data.iterrows():
        if row.notnull().all():
            df = raw_data.iloc[(i+1):].reset_index(drop=True)
            df.columns = list(raw_data.iloc[i])
            break
    # transforming columns to numeric where possible
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='ignore')
    
    
    # req = json.loads(data.json())
    # req_dict = {key: [i[key] for i in req["data"]] for key in req["data"][0]}
    # # print(req_dict)
    # segmen = req["segmen"]
    
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--profile-directory=Default")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    delay = 30
    driver.get('https://web.whatsapp.com')
    
    # nama_number_dict = dict(zip(df['nama'].tolist(), df['number'].tolist()))
    # nama_number_dict = dict(zip(req_dict['nama'], req_dict['number']))
    for _, row in df.iterrows():
    # for _, (nama, number) in enumerate(nama_number_dict.items()):
    # nama = 'Andri'
    # number = '+6285156454108'
        # segmen = "*" + str(df['segmen'][0]) + "*"
        try:
            segmen = row['segmen']
            # message = "Hi" + " " + nama + ",\n"
            # message = message + "\n \nKami ingin menawarkan produk " + segmen
            message = row['message'].replace("[name]", row['nama'])
            # number = "+" + str(number)
            # number = str(number)
            number = row['number']
            url = 'https://web.whatsapp.com/send?phone=' + str(number) + '&text=' + message
            # url = 'https://web.whatsapp.com/send?phone=' + str(number) + '&text='
            sent = False
            for i in range(3):
                if not sent:
                    driver.get(url)
                    try:
                        normal_send_btn = WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='compose-btn-send']")))
                        # click_btn = WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Send']")))
                        input_box = WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='conversation-compose-box-input']")))
                    except Exception as e:
                        print(f"\nFailed to send message to: {str(number)}, retry ({i+1}/3)")
                        print("Make sure your phone and computer is connected to the internet.")
                        print("If there is an alert, please dismiss it.")
                    else:
                        sleep(1)
                        input_box.send_keys(Keys.CONTROL, 'v')
                        # input_box.send_keys(message)
                        sleep(1)
                        click_btn = WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Send']")))
                        click_btn.click()
                        sent=True
                        sleep(7)
        except Exception as e:
            print('Failed to send message to ' + str(number) + str(e))
    # print(k, v)
    driver.close()
    return {"filename": file.filename}