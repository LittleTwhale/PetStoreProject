# api/order_api.py — 订单管理接口
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from database.database import get_db
from schemas.order_schema import (
    OrderCreate, OrderUpdate, OrderStatusUpdate,
    OrderResponse, OrderListResponse, OrderItemResponse,
)
from crud import order_crud
from models.user_model import User
from core import security

router = APIRouter(tags=["订单管理"])


def _build_order_response(order) -> OrderResponse:
    """构造带冗余字段的订单响应"""
    return OrderResponse(
        id=order.id,
        order_no=order.order_no,
        store_id=order.store_id,
        order_type=order.order_type,
        customer_id=order.customer_id,
        total_amount=order.total_amount,
        discount_amount=order.discount_amount,
        final_amount=order.final_amount,
        payment_method=order.payment_method,
        status=order.status,
        operator_id=order.operator_id,
        remark=order.remark,
        created_at=order.created_at,
        updated_at=order.updated_at,
        customer_name=order.customer.name if order.customer else None,
        operator_name=order.operator.nickname if order.operator else None,
        store_name=None,
        items=[
            OrderItemResponse(
                id=item.id,
                order_id=item.order_id,
                item_type=item.item_type,
                product_id=item.product_id,
                service_id=item.service_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
                staff_id=item.staff_id,
                product_name=item.product.name if item.product else None,
                service_name=item.service.name if item.service else None,
                staff_name=item.staff.nickname if item.staff else None,
            )
            for item in (order.items or [])
        ],
    )


# ==================== 订单接口 ====================

@router.get("/", response_model=list[OrderListResponse])
def read_orders(
    store_id: Optional[int] = Query(None, description="按门店过滤"),
    order_type: Optional[str] = Query(None, description="类型: sale / service"),
    status: Optional[str] = Query(None, description="状态: pending/paid/completed/cancelled/refunded"),
    search: Optional[str] = Query(None, description="按订单号搜索"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    customer_id: Optional[int] = Query(None, description="按客户过滤"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """获取订单列表。admin可查看全部或指定门店，staff仅能查看绑定门店的订单"""
    security.require_admin_or_staff(current_user)
    effective_store_id = security.get_effective_store_id(current_user, store_id, db)
    orders = order_crud.get_orders(
        db, store_id=effective_store_id, order_type=order_type, status=status,
        search=search, start_date=start_date, end_date=end_date,
        customer_id=customer_id, skip=skip, limit=limit,
    )
    result = []
    for o in orders:
        result.append(OrderListResponse(
            id=o.id, order_no=o.order_no, store_id=o.store_id,
            order_type=o.order_type, customer_id=o.customer_id,
            total_amount=o.total_amount, discount_amount=o.discount_amount,
            final_amount=o.final_amount, payment_method=o.payment_method,
            status=o.status, operator_id=o.operator_id, remark=o.remark,
            created_at=o.created_at, updated_at=o.updated_at,
            customer_name=o.customer.name if o.customer else None,
            operator_name=o.operator.nickname if o.operator else None,
            store_name=None,
            item_count=len(o.items) if o.items else 0,
        ))
    return result


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """创建订单。staff自动绑定到所属门店，admin可指定门店"""
    security.require_admin_or_staff(current_user)
    # 覆盖操作人为当前用户
    order.operator_id = current_user.id
    # staff自动绑定门店
    order.store_id = security.get_effective_store_id(current_user, order.store_id, db)
    result = order_crud.create_order(db, order)
    return _build_order_response(result)


@router.get("/{order_id}", response_model=OrderResponse)
def read_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """获取订单详情（含明细）"""
    security.require_admin_or_staff(current_user)
    o = order_crud.get_order_by_id(db, order_id)
    if not o:
        raise HTTPException(status_code=404, detail="订单不存在")
    # staff 只能查看绑定门店的订单
    if current_user.role == "staff":
        security.require_store_access(current_user, o.store_id, db)
    return _build_order_response(o)


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """更新订单基本信息"""
    security.require_admin_or_staff(current_user)
    updated = order_crud.update_order(db, order_id, order)
    if not updated:
        raise HTTPException(status_code=404, detail="订单不存在")
    return updated


@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """更新订单状态"""
    security.require_admin_or_staff(current_user)
    # 退款操作仅管理员可执行
    if status_data.status == "refunded":
        security.require_admin(current_user)
    try:
        updated = order_crud.update_order_status(db, order_id, status_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not updated:
        raise HTTPException(status_code=404, detail="订单不存在")
    return _build_order_response(updated)
