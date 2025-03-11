import requests
from bs4 import BeautifulSoup

def fetch_tvbs_news():
    url = 'https://news.tvbs.com.tw/'
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    news_list = []
    for item in soup.find_all('div', class_='news_list'):
        title = item.find('h2').text.strip()
        link = item.find('a')['href']
        news_list.append({'title': title, 'link': link})

    return news_list

if __name__ == "__main__":
    news = fetch_tvbs_news()
    for item in news:
        print(f"Title: {item['title']}")
        print(f"Link: {item['link']}")
        print()