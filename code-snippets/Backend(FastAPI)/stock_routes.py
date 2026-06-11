"""
Stock Routes - ENTERPRISE SECURITY EDITION

T3-1: GET  /stock/current/{product_id}  — live calculated quantity for one product.
T3-3: POST /stock/transfer              — atomic inter-branch stock transfer.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import uuid

from app.database.connection import get_db
from app.schemas.stock_schema import (
    StockInRequest,
    StockOutRequest,
    StockAdjustRequest,
    StockTransactionResponse,
    StockHistoryResponse,
    StockAdjustmentPendingApprovalResponse,
    StockTransferRequest,       # T3-3
    StockTransferResponse,      # T3-3
    CurrentStockResponse,       # T3-1
)
from app.crud.stock_crud import stock_crud
from app.crud.product_crud import product_crud
from app.models import Branch
from app.models.product import Product
from app.utils.validators import validate_quantity, validate_pagination
from app.utils.security import get_current_user
from app.utils.exceptions import (
    BranchNotFoundException,
    ProductNotFoundException,
    InsufficientStockException,
)
from app.utils.logger import LoggerAdapter
from config import get_settings

log = LoggerAdapter(__name__)
settings = get_settings()
router = APIRouter(prefix="/stock", tags=["Stock Operations"])

LARGE_ADJUSTMENT_THRESHOLD = getattr(settings, "LARGE_ADJUSTMENT_THRESHOLD", 500)


# ─────────────────────────────────────────────
# Stock IN
# ─────────────────────────────────────────────

@router.post("/in", response_model=StockTransactionResponse, status_code=201)
def stock_in(
    branch_id: str,
    request: StockInRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Add stock (receive inventory).
    Allowed for: Staff, Manager, Owner.
    """
    branch = db.query(Branch).filter(
        and_(
            Branch.id == branch_id,
            Branch.business_id == current_user.business_id,
        )
    ).first()
    if not branch:
        raise BranchNotFoundException(branch_id)

    product = product_crud.get(db, request.product_id, current_user.business_id)
    if not product or product.branch_id != branch_id:
        raise ProductNotFoundException(request.product_id)

    validate_quantity(request.quantity, "Quantity")

    transaction = stock_crud.stock_in(
        db,
        product_id=request.product_id,
        branch_id=branch_id,
        business_id=current_user.business_id,
        user_id=current_user.user_id,
        quantity=request.quantity,
        reason=request.reason,
    )

    log.info(
        "Stock IN",
        product_id=request.product_id,
        qty=request.quantity,
        user=current_user.user_id,
        business=current_user.business_id,
    )
    return StockTransactionResponse.from_orm(transaction)


# ─────────────────────────────────────────────
# Stock OUT
# ─────────────────────────────────────────────

