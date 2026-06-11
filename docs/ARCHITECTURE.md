# Architecture — THROVE

> Technical architecture, key decisions, data flow, and engineering rationale.

---

## Overview

THROVE is a Flutter mobile application following **Clean Architecture** principles with a **BLoC** state management pattern. The architecture is designed for three real-world constraints:

1. **Offline-first** — businesses in Lagos, Kano, and Accra can't rely on stable connectivity
2. **Multi-location** — a single account may manage 2–10 branches with separate inventory states
3. **AI integration** — demand forecasting runs server-side but results must be readable offline

---

## Folder Structure

```
lib/
├── core/
│   ├── errors/           # Failure types, exceptions
│   ├── network/          # API client, interceptors
│   ├── utils/            # Date helpers, currency formatters
│   └── di/               # Dependency injection (get_it)
│
├── features/
│   ├── dashboard/
│   │   ├── data/         # Models, data sources, repository impl
│   │   ├── domain/       # Entities, use cases, repository interface
│   │   └── presentation/ # BLoC, screens, widgets
│   │
│   ├── inventory/
│   ├── transactions/
│   ├── analytics/
│   ├── alerts/
│   ├── forecast/
│   └── auth/
│
└── main.dart
```

Each feature module is **fully self-contained** — its own data, domain, and presentation layers. Features communicate only through shared domain entities, never directly between presentation layers.

---

## Layer Breakdown

### Presentation Layer
- **Framework:** Flutter widgets + BLoC
- **Responsibility:** UI rendering, user input handling, BLoC event dispatching
- **Rule:** Zero business logic. Widgets only respond to state; they do not decide anything.

### Domain Layer
- **Pure Dart** — zero Flutter dependencies, fully unit-testable
- **Entities:** Core business objects (`Product`, `Transaction`, `StockAlert`, `ForecastResult`)
- **Use Cases:** Single-responsibility classes (`GetActiveAlerts`, `RecordStockTransaction`, `GetDemandForecast`)
- **Repository Interfaces:** Contracts the data layer must fulfil

### Data Layer
- **Remote Data Source:** REST API calls via `Dio`, response-to-model mapping
- **Local Data Source:** Hive (fast key-value for cache) + SQLite (structured transaction history)
- **Repository Implementation:** Tries remote first, falls back to local cache on `NetworkException`

---

## State Management — BLoC

BLoC was chosen over Provider or Riverpod because THROVE's state transitions are **complex and traceable**:

- A Stock In transaction must update inventory, trigger/clear alerts, update dashboard metrics, and append to transaction history — all atomically from the UI's perspective
- BLoC's explicit event → state mapping makes this predictable and debuggable

```
User Action
    │
    ▼
BLoC Event (e.g. RecordStockIn)
    │
    ▼
Use Case (RecordStockTransaction)
    │
    ▼
Repository → Remote + Local update
    │
    ▼
New BLoC State (TransactionRecorded)
    │
    ▼
UI reacts to new state
```

---

## Data Flow — Recording a Stock Transaction

```
User taps "Confirm" on Stock In screen
    │
    ▼
TransactionBloc.add(ConfirmStockIn(productId, qty, reference))
    │
    ▼
RecordStockTransaction use case validates inputs
    │
    ▼
InventoryRepository.updateStockLevel(productId, transaction)
    │
    ├── Remote: POST /transactions → updates server stock level
    └── Local: SQLite insert → appends to local transaction history
                │
                ▼
            Hive cache invalidated for affected product
    │
    ▼
AlertRepository.refreshAlerts(locationId)  ← re-evaluate alerts
    │
    ▼
Emit TransactionSuccess state
    │
    ▼
UI: show green checkmark + toast "Stock updated! You now have 95 units."
    │
    ▼
Navigator pops back to inventory list (refreshed)
```

---

## Offline Strategy

THROVE targets markets where 4G connectivity is inconsistent. Every read operation follows a cache-first strategy:

```
Request data
    │
    ├── Check local cache (Hive)
    │   ├── Cache fresh (< 5 min)? → Return cached data immediately
    │   └── Cache stale? → Fetch from API, update cache, return fresh data
    │
    └── API request fails (NetworkException)?
        └── Return stale cache with "Offline — last synced X ago" indicator
```

Write operations (stock updates) are queued locally when offline and synced when connection is restored. Conflict resolution strategy: **last-write-wins**, with timestamp comparison.

*(Offline write queue is a Phase 2 feature — Phase 1 requires connectivity for writes)*

---

## AI Forecasting Integration

The demand forecasting engine runs server-side (Python / scikit-learn), not on-device. The mobile app is a consumer of forecast results.

```
Server (nightly job)
    │
    ▼
Pull last 90 days of transaction history per location
    │
    ▼
Apply seasonal factors (Nigeria/Africa holiday calendar)
    │
    ▼
Generate 30/60/90-day predictions per product
    │
    ▼
Store results in forecast table with confidence scores
    │
    ▼
Mobile app fetches via GET /forecast?locationId=&period=30
    │
    ▼
Cached locally for 4-hour TTL
```

---

## Security Model

| Concern | Implementation |
|---|---|
| Authentication | JWT tokens with 24h expiry, refresh token flow |
| Biometric auth | Flutter `local_auth` package — device-level (no biometric data sent to server) |
| API communication | HTTPS only, certificate pinning |
| Role enforcement | Server-side RBAC — client role is UI-only, never trusted for permissions |
| Sensitive data | No inventory data stored in plaintext on device; Hive encryption enabled |

---

## Key Dependencies

| Package | Purpose |
|---|---|
| `flutter_bloc` | State management |
| `dio` | HTTP client with interceptors |
| `hive_flutter` | Fast local key-value cache |
| `sqflite` | SQLite for transaction history |
| `get_it` | Dependency injection |
| `freezed` | Immutable state classes + union types |
| `local_auth` | Biometric login |
| `fl_chart` | Analytics charts |
| `lottie` | Success/error animations |
| `flutter_barcode_scanner` | Barcode scanning (Phase 2) |

---

## Testing Strategy

| Layer | Approach |
|---|---|
| Domain (Use Cases) | Pure unit tests — no mocks needed |
| Repository | Unit tests with mocked data sources |
| BLoC | `bloc_test` package — test event → state sequences |
| Widgets | Widget tests for critical UI (dashboard, stock form) |
| Integration | End-to-end tests for core flows (Stock In, Stock Out) |

Target: **80% coverage** on domain and BLoC layers before beta launch.