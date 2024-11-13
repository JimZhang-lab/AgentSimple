# -*- coding: utf-8 -*-
'''
@File    :   tools.py
@Time    :   2024/11/05 19:27:23
@Author  :   Jim Zhang 
@Desc    :   None
'''



"""
1、写文件
2、读文件
3、追加
4、搜索
"""
import os
import json
# from langchain_community.tools.tavily_search import TavilySearchResult
import requests
from langchain_community.tools.tavily_search import TavilySearchResults


def __get__workdir__root__():
    workdir_root = os.environ.get('WORKDIR_ROOT',"./data/llm_result")
    return workdir_root

WORKDIR_ROOT = __get__workdir__root__()

def read_file(file_path):
    file_path = os.path.join(WORKDIR_ROOT, file_path)
    if not os.path.exists(file_path):
        return f"{file_path} not exists, please check it."
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return "\n".join(f.readlines())
    
    
def write_file(file_path, content):
    file_path = os.path.join(WORKDIR_ROOT, file_path)
    if not os.path.exists(WORKDIR_ROOT):
        os.makedirs(WORKDIR_ROOT)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    return "write success."

def append_file(file_path, content):
    file_path = os.path.join(WORKDIR_ROOT, file_path)
    if not os.path.exists(file_path):
        return f"{file_path} not exists, please check it."
    
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content)
        
    return "append success."

def search(search_query: str):
    """
    :param query:
    :return:
    """
    daily = TavilySearchResults(max_results=5)
    try:
        ret = daily.invoke(input=search_query)
        # print("搜索结果:{}".format(ret))
        # print("\n")
        content_list = []
        """
        # 从哪个网站上获取的内容
        ret = [
            {
                "content": "",
                "url": ""
            }
        ]
        """
        for obj in ret:
            content_list.append(obj["content"])
        # print("\n".join(content_list))
        # print("\n")
        return "\n".join(content_list)
    except Exception as e:
        return "search error:{}".format(e)

def google_search(search_query: str):
    '''google search'''
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": search_query})
    headers = {
		'X-API-KEY': os.environ.get("GOOGLE_SEARCHE_API_KEY"),
		'Content-Type': 'application/json'
	}
    response = requests.request("POST", url, headers=headers, data=payload).json()
    # print("google search result: "+response['organic'][0]['snippet'])
    return response['organic'][0]['snippet']


tools_info = [
    {
        "name": "read_file",
        "description": "read file from agent generated, should wirte file before read it.",
        "args": [{
            "name": "file_path",
            "type": "str",
            "description": "file path to read"
        }]
    },
    {
        "name": "write_file",
        "description": "write file to agent generated, should wirte file before read it.",
        "args": [{
            "name": "file_path",
            "type": "str",
            "description": "file path to write"
        }, {
            "name": "content",
            "type": "str",
            "description": "content to write"
        }]
    },
    {
        "name": "append_file",
        "description": "append content to file, should wirte file before append it.",
        "args": [{
            "name": "file_path",
            "type": "str",
            "description": "file path to append"
        }, {
            "name": "content",
            "type": "str",
            "description": "content to append"
        }]
    },
    # {
    #     "name": "search",
    #     "description": "search content from internet, you can gain some information from search result.",
    #     "args": [{
    #         "name": "search_query",
    #         "type": "str",
    #         "description": "search query"
    #     }]
    # },
    {
        "name": "google_search",
        "description": "search content from google search, you can gain some information from google search result.",
        "args": [{
            "name": "search_query",
            "type": "str",
            "description": "search query"
        }]
    },
    {
        "name": "finish",
        "description": "完成用户目标",
        "args": [
            {
                "name": "answer",
                "type": "string",
                "description": "最后的目标结果"
            }
        ]
    }
]

# 函数名不要带括号
tools_map = {
    "read_file": read_file,
    "write_file": write_file,
    "append_file": append_file,
    "google_search": google_search,
    "finish": "finish"
}

def gen_tools_desc():
    tools_desc = []
    for idx, t in enumerate(tools_info):
        args_desc = []
        for info in t['args']:
            args_desc.append({
                "name": info['name'],
                "description": info['description'],
                "type": info['type']
            })
        
        args_desc = json.dumps(args_desc, ensure_ascii=False)
        tool_desc = f"{idx}，{t['name']}:{t['description']}，参数：{args_desc}"
        tools_desc.append(tool_desc)
    tools_prompt = "\n".join(tools_desc)
    return tools_prompt
        
# if __name__ == '__main__':
#     print(google_search('今天北京天气怎么样？'))