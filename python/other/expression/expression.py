import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from memoryrag.config import LlmConfig
from memoryrag.llm import DeepSeekLLM

# 从同级文件夹下导入prompt
from other.expression.prompt import EXPRESSION_PROMPT, ACTION_PROMPT

def init_llm():
    """初始化配置"""
    load_dotenv()
    # 创建 LlmConfig 实例
    llm_config = LlmConfig.from_env()
    llm = DeepSeekLLM(llm_config.get_config())

    return llm
    
def init_llm2():
    """初始化 Groq 模型"""
    key = "gsk"
    
    # 创建 Groq 配置
    groq_config = {
        "model": "meta-llama/llama-4-maverick-17b-128e-instruct",  # 可根据实际模型名称调整
        "base_url": "http://124.156.212.23:8081/openai/v1", 
        "api_key": key,
        "temperature": 0.1,
        "max_tokens": 2000,
        "top_p": 0.1,
        "top_k": 1
    }
    
    # 使用 DeepSeekLLM 类来初始化 Groq 模型（因为都使用 OpenAI 兼容接口）
    llm = DeepSeekLLM(groq_config)
    
    return llm

def generate_expression(llm, expression):
    message = [
        {"role": "system", "content": EXPRESSION_PROMPT},
        {"role": "user", "content": f"{expression}"}
    ]
    response = llm.generate_response(message, response_format="json_object")

    print(response)

def generate_action(llm, expression):
    message = [
        {"role": "system", "content": ACTION_PROMPT},
        {"role": "user", "content": f"{expression}"}
    ]
    response = llm.generate_response(message, response_format="json_object")

    print(response)

if __name__ == "__main__":
    # 初始化 LLM
    llm = init_llm()

    expression = """
    # 历史对话
    - 用户: 今天要出去玩吗？
    - Ruby: 好啊，今天的天气不错，我们可以去公园散步。
    """
    generate_expression(llm, expression)

    expression2 = """
    # 历史对话
    - 用户: 我们去看电影吧。
    - Ruby: 可咱们这哪来电影院？
    """

    generate_action(llm, expression2)