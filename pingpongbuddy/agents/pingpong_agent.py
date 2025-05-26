from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from collections import defaultdict

# 导入统一的日志模块
from pingpongbuddy.logs.logger import get_logger

# 初始化日志
logger = get_logger('pingpongbuddy.agent')

class PingPongAgent:
    def __init__(self, model_name="glm-4-flash", api_base="https://open.bigmodel.cn/api/paas/v4"):
        logger.info(f"Initializing PingPongAgent with model: {model_name}")
        self.model = ChatOpenAI(
            model=model_name,
            openai_api_base=api_base,
            max_tokens=500,
            temperature=0.7
        )

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=(
                    "你是一个乒乓球约球助手，负责帮助用户寻找合适的球友并记录约球信息。请根据用户的不同需求提供相应服务：\n\n"
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
                    "数据库操作指南：\n"
                    "1. 添加新用户：\n"
                    "   - 使用 pingpong_db_tool 工具，action 设为 'add_user'\n"
                    "   - 参数：{\"username\": 用户名, \"contact\": 联系方式(可选)}\n"
                    "   - 返回：用户ID (user_id)\n\n"
                    "2. 存储约球请求：\n"
                    "   - 使用 pingpong_db_tool 工具，action 设为 'store_request'\n"
                    "   - 参数：{\"user_id\": 用户ID, \"time\": 时间, \"place\": 地点}\n"
                    "   - 返回：请求ID (request_id)\n\n"
                    "3. 查找匹配的球友：\n"
                    "   - 使用 pingpong_db_tool 工具，action 设为 'find_matches'\n"
                    "   - 参数：{\"time\": 时间, \"place\": 地点}\n"
                    "   - 返回：匹配的球友列表\n\n"
                    "请根据用户输入的内容，判断他们的意图并提供相应服务。对于约球和查询请求，必须使用上述数据库工具进行操作。"
                )),
                ("human", "{history}\n\n{input}")
            ]
        )

        self.parser_model = ChatOpenAI(
            model='glm-3-turbo',
            temperature=0.3,
            openai_api_base=api_base
        )

        # Store chat histories in memory (replace with persistent storage like Redis in production)
        self.chat_histories = defaultdict(InMemoryChatMessageHistory)

        # Define get_session_history function
        def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
            return self.chat_histories[session_id]

        # Create the chain with the prompt and model
        self.chain = (
                self.prompt_template
                | self.model
                | self._output_parser
        )

        # Initialize RunnableWithMessageHistory with get_session_history
        self.conversation = RunnableWithMessageHistory(
            runnable=self.chain,
            get_session_history=get_session_history,
            input_messages_key="input",
            history_messages_key="history"
        )

    def _output_parser(self, output):
        message = "你需要将传入的文本进行改写，尽可能地更加自然简洁，专注于关键信息。这是你需要改写的文本:`{text}`"
        return self.parser_model.invoke(message.format(text=output.content))

    def invoke(self, input_text=None, time=None, place=None, **optional_params):
        """调用智能体处理用户请求"""
        logger.info(f"Agent invoked with input_text: {input_text}, time: {time}, place: {place}")
        
        # 如果提供了结构化输入（时间和地点），构建约球请求文本
        if time and place:
            # 构建基本约球请求
            request_text = f"我想在{time}在{place}打乒乓球"
            
            # 记录可选参数
            if optional_params:
                logger.debug(f"Optional parameters: {optional_params}")
                
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

        # Use RunnableWithMessageHistory to process input
        response = self.conversation.invoke(
            {"input": input_text},
            config={"configurable": {"session_id": "default"}}  # Provide a session_id
        )
        
        # 记录最终响应
        logger.info(f"Agent response generated successfully")
        return response.content
