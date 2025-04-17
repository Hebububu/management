from discord.ext import commands
import discord
from app.utils.logger import mainLogger
from app.database.crud.product_crud import ProductCRUD
from app.bot.views.product_views import ProductTaggingView
from app.bot.views.product_list_view import ProductListView

# 로거 정의
logger = mainLogger()

# CRUD 객체 생성
crud = ProductCRUD()

class ProductCommands(commands.Cog):
    """
    공통 제품 관련 명령어를 처리하는 클래스입니다.
    """

    def __init__(self, bot):
        self.bot = bot
        self.tagging_sessions = {}  # 사용자별 태깅 세션 저장

    @commands.command(name="unfulfilled_products")
    async def unfulfilled_products(self, ctx, seller_id: str = None):
        """
        태그가 미입력된 제품 목록을 표시합니다.
        
        Args:
            ctx (commands.Context): 명령어 컨텍스트
            seller_id (str, optional): 판매자 ID로 필터링. 기본값은 None (모든 판매자).
        """
        try:
            # 태그 미입력 제품 조회
            products = crud.get_unfulfilled_products(seller_id)
            
            if not products:
                await ctx.send("미완성 제품이 없습니다.")
                return
            
            # 커스텀 포매터 정의
            def unfulfilled_formatter(product):
                return f"ID: {product.id}\n플랫폼: {product.platform}\n판매자: {product.seller_id}\n판매명: {product.sale_name}"
            
            # 제품 리스트 뷰 생성
            view = ProductListView(
                products=products,
                user_id=ctx.author.id,
                title="태그 미입력 제품 목록",
                per_page=5,
                custom_formatter=unfulfilled_formatter
            )
            
            await ctx.send(embed=view.get_current_page_embed(), view=view)
            logger.info(f"미완성 제품 목록 표시됨 (총 {len(products)}개)")
            
        except Exception as e:
            await ctx.send(f"제품 목록 조회 중 오류가 발생했습니다: {str(e)}")
            logger.error(f"미완성 제품 목록 조회 중 오류 발생: {e}")

    @commands.command(name="tag_next")
    async def tag_next(self, ctx, seller_id: str = None):
        """
        다음 미완성 제품의 태그를 추가합니다.
        
        Args:
            ctx (commands.Context): 명령어 컨텍스트
            seller_id (str, optional): 판매자 ID로 필터링. 기본값은 None (모든 판매자).
        """
        try:
            # 다음 미완성 제품 조회
            product = crud.get_next_unfulfilled_product(seller_id)
            
            if not product:
                await ctx.send("처리할 미완성 제품이 없습니다. 모든 제품에 태그가 입력되었습니다! 🎉")
                return
            
            # 임베드 생성
            embed = discord.Embed(
                title="제품 태그 추가", 
                color=discord.Color.green(),
                description=f"아래 제품의 태그와 정보를 입력합니다. (남은 미완성 제품: {len(crud.get_unfulfilled_products(seller_id))}개)"
            )
            
            embed.add_field(name="제품명", value=product.sale_name, inline=False)
            embed.add_field(name="ID", value=product.id, inline=True)
            embed.add_field(name="플랫폼", value=product.platform, inline=True)
            embed.add_field(name="판매자", value=product.seller_id, inline=True)
            
            # 기존 정보가 있는 경우 표시
            if product.category:
                embed.add_field(name="카테고리", value=product.category, inline=True)
            
            if product.company:
                embed.add_field(name="제조사", value=product.company, inline=True)
            
            if product.product_name:
                embed.add_field(name="관리제품명", value=product.product_name, inline=True)
            
            if product.tags:
                embed.add_field(name="태그", value=product.tags, inline=True)
            
            # 사용자 세션에 현재 제품 ID 저장
            self.tagging_sessions[ctx.author.id] = product.id
            
            # UI 생성 및 표시
            view = ProductTaggingView(product)
            message = await ctx.send(embed=embed, view=view)
            
            # 세션 정보에 메시지 ID 저장
            self.tagging_sessions[f"{ctx.author.id}_message"] = message.id
            
            logger.info(f"제품 ID {product.id} 태그 추가 UI 표시됨 (순차 처리)")
            
        except Exception as e:
            await ctx.send(f"다음 제품 태그 추가 중 오류가 발생했습니다: {str(e)}")
            logger.error(f"다음 제품 태그 추가 중 오류 발생: {e}")

    @commands.command(name="continue_tagging")
    async def continue_tagging(self, ctx, seller_id: str = None):
        """
        태그 입력 세션을 계속합니다. 이전 태그 입력이 완료된 후에 다음 제품으로 진행합니다.
        
        Args:
            ctx (commands.Context): 명령어 컨텍스트
            seller_id (str, optional): 판매자 ID로 필터링. 기본값은 None (모든 판매자).
        """
        if ctx.author.id in self.tagging_sessions:
            await ctx.send("이미 진행 중인 태그 입력 세션이 있습니다. 해당 세션을 먼저 완료해주세요.")
            return
        
        await self.tag_next(ctx, seller_id)

    @commands.command(name="tag_batch")
    async def tag_batch(self, ctx, seller_id: str = None, count: int = 5):
        """
        여러 미완성 제품을 연속으로 처리합니다.
        
        Args:
            ctx (commands.Context): 명령어 컨텍스트
            seller_id (str, optional): 판매자 ID로 필터링. 기본값은 None (모든 판매자).
            count (int, optional): 처리할 제품 수. 기본값은 5.
        """
        if count > 20:
            await ctx.send("한 번에 최대 20개까지만 처리할 수 있습니다.")
            count = 20
            
        products = crud.get_unfulfilled_products(seller_id)[:count]
        
        if not products:
            await ctx.send("처리할 미완성 제품이 없습니다.")
            return
            
        embed = discord.Embed(
            title="일괄 태그 입력 시작", 
            color=discord.Color.blue(),
            description=f"총 {len(products)}개 제품의 태그를 연속으로 입력합니다."
        )
        
        for i, product in enumerate(products, 1):
            embed.add_field(
                name=f"{i}. {product.sale_name}",
                value=f"ID: {product.id}",
                inline=True
            )
            
        embed.set_footer(text="';;tag_next' 명령어로 첫 번째 제품부터 태그 입력을 시작합니다.")
        await ctx.send(embed=embed)

    @commands.command(name="add_tags")
    async def add_tags(self, ctx, product_id: int):
        """
        제품의 태그 및 정보를 추가합니다.
        
        Args:
            ctx (commands.Context): 명령어 컨텍스트
            product_id (int): 태그를 추가할 제품 ID
        """
        try:
            # 제품 정보 조회
            product = crud.get_product(product_id)
            
            if not product:
                await ctx.send(f"ID {product_id}에 해당하는 제품을 찾을 수 없습니다.")
                return
            
            # 임베드 생성
            embed = discord.Embed(
                title="제품 태그 추가", 
                color=discord.Color.green(),
                description="아래 제품의 태그와 정보를 입력합니다."
            )
            
            embed.add_field(name="제품명", value=product.sale_name, inline=False)
            embed.add_field(name="플랫폼", value=product.platform, inline=True)
            embed.add_field(name="판매자", value=product.seller_id, inline=True)
            
            # 기존 정보가 있는 경우 표시
            if product.category:
                embed.add_field(name="카테고리", value=product.category, inline=True)
            
            if product.company:
                embed.add_field(name="제조사", value=product.company, inline=True)
            
            if product.product_name:
                embed.add_field(name="관리제품명", value=product.product_name, inline=True)
            
            if product.tags:
                embed.add_field(name="태그", value=product.tags, inline=True)
            
            # UI 생성 및 표시
            view = ProductTaggingView(product)
            await ctx.send(embed=embed, view=view)
            logger.info(f"제품 ID {product_id} 태그 추가 UI 표시됨")
            
        except Exception as e:
            await ctx.send(f"제품 태그 추가 중 오류가 발생했습니다: {str(e)}")
            logger.error(f"제품 태그 추가 중 오류 발생: {e}")
    
    @commands.command(name="search_products")
    async def search_products(self, ctx, *, search_term: str):
        """
        제품을 검색합니다.
        
        Args:
            ctx (commands.Context): 명령어 컨텍스트
            search_term (str): 검색어
        """
        try:
            # 제품 검색
            products = crud.search_products(search_term)
            
            if not products:
                await ctx.send(f"'{search_term}'에 대한 검색 결과가 없습니다.")
                return
            
            # 커스텀 포매터 정의
            def search_formatter(product):
                product_name = product.product_name if product.product_name else "미정의 제품명"
                company = product.company if product.company else "미정의 회사명"
                category = product.category if product.category else "미정의 카테고리"
                tags = product.tags if product.tags else "미정의 태그"
                
                return f"**제품명**: {product_name}\n" \
                       f"**회사명**: {company}\n" \
                       f"**카테고리**: {category}\n" \
                       f"**태그**: {tags}\n" \
                       f"**ID**: {product.id} | **플랫폼**: {product.platform} | **판매자**: {product.seller_id}"
            
            # 제품 리스트 뷰 생성
            view = ProductListView(
                products=products,
                user_id=ctx.author.id,
                title=f"'{search_term}' 검색 결과",
                per_page=5,
                custom_formatter=search_formatter
            )
            
            await ctx.send(embed=view.get_current_page_embed(), view=view)
            logger.info(f"'{search_term}' 검색 결과 표시됨 (총 {len(products)}개)")
            
        except Exception as e:
            await ctx.send(f"제품 검색 중 오류가 발생했습니다: {str(e)}")
            logger.error(f"제품 검색 중 오류 발생: {e}")
    
    @commands.command(name="product_info")
    async def product_info(self, ctx, product_id: int):
        """
        제품의 상세 정보를 표시합니다.
        
        Args:
            ctx (commands.Context): 명령어 컨텍스트
            product_id (int): 조회할 제품 ID
        """
        try:
            # 제품 정보 조회
            product = crud.get_product(product_id)
            
            if not product:
                await ctx.send(f"ID {product_id}에 해당하는 제품을 찾을 수 없습니다.")
                return
            
            # 임베드 생성
            embed = discord.Embed(
                title=f"제품 정보: {product.product_name if product.product_name else product.sale_name}", 
                color=discord.Color.green()
            )
            
            # 기본 정보 필드
            embed.add_field(name="ID", value=product.id, inline=True)
            embed.add_field(name="플랫폼", value=product.platform, inline=True)
            embed.add_field(name="판매자", value=product.seller_id, inline=True)
            embed.add_field(name="판매명", value=product.sale_name, inline=False)
            
            # 추가 정보 (있는 경우)
            if product.product_name:
                embed.add_field(name="관리제품명", value=product.product_name, inline=True)
            
            if product.company:
                embed.add_field(name="제조사", value=product.company, inline=True)
            
            if product.category:
                embed.add_field(name="카테고리", value=product.category, inline=True)
            
            if product.tags:
                embed.add_field(name="태그", value=product.tags, inline=False)
            
            # 생성 및 업데이트 시간
            embed.add_field(name="생성일", value=product.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            embed.add_field(name="수정일", value=product.updated_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            
            # 태그 상태에 따른 푸터
            if not product.category or not product.tags or not product.product_name or not product.company:
                embed.set_footer(text="⚠️ 이 제품은 아직 모든 정보가 입력되지 않았습니다.")
            
            await ctx.send(embed=embed)
            logger.info(f"제품 ID {product_id} 정보 표시됨")
            
        except Exception as e:
            await ctx.send(f"제품 정보 조회 중 오류가 발생했습니다: {str(e)}")
            logger.error(f"제품 정보 조회 중 오류 발생: {e}")

    @commands.command(name="category_stats")
    async def category_stats(self, ctx, seller_id: str = None):
        """
        카테고리별 제품 통계를 표시합니다.
        
        Args:
            ctx (commands.Context): 명령어 컨텍스트
            seller_id (str, optional): 판매자 ID로 필터링. 기본값은 None (모든 판매자).
        """
        try:
            # 카테고리별 통계 조회
            stats = crud.get_category_stats(seller_id)
            
            if not stats:
                await ctx.send("제품 통계 정보가 없습니다.")
                return
            
            # 임베드 생성
            embed = discord.Embed(
                title="카테고리별 제품 통계", 
                color=discord.Color.blue(),
                description=f"{'전체' if not seller_id else seller_id} 제품 통계입니다."
            )
            
            # 카테고리별 필드 추가
            total_count = 0
            for category, count in stats.items():
                category_name = category if category else "미분류"
                embed.add_field(name=category_name, value=f"{count}개", inline=True)
                total_count += count
            
            # 미완성 제품 수
            unfulfilled_count = len(crud.get_unfulfilled_products(seller_id))
            embed.add_field(name="미완성 제품", value=f"{unfulfilled_count}개", inline=True)
            
            # 총 제품 수
            embed.set_footer(text=f"총 제품 수: {total_count}개")
            
            await ctx.send(embed=embed)
            logger.info(f"카테고리별 통계 표시됨 (판매자: {seller_id if seller_id else '전체'})")
            
        except Exception as e:
            await ctx.send(f"제품 통계 조회 중 오류가 발생했습니다: {str(e)}")
            logger.error(f"카테고리별 통계 조회 중 오류 발생: {e}")
    
    @commands.command(name="recent_products")
    async def recent_products(self, ctx, limit: int = 10):
        """
        최근 추가된 제품 목록을 표시합니다.
        
        Args:
            ctx (commands.Context): 명령어 컨텍스트
            limit (int, optional): 표시할 제품 수. 기본값은 10.
        """
        try:
            # 제품 개수 제한
            if limit > 25:
                limit = 25
                await ctx.send("최대 25개까지만 표시 가능합니다.")
            
            # 최근 추가된 제품 조회
            products = crud.get_recent_products(limit)
            
            if not products:
                await ctx.send("제품 정보가 없습니다.")
                return
            
            # 커스텀 포매터 정의
            def recent_formatter(product):
                created_time = product.created_at.strftime("%Y-%m-%d %H:%M")
                status = "✅ 완료" if product.category and product.tags and product.product_name and product.company else "⚠️ 미완성"
                
                return f"**ID**: {product.id}\n" \
                       f"**판매명**: {product.sale_name}\n" \
                       f"**플랫폼**: {product.platform} | **판매자**: {product.seller_id}\n" \
                       f"**등록일**: {created_time}\n" \
                       f"**상태**: {status}"
            
            # 제품 리스트 뷰 생성
            view = ProductListView(
                products=products,
                user_id=ctx.author.id,
                title="최근 추가된 제품",
                per_page=5,
                custom_formatter=recent_formatter
            )
            
            await ctx.send(embed=view.get_current_page_embed(), view=view)
            logger.info(f"최근 추가된 제품 목록 표시됨 (총 {len(products)}개)")
            
        except Exception as e:
            await ctx.send(f"최근 제품 조회 중 오류가 발생했습니다: {str(e)}")
            logger.error(f"최근 제품 조회 중 오류 발생: {e}")

async def setup(bot):
    """
    봇에 ProductCommands 코그를 추가합니다.
    """
    await bot.add_cog(ProductCommands(bot))
