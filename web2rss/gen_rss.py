import json
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time as time_module
from soupsieve.util import SelectorSyntaxError
from datetime import datetime
from urllib.parse import urljoin
import os
from feedparser import parse
from gen_summary import SummaryGenerator


def create_webdriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 启用无头模式
    chrome_options.add_argument("--no-sandbox")  # 解决 DevToolsActivePort 文件错误
    chrome_options.add_argument("--disable-dev-shm-usage")  # 解决资源限制
    chrome_options.add_argument("--disable-gpu")  # 如果不需要 GPU 加速，禁用它
    chrome_options.add_argument("--window-size=1920x1080")  # 设置窗口大小

    # 创建 Chrome 驱动
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    return driver

def load_config(config_path='config.json'):
    with open(config_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def fetch_blog_posts(config):
    print(f"Fetching posts from: {config['url']}")
    print(f"Using selectors: block={config['block_css']}, title={config['title_css']}, description={config['description_css']}, link={config['link_css']}")

    if config['use_headless_browser']:
        driver = create_webdriver()

        driver.get(config['url'])
        time_module.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
    else:
        response = requests.get(config['url'])
        soup = BeautifulSoup(response.content, 'html.parser')

    # 使用部分类名匹配
    blocks = soup.find_all('a', class_=lambda x: x and all(
        cls in x for cls in ['PostCard_post-card', 'PostList_post-card']
    ))
    print(f"找到 {len(blocks)} 个文章块")
    
    posts = []
    for i, block in enumerate(blocks):
        # 使用部分类名匹配查找元素
        title = block.find('h3', class_=lambda x: x and 'PostCard_post-heading' in x)
        description = block.find('span', class_='text-label')
        
        print(f"文章 {i + 1}:")
        print(f"- 标题选择器匹配: {'成功' if title else '失败'}")
        print(f"- 描述选择器匹配: {'成功' if description else '失败'}")
        print(f"- 链接选择器匹配: '成功'")  # 链接直接从 block (a标签) 获取
        
        if title and description:
            # 获取发布日期
            date_div = block.find('div', class_=lambda x: x and 'PostList_post-date' in x)
            date_text = date_div.get_text(strip=True) if date_div else ''
            
            # 获取文章分类
            category = block.find('span', class_='text-label').get_text(strip=True)
            
            # 组合描述信息
            full_description = f"分类: {category}"
            if date_text:
                full_description += f" | 发布时间: {date_text}"
            
            posts.append({
                'title': title.get_text(strip=True),
                'description': full_description,
                'link': urljoin(config['url'], block['href'])
            })
    
    print(f"成功提取 {len(posts)} 篇文章")
    return posts

def read_existing_rss(file_path):
    """读取现有的RSS文件中的条目"""
    if not os.path.exists(file_path):
        return set()
    
    feed = parse(file_path)
    existing_links = set()
    for entry in feed.entries:
        existing_links.add(entry.link)
    return existing_links

def generate_rss(posts, site, file_name):
    """生成RSS feed，合并现有的和新的条目"""
    # 初始化摘要生成器
    summary_generator = SummaryGenerator(
        api_key=os.getenv("GLM_API_KEY"),
        jina_api_key=os.getenv("JINA_API_KEY")
    )
    
    feed = FeedGenerator()
    feed.id(site['url'])
    feed.title(site['name'])
    feed.link(href=site['url'])
    feed.description(f"Latest posts from {site['url']}. follow.is: {site['follow_desc']}")

    # 读取现有的RSS文件中的条目
    existing_links = read_existing_rss(file_name)
    
    # 如果文件已存在，读取现有的条目并添加到feed中
    if os.path.exists(file_name):
        existing_feed = parse(file_name)
        for entry in existing_feed.entries:
            feed_entry = feed.add_entry()
            feed_entry.title(entry.title)
            feed_entry.link(href=entry.link)
            feed_entry.description(entry.description)
            if hasattr(entry, 'published'):
                feed_entry.published(entry.published)

    # 添加新的条目
    new_entries_count = 0
    for post in posts:
        if post['link'] not in existing_links:
            try:
                # 获取文章内容并生成摘要
                content = summary_generator._fetch_webpage_content(post['link'])
                summary = summary_generator.generate_summary(
                    post['description'] + content,
                    max_length=500,
                    language="en"  # 或从配置中读取语言设置
                )
                
                entry = feed.add_entry()
                entry.title(post['title'])
                entry.link(href=post['link'])
                entry.description(summary)  # 使用生成的摘要替代原始描述
                new_entries_count += 1
                print(f"已为文章 '{post['title']}' 生成摘要")
            except Exception as e:
                print(f"生成摘要失败，使用原始描述: {str(e)}")
                # 如果摘要生成失败，使用原始描述
                entry = feed.add_entry()
                entry.title(post['title'])
                entry.link(href=post['link'])
                entry.description(post['description'])
                new_entries_count += 1
    
    print(f"添加了 {new_entries_count} 个新条目")
    return feed.rss_str(pretty=True).decode('utf-8')

def main():
    config = load_config()
    
    for site in config['sites']:
        print(site["url"])
        try:
            posts = fetch_blog_posts(site)
            if not posts:
                print(f"No posts found for {site['url']}, skipping RSS generation.")
                continue
                
            file_name = f"rss/{site['name']}.xml"
            rss_feed = generate_rss(posts, site, file_name)
            
            # 确保rss目录存在
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(rss_feed)
            print(f"Updated RSS feed for {site['url']} -> {file_name}")           
        except Exception as e:
            print(f"Error generating RSS feed for {site['url']}: {e}")


if __name__ == '__main__':
    main()