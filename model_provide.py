# -*- coding: utf-8 -*-
'''
@File    :   model_provide.py
@Time    :   2024/11/05 19:26:54
@Author  :   Jim Zhang 
@Desc    :   None
'''
# Hubris

import json
import os
from prompt import user_prompt
from openai import OpenAI
from dotenv import load_dotenv
import re
import json5

load_dotenv()

def process_response(content):
    # 匹配有效 JSON 对象或数组（确保不匹配到无效的部分）
    json_pattern = r'(\{.*\}|\[.*\])'  # 匹配大括号内的 JSON 对象或中括号内的 JSON 数组
    matches = re.findall(json_pattern, content, re.DOTALL)

    # 提取有效的 JSON 字符串
    parsed_jsons = []
    for json_string in matches:
        json_string = json_string.strip()  # 去除空白字符

        # 处理不合法的 JSON 格式
        # 1. 替换单引号为双引号
        json_string = json_string.replace("'", '"')

        # 2. 去除反斜杠（`\`）中的转义字符
        json_string = json_string.replace('\\"', '"')  # 还原被转义的双引号
        # json_string = re.sub(r'(?<=\s)\"(.*?)(?=\")', r'\"', json_string)

        # 3. 去除多余的字符或修复结构不完整的 JSON
        # 例如: 用正则表达式去掉不必要的文本，确保 JSON 数据完整
        json_string = re.sub(r'```json|\n|```', '', json_string).strip()  # 去除代码块标记

        try:
            # 尝试解析为 JSON
            content_json = json5.loads(json_string)
            parsed_jsons.append(content_json)  # 将解析后的内容添加到列表
        except json.JSONDecodeError as e:
            print("Error: Json Decode Error. Invalid JSON String:", json_string)
            print("Error details:", e)

    # 返回解析后的所有有效 JSON 或默认返回原版 content
    if parsed_jsons:
        return parsed_jsons[0]  # 返回所有有效 JSON 对象的列表
    else:
        print("No valid JSON found in content.")
        return content  # 如果没有找到有效的 JSON，则返回原版 content

    
    
# print("Error: {e}. Invalid JSON String:", json_string)
# 测试示例

# print(json5.loads("""
# ```json
# {
#     "action": {
#         "name": "write_file",
#         "args": {
#             "file_path": "jihua.txt",
#             "content": "周一：热身 - 5分钟，力量训练 - 30分钟，有氧运动 - 30分钟\n周二：休息\n周三：热身 - 5分钟，有氧运动 - 45分钟\n周四：休息\n周五：热身 - 5分钟，力量训练 - 30分钟，有氧运动 - 30分钟\n周六：休息\n周日：热身 - 5分钟，有氧运动 - 60分钟\n每天训练后，请确保进行适当的拉伸和放松。"
#         }
#     },
#     "thoughts": {
#         "plan": "已根据要求创建一份基础的周健身计划，并包含在内是休息日的安排。",
#         "criticism": "由于缺乏具体的个人健身信息和目标，计划是通用性的，需要用户根据自身情况进行调整。",
#         "speak": "健身计划已经创建并保存在 'jihua.txt' 文件中。",
#         "reasoning": "根据任务要求，我创建了一个简单的周健身计划，并且已经将其内容写入到 'jihua.txt' 文件中，以便用户可以查阅和遵循该计划。"
#     },
#     "observation": "健身计划已经保存。",
#     "answer": "完成"
# }
# ```
# """
#                        ))


class ModelProvide(object): 
    def __init__(self):
        self.api_key = os.environ.get('MINIMAX_API_KEY')
        self.model_name = os.environ.get('MINIMAX_MODEL_NAME')
        self.base_url = os.environ.get('MINIMAX_BASE_URL')
        self._client = None
        self.max_retry_times = 3
        
    @property
    def client(self):
        if not self._client:
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client
    
    def chat(self, prompt, chat_history):
        cur_retry_times = 0
        while cur_retry_times < self.max_retry_times:
            cur_retry_times += 1
            try:
                messages = [{"role": "system", "content": prompt}]
                for his in chat_history:
                    messages.append({"role": "user", "content": his[0]})
                    messages.append({"role": "assistant", "content": his[1]})
                messages.append({"role": "user", "content": user_prompt})
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    max_tokens=8192,
                    temperature=0.7,
                    messages = messages,
                    )
                
                content = process_response(response.choices[0].message.content)
                
                content_json = json5.loads(content)
                return content_json
                # content_json = json.loads(response.choices[0].message.content)
                # if json.loads(content):
                #     content = json.loads(content)
                
                
            except Exception as e:
                return(f"Error: {e}")   
            # return {}
        
    