"""
📌 Step 3: LangChain 整理代码审查逻辑
===============================================
目标：学会用 LangChain 的 ChatPromptTemplate 管理 Prompt
      让代码更规范、更易扩展

与 Step 2 的区别：
    Step 2: 直接拼接字符串 → 不好维护
    Step 3: 用模板管理 Prompt → 专业、可复用
"""

from openai import OpenAI
from config import API_KEY, BASE_URL, MODEL

# ---------- 先不引入LangChain，用Python类自己封装 ----------
# 这样你能看清每一行在做什么
# 等你理解了，再看 LangChain 源码会发现很简单

USE_MOCK = not API_KEY


def build_client():
    if USE_MOCK:
        return None
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


class PromptTemplate:
    """
    简单的 Prompt 模板引擎
    把 {变量名} 替换成实际内容

    这就是 LangChain 的 ChatPromptTemplate 的简化版
    """

    def __init__(self, template: str):
        self.template = template

    def format(self, **kwargs) -> str:
        """把模板里的 {xxx} 替换成传入的值"""
        result = self.template
        for key, value in kwargs.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result


# ========== 定义审查模板 ==========

# System Prompt 模板
SYSTEM_PROMPT_TPL = PromptTemplate(
    """你是一位资深代码审查专家，精通{language}开发。
你的专业领域包括：{expertise}
请以严格但建设性的态度审查代码。
输出语言：{language_output}"""
)

# 审查指令模板
REVIEW_PROMPT_TPL = PromptTemplate(
    """请审查以下代码，从这几个维度分析：

1. 🐛 潜在 Bug：是否存在逻辑错误或边界情况
2. 🔒 安全问题：是否存在安全隐患
3. ⚡ 性能问题：是否存在效率低下的实现
4. ✨ 可读性：代码是否清晰易维护
5. 💡 改进建议：如何让代码更好

代码内容：
```{language}
{code}
```

请按以下JSON格式输出：
{{
    "score": "1-10的分数",
    "bugs": [{{"severity": "高/中/低", "description": "...", "line": "行号", "suggestion": "..."}}],
    "security": [{{"severity": "高/中/低", "description": "..."}}],
    "suggestions": ["建议1", "建议2"],
    "summary": "总体评价"
}}"""
)


def review_code(
    client,
    code: str,
    language: str = "python",
    expertise: str = "bug检测, 安全审查, 性能优化",
    language_output: str = "中文"
) -> str:
    """使用模板化的Prompt进行代码审查"""

    system_prompt = SYSTEM_PROMPT_TPL.format(
        language=language,
        expertise=expertise,
        language_output=language_output
    )

    user_prompt = REVIEW_PROMPT_TPL.format(
        language=language,
        code=code
    )

    if USE_MOCK:
        return json_mock_result()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,  # 审查任务：低温度
        max_tokens=2048,
    )
    return response.choices[0].message.content


def json_mock_result():
    return '''{
    "score": 5,
    "bugs": [
        {"severity": "高", "description": "calculate_average 在空列表时会除零", "line": "3", "suggestion": "添加空列表检查"}
    ],
    "security": [
        {"severity": "高", "description": "SQL注入风险，使用f-string拼接SQL语句", "suggestion": "使用参数化查询"}
    ],
    "suggestions": [
        "process_list 可以用列表推导式简化",
        "save_to_file 缺少异常处理和文件关闭"
    ],
    "summary": "代码有基本功能，但存在严重的安全和边界问题，需要修复后才能用于生产环境"
}'''


# ========== 测试代码 ==========
TEST_CODE = """
class ShoppingCart:
    def __init__(self):
        self.items = []
        self.total = 0

    def add_item(self, name, price, quantity=1):
        self.items.append({"name": name, "price": price, "qty": quantity})
        self.total += price * quantity

    def remove_item(self, name):
        for item in self.items:
            if item["name"] == name:
                self.items.remove(item)
                self.total -= item["price"] * item["qty"]
                return True
        return False

    def checkout(self, user_input):
        # 用户输入了优惠码
        if user_input == "DISCOUNT10":
            self.total *= 0.9
        exec(user_input)  # 处理用户输入
        return self.total
"""


if __name__ == "__main__":
    client = build_client()

    print("📌 Step 3: 模板化的代码审查")
    print("=" * 60)

    print(f"\n📄 测试代码（ShoppingCart类）：\n{TEST_CODE}")
    print("=" * 60)

    print("\n🤖 审查结果：")
    result = review_code(client, TEST_CODE)

    # 美化输出
    try:
        import json
        parsed = json.loads(result)
        print(f"\n📊 评分: {parsed['score']}/10")
        print(f"\n📝 总结: {parsed['summary']}")
        print(f"\n🐛 Bug ({len(parsed['bugs'])}个):")
        for b in parsed['bugs']:
            print(f"  [{b['severity']}] {b['description']}")
        if parsed.get('security'):
            print(f"\n🔒 安全问题 ({len(parsed['security'])}个):")
            for s in parsed['security']:
                print(f"  [{s['severity']}] {s['description']}")
    except:
        print(result)

    print("\n" + "=" * 60)
    print("💡 思考题：")
    print("1. checkout 方法里有什么严重安全问题？")
    print("2. 如果把expertise改成 'Python安全专家'，结果会变吗？")
    print("3. 试试把语言改成 'java'，换一段Java代码审查")
