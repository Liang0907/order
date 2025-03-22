import time
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from PIL import Image
import io
from datetime import datetime
import os
import logging
import sys

#顯示當前版本
VERSION = "3.4"
logging.info(f"自動化腳本 - 版本號: {VERSION}")
print(f"=== 訂單擷取工具 - 版本 {VERSION} ===")


VERSION_URL = "https://your-server.com/version.txt"  # 版本號檢查網址
SCRIPT_URL = "https://your-server.com/latest_script.py"  # 最新腳本下載網址
SCRIPT_NAME = "3.4.py"  # 本地腳本名稱

def check_for_update():
    try:
        response = requests.get(VERSION_URL)
        latest_version = response.text.strip()

        if latest_version > VERSION:
            print(f"發現新版本: {latest_version}，正在更新...")
            download_latest_version()
        else:
            print("當前已是最新版本")
    except Exception as e:
        print(f"檢查更新失敗: {e}")

def download_latest_version():
    try:
        response = requests.get(SCRIPT_URL)
        with open(SCRIPT_NAME, "wb") as f:
            f.write(response.content)
        print("更新完成，請重新啟動程式")
        os._exit(0)  # 結束程式，讓使用者重新執行
    except Exception as e:
        print(f"下載更新失敗: {e}")

# 啟動時檢查更新
check_for_update()










# 設定 logging，將訊息存到 log 檔案，並在 console 顯示
logging.basicConfig(
    level=logging.INFO,  # 設定日誌級別，可選 DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(levelname)s - %(message)s",  # 設定輸出格式
    handlers=[
        logging.FileHandler("script.log", mode="a", encoding="utf-8"),  # 記錄到檔案
        logging.StreamHandler()  # 顯示在 console
    ]
)

# 設定 Chrome 選項
options = uc.ChromeOptions()
options.add_argument("--headless=new")  # 這樣可以避免顯示瀏覽器視窗
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-extensions")
options.add_argument("--disable-popup-blocking")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
)
options.add_argument("--incognito")
# 禁用所有日誌
logging.getLogger('undetected_chromedriver').setLevel(logging.CRITICAL)
# 啟動 WebDriver，這裡加上選項
driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 10)


# 目標網址
url = "https://eat.tagfans.com/ai/?GID=10901&noteId=9892379"
driver.get(url)

