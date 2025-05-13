from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

class PingPongAgent:
    def __init__(self, model_name="glm-4-flash", api_base="https://open.bigmodel.cn/api/paas/v4"):
        self.model = ChatOpenAI(
            model=model_name,
            openai_api_base=api_base,
            max_tokens=500,
            temperature=0.7
        )
        
        self.prompt_template = ChatPromptTemplate(
            [
                ('system', "你是一个乒乓球约球助手，负责帮助用户寻找合适的球友并记录约球信息。请根据用户的不同需求提供相应服务：\n\n"
                          "1. 如果用户想要约球：\n"
                          "   - 必须获取时间和地点信息\n"
                          "   - 可以了解用户的技术水平、希望寻找的球友数量和类型等（如果用户提供）\n"
                          "   - 如果用户是第一次约球，询问用户的用户名和联系方式\n"
                          "   - 把用户请求存储到数据库并寻找合适的球友\n\n"
                          "2. 如果用户想要查询约球信息：\n"
                          "   - 查询最近的约球信息\n"
                          "   - 如果用户指定了时间，查询该时间附近的约球信息\n\n"
                          "3. 如果用户询问其他问题：\n"
                          "   - 提供乒乓球相关的专业回答\n"
                          "   - 对于非乒乓球问题，简单友好地回应\n\n"
                          "请根据用户输入的内容，判断他们的意图并提供相应服务。"),
                ('human', "{input}")
            ]
        )
        
        self.parser_model = ChatOpenAI(
            model='glm-3-turbo',
            temperature=0.3,
            openai_api_base=api_base
        )
        
        self.chain = (
            self.prompt_template
            | self.model
            | self._output_parser
        )
    
    def _output_parser(self, output):
        message = "你需要将传入的文本进行改写，尽可能地更加自然简洁，专注于关键信息。这是你需要改写的文本:`{text}`"
        return self.parser_model.invoke(message.format(text=output))
    
    def invoke(self, input_text=None, time=None, place=None, **optional_params):
        """
        调用智能体处理用户请求
        
        Args:
            input_text: 用户输入的文本，如直接对话内容
            time: 时间，如"2025-05-10 14:00"（如果由表单提供）
            place: 地点，如"北京邮电大学体育馆"（如果由表单提供）
            optional_params: 其他可选参数，如技术水平、球友数量等
            
        Returns:
            智能体输出的回复内容
        """
        # 如果提供了结构化输入（时间和地点），构建约球请求文本
        if time and place:
            # 构建基本约球请求
            request_text = f"我想在{time}在{place}打乒乓球"
            
            # 添加可选信息（如果提供）
            if optional_params:
                additional_info = []
                if 'skill_level' in optional_params and optional_params['skill_level']:
                    additional_info.append(f"我的技术水平是{optional_params['skill_level']}")
                if 'opponent_count' in optional_params and optional_params['opponent_count']:
                    additional_info.append(f"希望找{optional_params['opponent_count']}个球友")
                if 'opponent_skill_level' in optional_params and optional_params['opponent_skill_level']:
                    additional_info.append(f"对手技术水平在{optional_params['opponent_skill_level']}左右")
                if 'match_type' in optional_params and optional_params['match_type']:
                    additional_info.append(f"比赛类型为{optional_params['match_type']}")
                if 'additional_notes' in optional_params and optional_params['additional_notes']:
                    additional_info.append(f"备注：{optional_params['additional_notes']}")
                
                if additional_info:
                    request_text += "，" + "，".join(additional_info)
            
            input_text = request_text
        
        # 如果没有提供结构化输入，使用用户直接输入的文本
        if not input_text:
            input_text = "你好"
            
        response = self.chain.invoke({"input": input_text})
        return response.content 