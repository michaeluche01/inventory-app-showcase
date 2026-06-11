<div align="center">

<img src="https://img.shields.io/badge/Status-In%20Development-blue?style=for-the-badge" />
<img src="https://img.shields.io/badge/Platform-iOS%20%7C%20Android-lightgrey?style=for-the-badge&logo=flutter" />
<img src="https://img.shields.io/badge/Built%20With-Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white" />
<img src="https://img.shields.io/badge/AI--Powered-Demand%20Forecasting-8B5CF6?style=for-the-badge" />
<img src="https://img.shields.io/badge/Market-Africa--First-F59E0B?style=for-the-badge" />

<br/><br/>

# 📦 THROVE
### *Your Business Thrives When Inventory Works*

**A mobile-first, AI-powered inventory management system built for African SMEs.**  
Real-time stock tracking · AI demand forecasting · Multi-location management · Automated alerts

<br/>

> 🚧 **This repository is a live build showcase** — documenting the full product journey from PRD to production: product thinking, UI/UX design, architecture decisions, and clean Flutter code.

</div>

---

## 📸 App Preview

> ⬆️ *Screenshots and demo GIFs coming soon — designs in progress*

| Onboarding | Dashboard | Stock In/Out |
|:---:|:---:|:---:|
| `screenshot coming soon` | `screenshot coming soon` | `screenshot coming soon` |

| Inventory List | AI Forecast | Alerts |
|:---:|:---:|:---:|
| `screenshot coming soon` | `screenshot coming soon` | `screenshot coming soon` |

---

## 🎯 The Problem

Most inventory tools built for African businesses fall into one of two traps:

- **Too complex** — Enterprise systems like SAP/Oracle are built for Fortune 500 companies, not a supermarket owner in Lekki managing 3 branches and 500 SKUs
- **Too basic** — Spreadsheets break down fast. No alerts, no forecasting, no audit trail

The result? Business owners either overspend on stock they can't sell, or lose customers to stockouts they never saw coming.

**THROVE sits in the gap:** smart enough to be useful, simple enough for a store manager with medium tech comfort.

---

## 💡 The Solution

A mobile-first app that gives small and medium businesses the kind of inventory intelligence previously only available to large enterprises — at a price point that makes sense for African SMEs ($50–500/month vs competitors at $5,000+).

### What makes THROVE different

| Feature | Traditional Tools | THROVE |
|---|---|---|
| AI forecasting | Generic predictions | Learns from *your* store's data |
| Market context | Global defaults | Nigeria/Africa holidays & seasons built-in |
| Platform | Desktop-first | Mobile-first, offline-capable |
| Price | $5,000+/month | $50–500/month |
| Setup | Months | Minutes |

---

## 👥 Who It's Built For

THROVE was designed around three real user archetypes:

<details>
<summary><strong>Grace — Store Owner (35–50)</strong></summary>

Owns a supermarket in Lagos. Medium tech comfort (WhatsApp, Instagram). Needs to see business health at a glance without learning complex software. Her biggest fears: stockouts that lose customers, and hours wasted on manual inventory.

**Core need:** Quick visibility + smart order prompts.

</details>

<details>
<summary><strong>James — Store Manager (25–35)</strong></summary>

Manages multiple branches. High tech comfort. Drowning in reconciliation work and blind to real-time stock movement across locations.

**Core need:** Real-time multi-location visibility + automated reporting.

</details>

<details>
<summary><strong>Amara — Warehouse Staff (20–30)</strong></summary>

On the floor counting stock. Tedious manual counting, no immediate feedback, pressure to be accurate.

**Core need:** Fast, mobile-friendly data entry with instant confirmation.

</details>

---

## ✨ Core Features (v1.0)

### 📊 Real-Time Inventory Tracking
- Live stock levels across all locations with color-coded status (healthy / warning / critical)
- Search, filter, and category organisation
- Last-updated timestamps per product

