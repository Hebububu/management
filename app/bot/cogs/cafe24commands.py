import discord
from discord import app_commands
from discord.ext import commands
from app.utils.logger import mainLogger
from app.scripts.cafe24datamanager import Cafe24DataManager
from app.database.crud.product_crud import ProductCRUD

# 로거 정의
logger = mainLogger()

# 카페24 데이터 매니저 정의
cafe24 = Cafe24DataManager()

# 제품 데이터 관리 클래스 정의
crud = ProductCRUD()

class Cafe24Commands(commands.Cog):
    """
    카페24 관련 명령어를 처리하는 클래스입니다.
    """

    def __init__(self, bot):
        self.bot = bot
    
    # get all products -> insert into db (fetch_cafe24_products)
    # 공통 임베드 만들어서 넣을거임.
    @commands.command(name='fetch_cafe24_products')
    @app_commands.choices(seller_id=[
        app_commands.Choice(name='샤슈컴퍼니', value='SIASIUCP'),
        app_commands.Choice(name='리치컴퍼니', value='RICHCP')
    ])
    async def fetch_cafe24_products(self, ctx, seller_id: str):

        all_products = cafe24.get_all_products(seller_id)  
        filtered_products = cafe24.filter_duplicated_products(all_products, seller_id)
        sorted_products = cafe24.sort_products_data(filtered_products, seller_id)

        try: 
            if not sorted_products:
                await ctx.send(f'새로 추가된 제품이 없습니다.')
            else:
                await ctx.send(f'새로 추가된 제품이 있습니다.')

            for product in sorted_products:
                crud.create_product(product)

        except Exception as e:
            logger.error(f'카페24 제품 조회 중 오류 발생: {e}')
            await ctx.send(f'카페24 제품 조회 중 오류 발생: {e}')

    # get missing products -> update tags/etc... -> update db


async def setup(bot):
    await bot.add_cog(Cafe24Commands(bot))
