# AI 助手 API 文档

## 概述

本文档详细描述了 AI 助手服务的 API 接口，包括助手管理、助手模板、助手配置和用户助手模板等功能。

---

## 目录

1. [助手管理 API](#1-助手管理-api)
2. [助手模板 API](#2-助手模板-api)
3. [助手配置 API](#3-助手配置-api)
4. [用户助手模板 API](#4-用户助手模板-api)
5. [配置选项 API](#5-配置选项-api)
6. [聊天 API](#6-聊天-api)

---

## 1. 助手管理 API

### 1.1 获取助手列表

获取所有可用的助手，默认只返回激活状态的助手。

**请求方法**：GET

**请求路径**：`/api/assistant/assistants/`

**查询参数**：

- `is_active`：（可选）是否只返回激活的助手，布尔值
- `is_memory`：（可选）是否只返回启用记忆的助手，布尔值
- `search`：（可选）搜索关键词，将在名称和描述中搜索
- `ordering`：（可选）排序字段，可选值：`name`, `created_at`, `updated_at`

**响应示例**：

```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "id": 1,
      "name": "通用助手",
      "description": "一个通用的AI助手",
      "is_active": true,
      "is_memory": true,
      "created_at": 1709251200,
      "updated_at": 1709251200
    },
    {
      "id": 2,
      "name": "客服助手",
      "description": "专门解答客户问题的助手",
      "is_active": true,
      "is_memory": false,
      "created_at": 1709251200,
      "updated_at": 1709251200
    }
  ]
}
```

### 1.2 获取助手详情

根据ID获取特定助手的详细信息。

**请求方法**：GET

**请求路径**：`/api/assistant/assistants/{id}/`

**路径参数**：

- `id`：助手ID

**响应示例**：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1,
    "name": "通用助手",
    "description": "一个通用的AI助手",
    "is_active": true,
    "is_memory": true,
    "created_at": 1709251200,
    "updated_at": 1709251200
  }
}
```

---

## 2. 助手模板 API

### 2.1 获取助手模板列表

获取所有可用的助手模板。

**请求方法**：GET

**请求路径**：`/api/assistant/templates/`

**查询参数**：

- `is_default`：（可选）是否只返回默认模板，布尔值
- `search`：（可选）搜索关键词，将在名称中搜索
- `ordering`：（可选）排序字段，可选值：`name`, `created_at`, `updated_at`

**响应示例**：

```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "id": 1,
      "name": "标准模板",
      "prompt_template": "你是一个AI助手，请回答用户的问题。",
      "is_default": true,
      "created_at": 1709251200,
      "updated_at": 1709251200
    },
    {
      "id": 2,
      "name": "专业模板",
      "prompt_template": "你是一个专业的AI助手，请用专业的语言回答用户的问题。",
      "is_default": false,
      "created_at": 1709251200,
      "updated_at": 1709251200
    }
  ]
}
```

### 2.2 获取助手模板详情

根据ID获取特定助手模板的详细信息。

**请求方法**：GET

**请求路径**：`/api/assistant/templates/{id}/`

**路径参数**：

- `id`：助手模板ID

**响应示例**：

```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "id": 1,
      "user_id": null,
      "name": "标准配置",
      "relationship": "Buddy",
      "nickname": "Friend",
      "personality": "Cheerful",
      "greeting": "你好！有什么我可以帮助你的吗？",
      "dialogue_style": "友好",
      "is_public": true,
      "is_premium": false
    },
    {
      "id": 2,
      "user_id": 123,
      "name": "个人配置",
      "relationship": "BFF",
      "nickname": "Bestie",
      "personality": "Fun & Humorous",
      "greeting": "嘿，老朋友！今天过得怎么样？",
      "dialogue_style": "幽默",
      "is_public": false,
      "is_premium": true
    }
  ]
}
```

---

## 3. 助手配置 API

### 3.1 获取助手配置列表

获取所有可用的助手配置，包括公共配置和当前用户的配置。

**请求方法**：GET

**请求路径**：`/api/assistant/configs/`

**查询参数**：

- `user_id`：（可选）用户ID，筛选特定用户的配置
- `name`：（可选）配置名称，精确匹配
- `is_public`：（可选）是否只返回公共配置，布尔值
- `is_premium`：（可选）是否只返回付费配置，布尔值
- `search`：（可选）搜索关键词，将在名称、关系、昵称和性格中搜索
- `ordering`：（可选）排序字段，可选值：`name`, `id`

**响应示例**：

```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "id": 1,
      "user_id": null,
      "name": "标准配置",
      "relationship": "Buddy",
      "nickname": "Friend",
      "personality": "Cheerful",
      "greeting": "你好！有什么我可以帮助你的吗？",
      "dialogue_style": "友好",
      "is_public": true,
      "is_premium": false
    },
    {
      "id": 2,
      "user_id": 123,
      "name": "个人配置",
      "relationship": "BFF",
      "nickname": "Bestie",
      "personality": "Fun & Humorous",
      "greeting": "嘿，老朋友！今天过得怎么样？",
      "dialogue_style": "幽默",
      "is_public": false,
      "is_premium": true
    }
  ]
}
```

### 3.2 创建助手配置

创建新的助手配置。

**请求方法**：POST

**请求路径**：`/api/assistant/configs/`

**请求体**：

```json
{
  "name": "我的配置",
  "relationship": "Buddy",
  "nickname": "Friend",
  "personality": "Cheerful",
  "greeting": "你好！有什么我可以帮助你的吗？",
  "dialogue_style": "友好",
  "is_public": false
}
```

**响应示例**：

```json
{
  "code": 201,
  "msg": "success",
  "data": {
    "id": 3,
    "user_id": 123,
    "name": "我的配置",
    "relationship": "Buddy",
    "nickname": "Friend",
    "personality": "Cheerful",
    "greeting": "你好！有什么我可以帮助你的吗？",
    "dialogue_style": "友好",
    "is_public": false,
    "is_premium": false
  }
}
```

### 3.3 获取助手配置详情

根据ID获取特定助手配置的详细信息。

**请求方法**：GET

**请求路径**：`/api/assistant/configs/{id}/`

**路径参数**：

- `id`：助手配置ID

**响应示例**：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1,
    "user_id": null,
    "name": "标准配置",
    "relationship": "Buddy",
    "nickname": "Friend",
    "personality": "Cheerful",
    "greeting": "你好！有什么我可以帮助你的吗？",
    "dialogue_style": "友好",
    "is_public": true,
    "is_premium": false
  }
}
```

