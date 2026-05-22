import time, os
from dotenv import load_dotenv
from openai import OpenAI
from pexpect import EOF

load_dotenv()

client = OpenAI(
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url=os.getenv("MINIMAX_BASE_URL", "https://api.minimax.io/v1"),
    timeout=30,
)

print("发送请求...")
t0 = time.time()

try:
    resp = client.chat.completions.create(
        model=os.getenv("MINIMAX_MODEL", "MiniMax-M2.7"),
        messages=[{"role": "user", "content": "说一个字"}],
        stream=False,
    )
    print(f"耗时: {time.time()-t0:.1f}s")
    print("回复:", resp.choices[0].message.content)
except Exception as e:
    print(f"失败({time.time()-t0:.1f}s): {type(e).__name__}: {e}")

