import discord
from discord.ui import Select, View, Button, Modal, TextInput
from app.utils.logger import mainLogger
from app.database.crud.product_crud import ProductCRUD
import datetime

from app.bot.views.product_modals import (
    ProductNameModal, CompanyModal, VolumeInputModal, NicotineInputModal,
    DeviceOptionsModal, AtomizerDetailModal, CoilOptionsModal, PodOhmModal,
    DisposableOptionsModal, DisposableDetailModal, AccessoryOptionsModal,
    OtherOptionsModal
)

# 로거 정의
logger = mainLogger()

# CRUD 객체 생성
crud = ProductCRUD()

class ProductTaggingView(View):
    """
    제품 태그 입력 메인 뷰
    """
    def __init__(self, product):
        super().__init__()
        self.product = product
        
        # 제품명 입력 버튼
        if not product.product_name:
            product_name_btn = Button(label="제품명 입력", style=discord.ButtonStyle.primary)
            product_name_btn.callback = self.product_name_callback
            self.add_item(product_name_btn)
        
        # 제조사 입력 버튼
        if not product.company:
            company_btn = Button(label="제조사 입력", style=discord.ButtonStyle.primary)
            company_btn.callback = self.company_callback
            self.add_item(company_btn)
        
        # 카테고리 선택 버튼
        category_select = CategorySelect(product)
        self.add_item(category_select)
    
    async def product_name_callback(self, interaction: discord.Interaction):
        """
        제품명 입력 콜백
        """
        modal = ProductNameModal(self.product)
        await interaction.response.send_modal(modal)
    
    async def company_callback(self, interaction: discord.Interaction):
        """
        제조사 입력 콜백
        """
        modal = CompanyModal(self.product)
        await interaction.response.send_modal(modal)