### 3.4 更新助手配置

更新特定助手配置的信息。

**请求方法**：PUT/PATCH

**请求路径**：`/api/assistant/configs/{id}/`

**路径参数**：

- `id`：助手配置ID

**请求体**：

```json
{
  "name": "更新后的配置",
  "greeting": "你好，我是你的AI助手！"
}
```

**响应示例**：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1,
    "user_id": null,
    "name": "更新后的配置",
    "relationship": "Buddy",
    "nickname": "Friend",
    "personality": "Cheerful",
    "greeting": "你好，我是你的AI助手！",
    "dialogue_style": "友好",
    "is_public": true,
    "is_premium": false
  }
}
```

### 3.5 删除助手配置

删除特定的助手配置。

**请求方法**：DELETE

**请求路径**：`/api/assistant/configs/{id}/`

**路径参数**：

- `id`：助手配置ID

**响应示例**：

```json
{
  "code": 204,
  "msg": "success",
  "data": null
}
```

---

## 4. 用户助手模板 API

### 4.1 获取用户助手模板列表

获取当前用户的所有助手模板。

**请求方法**：GET

**请求路径**：`/api/assistant/user-templates/`

**查询参数**：

- `is_default`：（可选）是否只返回默认模板，布尔值
- `search`：（可选）搜索关键词，将在名称中搜索
- `ordering`：（可选）排序字段，可选值：`name`, `created_at`, `updated_at`

**响应示例**：

```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "id": 1,
      "user_id": 123,
      "name": "我的模板",
      "prompt_template": "你是一个AI助手，请回答我的问题。",
      "is_default": true,
      "created_at": 1709251200,
      "updated_at": 1709251200
    },
    {
      "id": 2,
      "user_id": 123,
      "name": "专业模板",
      "prompt_template": "你是一个专业的AI助手，请用专业的语言回答我的问题。",
      "is_default": false,
      "created_at": 1709251200,
      "updated_at": 1709251200
    }
  ]
}
```

### 4.2 获取用户助手模板详情

根据ID获取特定用户助手模板的详细信息。

**请求方法**：GET

**请求路径**：`/api/assistant/user-templates/{id}/`

**路径参数**：

- `id`：用户助手模板ID

**响应示例**：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1,
    "user_id": 123,
    "name": "我的模板",
    "prompt_template": "你是一个AI助手，请回答我的问题。",
    "is_default": true,
    "created_at": 1709251200,
    "updated_at": 1709251200
  }
}
```

