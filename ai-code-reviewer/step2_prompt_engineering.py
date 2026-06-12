"""
📌 Step 2: Prompt Engineering — 让LLM分析代码
=============================================
目标：学会写高质量的 Prompt，让模型理解代码并找出bug

核心知识点：
    1. System Prompt 设定角色和规则
    2. 结构化输出（JSON格式）
    3. Few-shot（给例子）提升效果
    4. Chain-of-Thought（让模型逐步推理）

这个脚本会分析一段 Python 代码中的潜在缺陷。
"""

from openai import OpenAI
from config import API_KEY, BASE_URL, MODEL
import json

# 模拟模式
USE_MOCK = not API_KEY


def build_client():
    if USE_MOCK:
        return None
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


# ========== 你要审查的代码 ==========
# 🎯 试试看：把下面的代码换成你自己的，或找一段有bug的代码
SAMPLE_CODE = """
def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    return total / count

def get_user_data(user_id):
    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchone()

def process_list(items):
    result = []
    for i in range(len(items)):
        result.append(items[i] * 2)
    return result

def save_to_file(filename, content):
    f = open(filename, 'w')
    f.write(content)
"""


def review_code(client, code: str) -> str:
    """
    用LLM审查代码，找出潜在问题

    这里使用了：
    1. System Prompt → 设定为"资深代码审查员"角色
    2. 结构化输出 → 要求按固定格式回答
    3. Chain-of-Thought → 让模型一步步分析
    """
    system_prompt = """你是一位资深代码审查专家，有10年软件开发经验。
你的任务是审查代码并找出所有潜在问题。

请按以下格式分析每个问题：
1. 【严重程度】(高/中/低)
2. 【问题类型】(bug/安全/性能/可读性/最佳实践)
3. 【问题描述】
4. 【修复建议】

最后给出总体评价：代码质量分数(1-10分)"""

    user_prompt = f"""请审查以下Python代码，逐行分析潜在问题：

```python
{code}
```

请先一行行阅读代码，再给出分析结果。"""

    if USE_MOCK:
        return """【模拟审查结果】

1. 【严重程度】高 | 【类型】bug
   【描述】calculate_average 中 numbers 为空列表时会报 ZeroDivisionError
   【建议】添加 if not numbers: return 0 的判断

2. 【严重程度】高 | 【类型】安全
   【描述】get_user_data 使用了 f-string 拼接 SQL，存在 SQL注入风险
   【建议】改用参数化查询 cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

3. 【严重程度】中 | 【类型】性能
   【描述】process_list 可以用列表推导式简化，更Pythonic
   【建议】return [item * 2 for item in items]

📊 总体评分：5/10 — 存在严重安全和边界问题"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,      # 审查任务用低温度，更准确
        max_tokens=2048,
    )
    return response.choices[0].message.content


# ========== 动手试试 ==========
if __name__ == "__main__":
    client = build_client()

    print("🔍 AI Code Reviewer — Step 2: Prompt Engineering")
    print("=" * 50)
    print(f"\n📄 审查的代码：\n{SAMPLE_CODE}")
    print("\n" + "=" * 50)

    print("\n🤖 审查结果：\n")
    result = review_code(client, SAMPLE_CODE)
    print(result)
    print("\n" + "=" * 50)

    # 🎯 思考题：
    # 1. 把 temperature 从 0.3 改成 0.9，看看有什么变化？
    # 2. 换成一段你自己的代码试试
    # 3. 修改 System Prompt，让输出改成纯JSON格式
    print("\n💡 试试：修改 SAMPLE_CODE，换成你自己想审查的代码！")
