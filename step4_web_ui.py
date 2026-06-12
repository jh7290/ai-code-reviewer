"""
📌 Step 4: Streamlit Web UI
===============================================
目标：学会用 Streamlit 给 AI 应用做界面
纯 Python，不需要写 HTML/CSS/JS

安装：pip install streamlit
运行：streamlit run step4_web_ui.py
"""

import streamlit as st
from openai import OpenAI
from config import API_KEY, BASE_URL, MODEL

# ========== 页面配置 ==========
st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🔍",
    layout="wide"
)

# ========== API 客户端 ==========
@st.cache_resource
def get_client():
    """缓存客户端，避免重复创建"""
    if not API_KEY:
        return None
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


# ========== 核心函数 ==========
def review_code(code: str, language: str, review_type: str) -> str:
    """调用LLM审查代码"""
    client = get_client()
    if client is None:
        return "⚠️ 请先配置 API Key（在 .env 文件中）"

    # 根据审查类型调整 Prompt
    type_instructions = {
        "全面审查": "从bug、安全、性能、可读性、最佳实践五个维度全面审查",
        "仅Bug检测": "只关注潜在的Bug和逻辑错误",
        "安全检查": "只关注安全漏洞和风险",
        "性能优化": "只关注性能问题和优化建议",
    }

    system_prompt = f"""你是一位资深{language}代码审查专家。
请{type_instructions.get(review_type, type_instructions["全面审查"])}。
以JSON格式输出。"""

    user_prompt = f"""审查这段{language}代码：
```{language}
{code}
```

JSON格式：
{{"score": 分数, "issues": [{{"type": "bug/security/performance/style", "severity": "高/中/低", "line": "行号或范围", "description": "问题描述", "suggestion": "修复建议"}}], "summary": "总体评价"}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=2048,
    )
    return response.choices[0].message.content


# ========== 页面布局 ==========
st.title("🔍 AI Code Reviewer")
st.markdown("粘贴代码，AI自动帮你审查Bug、安全问题和性能瓶颈")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 设置")

    language = st.selectbox(
        "编程语言",
        ["Python", "Java", "JavaScript", "Go", "C++", "Rust", "其他"],
    )

    review_type = st.radio(
        "审查类型",
        ["全面审查", "仅Bug检测", "安全检查", "性能优化"],
    )

    st.divider()
    st.markdown("### 💡 使用说明")
    st.markdown("""
    1. 左侧粘贴代码
    2. 选择语言和审查类型
    3. 点击「开始审查」
    """)

# 主界面：左右两栏
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📄 输入代码")
    code_input = st.text_area(
        "粘贴你的代码",
        height=400,
        placeholder="在这里粘贴你想审查的代码...",
        label_visibility="collapsed"
    )

    review_btn = st.button("🚀 开始审查", type="primary", use_container_width=True)

with col2:
    st.subheader("📋 审查结果")

    if review_btn:
        if not code_input.strip():
            st.warning("请先粘贴代码！")
        else:
            with st.spinner("🤖 AI正在审查中..."):
                result = review_code(code_input, language, review_type)

            # 尝试解析 JSON
            import json
            try:
                # 提取 JSON 部分（模型有时会在JSON前后加说明）
                json_str = result
                if "```json" in result:
                    json_str = result.split("```json")[1].split("```")[0]
                elif "```" in result:
                    json_str = result.split("```")[1].split("```")[0]

                data = json.loads(json_str.strip())

                # 显示评分
                score = data.get("score", "?")
                col_score, _ = st.columns([1, 3])
                with col_score:
                    st.metric("代码质量评分", f"{score}/10")

                # 显示总结
                st.markdown(f"**📝 评价：** {data.get('summary', '')}")

                # 显示每个问题
                issues = data.get("issues", [])
                if issues:
                    st.markdown("---")
                    st.markdown("**🔍 发现的问题：**")
                    for i, issue in enumerate(issues, 1):
                        severity = issue.get("severity", "低")
                        emoji = {"高": "🔴", "中": "🟡", "低": "🟢"}
                        st.markdown(f"""
                        {emoji.get(severity, '⚪')} **问题 #{i}** | `[{issue.get('type', '未知')}]` **{severity}**
                        - **描述：** {issue.get('description', '')}
                        - **建议：** {issue.get('suggestion', '')}
                        """)

            except (json.JSONDecodeError, Exception):
                # JSON 解析失败，直接显示原文
                st.markdown(result)

    else:
        st.info("👈 左侧粘贴代码后，点击「开始审查」")

# 页脚
st.divider()
st.caption("AI Code Reviewer | 基于大语言模型实现 | 注意：AI审查结果仅供参考")
