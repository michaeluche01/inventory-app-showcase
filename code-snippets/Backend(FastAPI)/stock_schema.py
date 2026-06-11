"""
Stock Transaction Schemas - ENTERPRISE SECURITY EDITION

T3-3: Added StockTransferRequest / StockTransferResponse for the
      POST /stock/transfer endpoint.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import re


class StockTransactionType(str, Enum):
    IN = "in"
    OUT = "out"
    ADJUST = "adjust"


# ===== STOCK IN =====

class StockInRequest(BaseModel):
    product_id: str = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0, le=100000, description="Units to add (max 100,000)")
    reason: Optional[str] = Field(None, max_length=500)

    @field_validator("product_id")
    def validate_product_id(cls, v):
        if not v or len(v) < 1:
            raise ValueError("Product ID cannot be empty")
        return v

    @field_validator("quantity")
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        if v > 100000:
            raise ValueError("Quantity cannot exceed 100,000 units")
        return v


# ===== STOCK OUT =====

class StockOutRequest(BaseModel):
    product_id: str = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0, le=100000, description="Units to remove (max 100,000)")
    reason: str = Field(..., min_length=5, max_length=500)

    @field_validator("product_id")
    def validate_product_id(cls, v):
        if not v or len(v) < 1:
            raise ValueError("Product ID cannot be empty")
        return v

    @field_validator("quantity")
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v

    @field_validator("reason")
    def validate_reason(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError("Reason must be at least 5 characters")
        vague_terms = ["test", "temp", "random", "asdf", "xxx", "123"]
        if v.lower() in vague_terms:
            raise ValueError(f"Reason '{v}' is too vague. Please be specific.")
        return v.strip()


# ===== STOCK ADJUST =====

class StockAdjustRequest(BaseModel):
    """
    Correct inventory discrepancies — ENTERPRISE SECURITY EDITION.

    Requires Manager/Owner role. Overwrites the absolute quantity.
    Triggers fraud-detection and approval workflow when thresholds are exceeded.
    """
    product_id: str = Field(..., description="Product ID")
    new_quantity: int = Field(..., ge=0, le=1000000)
    reason: str = Field(..., min_length=15, max_length=500)
    adjustment_type: Optional[str] = Field(
        None,
        description=(
            "physical_count | system_error | found_stock | "
            "damaged_goods | theft | other"
        ),
    )

    @field_validator("product_id")
    def validate_product_id(cls, v):
        if not v or len(v) < 1:
            raise ValueError("Product ID cannot be empty")
        return v

    @field_validator("new_quantity")
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError("Quantity cannot be negative")
        if v > 1000000:
            raise ValueError("Quantity cannot exceed 1,000,000 units")
        return v

    @field_validator("reason")
    def validate_reason(cls, v):
        if not v or len(v.strip()) < 15:
            raise ValueError(
                "Adjustment reason MUST be at least 15 characters (provide details!)"
            )
        vague_terms = [
            "idk", "unknown", "random", "test", "temp", "asdf", "xxx",
            "123", "add", "remove", "change", "fix", "adjust", "error",
            "mistake", "oops", "???", "help", "???",
        ]
        reason_lower = v.lower().strip()
        if reason_lower in vague_terms:
            raise ValueError(
                f"Reason '{v}' is too vague!\n"
                "Please provide SPECIFIC details:\n"
                "✅ 'Physical count audit: found 169 units on shelf not recorded'\n"
                "✅ 'System error: shipment PO-12345 arrived but not scanned'\n"
                "❌ 'Adjust' or 'Fix' or 'Error'"
            )
        required_keywords = [
            "physical", "found", "count", "audit", "shipment",
            "damage", "system", "error", "corrected",
        ]
        has_detail = any(kw in reason_lower for kw in required_keywords)
        if not has_detail and len(reason_lower) < 25:
            raise ValueError(
                "Reason lacks specific details. Include HOW/WHEN/WHY the "
                "quantity differs from what the system shows."
            )
        return v.strip()

    @field_validator("adjustment_type")
    def validate_adjustment_type(cls, v):
        if v is None:
            return v
        valid_types = [
            "physical_count", "system_error", "found_stock",
            "damaged_goods", "theft", "other",
        ]
        if v not in valid_types:
            raise ValueError(f"adjustment_type must be one of: {', '.join(valid_types)}")
        return v


# ===== T3-3: STOCK TRANSFER =====

class StockTransferRequest(BaseModel):
    """
    T3-3: Transfer stock between two branches.

    Both source and destination products must already exist in their
    respective branches and must share the same SKU.
    The Flutter app should look up the product IDs beforehand using
    GET /products?branch_id=<dest_branch_id> filtered by SKU.
    """
    source_product_id: str = Field(
        ...,
        description="Product ID in the source branch",
    )
    dest_product_id: str = Field(
        ...,
        description=(
            "Product ID in the destination branch "
            "(must have the same SKU as the source product)"
        ),
    )
    quantity: int = Field(
        ...,
        gt=0,
        le=100000,
        description="Number of units to transfer",
    )
    reason: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional reason / reference (e.g., 'Restock Lagos store')",
    )

    @field_validator("source_product_id", "dest_product_id")
    def validate_ids(cls, v):
        if not v or not v.strip():
            raise ValueError("Product ID cannot be empty")
        return v.strip()

    @field_validator("quantity")
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Transfer quantity must be greater than 0")
        return v


class StockTransferResponse(BaseModel):
    """T3-3: Response after a successful stock transfer."""
    transfer_id: str
    source_product_id: str
    dest_product_id: str
    quantity: int
    reason: Optional[str]
    out_transaction_id: str
    in_transaction_id: str
    created_at: datetime


# ===== RESPONSE SCHEMAS =====

class StockTransactionResponse(BaseModel):
    id: str
    business_id: str
    transaction_type: StockTransactionType
    product_id: str
    branch_id: str
    user_id: Optional[str]
    quantity: int
    previous_quantity: int
    new_quantity: int
    reason: Optional[str]
    created_at: datetime
    approval_required: Optional[bool] = False
    approval_status: Optional[str] = None

    class Config:
        from_attributes = True


class StockHistoryResponse(BaseModel):
    items: List[StockTransactionResponse]
    total: int
    skip: int
    limit: int


class StockAdjustmentPendingApprovalResponse(BaseModel):
    status: str
    message: str
    adjustment_id: str
    transaction_id: str
    business_id: str
    product_id: str
    previous_quantity: int
    new_quantity: int
    change_amount: int
    reason: str
    requires_approval: bool
    created_at: datetime
    approval_url: Optional[str] = None


# ===== BRANCH SCHEMAS =====

class BranchCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    location: Optional[str] = Field(None, max_length=500)


class BranchUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=500)


class BranchResponse(BaseModel):
    id: str
    name: str
    location: Optional[str]
    business_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== T3-1: CURRENT STOCK RESPONSE =====

class CurrentStockResponse(BaseModel):
    """T3-1: Live quantity for a single product."""
    product_id: str
    product_name: str
    sku: str
    branch_id: str
    current_quantity: int
    low_stock_threshold: int
    is_low_stock: bool
    calculated_at: datetime