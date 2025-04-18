"""
자동 태깅 시스템 명령어
"""
import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import time
import asyncio
from typing import Dict, Any, List, Optional

from app.utils.logger import mainLogger
from app.database.crud.product_crud import ProductCRUD
from app.ml.tagger import AutoTaggingSystem

# 로거 정의
logger = mainLogger()

# CRUD 객체 생성
crud = ProductCRUD()


class TagEditModal(Modal):
    """
    태그 수정 모달
    """
    
    def __init__(self, product_id: int, predictions: Dict[str, str], tagger: AutoTaggingSystem, product_name: str):
        super().__init__(title=f"태그 수정 - {product_name}"[:44])
        
        self.product_id = product_id
        self.tagger = tagger
        
        # 각 필드에 예측 결과를 기본값으로 설정
        self.company_input = TextInput(
            label="회사명 (company)",
            placeholder="회사명을 입력하세요",
            default=predictions.get("company", ""),
            required=True
        )
        self.add_item(self.company_input)
        
        self.category_input = TextInput(
            label="카테고리 (category)",
            placeholder="카테고리를 입력하세요",
            default=predictions.get("category", ""),
            required=True
        )
        self.add_item(self.category_input)
        
        self.tags_input = TextInput(
            label="태그 (tags)",
            placeholder="태그를 입력하세요 (|로 구분)",
            default=predictions.get("tags", ""),
            required=False,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.tags_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        모달 제출 이벤트 처리
        """
        try:
            # 수정된 태그 값 가져오기
            corrected_tags = {
                "company": self.company_input.value,
                "category": self.category_input.value,
                "tags": self.tags_input.value
            }
            
            # 데이터베이스에 태그 적용
            update_result = crud.update_product_tags(
                self.product_id,
                company=corrected_tags["company"],
                category=corrected_tags["category"],
                tags=corrected_tags["tags"]
            )
            
            # 피드백 기록
            feedback_result = self.tagger.process_feedback(
                self.product_id, 
                corrected_tags, 
                user_id=str(interaction.user.id)
            )
            
            if update_result:
                await interaction.response.send_message(
                    content="✅ 수정된 태그가 성공적으로 적용되었습니다. 피드백을 통해 모델 성능이 향상됩니다.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    content="❌ 태그 적용 중 오류가 발생했습니다.",
                    ephemeral=True
                )
        except Exception as e:
            logger.error(f"태그 수정 중 오류 발생: {str(e)}")
            await interaction.response.send_message(
                content=f"❌ 태그 수정 중 오류가 발생했습니다: {str(e)}",
                ephemeral=True
            )


class AutoTaggingCommands(commands.Cog):
    """
    자동 태깅 명령어를 처리하는 클래스입니다.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.tagger = AutoTaggingSystem(db_connection=crud)
        self.batch_processing = {}  # 배치 처리 상태 추적
    
    @commands.command(name="auto_tag")
    async def auto_tag(self, ctx, product_id: int):
        """
        제품 자동 태깅 명령어
        
        Args:
            ctx (commands.Context): 명령어 컨텍스트
            product_id (int): 태깅할 제품 ID
        """
        try:
            # 처리 메시지 전송
            processing_msg = await ctx.send("🔍 자동 태깅 시스템이 분석 중입니다...")
            
            # 태그 예측
            result = self.tagger.tag_product(product_id)
            
            # 오류 처리
            if "error" in result:
                await processing_msg.edit(content=f"오류: {result['error']}")
                return
            
            # 제품 정보 가져오기
            product = crud.get_product(product_id)
            if not product:
                await processing_msg.edit(content=f"오류: 제품 정보를 찾을 수 없습니다.")
                return
            
            # 예측 결과 출력
            predictions = result["predictions"]
            confidence = result["confidence_scores"]
            
            embed = discord.Embed(
                title=f"제품 #{product_id} 자동 태깅 결과",
                color=discord.Color.green()
            )
            
            # 기본 정보 추가
            embed.add_field(
                name="제품명", 
                value=product.sale_name, 
                inline=False
            )
            
            # 예측 태그 추가
            embed.add_field(
                name="회사명 (company)", 
                value=predictions.get("company", "예측 실패"), 
                inline=True
            )
            embed.add_field(
                name="카테고리 (category)", 
                value=predictions.get("category", "예측 실패"), 
                inline=True
            )
            embed.add_field(
                name="태그 (tags)", 
                value=predictions.get("tags", "예측 실패"), 
                inline=True
            )
            
            # 신뢰도 점수 추가
            embed.add_field(
                name="신뢰도 점수", 
                value=f"전체: {confidence.get('overall', 0.0):.2f}\n" + 
                      f"회사명: {confidence.get('company', 0.0):.2f}\n" + 
                      f"카테고리: {confidence.get('category', 0.0):.2f}\n" + 
                      f"태그: {confidence.get('tags', 0.0):.2f}",
                inline=False
            )
            
            # 버튼 생성
            class AutoTagButtons(View):
                def __init__(self, cog, product_id, predictions):
                    super().__init__(timeout=300)  # 5분 타임아웃
                    self.cog = cog
                    self.product_id = product_id
                    self.predictions = predictions
                
                @discord.ui.button(label="✓ 태그 적용", style=discord.ButtonStyle.green)
                async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    try:
                        # 데이터베이스에 태그 적용
                        update_result = crud.update_product_tags(
                            self.product_id,
                            company=self.predictions.get("company", ""),
                            category=self.predictions.get("category", ""),
                            tags=self.predictions.get("tags", "")
                        )
                        
                        if update_result:
                            await interaction.response.send_message(
                                content="✅ 태그가 성공적으로 적용되었습니다.",
                                ephemeral=True
                            )
                            # 버튼 비활성화
                            self.disable_all_items()
                            await interaction.message.edit(view=self)
                        else:
                            await interaction.response.send_message(
                                content="❌ 태그 적용 중 오류가 발생했습니다.",
                                ephemeral=True
                            )
                    except Exception as e:
                        logger.error(f"태그 적용 중 오류 발생: {str(e)}")
                        await interaction.response.send_message(
                            content=f"❌ 태그 적용 중 오류가 발생했습니다: {str(e)}",
                            ephemeral=True
                        )
                
                @discord.ui.button(label="✎ 수정하기", style=discord.ButtonStyle.blurple)
                async def edit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    try:
                        # 수정 모달 표시
                        product = crud.get_product(self.product_id)
                        if not product:
                            raise Exception("제품 정보를 찾을 수 없습니다.")
                        modal = TagEditModal(self.product_id, self.predictions, self.cog.tagger, product.sale_name)
                        await interaction.response.send_modal(modal)
                        
                        # 모달이 제출된 후 버튼 비활성화
                        self.disable_all_items()
                        await interaction.message.edit(view=self)
                    except Exception as e:
                        logger.error(f"태그 수정 모달 표시 중 오류 발생: {str(e)}")
                        await interaction.response.send_message(
                            content=f"❌ 모달 표시 중 오류가 발생했습니다: {str(e)}",
                            ephemeral=True
                        )
                
                def disable_all_items(self):
                    for item in self.children:
                        item.disabled = True
            
            # 버튼 뷰 생성
            view = AutoTagButtons(self, product_id, predictions)
            
            # 처리 메시지 업데이트
            await processing_msg.edit(content=None, embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"자동 태깅 중 오류 발생: {str(e)}")
            await ctx.send(f"❌ 자동 태깅 중 오류가 발생했습니다: {str(e)}")
    
    @commands.command(name="auto_tag_batch")
    @commands.has_permissions(administrator=True)
    async def auto_tag_batch(self, ctx, limit: int = 100):
        """
        다수의 제품을 자동 태깅하는 배치 명령어
        
        Args:
            ctx (commands.Context): 명령어 컨텍스트
            limit (int, optional): 처리할 최대 제품 수. 기본값은 100.
        """
        # 이미 배치 처리 중인지 확인
        if ctx.guild.id in self.batch_processing and self.batch_processing[ctx.guild.id]:
            await ctx.send("❌ 이미 진행 중인 배치 처리가 있습니다. 완료될 때까지 기다려주세요.")
            return
        
        # 배치 처리 상태 업데이트
        self.batch_processing[ctx.guild.id] = True
        
        try:
            # 제한 수 검증
            if limit > 200:
                await ctx.send("⚠️ 최대 200개까지만 처리할 수 있습니다. 제한 수를 200으로 조정합니다.")
                limit = 200
            
            # 진행 메시지 전송
            progress_msg = await ctx.send(f"🔍 최대 {limit}개 제품의 자동 태깅을 시작합니다...")
            
            # 배치 처리 실행
            start_time = time.time()
            result = self.tagger.batch_tag_products(limit=limit)
            
            # 오류 처리
            if "error" in result:
                await progress_msg.edit(content=f"오류: {result['error']}")
                self.batch_processing[ctx.guild.id] = False
                return
                
            # 처리 결과
            products_count = result.get("total", 0)
            successful = result.get("successful", 0)
            failed = result.get("failed", 0)
            duration = time.time() - start_time
            
            # 결과 임베드 생성
            embed = discord.Embed(
                title="배치 자동 태깅 완료",
                color=discord.Color.green(),
                description=f"총 {products_count}개 제품을 처리했습니다."
            )
            
            embed.add_field(name="성공", value=f"{successful}개", inline=True)
            embed.add_field(name="실패", value=f"{failed}개", inline=True)
            embed.add_field(name="소요 시간", value=f"{duration:.1f}초", inline=True)
            
            # 실패한 제품 목록 (최대 10개)
            failed_products = [p for p in result.get("products", []) if p.get("status") == "failed"]
            if failed_products:
                failed_list = "\n".join([f"ID: {p['id']} - {p.get('error', '알 수 없는 오류')}" for p in failed_products[:10]])
                if len(failed_products) > 10:
                    failed_list += f"\n... 외 {len(failed_products) - 10}개"
                embed.add_field(name="실패한 제품", value=failed_list, inline=False)
            
            # 처리 메시지 업데이트
            await progress_msg.edit(content=None, embed=embed)
            
            # 배치 처리 완료
            self.batch_processing[ctx.guild.id] = False
            
        except Exception as e:
            logger.error(f"배치 자동 태깅 중 오류 발생: {str(e)}")
            await ctx.send(f"❌ 배치 처리 중 오류가 발생했습니다: {str(e)}")
            self.batch_processing[ctx.guild.id] = False
    
    @commands.command(name="retrain_model")
    @commands.has_permissions(administrator=True)
    async def retrain_model(self, ctx):
        """
        자동 태깅 모델을 재학습합니다.
        
        Args:
            ctx (commands.Context): 명령어 컨텍스트
        """
        try:
            # 진행 메시지 전송
            progress_msg = await ctx.send("🔄 모델 재학습을 시작합니다. 이 작업은 몇 분 정도 소요될 수 있습니다...")
            
            # 백그라운드 태스크로 모델 재학습 실행
            self.bot.loop.create_task(self._retrain_model_task(ctx, progress_msg))
        
        except Exception as e:
            logger.error(f"모델 재학습 명령 처리 중 오류 발생: {str(e)}")
            await ctx.send(f"❌ 모델 재학습 중 오류가 발생했습니다: {str(e)}")
    
    async def _retrain_model_task(self, ctx, message):
        """
        모델 재학습 백그라운드 태스크
        
        Args:
            ctx (commands.Context): 명령어 컨텍스트
            message (discord.Message): 진행 메시지
        """
        try:
            # 모델 재학습 실행
            start_time = time.time()
            self.tagger._retrain_models()
            duration = time.time() - start_time
            
            # 결과 임베드 생성
            embed = discord.Embed(
                title="모델 재학습 완료",
                color=discord.Color.green(),
                description=f"자동 태깅 모델이 성공적으로 재학습되었습니다."
            )
            
            embed.add_field(name="소요 시간", value=f"{duration:.1f}초", inline=True)
            
            # 처리 메시지 업데이트
            await message.edit(content=None, embed=embed)
            
        except Exception as e:
            logger.error(f"모델 재학습 백그라운드 태스크 중 오류 발생: {str(e)}")
            await message.edit(content=f"❌ 모델 재학습 중 오류가 발생했습니다: {str(e)}")
    
    @commands.command(name="model_info")
    async def model_info(self, ctx):
        """
        자동 태깅 모델 정보를 표시합니다.
        
        Args:
            ctx (commands.Context): 명령어 컨텍스트
        """
        try:
            # 회사명 모델 - 특성 중요도 상위 10개 추출
            company_importance = self.tagger.models['company'].get_feature_importance()
            top_company_features = sorted(company_importance.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # 카테고리 모델 - 특성 중요도 상위 10개 추출
            category_importance = self.tagger.models['category'].get_feature_importance()
            top_category_features = sorted(category_importance.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # 임베드 생성
            embed = discord.Embed(
                title="자동 태깅 모델 정보",
                color=discord.Color.blue(),
                description="현재 자동 태깅 시스템에서, 사용 중인 모델의 정보입니다."
            )
            
            # 회사명 모델 정보
            company_classes = len(self.tagger.models['company'].classes_)
            company_features = "\n".join([f"{name}: {importance:.4f}" for name, importance in top_company_features])
            
            embed.add_field(
                name=f"회사명 모델 (총 {company_classes}개 회사)",
                value=f"**주요 특성 (상위 10개):**\n{company_features}",
                inline=False
            )
            
            # 카테고리 모델 정보
            category_classes = len(self.tagger.models['category'].classes_)
            category_features = "\n".join([f"{name}: {importance:.4f}" for name, importance in top_category_features])
            
            embed.add_field(
                name=f"카테고리 모델 (총 {category_classes}개 카테고리)",
                value=f"**주요 특성 (상위 10개):**\n{category_features}",
                inline=False
            )
            
            # 태그 모델 정보
            if hasattr(self.tagger.models['tags'].mlb, 'classes_'):
                tag_classes = len(self.tagger.models['tags'].mlb.classes_)
                embed.add_field(
                    name=f"태그 모델 (총 {tag_classes}개 고유 태그)",
                    value="다중 레이블 분류 모델을 사용하여 태그를 예측합니다.",
                    inline=False
                )
            
            # 학습 정보
            last_update = self.tagger.config.get('last_model_update')
            update_info = last_update.strftime("%Y-%m-%d %H:%M:%S") if last_update else "정보 없음"
            
            embed.set_footer(text=f"마지막 모델 업데이트: {update_info}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"모델 정보 표시 중 오류 발생: {str(e)}")
            await ctx.send(f"❌ 모델 정보 조회 중 오류가 발생했습니다: {str(e)}")


async def setup(bot):
    """
    봇에 AutoTaggingCommands 코그를 추가합니다.
    """
    await bot.add_cog(AutoTaggingCommands(bot))
