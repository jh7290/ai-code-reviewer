"""
📌 Step 1: 调通 LLM API
======================
目标：学会用 Python 调用大模型 API
这是所有 AI 应用的第一步！

你需要先：
1. 去 https://platform.deepseek.com/ 注册账号
2. 充值（最低10元，够用很久）
3. 在 API Keys 页面创建 Key
4. 复制 Key，粘贴到 .env 文件里

然后运行这个文件：
    python step1_hello_llm.py

成功的话你会看到模型回复你一段话 🎉
"""

# ---------- 核心知识点 ----------
# 1. OpenAI SDK 是所有 LLM API 的事实标准
# 2. DeepSeek、智谱、通义千问等国产模型都兼容这套SDK
# 3. 核心概念：Client → 发请求 → 得到回复
# 4. Message 结构：
#    - system: 设定角色/规则（可选）
#    - user:  用户提问
#    - assistant: 模型回复

from openai import OpenAI
from config import API_KEY, BASE_URL, MODEL

# ------ 如果你没有 API Key，可以用这个模拟模式 ------
USE_MOCK = not API_KEY  # 没Key就用模拟

def build_client():
    """创建 API 客户端（大模型的对话窗口）"""
    if USE_MOCK:
        return None
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


def chat_with_llm(client, user_message: str, system_prompt: str = "") -> str:
    """
    和LLM对话的核心函数

    参数：
        client: OpenAI客户端
        user_message: 用户的输入
        system_prompt: 系统设定（可选）

    返回：
        模型的文字回复
    """
    # 构建消息列表
    messages = []
    if system_prompt:
        # system message：告诉模型它的角色和行事方式
        messages.append({"role": "system", "content": system_prompt})
    # user message：我们问的问题
    messages.append({"role": "user", "content": user_message})

    # 模拟模式（没有API Key时使用）
    if USE_MOCK:
        return f"[模拟回复] 收到你的消息了！你问了：\n{user_message}"

    # 真实调用API
    response = client.chat.completions.create(
        model=MODEL,        # 模型名称
        messages=messages,  # 对话历史
        temperature=0.7,    # 0-2 控制创造性，0最保守，2最放飞
        max_tokens=1024,    # 最大回复长度
    )

    # 从回复结构里提取文字内容
    return response.choices[0].message.content


# ========== 动手试试 ==========
if __name__ == "__main__":
    client = build_client()

    # 🎯 试一试：问个简单问题
    reply = chat_with_llm(
        client,
        user_message="用一句话解释什么是大语言模型（LLM）？"
    )
    print("\n🤖 模型回复：")
    print("-" * 50)
    print(reply)
    print("-" * 50)

    print("\n✅ 如果看到上面有回复，说明API调通了！")

    # 思考题：修改上面的 user_message，试试问别的问题
