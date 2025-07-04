import json
import os
from typing import Dict, List, Optional
from openai import OpenAI

class DeepSeekLLM():
    def __init__(self, config: dict):
        """
        初始化 DeepSeekLLM
        :param config: 配置字典，包含 model, base_url, api_key 等参数
        """
        self.model = config.get("model", "deepseek-chat")
        self.temperature = config.get("temperature", 0.1)
        self.max_tokens = config.get("max_tokens", 2000)
        self.top_p = config.get("top_p", 0.1)
        self.top_k = config.get("top_k", 1)

        # 从配置字典或环境变量获取 API Key
        api_key = config.get("api_key") or os.getenv("CHAT_API_KEY")
        if not api_key:
            raise ValueError("DeepSeek API Key 未找到，请设置 CHAT_API_KEY 环境变量或在配置中提供 api_key")
        
        base_url = config.get("base_url", "https://api.deepseek.com")
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def _parse_response(self, response, tools):
        """
        Process the response based on whether tools are used or not.

        Args:
            response: The raw response from API.
            tools: The list of tools provided in the request.

        Returns:
            str or dict: The processed response.
        """
        if tools:
            processed_response = {
                "content": response.choices[0].message.content,
                "tool_calls": [],
            }

            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    processed_response["tool_calls"].append(
                        {
                            "name": tool_call.function.name,
                            "arguments": json.loads(tool_call.function.arguments),
                        }
                    )

            return processed_response
        else:
            return response.choices[0].message.content

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        response_format=None,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
    ):
        """
        Generate a response based on the given messages using DeepSeek.

        Args:
            messages (list): List of message dicts containing 'role' and 'content'.
            response_format (str or object, optional): Format of the response. Defaults to "text".
            tools (list, optional): List of tools that the model can call. Defaults to None.
            tool_choice (str, optional): Tool choice method. Defaults to "auto".

        Returns:
            str: The generated response.
        """
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }
        
        # 处理 response_format 参数
        if response_format:
            if isinstance(response_format, str):
                if response_format == "json_object":
                    params["response_format"] = {"type": "json_object"}
                elif response_format == "text":
                    params["response_format"] = {"type": "text"}
                else:
                    params["response_format"] = {"type": response_format}
            else:
                params["response_format"] = response_format

        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice

        response = self.client.chat.completions.create(**params)
        return self._parse_response(response, tools)