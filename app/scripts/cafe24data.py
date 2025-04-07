from dotenv import load_dotenv
from app.utils.logger import mainLogger
import os

# 환경 변수 로드
load_dotenv()

# 로거 설정 
logger = mainLogger()

mall_id = "richcp"
client_id = os.getenv("RICHCP_CLIENT_ID")
client_secret = os.getenv("RICHCP_CLIENT_SECRET")
redirect_uri =f"https://{mall_id}.cafe24.com/order/basket.html"
state = "app_install"
scope = "mall.read_application,mall.write_application,mall.read_product,mall.write_product,mall.read_store,mall.write_store"

url = f"""https://{mall_id}.cafe24api.com/api/v2/oauth/authorize?response_type=code&client_id={client_id}&state={state}&redirect_uri={redirect_uri}&scope={scope}"""

print(url)