from langchain.chat_models import ChatOpenAI, DeepSeekChat, tongyi
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import ConversationChain
from langchain.schema.output_parser import BaseOutputParser
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from typing import Dict, Any, List, Optional

from assistant.models import Assistant as AssistantModel
from engines.models import Engines


class JsonOutputParser(BaseOutputParser):
    """
    自定义输出解析器，将输出格式化为JSON
    """
    def parse(self, text: str) -> Dict[str, Any]:
        """
        解析模型输出的文本，尝试提取JSON格式
        """
        import json
        import re
        
        # 尝试直接解析整个文本为JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # 尝试从文本中提取JSON部分
        json_pattern = r'```json\s*([\s\S]*?)\s*```'
        match = re.search(json_pattern, text)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 如果无法解析为JSON，返回原始文本
        return {"response": text, "format": "text"}


class Assistant:
    def __init__(self, model, assistant_id: int, language: str = "en", output_format: str = None):
        """
        初始化Assistant
        
        Args:
            model: LLM模型实例
            assistant_id: 助手ID
            language: 输出语言
            output_format: 输出格式，可选值: json, structured, text(默认)
        """
        self.model = model
        self.assistant = AssistantModel.objects.get(pk=assistant_id)  # 从数据库加载Assistant配置
        self.language = language
        self.prompt_template = self.assistant.prompt_template  # 存储原始提示词模板
        self.prompt = self._build_prompt_template()  # 构建提示词
        self.store_in_memory = self.assistant.is_memory  # 从数据库模型中读取是否存入记忆
        self.chain = None
        self.output_format = output_format
        self.output_parser = self._get_output_parser(output_format)

    def _get_output_parser(self, output_format: Optional[str]) -> Optional[BaseOutputParser]:
        """
        根据指定的输出格式获取相应的输出解析器
        """
        if not output_format:
            return None
            
        if output_format.lower() == 'json':
            return JsonOutputParser()
        elif output_format.lower() == 'structured':
            # 定义结构化输出的模式
            response_schemas = [
                ResponseSchema(name="response", description="The main response text"),
                ResponseSchema(name="sentiment", description="The sentiment of the response (positive, neutral, negative)"),
                ResponseSchema(name="keywords", description="Key words or phrases from the response")
            ]
            return StructuredOutputParser.from_response_schemas(response_schemas)
        
        return None

    def _build_prompt_template(self):
        """构建提示词模板，动态加入语言要求"""
        system_template = (
            f"{self.prompt_template}\n"
            f"请使用 {self.language} 语言进行回复。"  # 动态添加语言要求
        )
        
        # 如果设置了输出格式，添加相应的格式化指令
        if self.output_format:
            if self.output_format.lower() == 'json':
                system_template += "\n请以JSON格式返回你的回复，使用```json```标记。"
            elif self.output_format.lower() == 'structured':
                if self.output_parser:
                    system_template += f"\n{self.output_parser.get_format_instructions()}"
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template("{history}\n\n用户: {input}")
        ])

    def set_model(self, model):
        """切换模型"""
        self.model = model
        self.chain = None  # 重置chain，下次invoke时重新初始化

    def set_language(self, language: str):
        """切换输出语言"""
        self.language = language
        self.prompt = self._build_prompt_template()  # 更新提示词模板
        self.chain = None  # 重置chain

    def set_output_format(self, output_format: str):
        """
        设置输出格式
        
        Args:
            output_format: 输出格式，可选值: json, structured, text(默认)
        """
        self.output_format = output_format
        self.output_parser = self._get_output_parser(output_format)
        self.prompt = self._build_prompt_template()  # 更新提示词模板
        self.chain = None  # 重置chain

    def set_prompt_template(self, prompt_template=None):
        """
        切换提示词模板（运行时动态调整）
        如果不提供新的模板，则使用助手默认的模板
        """
        if prompt_template is not None:
            self.prompt_template = prompt_template
        else:
            # 重新从数据库加载最新的提示词模板
            self.assistant = AssistantModel.objects.get(pk=self.assistant.id)
            self.prompt_template = self.assistant.prompt_template
            
        self.prompt = self._build_prompt_template()
        self.chain = None  # 重置chain，下次invoke时重新初始化

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

        # 如果设置了输出解析器，解析输出
        if self.output_parser:
            try:
                parsed_response = self.output_parser.parse(response)
                # 如果是结构化输出，转换为字符串
                if isinstance(parsed_response, dict) and 'response' in parsed_response:
                    return parsed_response['response']
                return str(parsed_response)
            except Exception as e:
                # 解析失败时返回原始响应
                print(f"Output parsing failed: {e}")
                return response

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
        # 根据模型名称选择不同的模型类
        model_name = engine.name.lower()
        
        # 通义千问模型
        if 'qwen' in model_name:
            self.models[engine.name] = tongyi.ChatTongyi(
                api_key=engine.api_key,
                model_name=engine.name,
                base_url=engine.base_url or "https://api.qianwen-api.com/v1",
                temperature=engine.temperature,
                **kwargs
            )
        # DeepSeek模型
        elif 'deepseek' in model_name:
            self.models[engine.name] = DeepSeekChat(
                api_key=engine.api_key,
                model_name=engine.name,
                base_url=engine.base_url or "https://api.deepseek.com/v1",
                temperature=engine.temperature,
                **kwargs
            )
        # 默认OpenAI兼容模型
        else:
            self.models[engine.name] = ChatOpenAI(
                openai_api_key=engine.api_key,
                model_name=engine.name,
                base_url=engine.base_url,
                temperature=engine.temperature,
                **kwargs
            )

    def add_assistant(self, assistant: AssistantModel, model_name='qwen-max', language='en', output_format=None):
        """
        添加Assistant，从数据库加载配置
        
        Args:
            assistant: 助手模型实例
            model_name: 模型名称
            language: 输出语言
            output_format: 输出格式，可选值: json, structured, text(默认)
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found. Add it first.")
        self.assistants[assistant.name] = Assistant(
            model=self.models[model_name],
            assistant_id=assistant.id,
            language=language,
            output_format=output_format
        )

    def get_or_create_memory(self, user_id: str) -> ConversationBufferMemory:
        """获取或创建用户的记忆实例"""
        if user_id not in self.memory_dict:
            self.memory_dict[user_id] = ConversationBufferMemory(return_messages=True)
        return self.memory_dict[user_id]

    def invoke(self, assistant_name: str, user_id: str, user_input: str, language: str = None, 
               prompt_template: str = None, output_format: str = None, model_name: str = None) -> str:
        """
        调用指定Assistant并生成响应，基于用户ID管理记忆
        
        Args:
            assistant_name: 助手名称
            user_id: 用户ID
            user_input: 用户输入
            language: 指定输出语言
            prompt_template: 自定义提示词模板
            output_format: 输出格式，可选值: json, structured, text(默认)
            model_name: 模型名称，用于动态切换模型
        
        Returns:
            str: 助手的响应
        """
        if assistant_name not in self.assistants:
            raise ValueError(f"Assistant {assistant_name} not found.")
            
        assistant = self.assistants[assistant_name]
        
        # 如果提供了模型名称，切换模型
        if model_name and model_name in self.models:
            assistant.set_model(self.models[model_name])
        
        # 如果提供了自定义提示词模板，则更新
        if prompt_template:
            assistant.set_prompt_template(prompt_template)
            
        # 如果提供了语言设置，则更新
        if language and language != assistant.language:
            assistant.set_language(language)
            
        # 如果提供了输出格式，则更新
        if output_format and output_format != assistant.output_format:
            assistant.set_output_format(output_format)
            
        memory = self.get_or_create_memory(user_id)
        response = assistant.invoke(user_input, memory)
        
        # 管理对话历史长度
        if assistant.store_in_memory and len(memory.chat_memory.messages) > self.max_turns * 2:
            memory.chat_memory.messages = memory.chat_memory.messages[-self.max_turns * 2:]
            
        return response

    def clear_memory(self, user_id: str):
        """清除指定用户的记忆"""
        if user_id in self.memory_dict:
            self.memory_dict[user_id].clear()
            
    def update_assistant_prompt(self, assistant_name: str, prompt_template: str):
        """更新指定助手的提示词模板"""
        if assistant_name not in self.assistants:
            raise ValueError(f"Assistant {assistant_name} not found.")
        self.assistants[assistant_name].set_prompt_template(prompt_template)


def initialize() -> AssistantManager:
    """
    初始化助手管理器，加载所有模型和助手
    
    Returns:
        AssistantManager: 初始化后的助手管理器实例
    """
    manager = AssistantManager(max_turns=10)

    # 加载所有引擎
    engines = Engines.objects.all()
    for engine in engines:
        manager.add_model(engine)

    # 加载所有助手
    assistant_models = AssistantModel.objects.all()
    for assistant in assistant_models:
        manager.add_assistant(assistant)

    return manager