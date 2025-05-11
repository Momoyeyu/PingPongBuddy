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
                ('system', "你是一个乒乓球约球助手，当用户想要约球时，你会将用户的请求存储到数据库中，并帮助用户寻找合适的球友。"),
                ('human', "我想要在{time}、{place}打乒乓球，请你帮我寻找合适的球友。")
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
    
    def invoke(self, time, place):
        """
        调用智能体进行约球
        
        Args:
            time: 时间，如"2025-05-10 14:00"
            place: 地点，如"北京邮电大学体育馆"
            
        Returns:
            智能体输出的回复内容
        """
        response = self.chain.invoke({"time": time, "place": place})
        return response.content 