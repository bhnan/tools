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

# 使用示例
if __name__ == "__main__":
    API_KEY = "your_api_key_here"
    
    # 创建摘要生成器实例
    summary_gen = SummaryGenerator(API_KEY)
    
    # 示例文章
    article = """
    人工智能(AI)正在深刻改变着我们的生活方式。从智能手机助手到自动驾驶汽车，
    从医疗诊断到金融分析，AI技术的应用范围越来越广。但同时，AI的发展也带来了
    一些担忧，比如就业替代、隐私安全等问题。专家认为，要在发展AI技术的同时，
    建立相应的伦理框架和监管机制，确保AI的发展造福人类。
    """
    
    try:
        # 生成摘要
        summary = summary_gen.generate_summary(article, max_length=100)
        print("文章摘要：")
        print(summary)
    except Exception as e:
        print(f"错误: {str(e)}")
