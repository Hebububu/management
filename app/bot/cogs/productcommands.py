import discord
from discord.ext import commands
from app.utils.logger import mainLogger
from app.database.crud.product_crud import ProductCRUD

# 로거 정의
logger = mainLogger()

# CRUD
crud = ProductCRUD()

class ProductCommands(commands.Cog):
    """
    공통 제품 관련 명령어를 처리하는 클래스입니다.
    """

    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(ProductCommands(bot))