try:
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # 點擊日期選擇按鈕
    date_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="provide1"]/div/div[2]/div/div[2]/div/div[2]/div/div/div/div[1]/a/div/div[1]')
    ))
    driver.execute_script("arguments[0].click();", date_button)
    # 成功訊息
    logging.info("✅ 成功點擊日期選擇按鈕")

    # 點擊『確認』按鈕
    confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., '確認')]")))
    driver.execute_script("arguments[0].click();", confirm_button)
    logging.info("✅ 點擊『確認』進入登入流程")


    # 讓使用者選擇 A, N, P
    valid_choices = {'A': '01', 'N': '14', 'P': '16'}
    while True:
        choice = input("請輸入員編英文字母 (A, N, P): ").strip().upper()
        if choice in valid_choices:
            break
        logging.error("⚠️ 輸入不正確，請重新輸入 A, N 或 P。")

    # 輸入員工編號後四碼
    while True:
        last_four_digits = input("請輸入員工編號後四碼: ").strip()
        if re.match(r"^\d{4}$", last_four_digits):
            break
        logging.error("⚠️ 請輸入正確的 4 位數字！")

    # 創建資料夾名稱 (員編英文字母 + 後四碼)
    folder_name = f"{choice}{last_four_digits}"
    folder_path = os.path.join(os.getcwd(), folder_name)  # 使用當前工作目錄創建資料夾

    # 如果資料夾不存在則創建資料夾
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logging.info(f"✅ 資料夾已創建: {folder_path}")
    else:
        # 警告訊息
        logging.warning("⚠️ 資料夾已存在: %s", folder_path)

    phone_number = f"0031799493{valid_choices[choice]}00{last_four_digits}"
    logging.info(f"✅ 登入號碼為: {phone_number}")

    # 填入員工編號
    phone_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="phone"]')))
    phone_input.send_keys(phone_number)

    # 點擊『下一步』
    next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), '下一步')]")))
    driver.execute_script("arguments[0].click();", next_button)
    logging.info("✅ 點擊『下一步』按鈕")

    # 點擊『menu』
    menu_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'menu')]")))
    driver.execute_script("arguments[0].click();", menu_button)
    logging.info("✅ 點擊『menu』按鈕")

    # 點擊『查看訂單』
    order_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(., '查看訂單') and @class='asi-name']"))
    )
    driver.execute_script("arguments[0].click();", order_button)
    logging.info("✅ 點擊『查看訂單』")

    # 等待訂單列表載入
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.history-nav-block.history-layout-title')))




    # **滾動頁面確保所有訂單載入**
    def scroll_to_bottom():
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    scroll_to_bottom()

    # **找到所有訂單**
    orders = driver.find_elements(By.XPATH, '//*[@id="main"]/div/div/div[2]/div/div/div')

    # 取得當前年份
    current_year = datetime.now().year

    # 取得當前年份
    current_year = datetime.now().year

    # 處理日期範圍
    start_date = None
    end_date = None

    while True:
        start_date_input = input("請輸入取餐區間的開始日期 (格式: MM/DD)，若不指定請直接按 Enter: ").strip()

        if not start_date_input:  # 若使用者沒有輸入開始日期
            start_date = None
            break  # 跳出循環，不需要再詢問結束日期

        end_date_input = input("請輸入取餐區間的結束日期 (格式: MM/DD): ").strip()

        # 檢查日期區間是否有效
        try:
            start_date = datetime.strptime(f"{current_year}/{start_date_input}", "%Y/%m/%d")
            end_date = datetime.strptime(f"{current_year}/{end_date_input}", "%Y/%m/%d")

            if start_date > end_date:
                logging.error("⚠️ 開始日期不可晚於結束日期，請重新輸入！")
                continue  # 重新輸入日期
            break  # 日期區間有效，跳出循環
        except ValueError:
            logging.error("⚠️ 請輸入正確的日期格式 (MM/DD)！")

    # **顯示訂單總數**
    total_orders = len(orders)
    logging.info(f"📋 總共有 {total_orders} 筆訂單")
    # 檢查是否有輸入日期，若沒有則設為 None 來表示不篩選日期

    # 訂單遍歷部分，加入日期篩選
    for index, order in enumerate(orders):
        # 檢查是否有「已取消」的狀態
        try:
            status_element = order.find_element(By.XPATH, './/span[contains(@class, "statusCode")]')
            status_text = status_element.text.strip()

            if status_text == "已取消":
                logging.info(f"❌ 第 {index + 1} 筆訂單為『已取消』")
                continue  # 跳過這筆訂單
        except NoSuchElementException:
            logging.error(f"⚠️ 找不到訂單狀態，第 {index + 1} 筆訂單可能格式不同")

        # 確保訂單區塊可見
        driver.execute_script("arguments[0].scrollIntoView();", order)
        time.sleep(2)  # 等待頁面渲染

        # **第一筆訂單 (index = 0)** 只點擊「領貨條碼」
        if index == 0:
            try:
                pickup_button = order.find_element(By.XPATH, './/label[contains(text(), "領貨條碼")]')
                driver.execute_script("arguments[0].click();", pickup_button)
                logging.info(f"✅ 正在讀取 第 {index + 1} 筆訂單")
                time.sleep(2)
            except Exception as e:
                logging.warning(f"⚠️ 無法點擊領貨條碼: {str(e)}")

        # **從第二筆訂單開始 (index > 0)** 依序點擊「詳細資訊」→「領貨條碼」→「商品明細」
        else:
            try:
                # 點擊「詳細資訊」
                detail_button = order.find_element(By.XPATH, './/div[2]/div[1]/div[2]/div/div/div/a/div/div[1]')
                driver.execute_script("arguments[0].click();", detail_button)
                logging.info(f"✅ 正在讀取 第 {index + 1} 筆訂單")
                time.sleep(1)

                # 點擊「領貨條碼」
                pickup_button = order.find_element(By.XPATH, './/label[contains(text(), "領貨條碼")]')
                driver.execute_script("arguments[0].click();", pickup_button)
                # print(f"✅ 已點擊 第 {index + 1} 筆訂單的『領貨條碼』")
                time.sleep(1)

                # 點擊「商品明細」
                product_button = order.find_element(By.XPATH, './/div[2]/div[1]/div[4]/div/div/div/a/div/div[1]')
                driver.execute_script("arguments[0].click();", product_button)
                # print(f"✅ 已點擊 第 {index + 1} 筆訂單的『商品明細』")
                time.sleep(1)
            except Exception as e:
                logging.warning(f"⚠️ 點擊詳細資訊、領貨條碼或商品明細失敗: {str(e)}")

        try:
            # **找到包含「取餐時間」的元素**
            pickup_label = order.find_element(By.XPATH,
                                              './/div[contains(@class, "adm-list-item-content-main") and contains(text(), "取餐時間")]')

            # **找到對應的時間元素**
            pickup_time_element = pickup_label.find_element(By.XPATH,
                                                            './following-sibling::div[contains(@class, "adm-list-item-content-extra")]')
            pickup_time = pickup_time_element.text.strip()  # 取出文字

            # **將取餐時間轉換為 datetime 物件，並加上當前年份**
            pickup_datetime = datetime.strptime(f"{current_year}/{pickup_time}", "%Y/%m/%d %H:%M")
            # 只比較日期，不考慮時間
            pickup_date = pickup_datetime.date()

            # 檢查取餐時間是否為過期
            if pickup_datetime < datetime.now():
                logging.warning(f"⚠️ 訂單 {index + 1} 的取餐時間: {pickup_time} 取餐時間已過期，跳過此筆訂單")
                sys.exit()  # 終止程式執行

            # 如果有選定日期範圍，再進行區間檢查
            if start_date and end_date:
                if not (start_date.date() <= pickup_datetime.date() <= end_date.date()):
                    logging.error(f"❌ 訂單 {index + 1} 的取餐時間: {pickup_time} 不在選定的區間內")
                    continue  # 跳過此筆訂單
                else:
                    logging.info(f"✅ 訂單 {index + 1} 取餐時間: {pickup_time}")  # 顯示取餐時間
            else:
                logging.info(f"✅ 訂單 {index + 1} 取餐時間: {pickup_time}")  # 顯示取餐時間



            # **格式化時間 (03/13 11:30 → 03-13_11-30)**
            formatted_time = pickup_time.replace("/", "-").replace(":", "-")
            driver.execute_script("arguments[0].scrollIntoView(false);", order)
            time.sleep(2)  # 等待頁面渲染

            # **提高 Selenium 視窗解析度**
            driver.set_window_size(3840, 2160)  # 4K 超高解析度

            # **檢查檔名是否已存在，若存在則加數字**
            file_base = f"{formatted_time}"
            file_path = os.path.join(folder_path, f"{file_base}.png")
            counter = 1

            while os.path.exists(file_path):  # 如果檔案已存在，則加數字
                file_path = os.path.join(folder_path, f"{file_base}_{counter}.png")
                counter += 1

            # **直接存成 file_path**
            screenshot = order.screenshot_as_png
            image_pil = Image.open(io.BytesIO(screenshot))

            # **設定目標尺寸 (以公分計算)**
            target_width_cm = 6  # 你可以修改成你要的尺寸
            target_height_cm = 8  # 你可以修改成你要的尺寸
            dpi = 600  # 設定為 600 DPI

            # **將 cm 轉換為像素 (1 英吋 = 2.54 cm)**
            target_width_px = int((target_width_cm / 2.54) * dpi)
            target_height_px = int((target_height_cm / 2.54) * dpi)

            # **調整圖片大小，不失真縮放**
            resized_image = image_pil.resize((target_width_px, target_height_px), Image.LANCZOS)

            # **儲存圖片，設定 600 DPI**
            resized_image.save(file_path, dpi=(600, 600))
            print(f"📝 圖片已儲存成功: {file_path}")

            from PIL import Image
            import os
            from math import ceil

            # 設定 A4 紙張尺寸（600 DPI）
            A4_WIDTH, A4_HEIGHT = 4961, 7016  # 210 x 297 mm in pixels at 600 DPI
            IMAGE_WIDTH, IMAGE_HEIGHT = 1417, 1890  # 6 x 8 cm in pixels at 600 DPI
            IMAGES_PER_ROW = 3  # 一行最多 3 張
            IMAGES_PER_COL = 3  # 一列最多 3 張
            IMAGES_PER_PAGE = IMAGES_PER_ROW * IMAGES_PER_COL  # A4 一頁最多 9 張

            # 圖片來源資料夾
            folder_path = folder_name  # ⚠️ 替換為實際的圖片存放資料夾
            output_folder = os.path.join(folder_path, "A4_Pages")  # 輸出資料夾
            os.makedirs(output_folder, exist_ok=True)

            # 取得資料夾內的所有圖片
            image_files = [f for f in sorted(os.listdir(folder_path)) if f.endswith((".png", ".jpg", ".jpeg"))]

            # 計算總共需要幾頁
            num_pages = ceil(len(image_files) / IMAGES_PER_PAGE)

            # 開始生成 A4 排列圖
            for page in range(num_pages):
                # 創建 A4 畫布（白色背景）
                a4_canvas = Image.new("RGB", (A4_WIDTH, A4_HEIGHT), "white")

                # 當前頁面的圖片索引範圍
                start_idx = page * IMAGES_PER_PAGE
                end_idx = min(start_idx + IMAGES_PER_PAGE, len(image_files))

                # 逐一貼上圖片
                for i, img_name in enumerate(image_files[start_idx:end_idx]):
                    img_path = os.path.join(folder_path, img_name)
                    img = Image.open(img_path).convert("RGB")
                    img = img.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.LANCZOS)

                    # 計算圖片擺放位置
                    row = i // IMAGES_PER_ROW
                    col = i % IMAGES_PER_ROW
                    x_offset = col * IMAGE_WIDTH + (col + 1) * 50  # 左右間隔 50px
                    y_offset = row * IMAGE_HEIGHT + (row + 1) * 50  # 上下間隔 50px

                    # 貼上圖片
                    a4_canvas.paste(img, (x_offset, y_offset))

                # 儲存 A4 圖片
                a4_output_path = os.path.join(output_folder, f"A4_Page_{page + 1}.png")
                a4_canvas.save(a4_output_path, dpi=(600,600))
                print(f"✅ A4 頁面 {page + 1} 儲存成功: {a4_output_path}")

            # **可選**：將所有 A4 圖片轉換為 PDF
            pdf_output_path = os.path.join(folder_path,"All_Order.pdf")
            a4_images = [Image.open(os.path.join(output_folder, f"A4_Page_{i + 1}.png")).convert("RGB") for i in
                         range(num_pages)]
            a4_images[0].save(pdf_output_path, save_all=True, append_images=a4_images[1:])
            print(f"✅ 所有頁面已輸出為 PDF: {pdf_output_path}")


        except TimeoutException:
            logging.warning(f"⚠️ 取餐時間載入超時，第 {index + 1} 筆訂單可能有問題")
        except NoSuchElementException:
            logging.warning(f"⚠️ 無法找到取餐時間，第 {index + 1} 筆訂單可能有問題")

finally:
    driver.quit()
    input("📌 已擷取完成，請按任意鍵結束...")