### 4.3 更新用户助手模板

更新特定用户助手模板的信息。

**请求方法**：PUT/PATCH

**请求路径**：`/api/assistant/user-templates/{id}/`

**路径参数**：

- `id`：用户助手模板ID

**请求体**：

```json
{
  "name": "更新后的模板",
  "is_default": true
}
```

**响应示例**：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1,
    "user_id": 123,
    "name": "更新后的模板",
    "prompt_template": "你是一个AI助手，请回答我的问题。",
    "is_default": true,
    "created_at": 1709251200,
    "updated_at": 1709337600
  }
}
```

### 4.4 生成用户助手模板

从助手模板和助手配置生成用户助手模板。

**请求方法**：POST

**请求路径**：`/api/assistant/user-templates/generate/`

**请求体**：

```json
{
  "template_id": 1,
  "config_id": 2,
  "name": "我的自定义模板",
  "is_default": true
}
```

**响应示例**：

```json
{
  "code": 201,
  "msg": "success",
  "data": {
    "id": 3,
    "user_id": 123,
    "name": "我的自定义模板",
    "prompt_template": "你是一个AI助手，你的性格是Cheerful，请称呼我为Friend，我们的关系是Buddy。请回答我的问题。",
    "is_default": true,
    "created_at": 1709337600,
    "updated_at": 1709337600
  }
}
```
---
## 5. 配置选项 API

### 5.1 获取配置选项

获取关系、昵称和性格的可用选项，标识哪些是付费选项。

**请求方法**：GET

**请求路径**：`/api/assistant/options/available-options/`

**响应示例**：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "relationship": [
      {
        "value": "Newbie",
        "is_premium": false
      },
      {
        "value": "Companion",
        "is_premium": false
      },
      {
        "value": "Buddy",
        "is_premium": false
      },
      {
        "value": "BF",
        "is_premium": true
      },
      {
        "value": "GF",
        "is_premium": true
      },
      {
        "value": "BFF",
        "is_premium": true
      },
      {
        "value": "Muse",
        "is_premium": true
      },
      {
        "value": "Mystery",
        "is_premium": true
      },
      {
        "value": "Crush",
        "is_premium": true
      },
      {
        "value": "Money Guru",
        "is_premium": true
      },
      {
        "value": "Butler",
        "is_premium": true
      },
      {
        "value": "Boss",
        "is_premium": true
      },
      {
        "value": "Customization",
        "is_premium": true
      }
    ],
    "nickname": [
      {
        "value": "Friend",
        "is_premium": false
      },
      {
        "value": "Mate",
        "is_premium": false
      },
      {
        "value": "Dude",
        "is_premium": false
      },
      {
        "value": "Babe",
        "is_premium": true
      },
      {
        "value": "Angel",
        "is_premium": true
      },
      {
        "value": "Champ",
        "is_premium": true
      },
      {
        "value": "Sweetie",
        "is_premium": true
      },
      {
        "value": "Stranger",
        "is_premium": true
      },
      {
        "value": "Master",
        "is_premium": true
      },
      {
        "value": "Bestie",
        "is_premium": true
      },
      {
        "value": "Cutie",
        "is_premium": true
      },
      {
        "value": "Rookie",
        "is_premium": true
      },
      {
        "value": "Customization",
        "is_premium": true
      }
    ],
    "personality": [
      {
        "value": "Cheerful",
        "is_premium": false
      },
      {
        "value": "Cute",
        "is_premium": false
      },
      {
        "value": "Friendly & Warm",
        "is_premium": true
      },
      {
        "value": "Romantic & Flirty",
        "is_premium": true
      },
      {
        "value": "Professional & Smart",
        "is_premium": true
      },
      {
        "value": "Fun & Humorous",
        "is_premium": true
      },
      {
        "value": "Calm & Caring",
        "is_premium": true
      },
      {
        "value": "Unique & Fantasy",
        "is_premium": true
      },
      {
        "value": "Customization",
        "is_premium": true
      }
    ],
    "user_is_premium": true
  }
}
```
---
## 6. 聊天 API