@router.post("/out", response_model=StockTransactionResponse, status_code=201)
def stock_out(
    branch_id: str,
    request: StockOutRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Remove stock (sale, damage, loss, etc.).
    Allowed for: Staff, Manager, Owner.
    """
    branch = db.query(Branch).filter(
        and_(
            Branch.id == branch_id,
            Branch.business_id == current_user.business_id,
        )
    ).first()
    if not branch:
        raise BranchNotFoundException(branch_id)

    product = product_crud.get(db, request.product_id, current_user.business_id)
    if not product or product.branch_id != branch_id:
        raise ProductNotFoundException(request.product_id)

    validate_quantity(request.quantity, "Quantity")
    if len(request.reason) < 5:
        raise HTTPException(status_code=400, detail="Reason must be at least 5 characters")

    transaction = stock_crud.stock_out(
        db,
        product_id=request.product_id,
        branch_id=branch_id,
        business_id=current_user.business_id,
        user_id=current_user.user_id,
        quantity=request.quantity,
        reason=request.reason,
    )

    log.info(
        "Stock OUT",
        product_id=request.product_id,
        qty=request.quantity,
        reason=request.reason,
        user=current_user.user_id,
    )
    return StockTransactionResponse.from_orm(transaction)


# ─────────────────────────────────────────────
# Stock ADJUST
# ─────────────────────────────────────────────

@router.post("/adjust", status_code=202)
def stock_adjust(
    branch_id: str,
    request: StockAdjustRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Adjust stock — ENTERPRISE SECURITY.
    Only for: Manager, Owner.
    Overwrites the entire quantity; triggers approval workflow for large changes.
    """
    if current_user.role not in ("manager", "owner"):
        log.warning(
            "UNAUTHORIZED ADJUST ATTEMPT",
            user_id=current_user.user_id,
            role=current_user.role,
            business_id=current_user.business_id,
            product_id=request.product_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "🔒 Only Managers and Owners can adjust inventory. "
                "This action is restricted for security."
            ),
        )

    branch = db.query(Branch).filter(
        and_(
            Branch.id == branch_id,
            Branch.business_id == current_user.business_id,
        )
    ).first()
    if not branch:
        raise BranchNotFoundException(branch_id)

    product = product_crud.get(db, request.product_id, current_user.business_id)
    if not product or product.branch_id != branch_id:
        raise ProductNotFoundException(request.product_id)

    if len(request.reason) < 15:
        raise HTTPException(
            status_code=400,
            detail=(
                "⚠️ Adjustment reason MUST be at least 15 characters! "
                "Please provide specific details about WHY."
            ),
        )

    transaction, metadata = stock_crud.stock_adjust(
        db,
        product_id=request.product_id,
        branch_id=branch_id,
        business_id=current_user.business_id,
        user_id=current_user.user_id,
        new_quantity=request.new_quantity,
        reason=request.reason,
    )

    if metadata["requires_approval"]:
        log.warning(
            "ADJUSTMENT PENDING APPROVAL",
            product_id=request.product_id,
            alert_level=metadata["alert_level"],
            suspicious_patterns=metadata["suspicious_patterns"],
            user_id=current_user.user_id,
            business_id=current_user.business_id,
        )
        return {
            "status": "pending_approval",
            "status_code": 202,
            "message": (
                f"⚠️ This adjustment requires management approval "
                f"(Alert Level: {metadata['alert_level'].upper()})"
            ),
            "transaction_id": transaction.id,
            "business_id": current_user.business_id,
            "product_id": request.product_id,
            "previous_quantity": transaction.previous_quantity,
            "new_quantity": transaction.new_quantity,
            "change_amount": metadata["fraud_score"],
            "reason": request.reason,
            "alert_level": metadata["alert_level"],
            "suspicious_patterns": metadata["suspicious_patterns"],
            "fraud_score": metadata["fraud_score"],
            "requires_approval": True,
            "created_at": transaction.created_at,
            "next_action": "Management will review this adjustment shortly",
        }

    log.info(
        "ADJUSTMENT APPROVED",
        transaction_id=transaction.id,
        product_id=request.product_id,
        adjustment=transaction.quantity,
        user_id=current_user.user_id,
        business_id=current_user.business_id,
    )
    return {
        "status": "approved",
        "status_code": 201,
        "message": "✅ Adjustment approved and recorded",
        "transaction": StockTransactionResponse.from_orm(transaction),
        "approval_status": "immediate",
    }


# ─────────────────────────────────────────────
# T3-1: Current quantity for a single product
# ─────────────────────────────────────────────

