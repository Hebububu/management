import discord
from discord import app_commands
from discord.ext import commands
from app.utils.logger import mainLogger
from app.scripts.naverdatamanager import NaverDataManager
from app.database.crud.product_crud import ProductCRUD

logger = mainLogger()
naver = NaverDataManager()
crud = ProductCRUD()

class NaverCommerceCommands(commands.Cog):
    """
    네이버 커머스 관련 명령어를 처리하는 클래스입니다.
    """

    def __init__(self, bot):
        self.bot = bot

    # get_all_products_list -> insert into db 

async def setup(bot):
    await bot.add_cog(NaverCommerceCommands(bot))
