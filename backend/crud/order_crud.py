# crud/order_crud.py — 订单管理业务逻辑
from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from models.order_model import Order, OrderItem
from models.product_model import Product
from schemas.order_schema import OrderCreate, OrderUpdate, OrderStatusUpdate


def _generate_order_no(db: Session) -> str:
    """生成订单编号: 年月日时分秒 + 毫秒，如 20260513143025-001"""
    prefix = datetime.now().strftime("%Y%m%d%H%M%S")
    # 查询当天已有订单数作为序号
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    count = db.query(Order).filter(Order.created_at >= today_start).count()
    return f"{prefix}-{count + 1:03d}"


# ==================== 订单 CRUD ====================

def get_orders(
    db: Session,
    store_id: int | None = None,
    order_type: str | None = None,
    status: str | None = None,
    search: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    customer_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
):
    """获取订单列表，支持多条件过滤"""
    query = db.query(Order)
    if store_id is not None:
        query = query.filter(Order.store_id == store_id)
    if order_type:
        query = query.filter(Order.order_type == order_type)
    if status:
        query = query.filter(Order.status == status)
    if search:
        like = f"%{search}%"
        query = query.filter(Order.order_no.like(like))
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= f"{end_date} 23:59:59")
    if customer_id is not None:
        query = query.filter(Order.customer_id == customer_id)
    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


def get_order_by_id(db: Session, order_id: int):
    """获取订单详情（含明细）"""
    return db.query(Order).options(joinedload(Order.items)).filter(Order.id == order_id).first()


def create_order(db: Session, order_data: OrderCreate):
    """创建订单：自动生成编号、计算金额、扣减库存"""
    # 1. 计算总金额
    total_amount = 0.0
    for item in order_data.items:
        total_amount += item.subtotal
    final_amount = total_amount - (order_data.discount_amount or 0)

    # 2. 创建订单
    db_order = Order(
        order_no=_generate_order_no(db),
        store_id=order_data.store_id,
        order_type=order_data.order_type,
        customer_id=order_data.customer_id,
        total_amount=total_amount,
        discount_amount=order_data.discount_amount,
        final_amount=max(final_amount, 0),
        payment_method=order_data.payment_method,
        status="pending",  # 初始状态待支付
        operator_id=order_data.operator_id,
        remark=order_data.remark,
    )
    db.add(db_order)
    db.flush()  # 获取订单ID

    # 3. 创建明细 + 扣减库存
    for item in order_data.items:
        db_item = OrderItem(
            order_id=db_order.id,
            item_type=item.item_type,
            product_id=item.product_id,
            service_id=item.service_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.subtotal,
            staff_id=item.staff_id,
        )
        db.add(db_item)

        # 扣减商品库存（仅销售订单的商品类）
        if item.item_type == "product" and item.product_id:
            # 使用悲观行锁防止并发超卖
            product = db.query(Product).filter(
                Product.id == item.product_id
            ).with_for_update().first()
            if not product:
                raise ValueError(f"商品 {item.product_id} 不存在")
            if product.stock < item.quantity:
                raise ValueError(
                    f"商品「{product.name}」库存不足，当前库存 {product.stock}，需要 {item.quantity}"
                )
            product.stock -= item.quantity

    db.commit()
    db.refresh(db_order)
    return db_order


def update_order(db: Session, order_id: int, order_data: OrderUpdate):
    """更新订单基本信息"""
    db_order = get_order_by_id(db, order_id)
    if db_order:
        update_data = order_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_order, key, value)
        db.commit()
        db.refresh(db_order)
    return db_order


# 订单状态流转规则
ORDER_STATUS_TRANSITIONS: dict[str, set[str]] = {
    "pending":   {"paid", "cancelled"},
    "paid":      {"completed", "cancelled", "refunded"},
    "completed": set(),   # 终态，不可再变更
    "cancelled": set(),   # 终态
    "refunded":  set(),   # 终态
}


def update_order_status(db: Session, order_id: int, status_data: OrderStatusUpdate):
    """更新订单状态（含状态机校验 + 库存回滚）"""
    # 一次性加载订单及明细，避免后续懒加载 N+1
    db_order = db.query(Order).options(
        joinedload(Order.items)
    ).filter(Order.id == order_id).first()
    if not db_order:
        return None

    current_status = db_order.status
    target_status = status_data.status

    # 状态机校验：检查当前状态是否允许跳转到目标状态
    allowed = ORDER_STATUS_TRANSITIONS.get(current_status, set())
    if target_status not in allowed:
        raise ValueError(
            f"不允许从「{current_status}」直接变更为「{target_status}」",
        )

    db_order.status = target_status
    if status_data.remark:
        db_order.remark = (db_order.remark or '') + f" [{target_status}] {status_data.remark}"

    # ---- 取消 / 退款：回滚商品库存 ----
    if target_status in ("cancelled", "refunded"):
        for item in db_order.items:
            if item.item_type == "product" and item.product_id:
                product = db.query(Product).filter(
                    Product.id == item.product_id
                ).with_for_update().first()
                if product:
                    product.stock += item.quantity

    db.commit()
    db.refresh(db_order)
    return db_order
