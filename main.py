# -*- coding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2024/11/05 19:27:05
@Author  :   Jim Zhang 
@Desc    :   None
'''



'''
    todo:
        1. 环境变量
        2. 工具引入
        3. prompt模板
        4. 模型初始化
'''
import time
from tools import tools_map
from prompt import gen_prompt,user_prompt
from model_provide import ModelProvide
from dotenv import load_dotenv
load_dotenv()

mp = ModelProvide()

def parse_thoughts(response):
    '''
    response:
        {
            "action":{
                "name":"action_name",
                "args":{
                    "args_name":"args_value"
                }
            },
            "thoughts":{
                "text":"thoughts",
                "plan":"plan",
                "criticism":"criticism",
                "speak":"speak",
                "reasoning":"reasoning" 
            }
        }
    '''
    try:
        thoughts = response.get("thoughts")
        plan = thoughts.get("plan")
        reasoning = thoughts.get("reasoning")
        observation = thoughts.get("observation")
        criticism = thoughts.get("criticism")
        prompt = f"plan:{plan}\n reasoning:{reasoning}\n criticism:{criticism}\n observation:{observation}"
        return prompt
    except Exception as e:
        print("= 解析thoughts失败，请重试",e)
        return "".format(e)

def agent_executor(query,max_call_times=10):
    # 调用模型进行查询
    cur_request_time = 0
    
    chat_history = []
    agent_scratches = ''
    while cur_request_time < max_call_times:
        # 模型返回结果
        cur_request_time += 1
        '''
            如果返回结果达到预期，则返回
        '''
        """
            prompt：
                1、任务描述
                2、工具描述
                3、用户输入
                4、系统回复
                5、限制
                6、给出更好实践的描述
                
        """
        prompt = gen_prompt(query,agent_scratches)
        print("============ {}，开始调用大模型".format(cur_request_time),flush=True)
        start_time = time.time()
        # call model
        """
            sys_prompt:
                history, user_message, assistant_message
        """
        # if cur_request_time < 2:
        #     print(prompt)
        
        response = mp.chat(prompt,chat_history)
        end_time = time.time()
        print("= 调用大模型耗时：{}秒".format(end_time-start_time),flush=True)
        
        if not response or not isinstance(response,dict):
            print("= 调用大模型错误，请重试\n response:",response)
            continue
    
        action_info = response.get("action")
        action_name = action_info.get("name")
        action_args = action_info.get("args")
        
        print()
        print("================== info ==================")
        print(f"当前action_name:{action_name}||action_入参:{action_name}")
        # 其他输出信息
        thoughts = response.get("thoughts")
        plan = thoughts.get("plan")
        reasoning = thoughts.get("reasoning")
        criticism = thoughts.get("criticism")
        speak = thoughts.get("speak")
        observation = response.get("observation")
        print(f"# spek: {speak}")
        print(f"# plan: {plan}")
        print(f"# reasoning: {reasoning}")
        print(f"# criticism: {criticism}")
        print(f"# observation: {observation}")
        print("================== info ==================")
        print()
        
        print("========== 解析返回结果：",action_name,action_args)
        
        if action_name == "finish" or observation == "None" or observation == "finish":
            final_answer = action_args.get("answer")
            print(f"final answer: {final_answer}")
            break
        
        # observations = response.get("thoughts").get('speak')
        observations = response.get("observation")
        try:
            # action 到函数的映射, map -> {action_name:func}
            # todo: tools_map 实现
            # tools_map = {}
            func = tools_map.get(action_name)
            call_func_result = func(**action_args)
            
        except Exception as e:
            print("= 工具调用失败，请重试",e)
            call_function_result = "{}".format(e)

        
        agent_scratches = agent_scratches + f"\n: observation:{observations}\n execute action result: {call_func_result}"
        print(f"\nagent_scratches: \n{agent_scratches}\n")
        # user_message = "决定使用哪个工具"
        assistant_message = parse_thoughts(response)
        
        chat_history.append([user_prompt,assistant_message])
        
    if cur_request_time >= max_call_times:
        print("= 达到最大调用次数，结束对话")
    else:
        print("= 任务完成")
    
        
def main():
    # 需求支持用户多次交互
    # 设置最大调用次数
    max_call_times = 10
    
    while True:
        # query = input("请输入你的目标:")
        query = """
        请帮我制定一个健身计划，分以下几个步骤完成：
        1. 搜索网上健身计划
        2. 选择一个健身计划并保存到 jihua.txt 文件中
        """
        
        if query == 'exit':
            break
        agent_executor(query,max_call_times=max_call_times)
        break
    
if __name__ == '__main__':
    main()