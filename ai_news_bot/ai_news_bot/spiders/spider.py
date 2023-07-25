import scrapy 
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity



class My_Spider(scrapy.Spider):
    name = 'url_spider'
    results = {"title": [], "url": [], "publish_date": []}

    def start_requests(self):
        urls = []
        number_of_pages = int(input("Enter Number of Pages: "))
        for i in range(1, number_of_pages+1): urls.append('https://ainewstoday.co.uk/page/' + str(i) + '/')
        
        for url in urls:
            yield scrapy.Request(url = url, callback = self.parse)
        
    def parse(self, response):
        div_elements = response.xpath('//div[contains(@class, "bdp-post-list-content")]//a')
        for element in div_elements:
            text = element.xpath('text()').get()
            href = element.xpath('@href').get()
            publish_date = urlparse(href).path
            segments = publish_date.split('/')
            publish_date = f"{segments[1]}-{segments[2]}-{segments[3]}"
            
            if text.strip() != "" and href.strip() != "" and text.lower()!="read more":
                # write in file
                self.results['title'].append(text)
                self.results['url'].append(href)
                self.results['publish_date'].append(publish_date)

    def closed(self, reason):
        df = pd.DataFrame(self.results)
        try: 
            DF = pd.read_csv("news_url.csv", usecols=['title', 'url', 'publish_date'])
            df = pd.concat([df, DF]).drop_duplicates().reset_index(drop=True)
        except: print("file does not exist.")
        df = df.sort_values(by="publish_date", ascending=False, ignore_index=True)
        df.to_csv('news_url.csv')


class News_Spider(scrapy.Spider):
    name = 'news_spider'
    news_results = {'title': [], 'url': [], 'content': [], 'content_summary': [], 'thumbnail': [], 'publish_date': []}
    
    def start_requests(self):
        df = pd.read_csv('news_url.csv')
        number_of_post = int(input(f"Enter Number Of Posts [{len(df['title'])} posts has been crawlerd]: "))
        urls = list(df['url'])[:number_of_post]

        for url in urls:
            yield scrapy.Request(url = url, callback = self.parse)
    

    def check_nltk_and_punkt(self):
        try: nltk.data.find('tokenizers/punkt')
        except LookupError: nltk.download('punkt')


    def summarize_text(self, text, num_sentences):
        self.check_nltk_and_punkt()
        sentences = sent_tokenize(text)
        vectorizer = CountVectorizer().fit_transform(sentences)
        vectors = vectorizer.toarray()
        similarity_matrix = cosine_similarity(vectors)
        scores = similarity_matrix.sum(axis=1)
        ranked_sentences = [sentences[i] for i in scores.argsort()[-num_sentences:]]
        summarized_text = ' '.join(ranked_sentences)
        return summarized_text


    def parse(self, response):
        title = response.xpath('//h1[contains(@class, "entry-title")]/text()').get()
        url = response.url
        content = response.xpath('//div[contains(@class, "entry-content")]').get()
        thumbnail = response.xpath('//div[contains(@class, "post-thumbnail")]//img/@src').get()
        publish_date = response.xpath('//span[contains(@class, "posts-date")]//a/text()').get()

        soup = BeautifulSoup(content, 'html.parser')
        all_text = soup.find_all('p')[:-2]
        text_list = [p.get_text(strip=False) for p in all_text]
        content = '\n'.join(text_list)
        content = content.strip()
        content_summary = self.summarize_text(text=content, num_sentences=5)

        # write in file
        self.news_results['title'].append(title.strip())
        self.news_results['url'].append(url)
        self.news_results['content'].append(content)
        self.news_results['content_summary'].append(content_summary)
        self.news_results['thumbnail'].append(thumbnail)
        self.news_results['publish_date'].append(publish_date.strip())


    def closed(self, reason):
        df = pd.DataFrame(self.news_results)
        try:
            DF = pd.read_csv("news_content.csv", usecols=['title', 'url', 'content', 'content_summary', 'thumbnail', 'publish_date'])
            df = pd.concat([df, DF]).drop_duplicates().reset_index(drop=True)
        except: print("file does not exist.")
        df['publish_date'] = pd.to_datetime(df['publish_date'])
        df = df.sort_values(by="publish_date", ascending=False, ignore_index=True)
        df.to_csv('news_content.csv')
