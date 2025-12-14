from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.exceptions.seller_exceptions import SellerNotFoundException
from app.repositories.seller_repository import SellerRepository
from app.repositories.settlement_repository import SettlementRepository
from app.schemas.settlement import (
    SettlementCalculateResponse,
    SettlementListResponse,
    SettlementResponse,
)

# 수수료율 (10%)
COMMISSION_RATE = Decimal("0.10")


class SettlementService:
    def __init__(self, db: Session):
        self.db = db
        self.settlement_repo = SettlementRepository(db)
        self.seller_repo = SellerRepository(db)

    def get_my_settlements(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> SettlementListResponse:
        # 판매자 프로필 확인
        seller = self.seller_repo.get_by_user_id(user_id)
        if not seller:
            raise SellerNotFoundException()

        settlements, total = self.settlement_repo.get_by_seller_id(
            seller.id, start_date=start_date, end_date=end_date
        )

        return SettlementListResponse(
            settlements=[SettlementResponse.model_validate(s) for s in settlements],
            total=total,
        )

    def calculate_settlements(self) -> SettlementCalculateResponse:
        """정산 데이터 계산 및 생성 (Admin 전용)

        ARRIVED 상태이면서 아직 정산되지 않은 주문 아이템들을 조회하여
        판매자별로 그룹화한 후 정산 데이터를 생성합니다.

        Returns:
            SettlementCalculateResponse: 생성된 정산 건수 및 처리된 주문 수
        """
        # 1. 미정산 주문 아이템 조회
        unsettled_items = self.settlement_repo.get_unsettled_order_items()

        if not unsettled_items:
            return SettlementCalculateResponse(
                created_settlements=0,
                total_processed_orders=0,
                message="No unsettled orders found",
            )

        # 2. 판매자별로 그룹화
        seller_orders = defaultdict(list)
        for item in unsettled_items:
            if item.book and item.book.seller_id:
                seller_orders[item.book.seller_id].append(item)

        # 3. 정산 기간 설정 (오늘 기준)
        today = date.today()
        # 가장 오래된 주문과 최신 주문의 날짜를 기간으로 설정
        all_dates = [item.created_at.date() for item in unsettled_items]
        period_start = min(all_dates) if all_dates else today
        period_end = max(all_dates) if all_dates else today

        created_count = 0
        total_orders = 0

        # 4. 판매자별 정산 생성
        for seller_id, items in seller_orders.items():
            # 매출 합계 계산
            total_sales = sum(item.total_amount for item in items)

            # 수수료 계산 (10%)
            commission = total_sales * COMMISSION_RATE

            # 최종 정산액
            final_payout = total_sales - commission

            # 정산 레코드 생성
            settlement = self.settlement_repo.create(
                {
                    "seller_id": seller_id,
                    "total_sales": total_sales,
                    "commission": commission,
                    "final_payout": final_payout,
                    "period_start": period_start,
                    "period_end": period_end,
                    "settlement_date": today,
                },
                commit=False,
            )

            # 정산된 주문 아이템들을 SettlementOrder로 연결
            for item in items:
                self.settlement_repo.add_order(
                    settlement.id, item.id, commit=False
                )
                total_orders += 1

            created_count += 1

        # 5. 트랜잭션 커밋
        self.db.commit()

        return SettlementCalculateResponse(
            created_settlements=created_count,
            total_processed_orders=total_orders,
            message=f"Successfully created {created_count} settlements for {total_orders} order items",
        )
