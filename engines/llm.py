from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import ConversationChain

class Assistant:
    def __init__(self, model, prompt_template: str):
        """初始化Assistant"""
        self.model = model
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(prompt_template),
            HumanMessagePromptTemplate.from_template("{history}\n\n用户: {input}")
        ])
        self.chain = None

    def invoke(self, user_input: str, memory: ConversationBufferMemory) -> str:
        """调用助手并生成响应，动态绑定memory"""
        if self.chain is None or self.chain.memory != memory:
            self.chain = ConversationChain(llm=self.model, memory=memory, prompt=self.prompt)
        return self.chain.run(input=user_input)

class AssistantManager:
    def __init__(self, api_key: str, max_turns: int = 3):
        """初始化Assistant管理器"""
        self.api_key = api_key  # 默认API密钥，可被模型特定的密钥覆盖
        self.max_turns = max_turns
        self.models = {}
        self.assistants = {}
        self.memory_dict = {}

    def add_model(self, model_name: str, base_url: str = None, api_key: str = None, **kwargs):
        """添加模型，支持自定义base_url和api_key"""
        # 使用模型特定的API密钥，如果未提供则使用默认密钥
        effective_api_key = api_key if api_key else self.api_key
        # 创建模型实例
        self.models[model_name] = ChatOpenAI(
            openai_api_key=effective_api_key,
            model_name=model_name,
            base_url=base_url,  # 如果提供，则使用自定义base_url
            **kwargs
        )

    def add_assistant(self, assistant_name: str, model_name: str, prompt_template: str):
        """添加Assistant"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found. Add it first.")
        self.assistants[assistant_name] = Assistant(
            model=self.models[model_name],
            prompt_template=prompt_template
        )

    def get_or_create_memory(self, user_id: str) -> ConversationBufferMemory:
        """获取或创建用户的记忆实例"""
        if user_id not in self.memory_dict:
            self.memory_dict[user_id] = ConversationBufferMemory(return_messages=True)
        return self.memory_dict[user_id]

    def invoke(self, assistant_name: str, user_id: str, user_input: str) -> str:
        """调用指定Assistant并生成响应，基于用户ID管理记忆"""
        if assistant_name not in self.assistants:
            raise ValueError(f"Assistant {assistant_name} not found.")
        memory = self.get_or_create_memory(user_id)
        response = self.assistants[assistant_name].invoke(user_input, memory)
        if len(memory.chat_memory.messages) > self.max_turns * 2:
            memory.chat_memory.messages = memory.chat_memory.messages[-self.max_turns * 2:]
        return response

    def clear_memory(self, user_id: str):
        """清除指定用户的记忆"""
        if user_id in self.memory_dict:
            self.memory_dict[user_id].clear()

# 使用示例
def main():
    # 初始化管理器，默认API密钥可以留空，具体密钥在add_model时提供
    manager = AssistantManager(api_key="", max_turns=3)

    # 添加OpenAI模型
    manager.add_model(
        "gpt-3.5-turbo",
        api_key="your-openai-api-key",
        temperature=0.7
    )

    # 添加DeepSeek模型
    manager.add_model(
        "deepseek-chat",
        base_url="https://api.deepseek.com/v1",
        api_key="your-deepseek-api-key",
        temperature=0.9
    )

    # 添加通义千问模型
    manager.add_model(
        "qwen-turbo",
        base_url="https://dashscope.aliyuncs.com/api/v1",
        api_key="your-qwen-api-key",
        temperature=0.8
    )

    # 添加Assistants
    manager.add_assistant(
        "tech_expert",
        "gpt-3.5-turbo",
        "你是一个技术专家，擅长解答技术问题。请根据之前的对话自然地回答用户的问题。"
    )
    manager.add_assistant(
        "historian",
        "deepseek-chat",
        "你是一个历史学家，喜欢用轻松的语气分享历史知识。请根据之前的对话自然地回应用户。"
    )
    manager.add_assistant(
        "financial_analyst",
        "qwen-turbo",
        """你是一个记账助手。请分析用户输入的文本，提取所有可能的记账信息，并以JSON格式返回，包含transactions数组。每笔记账需包含：
        - type: 类型（expense: 支出, income: 收入）
        - amount: 金额（数字）
        - category: 分类（支出分类：餐饮、服装、交通、蔬菜、零食、杂货、购物、水果、运动、通讯、学习、美容、宠物、娱乐、数码、礼物、旅行、家居、其他；收入分类：工资、兼职、投资、其他）
        - note: 备注说明
        - confidence: 置信度（0-1之间的小数）
        如果找不到合适的分类，使用“其他”，并在备注中说明“没有明确交易信息”。"""
    )

    # 测试多用户对话
    print("User 1 - Tech Expert:", manager.invoke("tech_expert", "user1", "今天花了20吃早餐"))
    print("User 1 - Financial Analyst:", manager.invoke("financial_analyst", "user1", "今天花了20吃早餐"))
    print("User 1 - Historian:", manager.invoke("historian", "user1", "今天我花了多少来着"))
    print("User 2 - Tech Expert:", manager.invoke("tech_expert", "user2", "今天我花了多少来着"))

    manager.clear_memory("user1")

if __name__ == "__main__":
    main()