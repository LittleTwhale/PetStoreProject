# crud/dashboard_crud.py — 数据面板聚合查询
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from models.order_model import Order, OrderItem
from models.product_model import Product
from models.inventory_model import InventoryItem


def get_dashboard_data(db: Session, store_id: int | None = None):
    """获取数据面板聚合数据"""
    today = date.today()
    month_start = today.replace(day=1)
    tomorrow = today + timedelta(days=1)

    # ---- 基础过滤 ----
    def store_filter(query, model):
        if store_id is not None:
            return query.filter(model.store_id == store_id)
        return query

    # ---- 今日营收 / 订单数 ----
    today_query = db.query(
        func.count(Order.id),
        func.coalesce(func.sum(Order.final_amount), 0),
    ).filter(
        Order.created_at >= today,
        Order.created_at < tomorrow,
        Order.status.in_(['paid', 'completed']),
    )
    today_query = store_filter(today_query, Order)
    today_orders, today_revenue = today_query.first()

    # ---- 本月营收 / 订单数 ----
    month_query = db.query(
        func.count(Order.id),
        func.coalesce(func.sum(Order.final_amount), 0),
    ).filter(
        Order.created_at >= month_start,
        Order.created_at < tomorrow,
        Order.status.in_(['paid', 'completed']),
    )
    month_query = store_filter(month_query, Order)
    month_orders, month_revenue = month_query.first()

    # ---- 待处理订单数 ----
    pending_query = db.query(func.count(Order.id)).filter(
        Order.status.in_(['pending', 'paid']),
    )
    pending_query = store_filter(pending_query, Order)
    pending_orders = pending_query.scalar() or 0

    # ---- 库存预警 ----
    low_stock_query = db.query(InventoryItem).filter(
        InventoryItem.quantity <= InventoryItem.safety_stock,
        InventoryItem.is_active == True,
    )
    if store_id is not None:
        low_stock_query = low_stock_query.filter(InventoryItem.store_id == store_id)
    low_stock_items = low_stock_query.limit(10).all()
    low_stock_count = len(low_stock_items)

    # ---- 近7天趋势 ----
    daily_trend = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        day_start = datetime(d.year, d.month, d.day)
        day_end = day_start + timedelta(days=1)
        q = db.query(
            func.count(Order.id),
            func.coalesce(func.sum(Order.final_amount), 0),
        ).filter(
            Order.created_at >= day_start,
            Order.created_at < day_end,
            Order.status.in_(['paid', 'completed']),
        )
        if store_id is not None:
            q = q.filter(Order.store_id == store_id)
        cnt, rev = q.first()
        daily_trend.append({
            "date": d.strftime("%m-%d"),
            "order_count": cnt or 0,
            "revenue": float(rev or 0),
        })

    # ---- 热门商品 Top 5 ----
    product_q = db.query(
        OrderItem.product_id,
        func.count(OrderItem.id).label('cnt'),
        func.coalesce(func.sum(OrderItem.subtotal), 0).label('rev'),
    ).filter(
        OrderItem.item_type == 'product',
        OrderItem.product_id.isnot(None),
    ).group_by(OrderItem.product_id).order_by(text('cnt DESC')).limit(5)

    top_products = []
    for row in product_q.all():
        p = db.query(Product).filter(Product.id == row.product_id).first()
        top_products.append({
            "id": row.product_id,
            "name": p.name if p else "未知商品",
            "count": row.cnt,
            "revenue": float(row.rev),
        })

    # ---- 热门服务 Top 5 ----
    from models.service_model import Service
    service_q = db.query(
        OrderItem.service_id,
        func.count(OrderItem.id).label('cnt'),
        func.coalesce(func.sum(OrderItem.subtotal), 0).label('rev'),
    ).filter(
        OrderItem.item_type == 'service',
        OrderItem.service_id.isnot(None),
    ).group_by(OrderItem.service_id).order_by(text('cnt DESC')).limit(5)

    top_services = []
    for row in service_q.all():
        s = db.query(Service).filter(Service.id == row.service_id).first()
        top_services.append({
            "id": row.service_id,
            "name": s.name if s else "未知服务",
            "count": row.cnt,
            "revenue": float(row.rev),
        })

    # ---- 最近订单 ----
    recent_q = db.query(Order).order_by(Order.created_at.desc())
    recent_q = store_filter(recent_q, Order)
    recent_orders = []
    for o in recent_q.limit(10).all():
        recent_orders.append({
            "id": o.id,
            "order_no": o.order_no,
            "order_type": o.order_type,
            "final_amount": o.final_amount,
            "status": o.status,
            "customer_name": o.customer.name if o.customer else None,
            "created_at": o.created_at.strftime("%Y-%m-%d %H:%M") if o.created_at else "",
        })

    # ---- 库存预警列表 ----
    inventory_alerts = []
    for item in low_stock_items:
        inventory_alerts.append({
            "id": item.id,
            "name": item.name,
            "sku": item.sku or "",
            "quantity": item.quantity,
            "safety_stock": item.safety_stock,
            "unit": item.unit or "",
        })

    return {
        "today_revenue": float(today_revenue or 0),
        "today_orders": today_orders or 0,
        "month_revenue": float(month_revenue or 0),
        "month_orders": month_orders or 0,
        "pending_orders": pending_orders,
        "low_stock_count": low_stock_count,
        "daily_trend": daily_trend,
        "inventory_alerts": inventory_alerts,
        "top_products": top_products,
        "top_services": top_services,
        "recent_orders": recent_orders,
    }