### 6.1 发送聊天请求

向指定助手发送聊天请求并获取回复。

**请求方法**：POST

**请求路径**：`/api/agent/`

**请求体**：

```json
{
  "assistant_name": "通用助手",
  "user_input": "你好，请介绍一下你自己",
  "language": "zh",
  "model_name": "qwen-max"
}
```

**响应示例**：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "response": "你好！我是一个AI助手，我的名字是通用助手。我可以回答你的问题，提供信息，或者帮助你完成各种任务。有什么我可以帮助你的吗？",
    "content": {}
  }
}
```

### 6.2 清除聊天历史

清除指定用户的聊天历史记录。

**请求方法**：POST

**请求路径**：`/api/agent/clear_history/`

**响应示例**：

```json
{
  "code": 200,
  "msg": "聊天历史已清除",
  "data": null
}
```

### 6.3 更新助手提示词

更新指定助手的提示词模板。

**请求方法**：POST

**请求路径**：`/api/agent/update_prompt/`

**请求体**：

```json
{
  "assistant_name": "通用助手",
  "prompt_template": "你是一个专业的AI助手，擅长解答各种问题。请用简洁明了的语言回答用户的问题。"
}
```

## 错误响应

所有API在发生错误时都会返回统一格式的错误响应：

```json
{
  "code": 400,
  // HTTP状态码
  "msg": "错误信息",
  // 错误描述
  "data": null
  // 通常为null或包含详细错误信息
}
```

常见错误码：

- 400：请求参数错误
- 401：未授权（未登录）
- 403：权限不足
- 404：资源不存在
- 500：服务器内部错误

---

## 付费功能限制

某些功能和选项仅对付费用户开放：

1. **关系选项**：
    - 免费选项：Newbie, Companion, Buddy
    - 付费选项：BF, GF, BFF, Muse, Mystery, Crush, Money Guru, Butler, Boss, 自定义

2. **昵称选项**：
    - 免费选项：Friend, Mate, Dude
    - 付费选项：Babe, Angel, Champ, Sweetie, Stranger, Master, Bestie, Cutie, Rookie, 自定义

3. **性格选项**：
    - 免费选项：Cheerful, Cute
    - 付费选项：Friendly & Warm, Romantic & Flirty, Professional & Smart, Fun & Humorous, Calm & Caring, Unique &
      Fantasy, 自定义

非付费用户尝试使用付费选项时，将收到403错误响应。
