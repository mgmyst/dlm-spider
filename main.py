from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
import sqlite3
import re
import sys


def crawl(count=10, sleep=0, is_db_reset=False):
    # 使用する変数の初期化
    get_id = 1008000
    error_count = 0

    # ヘッドレスブラウザの用意
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # ローカル向け
    # chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    # driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options)

    # Colab向け
    sys.path.insert(0, '/usr/lib/chromium-browser/chromedriver')
    chrome_options.binary_location = '/usr/bin/chromium-browser'
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_argument('--disable-software-rasterizer')
    driver = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()), options=chrome_options)

    # データベースの用意
    # connection = sqlite3.connect("db/sqlite.db")
    connection = sqlite3.connect("/content/drive/MyDrive/Colab Notebooks/db/sqlite.db")
    cursor = connection.cursor()
    if is_db_reset:
        sql_file = 'db/_create_works_table.sql'
        with open(sql_file, 'r') as file:
            sql_script = file.read()

        cursor = connection.cursor()
        cursor.executescript(sql_script)
        connection.commit()

    # スクレイピング
    for i in range(count):
        # htmlファイルの取得
        url = f"https://www.dlsite.com/maniax/work/=/product_id/RJ0{get_id}"
        try:
            # URLからコンテンツを取得
            driver.get(url)
            target_file = driver.page_source

            # ファイルにコンテンツを出力
            with open("target.html", "w", encoding="utf-8") as out_file:
                out_file.write(target_file)

            # コンソールにログを表示
            print(f"RJ{get_id} is saved. Total {i+1} pages.")

        except Exception as e:
            # エラー処理
            print(f"ERROR! : {e}")
            error_count += 1

        # データのスクレイピングとDBへの保存
        with open("target.html", "r", encoding="utf-8") as file:
            content = file.read()

        # lxml の HTML パーサーを使ってパース
        parser = etree.HTMLParser()
        tree = etree.fromstring(content, parser)

        # XPath で 各種要素を取得
        # 作品ID
        product_id_element = tree.xpath('//div[@data-product-id]/@data-product-id')
        if product_id_element:
            product_id = product_id_element[0]
        else:
            continue  # idがとれない=404なのでとばす

        # 作品名
        work_name = '-'
        work_name_element = tree.xpath('//*[@id="work_name"]')
        if work_name_element:
            work_name = work_name_element[0].text

        # 作品リンク
        product_link = f"https://www.dlsite.com/maniax/work/=/product_id/{product_id}"

        # サークル名
        circle_name = '-'
        circle_name_element = tree.xpath('//*[@id="work_maker"]/tbody/tr/td/span/a')
        if circle_name_element:
            circle_name = circle_name_element[0].text

        # サークルリンク
        circle_link = '-'
        circle_link_element = tree.xpath('//*[@id="work_maker"]/tbody/tr/td/span/a/@href')
        if circle_link_element:
            circle_link = circle_link_element[0]

        # サークル設定価格
        price = '0'
        price_element = tree.xpath('//*[@id="work_price"]/div/div[2]/div[1]/div[2]/span/text()')
        if price_element:
            price = price_element[0]
        else:
            price_element = tree.xpath('//*[@id="work_price"]/div/div/div[1]/div[2]/span/text()')
            if price_element:
                price = price_element[0]
        price = price.replace(',', '')

        # 販売日
        release_date_string = '9999年12月31日'
        release_date_elements = tree.xpath('//table[@id="work_outline"]//th[text()="販売日"]/following-sibling::td/a')
        if release_date_elements:
            release_date_string = release_date_elements[0].text
        release_date_string = re.sub(" (.*?)$", '', release_date_string)
        release_date_obj = datetime.strptime(release_date_string, "%Y年%m月%d日")
        release_date = release_date_obj.strftime("%Y-%m-%d")

        # 販売日数
        days_elapsed = 0
        if release_date_string != '9999年12月31日':
            days_elapsed = (datetime.now() - release_date_obj).days

        # 年齢制限
        age_rating = '-'
        age_rating_element = tree.xpath('//table[@id="work_outline"]//span[@class="icon_ADL"]')
        if age_rating_element:
            age_rating = age_rating_element[0].text

        # 作品形式
        category = ' '.join(
            [element.text for element in
             tree.xpath('//table[@id="work_outline"]//div[@id="category_type"]/a/span')])

        # ファイル形式
        file_format = '-'
        file_format_element = tree\
            .xpath('//table[@id="work_outline"]//th[text()="ファイル形式"]/following-sibling::td/div/a/span')
        if file_format_element:
            file_format = file_format_element[0].text

        # その他
        other = '-'
        other_elements = tree.xpath('//table[@id="work_outline"]//th[text()="その他"]/following-sibling::td/div/span')
        if other_elements:
            other = other_elements[0].text

        # ジャンル
        genre_elements = tree.xpath(
            '//table[@id="work_outline"]//th[text()="ジャンル"]/following-sibling::td/div[@class="main_genre"]/a')
        genres = ' '.join([element.text for element in genre_elements])

        # ファイル容量
        file_size = '0'
        file_size_element = \
            tree.xpath(
                '//table[@id="work_outline"]//th[text()="ファイル容量"]/following-sibling::td/div[@class="main_genre"]'
            )
        if file_size_element:
            file_size = file_size_element[0].text.strip()
        file_size = file_size.replace("総計 ", '')

        # 販売数
        sales = '0'
        sales_elements = tree.xpath('//*[@id="work_right"]//dt[text()="販売数："]/following-sibling::dd')
        if sales_elements:
            sales = sales_elements[0].text
        else:
            sales_elements = tree.xpath('//*[@id="work_right"]/div[1]/div[2]/dl/dd[1]/text()')
            if sales_elements:
                sales = sales_elements[0]
        sales = sales.replace("\n            ", '')
        sales = sales.replace(",", '')

        # 評価
        average_rating = '0'
        average_rating_elements = tree.xpath('//*[@id="work_right"]//span[@class="point average_count"]')
        if average_rating_elements:
            average_rating = average_rating_elements[0].text

        # お気に入り数
        favorites = '0'
        favorites_elements = tree.xpath('//*[@id="work_right"]//dt[text()="お気に入り数："]/following-sibling::dd')
        if favorites_elements:
            favorites = favorites_elements[0].text
        favorites = favorites.replace(',', '')

        # レビュー数
        reviews = '0'
        review_elements = tree.xpath('//*[@id="work_right"]//dt[text()="レビュー数："]/following-sibling::dd/span')
        if review_elements:
            reviews = review_elements[0].text

        values = (
            f"{product_id}",
            f"{work_name}",
            f"{circle_name}",
            f"{price}",
            f"{release_date}",
            f"{days_elapsed}",
            f"{age_rating}",
            f"{category}",
            f"{file_format}",
            f"{genres}",
            f"{other}",
            f"{file_size}",
            f"{sales}",
            f"{average_rating}",
            f"{favorites}",
            f"{reviews}",
            f"{product_link}",
            f"{circle_link}"
        )

        try:
            cursor.execute("""
            INSERT INTO works (
                product_id, work_name, circle_name, price, release_date, days_elapsed, age_rating,
                category, file_format, genres, other, file_size, sales, average_rating, favorites,
                reviews, product_link, circle_link
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, values)
            connection.commit()
        except sqlite3.IntegrityError as e:
            print(e)
            print(f"Error has occurred at product_id:{product_id}")

        # 次のループのためにget_idをデクリメント
        get_id -= 1

        # 接続過多によるエラー防止のためのスリープ
        time.sleep(sleep)

    # WebDriverとDBへのコネクションを終了
    driver.quit()
    connection.close()


if __name__ == '__main__':
    crawl(10, 0, True)
