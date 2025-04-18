"""
extract_company 메서드 테스트

이 스크립트는 ProductTagger 클래스의 extract_company 메서드를 테스트합니다.
데이터베이스에서 임의로 50개의 제품을 가져와 회사명 추출 결과를 확인합니다.
"""

import sys
import os
import random
import json
from datetime import datetime

from app.scripts.producttagger import ProductTagger
from app.database.crud.product_crud import ProductCRUD
from app.utils.logger import mainLogger

# 로거 설정
logger = mainLogger()

def test_extract_company():
    """
    extract_company 메서드 테스트 함수
    """
    # ProductTagger 초기화
    tagger = ProductTagger()
    
    # ProductCRUD 초기화
    product_crud = ProductCRUD()
    
    # 현재 시간
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    logger.info(f"===== extract_company 메서드 테스트 시작 ({now}) =====")
    
    # 최근 제품 100개 가져오기 (또는 더 적은 수의 모든 제품)
    products = product_crud.get_recent_products(100)
    
    # 랜덤하게 50개 선택 (100개 미만이면 모두 사용)
    if len(products) > 50:
        test_products = random.sample(products, 50)
    else:
        test_products = products
    
    logger.info(f"테스트할 제품 수: {len(test_products)}")
    logger.info("-" * 80)
    
    # 결과 저장
    results = []
    success_count = 0
    total_with_company = 0
    
    # 각 제품에 대해 회사명 추출 테스트
    for idx, product in enumerate(test_products, 1):
        platform = product.platform
        sale_name = product.sale_name
        data = product.data
        
        try:
            # 회사명 추출
            extracted_company = tagger.extract_company(sale_name, data, platform)
            
            # 결과 저장
            result = {
                "product_id": product.id,
                "platform": platform,
                "sale_name": sale_name,
                "extracted_company": extracted_company,
                "existing_company": product.company if product.company else None
            }
            results.append(result)
            
            # 성공률 계산 (기존 회사명이 있는 경우만)
            if product.company:
                total_with_company += 1
                if extracted_company == product.company:
                    success_count += 1
            
            # 결과 출력
            logger.info(f"{idx}. 제품 ID: {product.id}")
            logger.info(f"   플랫폼: {platform}")
            logger.info(f"   판매명: {sale_name}")
            logger.info(f"   추출된 회사명: {extracted_company}")
            if product.company:
                logger.info(f"   기존 회사명: {product.company}")
                if extracted_company != product.company:
                    logger.info(f"   [주의] 추출된 회사명이 기존 회사명과 다릅니다!")
            else:
                logger.info(f"   기존 회사명: (없음)")
            logger.info("-" * 80)
            
        except Exception as e:
            logger.info(f"{idx}. 제품 ID: {product.id}")
            logger.info(f"   오류 발생: {str(e)}")
            logger.info("-" * 80)
    
    # 성공률 계산
    success_rate = (success_count / total_with_company) * 100 if total_with_company > 0 else 0
    
    logger.info(f"테스트 결과 요약:")
    logger.info(f"- 총 테스트 제품 수: {len(test_products)}")
    logger.info(f"- 기존 회사명이 있는 제품 수: {total_with_company}")
    logger.info(f"- 기존 회사명과 일치한 제품 수: {success_count}")
    logger.info(f"- 성공률: {success_rate:.2f}%")
    
    # 결과를 JSON 파일로 저장 (app/tests/results 디렉토리 생성)
    results_dir = "app/tests/results"
    os.makedirs(results_dir, exist_ok=True)
    
    result_file = f"{results_dir}/extract_company_results_{now.replace(':', '-').replace(' ', '_')}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"상세 결과가 다음 파일에 저장되었습니다: {result_file}")
    logger.info(f"===== extract_company 메서드 테스트 종료 =====")

def analyze_failures():
    """
    추출 실패 사례를 분석합니다.
    """
    # 결과 디렉토리 확인
    results_dir = "app/tests/results"
    if not os.path.exists(results_dir):
        logger.info("분석할 결과 파일이 없습니다.")
        return
    
    # 가장 최근 결과 파일 찾기
    result_files = [f for f in os.listdir(results_dir) if f.startswith("extract_company_results_")]
    if not result_files:
        logger.info("분석할 결과 파일이 없습니다.")
        return
    
    latest_file = max(result_files, key=lambda x: os.path.getmtime(os.path.join(results_dir, x)))
    file_path = os.path.join(results_dir, latest_file)
    
    try:
        # 결과 파일 로드
        with open(file_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        # 실패 사례 필터링 (기존 회사명이 있고 추출된 회사명과 다른 경우)
        failures = [r for r in results if r["existing_company"] and r["extracted_company"] != r["existing_company"]]
        
        if not failures:
            logger.info("모든 테스트가 성공했습니다!")
            return
        
        logger.info(f"===== 실패 사례 분석 ({len(failures)}건) =====")
        for idx, failure in enumerate(failures, 1):
            logger.info(f"{idx}. 제품 ID: {failure['product_id']}")
            logger.info(f"   플랫폼: {failure['platform']}")
            logger.info(f"   판매명: {failure['sale_name']}")
            logger.info(f"   추출된 회사명: {failure['extracted_company']}")
            logger.info(f"   기존 회사명: {failure['existing_company']}")
            logger.info("-" * 80)
        
        # 플랫폼별 실패율
        platform_stats = {}
        for r in results:
            if r["existing_company"]:
                platform = r["platform"]
                if platform not in platform_stats:
                    platform_stats[platform] = {"total": 0, "failures": 0}
                platform_stats[platform]["total"] += 1
                if r["extracted_company"] != r["existing_company"]:
                    platform_stats[platform]["failures"] += 1
        
        logger.info("플랫폼별 실패율:")
        for platform, stats in platform_stats.items():
            failure_rate = (stats["failures"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            logger.info(f"- {platform}: {failure_rate:.2f}% ({stats['failures']}/{stats['total']})")
    
    except Exception as e:
        logger.error(f"결과 분석 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    # 회사명 추출 테스트 실행
    test_extract_company()
    
    # 실패 사례 분석 (옵션)
    logger.info("\n")
    analyze_failures()