@router.get("/current/{product_id}", response_model=CurrentStockResponse)
def get_current_stock(
    product_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    T3-1: Return the live calculated quantity for a single product.

    Quantity is derived from the full transaction log (same algorithm as
    the dashboard bulk query) so it is always accurate, never stale.

    Use this endpoint from Flutter when you need the exact stock level
    for a product detail screen or before recording a stock-out.
    """
    product = product_crud.get(db, product_id, current_user.business_id)
    if not product:
        raise ProductNotFoundException(product_id)

    # Verify the product's branch belongs to this business (multi-tenancy)
    branch = db.query(Branch).filter(
        and_(
            Branch.id == product.branch_id,
            Branch.business_id == current_user.business_id,
        )
    ).first()
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this product",
        )

    current_quantity = stock_crud._calculate_quantity(
        db, product_id=product_id, business_id=current_user.business_id
    )

    log.info(
        "Current stock retrieved",
        product_id=product_id,
        quantity=current_quantity,
        user_id=current_user.user_id,
        business_id=current_user.business_id,
    )

    return CurrentStockResponse(
        product_id=product.id,
        product_name=product.name,
        sku=product.sku,
        branch_id=product.branch_id,
        current_quantity=current_quantity,
        low_stock_threshold=product.low_stock_threshold,
        is_low_stock=current_quantity <= product.low_stock_threshold,
        calculated_at=datetime.utcnow(),
    )


# ─────────────────────────────────────────────
# T3-3: Inter-branch stock transfer
# ─────────────────────────────────────────────

@router.post("/transfer", response_model=StockTransferResponse, status_code=201)
def transfer_stock(
    request: StockTransferRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    T3-3: Transfer stock between two branches.

    Atomically records a stock_out on the source product and a stock_in on
    the destination product in the same DB transaction.

    Rules:
    - Both products must belong to the authenticated user's business.
    - Source and destination must be in different branches.
    - Both products must share the same SKU.
    - Source must have sufficient stock.

    Allowed for: Manager, Owner (staff cannot transfer stock).

    The transfer_id links the two transactions so they can be traced
    in the stock history of both branches.
    """
    if current_user.role not in ("manager", "owner", "super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="🔒 Only Managers and Owners can transfer stock between branches.",
        )

    try:
        out_txn, in_txn, transfer_id = stock_crud.stock_transfer(
            db,
            source_product_id=request.source_product_id,
            dest_product_id=request.dest_product_id,
            business_id=current_user.business_id,
            user_id=current_user.user_id,
            quantity=request.quantity,
            reason=request.reason,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except InsufficientStockException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        )

    log.info(
        "Stock transfer endpoint completed",
        transfer_id=transfer_id,
        source=request.source_product_id,
        dest=request.dest_product_id,
        qty=request.quantity,
        user=current_user.user_id,
    )

    return StockTransferResponse(
        transfer_id=transfer_id,
        source_product_id=request.source_product_id,
        dest_product_id=request.dest_product_id,
        quantity=request.quantity,
        reason=request.reason,
        out_transaction_id=out_txn.id,
        in_transaction_id=in_txn.id,
        created_at=out_txn.created_at,
    )


# ─────────────────────────────────────────────
# History endpoints (unchanged)
# ─────────────────────────────────────────────

@router.get("/history/{product_id}", response_model=StockHistoryResponse)
def get_product_history(
    product_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get stock transaction history for a product."""
    product = product_crud.get(db, product_id, current_user.business_id)
    if not product:
        raise ProductNotFoundException(product_id)

    branch = db.query(Branch).filter(
        and_(
            Branch.id == product.branch_id,
            Branch.business_id == current_user.business_id,
        )
    ).first()
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this product",
        )

    skip, limit = validate_pagination(skip, limit)
    transactions, total = stock_crud.get_by_product(
        db, product_id, current_user.business_id, skip, limit
    )

    return StockHistoryResponse(
        items=[StockTransactionResponse.from_orm(t) for t in transactions],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/history/branch/{branch_id}", response_model=StockHistoryResponse)
def get_branch_history(
    branch_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all stock transactions in a branch."""
    branch = db.query(Branch).filter(
        and_(
            Branch.id == branch_id,
            Branch.business_id == current_user.business_id,
        )
    ).first()
    if not branch:
        raise BranchNotFoundException(branch_id)

    skip, limit = validate_pagination(skip, limit)
    transactions, total = stock_crud.get_by_branch(
        db, branch_id, current_user.business_id, skip, limit
    )

    return StockHistoryResponse(
        items=[StockTransactionResponse.from_orm(t) for t in transactions],
        total=total,
        skip=skip,
        limit=limit,
    )