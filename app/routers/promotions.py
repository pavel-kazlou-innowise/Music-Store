from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import secrets

from ..models.database import get_db
from ..models.models import (
    Discount, PromoCode, PromoCodeUsage, GiftCard, 
    GiftCardTransaction, LoyaltyTier, UserLoyalty, 
    LoyaltyPointTransaction, User, Order
)
from ..schemas.schemas import (
    DiscountCreate, DiscountResponse,
    PromoCodeCreate, PromoCodeResponse,
    GiftCardCreate, GiftCardResponse,
    LoyaltyTierCreate, LoyaltyTierResponse,
    UserLoyaltyResponse
)
from ..utils.security import get_current_admin_user, get_current_user

router = APIRouter(
    prefix="/promotions",
    tags=["promotions"]
)

# Discount endpoints
@router.post("/discounts/", response_model=DiscountResponse)
def create_discount(
    discount: DiscountCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """Create a new discount (Admin only)"""
    if discount.end_date <= discount.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )
    
    db_discount = Discount(**discount.dict())
    db.add(db_discount)
    db.commit()
    db.refresh(db_discount)
    return db_discount

@router.get("/discounts/", response_model=List[DiscountResponse])
def get_discounts(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    """Get all discounts with optional filtering for active ones"""
    query = db.query(Discount)
    if active_only:
        now = datetime.utcnow()
        query = query.filter(
            Discount.is_active == True,
            Discount.start_date <= now,
            Discount.end_date > now
        )
    return query.offset(skip).limit(limit).all()

@router.get("/discounts/{discount_id}", response_model=DiscountResponse)
def get_discount(
    discount_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    """Get discount by ID"""
    discount = db.query(Discount).filter(Discount.id == discount_id).first()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    return discount

@router.put("/discounts/{discount_id}", response_model=DiscountResponse)
def update_discount(
    discount_id: int,
    discount: DiscountCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """Update discount details (Admin only)"""
    db_discount = db.query(Discount).filter(Discount.id == discount_id).first()
    if not db_discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    if discount.end_date <= discount.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )
    
    for key, value in discount.dict().items():
        setattr(db_discount, key, value)
    
    db.commit()
    db.refresh(db_discount)
    return db_discount

@router.delete("/discounts/{discount_id}")
def delete_discount(
    discount_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """Delete a discount (Admin only)"""
    db_discount = db.query(Discount).filter(Discount.id == discount_id).first()
    if not db_discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    db.delete(db_discount)
    db.commit()
    return {"message": "Discount deleted successfully"}

# Promo code endpoints
@router.post("/promo-codes/", response_model=PromoCodeResponse)
def create_promo_code(
    promo_code: PromoCodeCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """Create a new promo code (Admin only)"""
    if promo_code.end_date <= promo_code.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )
    
    # Проверка уникальности кода
    existing = db.query(PromoCode).filter(PromoCode.code == promo_code.code).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Promo code already exists"
        )
    
    db_promo = PromoCode(**promo_code.dict())
    db.add(db_promo)
    db.commit()
    db.refresh(db_promo)
    return db_promo

@router.post("/promo-codes/{code}/validate")
def validate_promo_code(
    code: str,
    order_amount: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate a promo code for the current user and order amount"""
    promo = db.query(PromoCode).filter(PromoCode.code == code.upper()).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promo code not found")
    
    now = datetime.utcnow()
    
    # Проверки валидности
    if not promo.is_active:
        raise HTTPException(status_code=400, detail="Promo code is not active")
    
    if now < promo.start_date or now > promo.end_date:
        raise HTTPException(status_code=400, detail="Promo code is not valid at this time")
    
    if promo.minimum_order_amount > order_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Order amount must be at least {promo.minimum_order_amount}"
        )
    
    if promo.max_uses and promo.uses_count >= promo.max_uses:
        raise HTTPException(status_code=400, detail="Promo code has reached maximum uses")
    
    if promo.is_single_use:
        # Проверка использования данным пользователем
        usage = db.query(PromoCodeUsage).filter(
            PromoCodeUsage.promo_code_id == promo.id,
            PromoCodeUsage.user_id == current_user.id
        ).first()
        if usage:
            raise HTTPException(status_code=400, detail="You have already used this promo code")
    
    # Расчет скидки
    discount_amount = promo.discount_amount
    if promo.discount_percent:
        percent_discount = order_amount * (promo.discount_percent / 100)
        discount_amount = max(discount_amount, percent_discount)
    
    return {
        "valid": True,
        "discount_amount": discount_amount,
        "message": "Promo code is valid"
    }

# Gift card endpoints
@router.post("/gift-cards/", response_model=GiftCardResponse)
def create_gift_card(
    gift_card: GiftCardCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """Create a new gift card (Admin only)"""
    # Генерация уникального кода
    while True:
        code = ''.join(secrets.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(16))
        existing = db.query(GiftCard).filter(GiftCard.code == code).first()
        if not existing:
            break
    
    db_card = GiftCard(
        code=code,
        initial_balance=gift_card.initial_balance,
        current_balance=gift_card.initial_balance,
        expiry_date=gift_card.expiry_date,
        is_active=True
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

@router.get("/gift-cards/{code}/balance")
def check_gift_card_balance(
    code: str,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    """Check gift card balance"""
    card = db.query(GiftCard).filter(GiftCard.code == code.upper()).first()
    if not card:
        raise HTTPException(status_code=404, detail="Gift card not found")
    
    if not card.is_active:
        raise HTTPException(status_code=400, detail="Gift card is not active")
    
    if datetime.utcnow() > card.expiry_date:
        raise HTTPException(status_code=400, detail="Gift card has expired")
    
    return {
        "code": card.code,
        "current_balance": card.current_balance,
        "expiry_date": card.expiry_date
    }

# Loyalty program endpoints
@router.post("/loyalty/tiers/", response_model=LoyaltyTierResponse)
def create_loyalty_tier(
    tier: LoyaltyTierCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """Create a new loyalty tier (Admin only)"""
    db_tier = LoyaltyTier(**tier.dict())
    db.add(db_tier)
    db.commit()
    db.refresh(db_tier)
    return db_tier

@router.get("/loyalty/users/{user_id}", response_model=UserLoyaltyResponse)
def get_user_loyalty(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user loyalty information"""
    # Проверка прав доступа
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own loyalty information"
        )
    
    loyalty = db.query(UserLoyalty).filter(UserLoyalty.user_id == user_id).first()
    if not loyalty:
        raise HTTPException(status_code=404, detail="Loyalty information not found")
    
    return loyalty

@router.post("/loyalty/points/add")
def add_loyalty_points(
    user_id: int,
    points: int,
    description: str,
    order_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """Add loyalty points to user (Admin only)"""
    loyalty = db.query(UserLoyalty).filter(UserLoyalty.user_id == user_id).first()
    if not loyalty:
        raise HTTPException(status_code=404, detail="User loyalty not found")
    
    # Создание транзакции
    transaction = LoyaltyPointTransaction(
        user_loyalty_id=loyalty.id,
        order_id=order_id,
        points=points,
        description=description
    )
    db.add(transaction)
    
    # Обновление баланса баллов
    loyalty.points += points
    loyalty.lifetime_points += points
    
    # Проверка на повышение уровня
    next_tier = db.query(LoyaltyTier).filter(
        LoyaltyTier.minimum_points <= loyalty.lifetime_points
    ).order_by(LoyaltyTier.minimum_points.desc()).first()
    
    if next_tier and next_tier.id != loyalty.tier_id:
        loyalty.tier_id = next_tier.id
    
    db.commit()
    db.refresh(loyalty)
    
    return {
        "success": True,
        "new_balance": loyalty.points,
        "tier_name": next_tier.name if next_tier else None
    }

@router.post("/loyalty/points/redeem")
def redeem_loyalty_points(
    points_to_redeem: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Redeem loyalty points for a discount"""
    loyalty = db.query(UserLoyalty).filter(UserLoyalty.user_id == current_user.id).first()
    if not loyalty:
        raise HTTPException(status_code=404, detail="Loyalty information not found")
    
    if points_to_redeem > loyalty.points:
        raise HTTPException(
            status_code=400,
            detail="Insufficient points balance"
        )
    
    # Расчет скидки (например, 1 балл = 1 рубль скидки)
    discount_amount = points_to_redeem
    
    # Создание транзакции списания баллов
    transaction = LoyaltyPointTransaction(
        user_loyalty_id=loyalty.id,
        points=-points_to_redeem,
        description="Points redemption for discount"
    )
    db.add(transaction)
    
    # Обновление баланса баллов
    loyalty.points -= points_to_redeem
    
    db.commit()
    
    return {
        "success": True,
        "points_redeemed": points_to_redeem,
        "discount_amount": discount_amount,
        "remaining_points": loyalty.points
    }