### 🔄 Stock Transactions
- **Stock In** — purchases, returns, adjustments
- **Stock Out** — sales, damage, losses
- Full audit trail with reference numbers (PO #, Invoice #)
- Undo last transaction within a time window

### 🤖 AI Demand Forecasting
- Predicts demand for next 30 / 60 / 90 days with confidence levels
- Identifies Nigeria/Africa seasonal patterns (Easter, Ramadan, Harmattan)
- Flags fast-moving vs slow-moving items
- Recommends replenishment quantities and reorder dates

### 🔔 Automated Alerts
- Low stock warnings, out-of-stock alerts, expiry date notifications
- Push, SMS, and email delivery options
- Critical stock red alerts with estimated revenue impact

### 📈 Analytics & Reporting
- Inventory value tracking (NGN + multi-currency)
- Stock turnover rate, days inventory outstanding
- Top 10 fast-movers, slow-mover analysis
- Export to PDF, CSV, Excel

### 🏢 Multi-Location Management
- Manage multiple branches / warehouses from one account
- Switch locations seamlessly
- Location-level analytics and comparisons

### 🔐 User Roles & Security
- Role-based access: Owner / Manager / Staff
- Biometric login (Face ID / Fingerprint)
- Activity logging and session management

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    THROVE MOBILE APP                     │
│                     (Flutter 3.x)                        │
├────────────────────┬────────────────────────────────────┤
│   Presentation     │  Feature Modules                   │
│   Layer            │  ─ Dashboard                       │
│   (BLoC / Riverpod)│  ─ Inventory                       │
│                    │  ─ Transactions                     │
│                    │  ─ Analytics                        │
│                    │  ─ Alerts                           │
├────────────────────┴────────────────────────────────────┤
│                   Domain Layer                           │
│         Entities · Use Cases · Repository Interfaces    │
├─────────────────────────────────────────────────────────┤
│                   Data Layer                             │
│    Remote (REST API)  │  Local (PostgreSQL / Hive cache)    │
└──────────────────────────────────────────────────────────┘
                          │
              ┌───────────┴────────────┐
              │     THROVE BACKEND     │
              │   Python / FastAPI   │
              │  AI Forecasting Engine │
              └────────────────────────┘
```

**Key architectural decisions:**
- **BLoC pattern** for state management — predictable state changes, testable business logic
- **Clean Architecture** — strict separation of concerns between presentation, domain, and data layers
- **Offline-first** — local SQLite cache with sync-on-connect (Phase 2)
- **Feature-first folder structure** — each feature is self-contained and independently testable

📄 See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full technical breakdown.

---

## 🎨 Design System

The THROVE design language is built around **trust, clarity, and urgency** — the three things a store owner needs when making a stock decision under pressure.

| Token | Value | Usage |
|---|---|---|
| `primary-blue` | `#0066CC` | Main actions, navigation, trust signals |
| `success-green` | `#10B981` | Stock In, confirmations, healthy status |
| `warning-orange` | `#F59E0B` | Low stock, attention needed |
| `critical-red` | `#EF4444` | Out of stock, urgent alerts |
| `dark-text` | `#1F2937` | Primary readable text |
| `bg-light` | `#F9FAFB` | Clean, minimal background |

- **Typography:** SF Pro (iOS) / Roboto (Android) — 12px minimum, 1.5 line-height for readability
- **Touch targets:** Minimum 48×48px — no mis-taps for warehouse staff
- **Contrast ratio:** 4.5:1 for all body text (WCAG AA compliant)
- **Animations:** 300ms fade/slide transitions, Lottie success confirmations, skeleton loading screens

📄 See [`docs/DESIGN_SYSTEM.md`](docs/THROVE_DESIGN_SYSTEM.md) for the full design language.  
🎨 

---

## 🧩 Code Highlights

Three snippets that show how the core logic is structured:

### 1. Stock Alert Service — calculating urgency levels
```dart
// code-snippets/stock_alert_service.dart

enum AlertLevel { healthy, warning, critical, outOfStock }

class StockAlertService {
  /// Returns the alert level for a product based on current quantity
  /// vs its configured minimum threshold.
  AlertLevel getAlertLevel(Product product) {
    if (product.currentQuantity <= 0) return AlertLevel.outOfStock;
    if (product.currentQuantity <= product.criticalThreshold) return AlertLevel.critical;
    if (product.currentQuantity <= product.lowStockThreshold) return AlertLevel.warning;
    return AlertLevel.healthy;
  }

  /// Estimates days until a product runs out based on average daily sales.
  int? estimateDaysUntilStockout(Product product) {
    if (product.averageDailySales <= 0) return null;
    return (product.currentQuantity / product.averageDailySales).floor();
  }

  /// Returns all products that need immediate attention, sorted by urgency.
  List<AlertItem> getActiveAlerts(List<Product> products) {
    return products
        .where((p) => getAlertLevel(p) != AlertLevel.healthy)
        .map((p) => AlertItem(
              product: p,
              level: getAlertLevel(p),
              daysUntilStockout: estimateDaysUntilStockout(p),
            ))
        .toList()
      ..sort((a, b) => a.level.index.compareTo(b.level.index));
  }
}
```

### 2. Inventory Repository — clean data contract
```dart
// code-snippets/inventory_repository.dart

abstract class InventoryRepository {
  Future<List<Product>> getProducts({String? locationId, String? category});
  Future<Product> getProductById(String id);
  Future<void> createProduct(CreateProductInput input);
  Future<void> updateStockLevel(String productId, StockTransaction transaction);
  Stream<List<AlertItem>> watchActiveAlerts(String locationId);
}

class InventoryRepositoryImpl implements InventoryRepository {
  final InventoryRemoteDataSource _remote;
  final InventoryLocalDataSource _local;

  const InventoryRepositoryImpl({
    required InventoryRemoteDataSource remote,
    required InventoryLocalDataSource local,
  })  : _remote = remote,
        _local = local;

  @override
  Future<List<Product>> getProducts({String? locationId, String? category}) async {
    try {
      // Try remote first, fall back to local cache on failure
      final products = await _remote.fetchProducts(
        locationId: locationId,
        category: category,
      );
      await _local.cacheProducts(products); // Keep cache fresh
      return products;
    } on NetworkException {
      return _local.getCachedProducts(locationId: locationId);
    }
  }

  @override
  Stream<List<AlertItem>> watchActiveAlerts(String locationId) {
    // Real-time stream — updates UI whenever stock levels change
    return _remote
        .watchProducts(locationId: locationId)
        .map((products) => StockAlertService().getActiveAlerts(products));
  }
}
```

### 3. Dashboard BLoC — state management
```dart
// code-snippets/dashboard_bloc.dart

// Events
abstract class DashboardEvent {}
class LoadDashboard extends DashboardEvent { final String locationId; }
class RefreshDashboard extends DashboardEvent {}

// States
abstract class DashboardState {}
class DashboardLoading extends DashboardState {}
class DashboardLoaded extends DashboardState {
  final DashboardMetrics metrics;
  final List<AlertItem> alerts;
  final List<Transaction> recentTransactions;
}
class DashboardError extends DashboardState { final String message; }

// BLoC
class DashboardBloc extends Bloc<DashboardEvent, DashboardState> {
  final InventoryRepository _inventoryRepo;
  final TransactionRepository _transactionRepo;

  DashboardBloc({
    required InventoryRepository inventoryRepo,
    required TransactionRepository transactionRepo,
  })  : _inventoryRepo = inventoryRepo,
        _transactionRepo = transactionRepo,
        super(DashboardLoading()) {
    on<LoadDashboard>(_onLoadDashboard);
    on<RefreshDashboard>(_onRefreshDashboard);
  }

  Future<void> _onLoadDashboard(
    LoadDashboard event,
    Emitter<DashboardState> emit,
  ) async {
    emit(DashboardLoading());
    try {
      final results = await Future.wait([
        _inventoryRepo.getDashboardMetrics(event.locationId),
        _inventoryRepo.getActiveAlerts(event.locationId),
        _transactionRepo.getRecent(locationId: event.locationId, limit: 6),
      ]);
      emit(DashboardLoaded(
        metrics: results[0] as DashboardMetrics,
        alerts: results[1] as List<AlertItem>,
        recentTransactions: results[2] as List<Transaction>,
      ));
    } catch (e) {
      emit(DashboardError(message: 'Could not load dashboard. Pull to refresh.'));
    }
  }
}
```

📁 Full snippet files are in [`/code-snippets`](code-snippets/).

---

## 🗺️ Build Roadmap

```
Phase 1 — Design & Core (Now)
├── ✅ Product requirements document (PRD)
├── 🔄 Figma UI/UX design (12 core screens)
├── 🔄 Design system & component library
└── 🔄 Flutter project scaffold & architecture

Phase 2 — MVP (Q3 2026)
├── ⬜ Core inventory CRUD
├── ⬜ Stock In / Stock Out transactions
├── ⬜ Real-time alerts
├── ⬜ Basic analytics dashboard
└── ⬜ Multi-location support

Phase 3 — AI & Scale (Q4 2026)
├── ⬜ AI demand forecasting engine
├── ⬜ Seasonal pattern detection (Africa-first)
├── ⬜ Barcode scanning
├── ⬜ Offline mode + sync
└── ⬜ Beta launch (1,000 users)

Phase 4 — Launch (Q1 2027)
├── ⬜ App Store & Play Store release
├── ⬜ POS integration
└── ⬜ E-commerce platform sync
```

---

## 📁 Repository Structure

```
inventory-app-showcase/
├── README.md                   ← You are here
├── docs/
│   ├── PRD.md                  ← Full product requirements document
│   ├── ARCHITECTURE.md         ← Technical architecture decisions
│   └── DESIGN_SYSTEM.md        ← Design tokens, components, guidelines
├── screenshots/
│   └── (app screenshots — uploading soon)
└── code-snippets/
    ├── stock_alert_service.dart
    ├── inventory_repository.dart
    └── dashboard_bloc.dart
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Mobile | Flutter 3.x (Dart) |
| State Management | BLoC / Riverpod |
| Local Storage | Hive + SQLite |
| Backend | Node.js + Firebase |
| AI/ML | Python (demand forecasting engine) |
| Design | Figma |
| CI/CD | GitHub Actions |

---

## 📄 Full Documentation

| Document | Description |
|---|---|
| [`docs/PRD.md`](docs/PRD.md) | Full product requirements — vision, personas, features, screen specs |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Technical architecture, data flow, key decisions |
| [`docs/DESIGN_SYSTEM.md`](docs/DESIGN_SYSTEM.md) | Design tokens, component specs, accessibility guidelines |

---

## 👤 About

**Built by Michael Chiedozie** — a product-minded developer passionate about building tools for African businesses.

- 🌍 Lagos, Nigeria
- 💼 [Portfolio](#) `coming soon`
- 🐦 [Twitter/X](#)
- 💼 [LinkedIn](#)

---

<div align="center">

*THROVE is actively being built. Follow this repo to track progress.*

⭐ **Star this repo** if the project interests you

</div>