from discord.ext import commands
from app.utils.logger import mainLogger

logger = mainLogger()

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='load')
    @commands.is_owner()
    async def load_cog(self, ctx, extension: str):
        try:
            await self.bot.load_extension(f'app.bot.cogs.{extension}')
            await ctx.send(f'{extension} 익스텐션이 성공적으로 로드되었습니다.')
            logger.info(f'{extension} 익스텐션 로드 완료')
            await self.bot.tree.sync()
        except Exception as e:
            await ctx.send(f'{extension} 익스텐션 로드 중 오류가 발생했습니다: {e}')
            logger.error(f'{extension} 익스텐션 로드 중 오류 발생: {e}')

    @commands.command(name='unload')
    @commands.is_owner()
    async def unload_cog(self, ctx, extension: str):
        try:
            await self.bot.unload_extension(f'app.bot.cogs.{extension}')
            await ctx.send(f'{extension} 익스텐션이 성공적으로 언로드되었습니다.')
            logger.info(f'{extension} 익스텐션 언로드 완료')
            await self.bot.tree.sync()
        except Exception as e:
            await ctx.send(f'{extension} 익스텐션 언로드 중 오류가 발생했습니다: {e}')
            logger.error(f'{extension} 익스텐션 언로드 중 오류 발생: {e}')

    @commands.command(name='reload')
    @commands.is_owner()
    async def reload_cog(self, ctx, extension: str):
        try:
            await self.bot.reload_extension(f'app.bot.cogs.{extension}')
            await ctx.send(f'{extension} 익스텐션이 성공적으로 리로드되었습니다.')
            logger.info(f'{extension} 익스텐션 리로드 완료')
            await self.bot.tree.sync()
        except Exception as e:
            await ctx.send(f'{extension} 익스텐션 리로드 중 오류가 발생했습니다: {e}')
            logger.error(f'{extension} 익스텐션 리로드 중 오류 발생: {e}')
            
async def setup(bot):
    await bot.add_cog(AdminCommands(bot))