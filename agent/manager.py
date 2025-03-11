from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import ConversationChain

from assistant.models import Assistant as AssistantModel
from engines.models import Engines


class Assistant:
    def __init__(self, model, assistant_id: int):
        """初始化Assistant"""
        self.model = model
        self.assistant = AssistantModel.objects.get(pk=assistant_id)  # 从数据库加载Assistant配置
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.assistant.prompt_template),
            HumanMessagePromptTemplate.from_template("{history}\n\n用户: {input}")
        ])
        self.store_in_memory = self.assistant.is_memory  # 从数据库模型中读取是否存入记忆
        self.chain = None

    def set_model(self, model):
        """切换模型"""
        self.model = model
        self.chain = None  # 重置chain，下次invoke时重新初始化

    def set_prompt_template(self):
        """切换提示词模板（运行时动态调整）"""
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.assistant.prompt_template),
            HumanMessagePromptTemplate.from_template("{history}\n\n用户: {input}")
        ])
        self.chain = None  # 重置chain

    def invoke(self, user_input: str, memory: ConversationBufferMemory) -> str:
        """调用助手并生成响应，动态绑定memory"""
        if self.chain is None or self.chain.memory != memory:
            self.chain = ConversationChain(llm=self.model, memory=memory, prompt=self.prompt)
            
        # 如果不存入记忆，临时移除memory
        original_memory = None
        if not self.store_in_memory:
            original_memory = self.chain.memory  # 备份原始memory对象
            self.chain.memory = None  # 移除memory，阻止自动更新
        
        # 执行对话
        response = self.chain.run(input=user_input)
        
        # 恢复memory（如果之前移除）
        if not self.store_in_memory and original_memory is not None:
            self.chain.memory = original_memory
        
        return response


class AssistantManager:
    def __init__(self, max_turns: int = 10):
        """初始化Assistant管理器"""
        self.max_turns = max_turns
        self.models = {}
        self.assistants = {}
        self.memory_dict = {}

    def add_model(self, engine: Engines, **kwargs):
        """添加模型，从数据库加载配置"""
        self.models[engine.name] = ChatOpenAI(
            openai_api_key=engine.api_key,
            model_name=engine.name,
            base_url=engine.base_url,
            **kwargs
        )

    def add_assistant(self, assistant: AssistantModel, model_name = 'qwen-max'):
        """添加Assistant，从数据库加载配置"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found. Add it first.")
        self.assistants[assistant.name] = Assistant(
            model=self.models[model_name],
            assistant_id=assistant.id
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
        if self.assistants[assistant_name].store_in_memory and len(memory.chat_memory.messages) > self.max_turns * 2:
            memory.chat_memory.messages = memory.chat_memory.messages[-self.max_turns * 2:]
        return response

    def clear_memory(self, user_id: str):
        """清除指定用户的记忆"""
        if user_id in self.memory_dict:
            self.memory_dict[user_id].clear()


def initialize() -> AssistantManager:
    manager = AssistantManager(max_turns=10)

    engines = Engines.objects.all()
    for engine in engines:
        manager.add_model(engine)

    assistant_models =  AssistantModel.objects.all()

    for assistant in assistant_models:
        manager.add_assistant(assistant)
        manager.assistants[assistant.name].set_prompt_template()

    return manager