class CategorySelect(Select):
    """
    카테고리 선택 UI 컴포넌트입니다.
    """
    def __init__(self, product):
        self.product = product
        options = [
            discord.SelectOption(label="액상", value="액상", description="액상 카테고리"),
            discord.SelectOption(label="기기", value="기기", description="기기 카테고리"),
            discord.SelectOption(label="무화기", value="무화기", description="무화기 카테고리"),
            discord.SelectOption(label="코일", value="코일", description="코일 카테고리"),
            discord.SelectOption(label="팟", value="팟", description="팟 카테고리"),
            discord.SelectOption(label="일회용기기", value="일회용기기", description="일회용기기 카테고리"),
            discord.SelectOption(label="악세사리", value="악세사리", description="악세사리 카테고리"),
            discord.SelectOption(label="기타", value="기타", description="기타 카테고리")
        ]
        super().__init__(placeholder="카테고리 선택", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        """
        카테고리 선택 콜백 메서드
        """
        # 카테고리 저장
        self.product.category = self.values[0]
        
        # 선택된 카테고리에 따라 소분류 옵션 생성
        view = SubcategoryView(self.product)
        await interaction.response.edit_message(
            content=f"카테고리 '{self.values[0]}' 선택됨. 소분류를 선택하세요.", 
            view=view
        )
        logger.info(f"카테고리 '{self.values[0]}' 선택됨")

class SubcategoryView(View):
    """
    카테고리별 소분류 선택 뷰입니다.
    """
    def __init__(self, product):
        super().__init__()
        self.product = product
        
        # 카테고리에 따른 소분류 옵션 생성
        if product.category == "액상":
            options = [
                discord.SelectOption(label="입호흡액상", value="입호흡액상"),
                discord.SelectOption(label="폐호흡액상", value="폐호흡액상"),
                discord.SelectOption(label="기타액상", value="기타액상")
            ]
            select = Select(placeholder="액상 소분류 선택", options=options)
            select.callback = self.subcategory_callback
            self.add_item(select)
        
        elif product.category == "기기":
            options = [
                discord.SelectOption(label="입호흡기기", value="입호흡기기"),
                discord.SelectOption(label="폐호흡기기", value="폐호흡기기"),
                discord.SelectOption(label="AIO기기", value="AIO기기"),
                discord.SelectOption(label="기타기기", value="기타기기")
            ]
            select = Select(placeholder="기기 소분류 선택", options=options)
            select.callback = self.subcategory_callback
            self.add_item(select)
        
        elif product.category == "무화기":
            options = [
                discord.SelectOption(label="RDA", value="RDA"),
                discord.SelectOption(label="RTA", value="RTA"),
                discord.SelectOption(label="RDTA", value="RDTA"),
                discord.SelectOption(label="기성탱크", value="기성탱크"),
                discord.SelectOption(label="팟탱크", value="팟탱크"),
                discord.SelectOption(label="AIO팟", value="AIO팟"),
                discord.SelectOption(label="일회용무화기", value="일회용무화기"),
                discord.SelectOption(label="기타무화기", value="기타무화기")
            ]
            select = Select(placeholder="무화기 소분류 선택", options=options)
            select.callback = self.subcategory_callback
            self.add_item(select)
        
        elif product.category == "코일":
            # 코일은 소분류 없이 바로 옵션 입력으로 이동
            button = Button(label="옵션 입력", style=discord.ButtonStyle.primary)
            button.callback = self.coil_options_callback
            self.add_item(button)
        
        elif product.category == "팟":
            options = [
                discord.SelectOption(label="일체형팟", value="일체형팟"),
                discord.SelectOption(label="공팟", value="공팟"),
                discord.SelectOption(label="기타팟", value="기타팟")
            ]
            select = Select(placeholder="팟 소분류 선택", options=options)
            select.callback = self.subcategory_callback
            self.add_item(select)
        
        elif product.category == "일회용기기":
            options = [
                discord.SelectOption(label="일체형", value="일체형"),
                discord.SelectOption(label="교체형", value="교체형"),
                discord.SelectOption(label="무니코틴", value="무니코틴"),
                discord.SelectOption(label="기타일회용기기", value="기타일회용기기")
            ]
            select = Select(placeholder="일회용기기 소분류 선택", options=options)
            select.callback = self.subcategory_callback
            self.add_item(select)
        
        elif product.category == "악세사리":
            options = [
                discord.SelectOption(label="경통", value="경통"),
                discord.SelectOption(label="드립팁", value="드립팁"),
                discord.SelectOption(label="캡", value="캡"),
                discord.SelectOption(label="케이스", value="케이스"),
                discord.SelectOption(label="도어", value="도어"),
                discord.SelectOption(label="배터리", value="배터리"),
                discord.SelectOption(label="충전기", value="충전기"),
                discord.SelectOption(label="리빌드용품", value="리빌드용품"),
                discord.SelectOption(label="기타악세사리", value="기타악세사리")
            ]
            select = Select(placeholder="악세사리 소분류 선택", options=options)
            select.callback = self.subcategory_callback
            self.add_item(select)
        
        elif product.category == "기타":
            # 기타 카테고리는 바로 직접 입력으로 이동
            self.product.tags = "|기타"
            button = Button(label="세부 옵션 입력", style=discord.ButtonStyle.primary)
            button.callback = self.other_options_callback
            self.add_item(button)
        
        # 뒤로 가기 버튼
        back_button = Button(label="뒤로 가기", style=discord.ButtonStyle.secondary)
        back_button.callback = self.back_callback
        self.add_item(back_button)
    
    async def subcategory_callback(self, interaction: discord.Interaction):
        """
        소분류 선택 콜백
        """
        subcategory = interaction.data["values"][0]
        self.product.tags = f"|{subcategory}"
        logger.info(f"소분류 '{subcategory}' 선택됨")
        
        # 카테고리별 다음 단계 처리
        if self.product.category == "액상":
            view = LiquidOptionsView(self.product)
            await interaction.response.edit_message(content=f"소분류 '{subcategory}' 선택됨. 옵션을 선택하세요.", view=view)
        
        elif self.product.category == "기기":
            # 기기는 추가 옵션 입력
            modal = DeviceOptionsModal(self.product)
            await interaction.response.send_modal(modal)
        
        elif self.product.category == "무화기":
            view = AtomizerOptionsView(self.product)
            await interaction.response.edit_message(content=f"소분류 '{subcategory}' 선택됨. 옵션을 선택하세요.", view=view)
        
        elif self.product.category == "팟":
            # 팟 옴 옵션 입력
            modal = PodOhmModal(self.product)
            await interaction.response.send_modal(modal)
        
        elif self.product.category == "일회용기기":
            if subcategory == "교체형":
                view = DisposableOptionsView(self.product)
                await interaction.response.edit_message(content=f"소분류 '{subcategory}' 선택됨. 세부 옵션을 선택하세요.", view=view)
            else:
                # 직접 입력 모달
                modal = DisposableOptionsModal(self.product)
                await interaction.response.send_modal(modal)
        
        elif self.product.category == "악세사리":
            # 악세사리 세부 옵션 직접 입력
            modal = AccessoryOptionsModal(self.product)
            await interaction.response.send_modal(modal)
        
        else:
            # 기본 저장 뷰로 이동
            view = FinalSaveView(self.product)
            await interaction.response.edit_message(content=f"소분류 '{subcategory}' 선택됨. 정보를 확인하고 저장하세요.", view=view)
    
    async def coil_options_callback(self, interaction: discord.Interaction):
        """
        코일 옵션 입력 콜백
        """
        self.product.tags = "|코일"
        modal = CoilOptionsModal(self.product)
        await interaction.response.send_modal(modal)
    
    async def other_options_callback(self, interaction: discord.Interaction):
        """
        기타 카테고리 옵션 입력 콜백
        """
        modal = OtherOptionsModal(self.product)
        await interaction.response.send_modal(modal)
    
    async def back_callback(self, interaction: discord.Interaction):
        """
        뒤로 가기 콜백
        """
        view = ProductTaggingView(self.product)
        await interaction.response.edit_message(content="카테고리를 선택하세요.", view=view)

class LiquidOptionsView(View):
    """
    액상 옵션 선택 뷰
    """
    def __init__(self, product):
        super().__init__()
        self.product = product
        
        # 용량 선택
        volume_options = [
            discord.SelectOption(label="60ml", value="60ml"),
            discord.SelectOption(label="30ml", value="30ml"),
            discord.SelectOption(label="100ml", value="100ml"),
            discord.SelectOption(label="직접입력", value="직접입력")
        ]
        volume_select = Select(placeholder="용량 선택", options=volume_options)
        volume_select.callback = self.volume_callback
        self.add_item(volume_select)
        
        # 뒤로 가기 버튼
        back_button = Button(label="뒤로 가기", style=discord.ButtonStyle.secondary)
        back_button.callback = self.back_callback
        self.add_item(back_button)
    
    async def volume_callback(self, interaction: discord.Interaction):
        """
        용량 선택 콜백
        """
        volume = interaction.data["values"][0]
        
        if volume == "직접입력":
            # 직접 입력 모달 표시
            modal = VolumeInputModal(self.product)
            await interaction.response.send_modal(modal)
        else:
            # 태그에 용량 추가
            self.product.tags += f"|{volume}"
            logger.info(f"용량 '{volume}' 선택됨")
            
            # 다음 단계 (니코틴 선택) 표시
            nicotine_view = NicotineOptionsView(self.product)
            await interaction.response.edit_message(content=f"용량 '{volume}' 선택됨. 니코틴 함량을 선택하세요.", view=nicotine_view)
    
    async def back_callback(self, interaction: discord.Interaction):
        """
        뒤로 가기 콜백
        """
        view = SubcategoryView(self.product)
        await interaction.response.edit_message(content="소분류를 선택하세요.", view=view)

class NicotineOptionsView(View):
    """
    니코틴 옵션 선택 뷰
    """
    def __init__(self, product):
        super().__init__()
        self.product = product
        
        # 니코틴 선택
        nicotine_options = [
            discord.SelectOption(label="3mg", value="3mg"),
            discord.SelectOption(label="6mg", value="6mg"),
            discord.SelectOption(label="9mg", value="9mg"),
            discord.SelectOption(label="무니코틴", value="무니코틴"),
            discord.SelectOption(label="직접입력", value="직접입력")
        ]
        nicotine_select = Select(placeholder="니코틴 함량 선택", options=nicotine_options)
        nicotine_select.callback = self.nicotine_callback
        self.add_item(nicotine_select)
        
        # 뒤로 가기 버튼
        back_button = Button(label="뒤로 가기", style=discord.ButtonStyle.secondary)
        back_button.callback = self.back_callback
        self.add_item(back_button)
    
    async def nicotine_callback(self, interaction: discord.Interaction):
        """
        니코틴 선택 콜백
        """
        nicotine = interaction.data["values"][0]
        
        if nicotine == "직접입력":
            # 직접 입력 모달 표시
            modal = NicotineInputModal(self.product)
            await interaction.response.send_modal(modal)
        else:
            # 태그에 니코틴 함량 추가
            self.product.tags += f"|{nicotine}"
            logger.info(f"니코틴 함량 '{nicotine}' 선택됨")
            
            # 최종 정보 확인 및 저장 뷰
            view = FinalSaveView(self.product)
            await interaction.response.edit_message(content=f"니코틴 함량 '{nicotine}' 선택됨. 정보를 확인하고 저장하세요.", view=view)
    
    async def back_callback(self, interaction: discord.Interaction):
        """
        뒤로 가기 콜백
        """
        view = LiquidOptionsView(self.product)
        await interaction.response.edit_message(content="용량을 선택하세요.", view=view)

class AtomizerOptionsView(View):
    """
    무화기 옵션 선택 뷰
    """
    def __init__(self, product):
        super().__init__()
        self.product = product
        
        # 무화기 호흡법 선택
        options = [
            discord.SelectOption(label="입호흡무화기", value="입호흡무화기"),
            discord.SelectOption(label="폐호흡무화기", value="폐호흡무화기")
        ]
        select = Select(placeholder="호흡법 선택", options=options)
        select.callback = self.option_callback
        self.add_item(select)
        
        # 뒤로 가기 버튼
        back_button = Button(label="뒤로 가기", style=discord.ButtonStyle.secondary)
        back_button.callback = self.back_callback
        self.add_item(back_button)
    
    async def option_callback(self, interaction: discord.Interaction):
        """
        무화기 옵션 선택 콜백
        """
        option = interaction.data["values"][0]
        self.product.tags += f"|{option}"
        logger.info(f"무화기 옵션 '{option}' 선택됨")
        
        # 세부 옵션 입력 모달
        modal = AtomizerDetailModal(self.product)
        await interaction.response.send_modal(modal)
    
    async def back_callback(self, interaction: discord.Interaction):
        """
        뒤로 가기 콜백
        """
        view = SubcategoryView(self.product)
        await interaction.response.edit_message(content="소분류를 선택하세요.", view=view)

class DisposableOptionsView(View):
    """
    일회용기기(교체형) 옵션 선택 뷰
    """
    def __init__(self, product):
        super().__init__()
        self.product = product
        
        # 일회용기기 교체형 세부 옵션
        options = [
            discord.SelectOption(label="배터리", value="배터리"),
            discord.SelectOption(label="카트리지", value="카트리지")
        ]
        select = Select(placeholder="교체형 세부 옵션 선택", options=options)
        select.callback = self.option_callback
        self.add_item(select)
        
        # 뒤로 가기 버튼
        back_button = Button(label="뒤로 가기", style=discord.ButtonStyle.secondary)
        back_button.callback = self.back_callback
        self.add_item(back_button)
    
    async def option_callback(self, interaction: discord.Interaction):
        """
        교체형 옵션 선택 콜백
        """
        option = interaction.data["values"][0]
        self.product.tags += f"|{option}"
        logger.info(f"교체형 세부 옵션 '{option}' 선택됨")
        
        # 추가 세부 옵션 입력 모달
        modal = DisposableDetailModal(self.product)
        await interaction.response.send_modal(modal)
    
    async def back_callback(self, interaction: discord.Interaction):
        """
        뒤로 가기 콜백
        """
        view = SubcategoryView(self.product)
        await interaction.response.edit_message(content="소분류를 선택하세요.", view=view)

class FinalSaveView(View):
    """
    최종 정보 확인 및 저장 뷰
    """
    def __init__(self, product):
        super().__init__()
        self.product = product
        
        # 제품명 입력 버튼
        if not product.product_name:
            product_name_btn = Button(label="제품명 입력", style=discord.ButtonStyle.primary)
            product_name_btn.callback = self.product_name_callback
            self.add_item(product_name_btn)
        
        # 제조사 입력 버튼
        if not product.company:
            company_btn = Button(label="제조사 입력", style=discord.ButtonStyle.primary)
            company_btn.callback = self.company_callback
            self.add_item(company_btn)
        
        # 저장 버튼
        save_btn = Button(label="저장", style=discord.ButtonStyle.success)
        save_btn.callback = self.save_callback
        self.add_item(save_btn)
        
        # 취소 버튼
        cancel_btn = Button(label="취소", style=discord.ButtonStyle.danger)
        cancel_btn.callback = self.cancel_callback
        self.add_item(cancel_btn)
    
    async def product_name_callback(self, interaction: discord.Interaction):
        """
        제품명 입력 콜백
        """
        modal = ProductNameModal(self.product)
        await interaction.response.send_modal(modal)
    
    async def company_callback(self, interaction: discord.Interaction):
        """
        제조사 입력 콜백
        """
        modal = CompanyModal(self.product)
        await interaction.response.send_modal(modal)
    
    async def save_callback(self, interaction: discord.Interaction):
        """
        저장 콜백
        """
        if not self.product.product_name:
            await interaction.response.send_message("제품명을 먼저 입력해주세요.", ephemeral=True)
            return
        
        if not self.product.company:
            await interaction.response.send_message("제조사를 먼저 입력해주세요.", ephemeral=True)
            return
        
        # 제품 정보 업데이트
        result = crud.update_product_tags(
            product_id=self.product.id,
            category=self.product.category,
            tags=self.product.tags,
            company=self.product.company,
            product_name=self.product.product_name
        )
        
        if result:
            await interaction.response.edit_message(
                content=f"✅ 제품 정보가 업데이트되었습니다.\n제품명: {self.product.product_name}\n카테고리: {self.product.category}\n태그: {self.product.tags}\n제조사: {self.product.company}",
                view=None
            )
            logger.info(f"제품 ID {self.product.id} 정보 업데이트됨")
        else:
            await interaction.response.edit_message(
                content="❌ 제품 정보 업데이트 중 오류가 발생했습니다.",
                view=None
            )
            logger.error(f"제품 ID {self.product.id} 정보 업데이트 실패")
    
    async def cancel_callback(self, interaction: discord.Interaction):
        """
        취소 콜백
        """
        await interaction.response.edit_message(content="작업이 취소되었습니다.", view=None)
