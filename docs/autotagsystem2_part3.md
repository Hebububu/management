### 3.3 3단계: 서비스 통합 및 UI 개발 (1주)

#### 3.3.1 Discord 봇 명령어 구현
```python
@bot.command(name="auto_tag")
async def auto_tag(ctx, product_id: int):
    """제품 자동 태깅 명령어"""
    # 태깅 시스템 초기화
    tagging_system = AutoTaggingSystem()
    
    # 태그 예측
    result = tagging_system.tag_product(product_id)
    
    # 결과 표시
    if "error" in result:
        await ctx.send(f"오류: {result['error']}")
        return
    
    # 예측 결과 출력
    predictions = result["predictions"]
    embed = discord.Embed(title=f"제품 #{product_id} 자동 태깅 결과", color=0x00ff00)
    
    # 기본 정보 추가
    product = await get_product_info(product_id)
    embed.add_field(
        name="제품명", 
        value=product.get("sale_name", "정보 없음"), 
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
    
    # 버튼으로 피드백 옵션 추가
    components = [
        Button(style=ButtonStyle.green, label="✓ 태그 적용", custom_id=f"apply_{product_id}"),
        Button(style=ButtonStyle.blue, label="✎ 수정하기", custom_id=f"edit_{product_id}")
    ]
    
    await ctx.send(embed=embed, components=components)
```

#### 3.3.2 피드백 UI 구현
```python
@bot.event
async def on_button_click(interaction):
    """버튼 클릭 이벤트 처리"""
    custom_id = interaction.custom_id
    
    if custom_id.startswith("apply_"):
        # 태그 적용 버튼 처리
        product_id = int(custom_id.split("_")[1])
        
        # 태그 적용 처리
        tagging_system = AutoTaggingSystem()
        result = tagging_system.tag_product(product_id)
        predictions = result["predictions"]
        
        # 데이터베이스에 태그 적용
        product_crud = ProductCRUD()
        update_result = product_crud.update_product_tags(
            product_id,
            predictions.get("company"),
            predictions.get("category"),
            predictions.get("tags")
        )
        
        if update_result:
            await interaction.respond(content="✅ 태그가 성공적으로 적용되었습니다.")
        else:
            await interaction.respond(content="❌ 태그 적용 중 오류가 발생했습니다.")
    
    elif custom_id.startswith("edit_"):
        # 수정 버튼 처리
        product_id = int(custom_id.split("_")[1])
        
        # 수정 모달 표시
        tagging_system = AutoTaggingSystem()
        result = tagging_system.tag_product(product_id)
        predictions = result["predictions"]
        
        modal = Modal(
            title="태그 수정",
            custom_id=f"edit_modal_{product_id}",
            components=[
                TextInput(
                    label="회사명 (company)",
                    custom_id="company",
                    value=predictions.get("company", ""),
                    style=TextInputStyle.short
                ),
                TextInput(
                    label="카테고리 (category)",
                    custom_id="category",
                    value=predictions.get("category", ""),
                    style=TextInputStyle.short
                ),
                TextInput(
                    label="태그 (tags)",
                    custom_id="tags", 
                    value=predictions.get("tags", ""),
                    style=TextInputStyle.paragraph
                )
            ]
        )
        
        await interaction.respond(modal=modal)

@bot.event
async def on_modal_submit(interaction):
    """모달 제출 이벤트 처리"""
    custom_id = interaction.custom_id
    
    if custom_id.startswith("edit_modal_"):
        # 수정 모달 처리
        product_id = int(custom_id.split("_")[2])
        
        # 수정된 태그 값 가져오기
        corrected_tags = {
            "company": interaction.values["company"],
            "category": interaction.values["category"],
            "tags": interaction.values["tags"]
        }
        
        # 데이터베이스에 수정된 태그 적용
        product_crud = ProductCRUD()
        update_result = product_crud.update_product_tags(
            product_id,
            corrected_tags["company"],
            corrected_tags["category"],
            corrected_tags["tags"]
        )
        
        # 피드백 기록
        tagging_system = AutoTaggingSystem()
        tagging_system.process_feedback(
            product_id, 
            corrected_tags, 
            user_id=str(interaction.user.id)
        )
        
        if update_result:
            await interaction.respond(content="✅ 수정된 태그가 성공적으로 적용되었습니다. 피드백을 통해 모델 성능이 향상됩니다.")
        else:
            await interaction.respond(content="❌ 태그 적용 중 오류가 발생했습니다.")
```

