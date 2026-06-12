"""
配置文件
负责读取环境变量，管理API配置
"""
import os
from dotenv import load_dotenv

load_dotenv()  # 读取 .env 文件

# ---------- DeepSeek 配置 (默认) ----------
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = "deepseek-chat"  # DeepSeek-V3 模型

# ---------- OpenAI 配置 (备选) ----------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = "gpt-4o-mini"       # 便宜且够用

# ---------- 选择用哪个 ----------
# 优先用 DeepSeek，没用就切 OpenAI
if DEEPSEEK_API_KEY:
    API_KEY = DEEPSEEK_API_KEY
    BASE_URL = DEEPSEEK_BASE_URL
    MODEL = DEEPSEEK_MODEL
elif OPENAI_API_KEY:
    API_KEY = OPENAI_API_KEY
    BASE_URL = OPENAI_BASE_URL
    MODEL = OPENAI_MODEL
else:
    API_KEY = ""
    BASE_URL = ""
    MODEL = ""
