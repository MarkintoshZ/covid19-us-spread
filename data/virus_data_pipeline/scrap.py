from time import sleep

from tqdm import trange
import numpy as np
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup


FILE_NAME = 'data/raw/virus.csv'
URL = 'https://coronavirus.1point3acres.com'

columns=['Case', 'Date', 'State', 'County']


def retrieve_data():
    data = []
    try: 
        browser = webdriver.Chrome()
        browser.get((URL))
        sleep(2)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        page_count = int(soup.find('li', attrs={'title': 'Next Page'}).find_previous('li').text.strip())
        for i in trange(page_count):
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            table = soup.find('div', attrs={"class": 'ant-table-wrapper'})
            rows = table.find_all('tr', attrs={"class": 'ant-table-row-level-0'})
            for r in rows:
                info = [children.text.strip() for children in r.find_all('td')[:4]]
                data.append(info)

            next_page_btn = browser.find_element_by_xpath(f"//li[@title='{i+1}']/a")
            # scroll to button
            browser.execute_script("arguments[0].scrollIntoView();", next_page_btn)
            browser.execute_script("window.scrollBy(0, arguments[0]);", -50)
            sleep(0.1)
            next_page_btn.click()
            sleep(0.1)
        
    except Exception as e:
        print(f'error: {e}')
    finally:
        browser.quit()
        if len(data) == 0:
            return None
        df = pd.DataFrame(data=np.array(data), columns=columns)
        return df


if __name__ == "__main__":
    df = retrieve_data()
    if df is not None:
        df.to_csv(FILE_NAME, index=False)