### 3.4 4단계: 테스트, 배포 및 최적화 (1주)

#### 3.4.1 테스트 및 평가
- 모델 성능 평가 (정확도, 정밀도, 재현율)
- 사용자 경험 테스트 
- 배치 처리 성능 테스트

#### 3.4.2 배치 처리 시스템 구현
```python
@bot.command(name="auto_tag_batch")
async def auto_tag_batch(ctx, limit: int = 100):
    """다수의 제품을 자동 태깅하는 배치 명령어"""
    # 권한 확인
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("이 명령어는 관리자만 사용할 수 있습니다.")
        return
    
    # 진행 메시지 전송
    progress_msg = await ctx.send(f"최대 {limit}개 제품의 자동 태깅을 시작합니다...")
    
    # 태깅 시스템 초기화
    tagging_system = AutoTaggingSystem()
    
    # 태그가 없는 제품 조회
    product_crud = ProductCRUD()
    untagged_products = product_crud.get_untagged_products(limit=limit)
    
    if not untagged_products:
        await progress_msg.edit(content="태그가 필요한 제품이 없습니다.")
        return
    
    # 배치 처리 결과 추적
    successful = 0
    failed = 0
    products_count = len(untagged_products)
    
    # 처리 시작
    start_time = time.time()
    
    # 프로그레스 바 업데이트 함수
    async def update_progress(current, total):
        progress = min(current / total * 20, 20)  # 20칸짜리 프로그레스 바
        bar = "█" * int(progress) + "░" * (20 - int(progress))
        percent = current / total * 100
        await progress_msg.edit(content=f"처리 중: {bar} {percent:.1f}% ({current}/{total})")
    
    # 각 제품 처리
    for i, product in enumerate(untagged_products):
        # 진행 상황 업데이트 (10개마다)
        if i % 10 == 0:
            await update_progress(i, products_count)
        
        try:
            # 태그 예측
            result = tagging_system.tag_product(product["id"])
            predictions = result["predictions"]
            
            # 데이터베이스에 태그 적용
            update_result = product_crud.update_product_tags(
                product["id"],
                predictions.get("company"),
                predictions.get("category"),
                predictions.get("tags")
            )
            
            if update_result:
                successful += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            logger.error(f"Error processing product {product['id']}: {str(e)}")
    
    # 완료 메시지
    duration = time.time() - start_time
    await progress_msg.edit(
        content=f"✅ 배치 처리 완료!\n"
               f"- 총 제품 수: {products_count}\n"
               f"- 성공: {successful}\n"
               f"- 실패: {failed}\n"
               f"- 소요 시간: {duration:.1f}초"
    )
```

#### 3.4.3 정기적인 모델 재학습 스케줄러
```python
def schedule_model_retraining():
    """정기적인 모델 재학습 스케줄링"""
    scheduler = BackgroundScheduler()
    
    # 매일 새벽 4시에 모델 재학습
    scheduler.add_job(retrain_models, 'cron', hour=4)
    
    # 스케줄러 시작
    scheduler.start()

def retrain_models():
    """모델 재학습 실행"""
    logger.info("정기 모델 재학습 시작")
    
    try:
        # 태깅 시스템 초기화
        tagging_system = AutoTaggingSystem()
        
        # 모델 재학습 실행
        tagging_system._retrain_models()
        
        logger.info("모델 재학습 완료")
    except Exception as e:
        logger.error(f"모델 재학습 중 오류 발생: {str(e)}")
```