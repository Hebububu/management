import pytest
import discord
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

from app.bot.cogs.productcommands import ProductCommands
from app.database.models import Product
from app.database.crud.product_crud import ProductCRUD
from app.bot.views.product_views import ProductTaggingView, CategorySelect, SubcategoryView

# 테스트 데이터
mock_product = Product(
    id=1,
    platform="cafe24",
    seller_id="SIASIUCP",
    product_id=12345,
    sale_name="테스트 상품",
    data={},
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)

mock_unfulfilled_products = [
    Product(
        id=i,
        platform="cafe24",
        seller_id="SIASIUCP",
        product_id=10000 + i,
        sale_name=f"테스트 상품 {i}",
        data={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    ) for i in range(1, 13)  # 12개의 상품 생성
]

# 픽스처: 모의 봇 객체
@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.add_cog = AsyncMock()
    bot.tree = MagicMock()
    bot.tree.sync = AsyncMock()
    return bot

# 픽스처: 모의 컨텍스트 객체
@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    ctx.send = AsyncMock()
    return ctx

# 픽스처: 모의 ProductCRUD 객체
@pytest.fixture
def mock_product_crud():
    with patch('app.database.crud.product_crud.ProductCRUD') as mock:
        mock_instance = mock.return_value
        mock_instance.get_product = MagicMock(return_value=mock_product)
        mock_instance.get_unfulfilled_products = MagicMock(return_value=mock_unfulfilled_products)
        mock_instance.update_product_tags = MagicMock(return_value=True)
        yield mock_instance

# 픽스처: 모의 상호작용 객체
@pytest.fixture
def mock_interaction():
    interaction = AsyncMock()
    interaction.response = AsyncMock()
    interaction.response.edit_message = AsyncMock()
    interaction.response.send_modal = AsyncMock()
    interaction.data = {"values": ["액상"]}
    return interaction

# ProductCommands 테스트
@pytest.mark.asyncio
async def test_add_tags_command(mock_ctx, mock_product_crud):
    # ProductCRUD 패치
    with patch('app.bot.cogs.productcommands.ProductCRUD', return_value=mock_product_crud):
        # ProductTaggingView 패치
        with patch('app.bot.cogs.productcommands.ProductTaggingView') as mock_view:
            # 테스트할 코그 객체 생성
            cog = ProductCommands(MagicMock())
            
            # add_tags 명령어 호출
            await cog.add_tags(mock_ctx, 1)
            
            # 검증
            mock_product_crud.get_product.assert_called_once_with(1)
            mock_ctx.send.assert_called_once()
            mock_view.assert_called_once()
            
            # send 메서드에 전달된 embed와 view 매개변수 확인
            call_args = mock_ctx.send.call_args
            assert 'embed' in call_args.kwargs
            assert 'view' in call_args.kwargs
            
            # embed 내용 확인
            embed = call_args.kwargs['embed']
            assert isinstance(embed, discord.Embed)
            assert "제품 태그 추가" in embed.title
            
            # 필드 확인
            assert any(field.name == "제품명" and field.value == "테스트 상품" for field in embed.fields)

@pytest.mark.asyncio
async def test_unfulfilled_products_command(mock_ctx, mock_product_crud):
    # ProductCRUD 패치
    with patch('app.bot.cogs.productcommands.ProductCRUD', return_value=mock_product_crud):
        # 테스트할 코그 객체 생성
        cog = ProductCommands(MagicMock())
        
        # unfulfilled_products 명령어 호출
        await cog.unfulfilled_products(mock_ctx)
        
        # 검증
        mock_product_crud.get_unfulfilled_products.assert_called_once()
        mock_ctx.send.assert_called_once()
        
        # send 메서드에 전달된 embed 매개변수 확인
        call_args = mock_ctx.send.call_args
        assert 'embed' in call_args.kwargs
        
        # embed 내용 확인
        embed = call_args.kwargs['embed']
        assert isinstance(embed, discord.Embed)
        assert "태그 미입력 제품 목록" in embed.title
        
        # 최대 10개의 제품만 표시되는지 확인
        assert len(embed.fields) <= 10
        
        # 추가 제품이 있다는 footer 확인
        assert "외 2개 제품이 더 있습니다" in embed.footer.text

@pytest.mark.asyncio
async def test_unfulfilled_products_command_with_seller_id(mock_ctx, mock_product_crud):
    # ProductCRUD 패치
    with patch('app.bot.cogs.productcommands.ProductCRUD', return_value=mock_product_crud):
        # 테스트할 코그 객체 생성
        cog = ProductCommands(MagicMock())
        
        # unfulfilled_products 명령어 호출 (판매자 ID 지정)
        await cog.unfulfilled_products(mock_ctx, "SIASIUCP")
        
        # 검증
        mock_product_crud.get_unfulfilled_products.assert_called_once_with("SIASIUCP")

@pytest.mark.asyncio
async def test_unfulfilled_products_command_no_products(mock_ctx, mock_product_crud):
    # 빈 목록 반환하도록 설정
    mock_product_crud.get_unfulfilled_products.return_value = []
    
    # ProductCRUD 패치
    with patch('app.bot.cogs.productcommands.ProductCRUD', return_value=mock_product_crud):
        # 테스트할 코그 객체 생성
        cog = ProductCommands(MagicMock())
        
        # unfulfilled_products 명령어 호출
        await cog.unfulfilled_products(mock_ctx)
        
        # 검증
        mock_product_crud.get_unfulfilled_products.assert_called_once()
        mock_ctx.send.assert_called_once_with("미완성 제품이 없습니다.")

# UI 컴포넌트 테스트
@pytest.mark.asyncio
async def test_category_select_callback(mock_interaction):
    # SubcategoryView 패치
    with patch('app.bot.views.product_views.SubcategoryView') as mock_subcategory_view:
        # 테스트할 객체 생성
        product = MagicMock()
        category_select = CategorySelect(product)
        
        # 콜백 호출
        await category_select.callback(mock_interaction)
        
        # 검증
        assert product.category == "액상"
        mock_subcategory_view.assert_called_once_with(product)
        mock_interaction.response.edit_message.assert_called_once()

@pytest.mark.asyncio
async def test_subcategory_view_liquid_options(mock_interaction):
    # 액상 카테고리를 가진 제품
    product = MagicMock()
    product.category = "액상"
    
    # 테스트할 객체 생성
    subcategory_view = SubcategoryView(product)
    
    # 각 항목이 추가되었는지 확인
    select_items = [item for item in subcategory_view.children if isinstance(item, discord.ui.Select)]
    assert len(select_items) == 1
    
    # Select 항목 콜백 호출
    await select_items[0].callback(mock_interaction)
    
    # 검증
    assert product.tags.startswith("|액상")
    mock_interaction.response.edit_message.assert_called_once()

@pytest.mark.asyncio
async def test_save_tags_button_callback(mock_interaction, mock_product_crud):
    # ProductCRUD 패치
    with patch('app.bot.views.product_views.ProductCRUD', return_value=mock_product_crud):
        from app.bot.views.product_views import SaveTagsButton
        
        # 테스트할 객체 생성
        product = MagicMock()
        product.id = 1
        product.category = "액상"
        product.tags = "|입호흡액상|30ml|3mg"
        product.company = "테스트 제조사"
        product.product_name = "테스트 제품명"
        
        save_button = SaveTagsButton(product)
        
        # 콜백 호출
        await save_button.callback(mock_interaction)
        
        # 검증
        mock_product_crud.update_product_tags.assert_called_once_with(
            product_id=1,
            category="액상",
            tags="|입호흡액상|30ml|3mg",
            company="테스트 제조사",
            product_name="테스트 제품명"
        )
        
        mock_interaction.response.edit_message.assert_called_once()
        call_args = mock_interaction.response.edit_message.call_args
        assert "✅ 제품 정보가 업데이트되었습니다" in call_args.kwargs['content']

@pytest.mark.asyncio
async def test_save_tags_button_callback_failure(mock_interaction, mock_product_crud):
    # 업데이트 실패 설정
    mock_product_crud.update_product_tags.return_value = False
    
    # ProductCRUD 패치
    with patch('app.bot.views.product_views.ProductCRUD', return_value=mock_product_crud):
        from app.bot.views.product_views import SaveTagsButton
        
        # 테스트할 객체 생성
        product = MagicMock()
        save_button = SaveTagsButton(product)
        
        # 콜백 호출
        await save_button.callback(mock_interaction)
        
        # 검증
        mock_interaction.response.edit_message.assert_called_once()
        call_args = mock_interaction.response.edit_message.call_args
        assert "❌ 제품 정보 업데이트 중 오류가 발생했습니다" in call_args.kwargs['content']

# 모달 테스트
@pytest.mark.asyncio
async def test_product_name_modal_submit(mock_interaction):
    # 모의 TextInput 값 설정
    from app.bot.views.product_views import ProductNameModal
    
    # 테스트할 객체 생성
    product = MagicMock()
    modal = ProductNameModal(product)
    
    # TextInput 값 설정
    modal.product_name_input.value = "새 제품명"
    
    # 제출 이벤트 호출
    await modal.on_submit(mock_interaction)
    
    # 검증
    assert product.product_name == "새 제품명"
    mock_interaction.response.edit_message.assert_called_once()

@pytest.mark.asyncio
async def test_company_modal_submit(mock_interaction):
    # 모의 TextInput 값 설정
    from app.bot.views.product_views import CompanyModal
    
    # 테스트할 객체 생성
    product = MagicMock()
    modal = CompanyModal(product)
    
    # TextInput 값 설정
    modal.company_input.value = "새 제조사"
    
    # 제출 이벤트 호출
    await modal.on_submit(mock_interaction)
    
    # 검증
    assert product.company == "새 제조사"
    mock_interaction.response.edit_message.assert_called_once()
