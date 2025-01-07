import requests
from bs4 import BeautifulSoup
from typing import Optional
from .model import ChatModel

class SummaryGenerator:
    """文章摘要生成器类"""
    
    def __init__(self, api_key: str, model: str = "google/gemma-2-9b-it"):
        """
        初始化摘要生成器
        :param api_key: API密钥
        :param model: 使用的模型名称
        """
        self.chat_model = ChatModel(api_key, model=model)
        
    def generate_summary(self, 
                        text: str, 
                        max_length: Optional[int] = 200,
                        language: str = "zh") -> str:
        """
        生成文章摘要
        :param text: 输入的文章内容
        :param max_length: 摘要最大长度
        :param language: 摘要语言，默认中文
        :return: 生成的摘要
        """
        # 构建提示词
        prompt = self._create_summary_prompt(text, max_length, language)
        
        messages = [
            {
                "role": "system",
                "content": "You are a professional article summarization assistant, skilled at extracting the core content of articles and generating concise and clear summaries."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            # 调整模型参数以获得更稳定的摘要
            response = self.chat_model.create_chat_completion(
                messages,
                temperature=0.3,  # 降低随机性
                max_tokens=max_length,
                top_p=0.8
            )
            return response.strip()
        except Exception as e:
            raise Exception(f"生成摘要失败: {str(e)}")
            
    def _create_summary_prompt(self, 
                             text: str, 
                             max_length: int,
                             language: str) -> str:
        """
        创建摘要生成的提示词
        :param text: 文章内容
        :param max_length: 最大长度
        :param language: 语言
        :return: 格式化的提示词
        """
        lang_prompt = "in Chinese" if language == "zh" else "in English"
        return f"""Please summarize the main content of the following article {lang_prompt}, 
        generating a summary of no more than {max_length} characters.
        The summary should contain the core points and important information of the article, 
        with concise and clear language.

        Article content:
        {text}
        """

    def _fetch_webpage_content(self, url: str) -> str:
        """
        获取网页内容
        :param url: 网页URL
        :return: 网页正文内容
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除脚本和样式元素
            for script in soup(['script', 'style']):
                script.decompose()
                
            # 获取正文内容
            text = ' '.join([p.get_text().strip() for p in soup.find_all(['p', 'article'])])
            return text
        except Exception as e:
            raise Exception(f"获取网页内容失败: {str(e)}")

# 使用示例
if __name__ == "__main__":
    API_KEY = "your_api_key_here"
    
    # 创建摘要生成器实例
    summary_gen = SummaryGenerator(API_KEY)
    
    # 示例URL
    url = "https://example.com/article"
    
    try:
        # 获取网页内容并生成摘要
        content = summary_gen._fetch_webpage_content(url)
        summary = summary_gen.generate_summary(content)
        print("文章摘要：")
        print(summary)
    except Exception as e:
        print(f"错误: {str(e)}")
