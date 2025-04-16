import discord
from discord.ui import Modal, TextInput
from app.utils.logger import mainLogger

# 로거 정의
logger = mainLogger()

class ProductNameModal(Modal):
    """
    제품명 입력 모달
    """
    def __init__(self, product):
        super().__init__(title="제품명 입력")
        self.product = product
        
        self.product_name_input = TextInput(
            label="제품명을 입력하세요",
            placeholder="예: OB MTL 액상",
            required=True,
            max_length=100
        )
        self.add_item(self.product_name_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        모달 제출 시 호출
        """
        self.product.product_name = self.product_name_input.value
        logger.info(f"제품명 '{self.product.product_name}' 입력됨")
        
        # 임포트 문제 방지를 위한 지연 임포트
        from app.bot.views.product_views import FinalSaveView
        
        # 정보 확인 메시지 업데이트
        view = FinalSaveView(self.product)
        await interaction.response.edit_message(
            content=f"제품명 '{self.product.product_name}' 입력됨. 정보를 확인하고 저장하세요.",
            view=view
        )

class CompanyModal(Modal):
    """
    제조사 입력 모달
    """
    def __init__(self, product):
        super().__init__(title="제조사 입력")
        self.product = product
        
        self.company_input = TextInput(
            label="제조사를 입력하세요",
            placeholder="예: OB유통",
            required=True,
            max_length=100
        )
        self.add_item(self.company_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        모달 제출 시 호출
        """
        self.product.company = self.company_input.value
        logger.info(f"제조사 '{self.product.company}' 입력됨")
        
        # 임포트 문제 방지를 위한 지연 임포트
        from app.bot.views.product_views import FinalSaveView
        
        # 정보 확인 메시지 업데이트
        view = FinalSaveView(self.product)
        await interaction.response.edit_message(
            content=f"제조사 '{self.product.company}' 입력됨. 정보를 확인하고 저장하세요.",
            view=view
        )

class VolumeInputModal(Modal):
    """
    용량 직접 입력 모달
    """
    def __init__(self, product):
        super().__init__(title="용량 직접 입력")
        self.product = product
        
        self.volume_input = TextInput(
            label="용량을 입력하세요",
            placeholder="예: 50ml",
            required=True,
            max_length=20
        )
        self.add_item(self.volume_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        모달 제출 시 호출
        """
        volume = self.volume_input.value
        self.product.tags += f"|{volume}"
        logger.info(f"용량 '{volume}' 입력됨")
        
        # 임포트 문제 방지를 위한 지연 임포트
        from app.bot.views.product_views import NicotineOptionsView
        
        # 다음 단계 (니코틴 선택) 뷰
        view = NicotineOptionsView(self.product)
        await interaction.response.edit_message(
            content=f"용량 '{volume}' 입력됨. 니코틴 함량을 선택하세요.",
            view=view
        )

class NicotineInputModal(Modal):
    """
    니코틴 함량 직접 입력 모달
    """
    def __init__(self, product):
        super().__init__(title="니코틴 함량 직접 입력")
        self.product = product
        
        self.nicotine_input = TextInput(
            label="니코틴 함량을 입력하세요",
            placeholder="예: 1.5mg",
            required=True,
            max_length=20
        )
        self.add_item(self.nicotine_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        모달 제출 시 호출
        """
        nicotine = self.nicotine_input.value
        self.product.tags += f"|{nicotine}"
        logger.info(f"니코틴 함량 '{nicotine}' 입력됨")
        
        # 임포트 문제 방지를 위한 지연 임포트
        from app.bot.views.product_views import FinalSaveView
        
        # 최종 저장 뷰
        view = FinalSaveView(self.product)
        await interaction.response.edit_message(
            content=f"니코틴 함량 '{nicotine}' 입력됨. 정보를 확인하고 저장하세요.",
            view=view
        )

class DeviceOptionsModal(Modal):
    """
    기기 옵션 입력 모달
    """
    def __init__(self, product):
        super().__init__(title="기기 옵션 입력")
        self.product = product
        
        self.options_input = TextInput(
            label="옵션을 입력하세요 (선택사항)",
            placeholder="예: 200W, 온도조절 등",
            required=False,
            max_length=100
        )
        self.add_item(self.options_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        모달 제출 시 호출
        """
        options = self.options_input.value
        if options.strip():
            self.product.tags += f"|{options}"
            logger.info(f"기기 옵션 '{options}' 입력됨")
        
        # 임포트 문제 방지를 위한 지연 임포트
        from app.bot.views.product_views import FinalSaveView
        
        # 최종 저장 뷰
        view = FinalSaveView(self.product)
        await interaction.response.edit_message(
            content="기기 옵션이 입력되었습니다. 정보를 확인하고 저장하세요.",
            view=view
        )

class AtomizerDetailModal(Modal):
    """
    무화기 세부 옵션 입력 모달
    """
    def __init__(self, product):
        super().__init__(title="무화기 세부 옵션 입력")
        self.product = product
        
        self.detail_input = TextInput(
            label="세부 옵션을 입력하세요 (선택사항)",
            placeholder="예: 직경 22mm, 싱글코일 등",
            required=False,
            max_length=100
        )
        self.add_item(self.detail_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        모달 제출 시 호출
        """
        detail = self.detail_input.value
        if detail.strip():
            self.product.tags += f"|{detail}"
            logger.info(f"무화기 세부 옵션 '{detail}' 입력됨")
        
        # 임포트 문제 방지를 위한 지연 임포트
        from app.bot.views.product_views import FinalSaveView
        
        # 최종 저장 뷰
        view = FinalSaveView(self.product)
        await interaction.response.edit_message(
            content="무화기 세부 옵션이 입력되었습니다. 정보를 확인하고 저장하세요.",
            view=view
        )

class CoilOptionsModal(Modal):
    """
    코일 옵션 입력 모달
    """
    def __init__(self, product):
        super().__init__(title="코일 옵션 입력")
        self.product = product
        
        self.options_input = TextInput(
            label="코일 옵션을 입력하세요 (선택사항)",
            placeholder="예: 0.5옴, 클랩튼 등",
            required=False,
            max_length=100
        )
        self.add_item(self.options_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        모달 제출 시 호출
        """
        options = self.options_input.value
        if options.strip():
            self.product.tags += f"|{options}"
            logger.info(f"코일 옵션 '{options}' 입력됨")
        
        # 임포트 문제 방지를 위한 지연 임포트
        from app.bot.views.product_views import FinalSaveView
        
        # 최종 저장 뷰
        view = FinalSaveView(self.product)
        await interaction.response.edit_message(
            content="코일 옵션이 입력되었습니다. 정보를 확인하고 저장하세요.",
            view=view
        )

class PodOhmModal(Modal):
    """
    팟 옴 옵션 입력 모달
    """
    def __init__(self, product):
        super().__init__(title="팟 옴 옵션 입력")
        self.product = product
        
        self.ohm_input = TextInput(
            label="옴 옵션을 입력하세요 (선택사항)",
            placeholder="예: 0.8옴, 1.2옴 등",
            required=False,
            max_length=100
        )
        self.add_item(self.ohm_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        모달 제출 시 호출
        """
        ohm = self.ohm_input.value
        if ohm.strip():
            self.product.tags += f"|{ohm}"
            logger.info(f"팟 옴 옵션 '{ohm}' 입력됨")
        
        # 임포트 문제 방지를 위한 지연 임포트
        from app.bot.views.product_views import FinalSaveView
        
        # 최종 저장 뷰
        view = FinalSaveView(self.product)
        await interaction.response.edit_message(
            content="팟 옴 옵션이 입력되었습니다. 정보를 확인하고 저장하세요.",
            view=view
        )

class DisposableOptionsModal(Modal):
    """
    일회용기기 옵션 입력 모달
    """
    def __init__(self, product):
        super().__init__(title="일회용기기 옵션 입력")
        self.product = product
        
        self.options_input = TextInput(
            label="세부 옵션을 입력하세요 (선택사항)",
            placeholder="예: 2000회, 1500mAh 등",
            required=False,
            max_length=100
        )
        self.add_item(self.options_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        모달 제출 시 호출
        """
        options = self.options_input.value
        if options.strip():
            self.product.tags += f"|{options}"
            logger.info(f"일회용기기 옵션 '{options}' 입력됨")
        
        # 임포트 문제 방지를 위한 지연 임포트
        from app.bot.views.product_views import FinalSaveView
        
        # 최종 저장 뷰
        view = FinalSaveView(self.product)
        await interaction.response.edit_message(
            content="일회용기기 옵션이 입력되었습니다. 정보를 확인하고 저장하세요.",
            view=view
        )

class DisposableDetailModal(Modal):
    """
    일회용기기 교체형 세부 옵션 입력 모달
    """
    def __init__(self, product):
        super().__init__(title="교체형 세부 옵션 입력")
        self.product = product
        
        self.detail_input = TextInput(
            label="세부 옵션을 입력하세요 (선택사항)",
            placeholder="예: 용량, 배터리 용량 등",
            required=False,
            max_length=100
        )
        self.add_item(self.detail_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        모달 제출 시 호출
        """
        detail = self.detail_input.value
        if detail.strip():
            self.product.tags += f"|{detail}"
            logger.info(f"교체형 세부 옵션 '{detail}' 입력됨")
        
        # 임포트 문제 방지를 위한 지연 임포트
        from app.bot.views.product_views import FinalSaveView
        
        # 최종 저장 뷰
        view = FinalSaveView(self.product)
        await interaction.response.edit_message(
            content="교체형 세부 옵션이 입력되었습니다. 정보를 확인하고 저장하세요.",
            view=view
        )

class AccessoryOptionsModal(Modal):
    """
    악세사리 세부 옵션 입력 모달
    """
    def __init__(self, product):
        super().__init__(title="악세사리 세부 옵션 입력")
        self.product = product
        
        self.detail_input = TextInput(
            label="세부 옵션을 입력하세요 (선택사항)",
            placeholder="예: 컬러, 사이즈 등",
            required=False,
            max_length=100
        )
        self.add_item(self.detail_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        모달 제출 시 호출
        """
        detail = self.detail_input.value
        if detail.strip():
            self.product.tags += f"|{detail}"
            logger.info(f"악세사리 세부 옵션 '{detail}' 입력됨")
        
        # 임포트 문제 방지를 위한 지연 임포트
        from app.bot.views.product_views import FinalSaveView
        
        # 최종 저장 뷰
        view = FinalSaveView(self.product)
        await interaction.response.edit_message(
            content="악세사리 세부 옵션이 입력되었습니다. 정보를 확인하고 저장하세요.",
            view=view
        )

class OtherOptionsModal(Modal):
    """
    기타 카테고리 옵션 입력 모달
    """
    def __init__(self, product):
        super().__init__(title="기타 카테고리 옵션 입력")
        self.product = product
        
        self.detail_input = TextInput(
            label="세부 옵션을 입력하세요 (선택사항)",
            placeholder="예: 크기, 용도 등",
            required=False,
            max_length=100
        )
        self.add_item(self.detail_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        모달 제출 시 호출
        """
        detail = self.detail_input.value
        if detail.strip():
            self.product.tags += f"|{detail}"
            logger.info(f"기타 카테고리 세부 옵션 '{detail}' 입력됨")
        
        # 임포트 문제 방지를 위한 지연 임포트
        from app.bot.views.product_views import FinalSaveView
        
        # 최종 저장 뷰
        view = FinalSaveView(self.product)
        await interaction.response.edit_message(
            content="기타 카테고리 세부 옵션이 입력되었습니다. 정보를 확인하고 저장하세요.",
            view=view
        )
