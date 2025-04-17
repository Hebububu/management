import discord
from discord.ui import View, Button
from typing import List, Callable, Optional, Any

class ProductListView(View):
    """
    제품 리스트를 표시하기 위한 페이지네이션 뷰
    다양한 제품 리스트 명령어(search_products, unfulfilled_products, recent_products 등)에서 
    공통으로 사용할 수 있는 UI 컴포넌트입니다.
    """
    
    def __init__(self, 
                 products: List[Any], 
                 user_id: int, 
                 title: str = "제품 목록", 
                 per_page: int = 10,
                 timeout: float = 180.0,
                 custom_formatter: Optional[Callable] = None):
        """
        제품 리스트 뷰 초기화
        Args:
            products: 표시할 제품 목록
            user_id: 뷰를 요청한 사용자의 ID
            title: 임베드 제목
            per_page: 페이지당 표시할 제품 수
            timeout: 뷰 타임아웃(초)
            custom_formatter: 커스텀 제품 정보 포맷팅 함수
        """
        super().__init__(timeout=timeout)
        self.products = products
        self.user_id = user_id
        self.title = title
        self.per_page = per_page
        self.current_page = 0
        self.total_pages = max((len(products) - 1) // per_page + 1, 1)
        self.custom_formatter = custom_formatter
        
        # 페이지가 1개 이상인 경우에만 버튼 추가
        if self.total_pages > 1:
            self.add_nav_buttons()
        
    def add_nav_buttons(self):
        """페이지네이션 버튼 추가"""
        # 첫 페이지 버튼
        first_page_button = Button(style=discord.ButtonStyle.gray, emoji="⏮️", custom_id="first_page")
        first_page_button.callback = self.first_page_callback
        self.add_item(first_page_button)
        
        # 이전 페이지 버튼
        prev_page_button = Button(style=discord.ButtonStyle.blurple, emoji="◀️", custom_id="prev_page")
        prev_page_button.callback = self.prev_page_callback
        self.add_item(prev_page_button)
        
        # 페이지 정보 버튼 (비활성화 상태로 표시)
        page_info_button = Button(
            style=discord.ButtonStyle.gray, 
            label=f"페이지 {self.current_page + 1}/{self.total_pages}", 
            custom_id="page_info", 
            disabled=True
        )
        self.add_item(page_info_button)
        
        # 다음 페이지 버튼
        next_page_button = Button(style=discord.ButtonStyle.blurple, emoji="▶️", custom_id="next_page")
        next_page_button.callback = self.next_page_callback
        self.add_item(next_page_button)
        
        # 마지막 페이지 버튼
        last_page_button = Button(style=discord.ButtonStyle.gray, emoji="⏭️", custom_id="last_page")
        last_page_button.callback = self.last_page_callback
        self.add_item(last_page_button)
    
    def format_product(self, product):
        """
        제품 정보를 포맷팅합니다.
        커스텀 포맷터가 제공된 경우 해당 함수를 사용하고,
        그렇지 않으면 기본 포맷을 적용합니다.
        """
        if self.custom_formatter:
            return self.custom_formatter(product)
        
        # 기본 포맷: 제품명, 회사명, 판매가 등 표시
        platform = product.platform
        seller_id = product.seller_id
        product_name = product.product_name or "미정의 제품명"
        company = product.company or "미정의 회사명"
        category = product.category or "미정의 카테고리"
        
        return f"**{product_name}**\n" \
               f"회사명: {company}\n" \
               f"카테고리: {category}\n" \
               f"플랫폼: {platform} ({seller_id})\n" \
               f"제품 ID: {product.product_id}\n"
    
    def get_current_page_embed(self) -> discord.Embed:
        """현재 페이지의 제품 목록을 포함한 임베드를 생성합니다."""
        start_idx = self.current_page * self.per_page
        end_idx = min(start_idx + self.per_page, len(self.products))
        
        embed = discord.Embed(
            title=f"{self.title} ({len(self.products)}개)",
            description=f"총 {len(self.products)}개의 제품 중 {start_idx + 1}-{end_idx}번째 제품",
            color=discord.Color.blue()
        )
        
        current_page_products = self.products[start_idx:end_idx]
        
        if not current_page_products:
            embed.add_field(name="결과 없음", value="표시할 제품이 없습니다.", inline=False)
        else:
            for i, product in enumerate(current_page_products, start_idx + 1):
                embed.add_field(
                    name=f"{i}. {product.sale_name[:30] + '...' if len(product.sale_name) > 30 else product.sale_name}",
                    value=self.format_product(product),
                    inline=False
                )
        
        embed.set_footer(text=f"페이지 {self.current_page + 1}/{self.total_pages}")
        return embed
    
    async def update_view(self, interaction: discord.Interaction):
        """뷰를 업데이트합니다."""
        # 페이지 정보 버튼 업데이트
        for item in self.children:
            if isinstance(item, Button) and item.custom_id == "page_info":
                item.label = f"페이지 {self.current_page + 1}/{self.total_pages}"
        
        await interaction.response.edit_message(embed=self.get_current_page_embed(), view=self)
    
    async def first_page_callback(self, interaction: discord.Interaction):
        """첫 페이지로 이동"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("이 버튼은 명령어를 실행한 사용자만 사용할 수 있습니다.", ephemeral=True)
            return
        
        self.current_page = 0
        await self.update_view(interaction)
    
    async def prev_page_callback(self, interaction: discord.Interaction):
        """이전 페이지로 이동"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("이 버튼은 명령어를 실행한 사용자만 사용할 수 있습니다.", ephemeral=True)
            return
        
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_view(interaction)
        else:
            await interaction.response.send_message("이미 첫 페이지입니다.", ephemeral=True)
    
    async def next_page_callback(self, interaction: discord.Interaction):
        """다음 페이지로 이동"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("이 버튼은 명령어를 실행한 사용자만 사용할 수 있습니다.", ephemeral=True)
            return
        
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            await self.update_view(interaction)
        else:
            await interaction.response.send_message("이미 마지막 페이지입니다.", ephemeral=True)
    
    async def last_page_callback(self, interaction: discord.Interaction):
        """마지막 페이지로 이동"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("이 버튼은 명령어를 실행한 사용자만 사용할 수 있습니다.", ephemeral=True)
            return
        
        self.current_page = self.total_pages - 1
        await self.update_view(interaction)
    
    async def on_timeout(self):
        """타임아웃 시 모든 버튼 비활성화"""
        for item in self.children:
            item.disabled = True
