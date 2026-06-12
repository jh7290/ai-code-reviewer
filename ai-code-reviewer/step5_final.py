"""
📌 Step 5: 完结篇 — 代码测试用例自动生成
===============================================
目标：让AI根据代码自动生成测试用例
这是 JD 里明确写到的 "测试用例自动生成" 能力！

学完这个项目，你就能在简历上写：
    项目名称：AI Code Reviewer 智能代码审查系统
    技术栈：Python + LangChain + Streamlit + LLM API
    核心能力：
    - 基于LLM的智能代码缺陷检测
    - 代码安全风险分析
    - 自动化测试用例生成
    - 交互式Web UI
"""

from openai import OpenAI
from config import API_KEY, BASE_URL, MODEL
import json

USE_MOCK = not API_KEY


def build_client():
    if USE_MOCK:
        return None
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


# ========== 生成测试用例 ==========
TEST_CODE = """
def is_valid_password(password):
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True
"""


def generate_tests(client, code: str) -> str:
    """让模型为代码生成测试用例"""

    system_prompt = """你是一位测试工程师，擅长编写高质量的单元测试。
请为以下函数生成全面的测试用例，包括：
1. 正常情况（Happy Path）
2. 边界情况（Edge Cases）
3. 异常情况（Error Cases）"""

    user_prompt = f"""为以下代码生成 pytest 测试用例：

```python
{code}
```

要求：
- 每个测试用例有清晰的函数名和注释
- 覆盖所有边界条件
- 使用 assert 断言
- 输出可直接运行的 Python 代码"""

    if USE_MOCK:
        return '''import pytest

def test_valid_password():
    """正常情况：符合所有规则的密码"""
    assert is_valid_password("Abc12345") == True

def test_too_short():
    """边界情况：密码太短"""
    assert is_valid_password("Ab1") == False

def test_no_uppercase():
    """边界情况：缺少大写字母"""
    assert is_valid_password("abc12345") == False

def test_no_lowercase():
    """边界情况：缺少小写字母"""
    assert is_valid_password("ABC12345") == False

def test_no_digit():
    """边界情况：缺少数字"""
    assert is_valid_password("Abcdefgh") == False

def test_empty_string():
    """异常情况：空密码"""
    assert is_valid_password("") == False

def test_exactly_8_chars():
    """边界情况：刚好8位"""
    assert is_valid_password("Abcd1234") == True

def test_with_special_chars():
    """边界情况：包含特殊字符"""
    assert is_valid_password("Abcd@#$%") == True  # 没有数字，应该返回False
'''

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=2048,
    )
    return response.choices[0].message.content


# ========== 最终改进：Add Review History ==========
# 这是我们最终项目的一个加强功能
# 记录每次审查的日志

import time
from datetime import datetime


class ReviewHistory:
    """审查历史记录器"""

    def __init__(self):
        self.records = []

    def add_record(self, code: str, result: str, language: str = "python"):
        """添加一条审查记录"""
        self.records.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "language": language,
            "code_length": len(code),
            "result_preview": result[:100] + "..." if len(result) > 100 else result,
        })

    def show_summary(self):
        """显示历史统计"""
        print(f"\n📊 审查统计")
        print(f"   总审查次数: {len(self.records)}")
        if self.records:
            print(f"   最后一次: {self.records[-1]['time']}")
            print(f"   代码长度: {self.records[-1]['code_length']} 字符")

    def export_to_markdown(self) -> str:
        """导出为 Markdown 格式（可以放到GitHub上）"""
        lines = ["# AI Code Reviewer 审查记录\n"]
        lines.append(f"总审查次数：{len(self.records)}\n")
        lines.append("| 时间 | 语言 | 代码长度 | 结果预览 |")
        lines.append("|------|------|----------|----------|")
        for r in self.records:
            lines.append(f"| {r['time']} | {r['language']} | {r['code_length']} | {r['result_preview'][:50]} |")
        return "\n".join(lines)


# ========== 主流程 ==========
if __name__ == "__main__":
    client = build_client()
    history = ReviewHistory()

    print("=" * 60)
    print("  🔍 AI Code Reviewer — 完结篇")
    print("=" * 60)

    # 1. 审查代码
    print(f"\n📄 待测代码：")
    print(TEST_CODE)
    print("\n" + "-" * 60)

    from step3_prompt_template import review_code as do_review
    review_result = do_review(client, TEST_CODE, language="python")

    print("\n🔍 审查结果：")
    try:
        parsed = json.loads(review_result)
        print(f"\n  评分: {parsed.get('score', '?')}/10")
        print(f"  总结: {parsed.get('summary', '')}")
    except:
        print(review_result)

    history.add_record(TEST_CODE, review_result)

    # 2. 生成测试用例
    print("\n" + "-" * 60)
    print("\n🧪 自动生成测试用例：")
    tests = generate_tests(client, TEST_CODE)
    print(tests)

    # 3. 显示历史
    print("\n" + "-" * 60)
    history.show_summary()

    print("\n\n✅ 项目完成！")
    print("""
🎯 你刚刚完成了：
  ✅ Step 1: LLM API 调用
  ✅ Step 2: Prompt Engineering
  ✅ Step 3: 模板化代码管理
  ✅ Step 4: Streamlit Web UI
  ✅ Step 5: 测试用例生成 + 历史记录

📝 简历可以这样写：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
项目名称：AI Code Reviewer 智能代码审查系统
技术栈：Python / LangChain / Streamlit / LLM API

- 基于大语言模型构建智能代码审查工具，覆盖Bug检测、
  安全分析、性能优化三大维度
- 通过Prompt Engineering实现结构化JSON输出，支持
  多语言代码审查
- 采用Streamlit构建交互式Web界面，提升使用体验
- 实现自动测试用例生成功能，辅助开发者提升代码质量
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
