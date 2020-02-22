import csv
import requests
from bs4 import BeautifulSoup

# 從網頁的分析中, 查到有清單在 javascript 語法中, 節錄下來折解清單內容
hotel = "[ ,[null,'中區旅館','./?mode=aG90ZWw==&class=NA==',null,'中區旅館'],,[null,'北屯區旅館','./?mode=aG90ZWw==&class=MQ==',null,'北屯區旅館'],,[null,'和平區旅館','./?mode=aG90ZWw==&class=MzM=',null,'和平區旅館'],,[null,'梧棲區','./?mode=aG90ZWw==&class=MzI=',null,'梧棲區'],,[null,'后里區旅館','./?mode=aG90ZWw==&class=MTU=',null,'后里區旅館'],,[null,'豐原區旅館','./?mode=aG90ZWw==&class=MTQ=',null,'豐原區旅館'],,[null,'大雅區','./?mode=aG90ZWw==&class=MzE=',null,'大雅區'],,[null,'大里區旅館','./?mode=aG90ZWw==&class=MTE=',null,'大里區旅館'],,[null,'太平區旅館','./?mode=aG90ZWw==&class=MTA=',null,'太平區旅館'],,[null,'東區旅館','./?mode=aG90ZWw==&class=OA==',null,'東區旅館'],,[null,'南區旅館','./?mode=aG90ZWw==&class=Nw==',null,'南區旅館'],,[null,'西區旅館','./?mode=aG90ZWw==&class=Ng==',null,'西區旅館'],,[null,'北區旅館','./?mode=aG90ZWw==&class=NQ==',null,'北區旅館'],,[null,'南屯區旅館','./?mode=aG90ZWw==&class=Mw==',null,'南屯區旅館'],,[null,'西屯區旅館','./?mode=aG90ZWw==&class=Mg==',null,'西屯區旅館'],,[null,'大安區旅館','./?mode=aG90ZWw==&class=MzA=',null,'大安區旅館']"
hotel = hotel.replace('[','')
hotel = hotel.replace(']','')
hotel = hotel.replace(',null','')
hotel = hotel.replace(',,',',')
hotel = hotel.replace("'","")
hotel_list = hotel.split(',')
del hotel_list[0]

# 清單內容解析為 hotel_area的 dict結構
hotel_area = {}
for i in range(0,len(hotel_list),3):
    hotel_area[hotel_list[i]] = hotel_list[i + 1].replace('./','http://www.thotel.org/')
#列出區域清單
print(hotel_area)
# 從 hotel_area中將所有區域連結網址都爬蟲下來
hotels_taichung = []
for area in hotel_area:
    url = hotel_area[area]    
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
    resp = requests.get(url, headers=headers)
# 設定編碼為 utf-8 避免中文亂碼問題
    resp.encoding = 'utf-8'
# 根據 HTTP header 的編碼解碼後的內容資料（ex. UTF-8），若該網站沒設定可能會有中文亂碼問題。所以通常會使用 resp.encoding 設定
    raw_html = resp.text
# 將 HTML 轉成 BeautifulSoup 物件，這裡使用 html.parser 內建解析器
    soup = BeautifulSoup(raw_html, 'html.parser')
# 利用 css select 來判斷是否有資料    
    if soup.select('#content_detail > div.side > div.p_page') != []:
# 利用 css select 取出資料筆數 及 頁數
        page = int(soup.select('#content_detail > div.side > div.p_page')[0].text.split('共')[1].split('頁')[0])
        total = int(soup.select('#content_detail > div.side > div.p_page')[0].text.split('共')[2].split('筆')[0])
        counter =  0
        for i in range(1,page + 1):
            url = url + '&page=' + str(i)
            resp = requests.get(url, headers=headers)
# 設定編碼為 utf-8 避免中文亂碼問題            
            resp.encoding = 'utf-8'
# 根據 HTTP header 的編碼解碼後的內容資料（ex. UTF-8），若該網站沒設定可能會有中文亂碼問題。所以通常會使用 resp.encoding 設定    
            raw_html = resp.text
# 將 HTML 轉成 BeautifulSoup 物件，這裡使用 html.parser 內建解析器    
            soup = BeautifulSoup(raw_html, 'html.parser')
            for j in range(1,21):
                hotel_taichung = {}
# 利用總筆數 total 控制 css select 要篩選的動作, 防止錯誤產生
                if counter < total:
                    counter += 1
                    css = '#content_detail > div.side > div:nth-child(' + str(j) + ')'
                    hotel_list = soup.select(css)[0].text.split('\n')
                    #列出飯店資料, 得知程式有動作
                    print(hotel_list)                    
                    hotel_taichung['name'] = hotel_list[6]
                    hotel_taichung['tel'] = hotel_list[9].replace('電話：','')
                    hotel_taichung['fax'] = hotel_list[10].replace('傳真：','')
                    hotel_taichung['address'] = hotel_list[13].replace('地址：','')
                    hotels_taichung.append(hotel_taichung)
#列出飯店清單, 確認寫入檔案有資料
print(hotels_taichung)
# CSV 檔案第一列標題記得要和 dict 的 key 相同，不然會出現錯誤
headers = ['name', 'tel', 'fax', 'address']
# 使用檔案 with ... open 開啟寫入檔案模式（w），透過 csv 模組將資料寫入工作資料
with open('hotel_taichung.csv', 'w', encoding='utf_8') as output_file:
    dict_writer = csv.DictWriter(output_file, headers)
    # 寫入標題
    dict_writer.writeheader()
    # 寫入值
    dict_writer.writerows(hotels_taichung)