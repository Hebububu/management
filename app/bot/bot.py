import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from app.utils.logger import mainLogger

# 로거 정의
logger = mainLogger()

# 토큰 로드
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# 봇 정의
bot = commands.Bot(command_prefix=';;', intents=discord.Intents.all())

# 익스텐션 로드
@bot.event
async def load_extensions():
    for filename in os.listdir('./app/bot/cogs'):
        if filename.endswith('.py') and filename != '__init__.py':
            extension = 'cogs.' + filename[:-3]
            logger.info(f'{extension} 익스텐션 로드 중...')
            try:
                await bot.load_extension(extension)
                logger.info(f'{extension} 익스텐션 로드 완료')
            except Exception as e:
                logger.error(f'{extension} 익스텐션 로드 실패: {e}')

# 셋업 
@bot.event
async def setup_hook():
    try:
        await load_extensions()
        await bot.tree.sync()
    except Exception as e:
        logger.error(f'셋업 함수 실행 중 오류 발생: {e}')

# on_ready 이벤트
@bot.event
async def on_ready():
    logger.info(f'{bot.user} 봇이 준비되었습니다.')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='::hebuthinking::'))

# 봇 실행
bot.run(TOKEN)




