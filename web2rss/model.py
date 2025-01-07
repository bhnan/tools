import requests
import json
from typing import List, Dict, Any, Optional

class ChatModel:
    """聊天模型服务类"""
    
    def __init__(self, 
                 api_key: str, 
                 model: str = "google/gemma-2-9b-it",
                 api_url: str = "https://api.siliconflow.cn/v1/chat/completions"):
        """
        初始化聊天模型
        :param api_key: API密钥
        :param model: 模型名称
        :param api_url: API地址
        """
        self.api_key = api_key
        self.model = model
        self.api_url = api_url
        
        # 统一配置参数
        self.default_params = {
            "model": model,
            "stream": False,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.7,
            "stop": ["null"],
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1,
            "response_format": {"type": "text"}
        }
        
        # 添加模型配置字典
        self.model_configs = {
            "glm-4-flash": {
                "api_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                "params": self.default_params.copy()
            },
            "google/gemma-2-9b-it": {
                "api_url": "https://api.siliconflow.cn/v1/chat/completions",
                "params": self.default_params.copy()
            }
        }

    def create_chat_completion(self, 
                             messages: List[Dict[str, str]], 
                             **kwargs) -> str:
        """
        发送聊天完成请求
        :param messages: 消息列表
        :param kwargs: 可选参数,用于覆盖默认配置
        :return: AI回答内容
        """
        # 添加参数验证
        if not messages:
            raise ValueError("消息列表不能为空")
            
        model_name = kwargs.get("model", self.model)
        
        # 获取模型特定配置
        if model_name in self.model_configs:
            config = self.model_configs[model_name]
            payload = config["params"].copy()
            api_url = config["api_url"]
        else:
            payload = self.default_params.copy()
            api_url = self.api_url
            
        payload.update(kwargs)
        payload["messages"] = messages
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            response_json = json.loads(response.text)
            return response_json["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {str(e)}")
        except (KeyError, json.JSONDecodeError) as e:
            raise Exception(f"解析响应失败: {str(e)}")

    def update_default_params(self, **kwargs) -> None:
        """
        更新默认参数配置
        :param kwargs: 要更新的参数
        """
        self.default_params.update(kwargs)

    def reset_default_params(self, model: Optional[str] = None) -> None:
        """
        重置为初始默认参数
        :param model: 可选的新模型名称
        """
        self.default_params = {
            "model": model or self.default_params["model"],
            "stream": False,
            "max_tokens": 512,
            "stop": ["null"],
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1,
            "response_format": {"type": "text"}
        }


# 使用示例
if __name__ == "__main__":
    API_KEY = "***"
    chat_model = ChatModel(API_KEY, model="google/gemma-2-9b-it")
    
    messages = [
        {
            "role": "user",
            "content": "你好，请介绍一下你自己"
        }
    ]
    
    try:
        response = chat_model.create_chat_completion(messages)
        print(response)
    except Exception as e:
        print(f"错误: {str(e)}")
