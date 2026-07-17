<div align="center">
  <img src="https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" />

  <br />
  <br />

  <h1 style="color: #2EAD33;">🧪 Akdemia Enterprise E2E Test Suite</h1>
  <p><b>Automated Role-Based Access Control & Payment Flow Validations</b></p>
</div>

---

## 🎯 Overview

This is an **Enterprise-grade End-to-End (E2E) testing framework** built with Python and Playwright. It was designed to automatically test and validate the **Akdemia** school management platform (used by 60+ schools in LATAM).

Testing a SaaS platform with complex Role-Based Access Control (RBAC) requires rigorous automation to ensure that different user types (Parents, Teachers, Admins, Financial Staff) cannot access unauthorized endpoints. 

This framework dynamically crawls, tests, and validates access rules across the entire ecosystem.

## ⚙️ Architecture

- **Engine:** Python + Playwright (Async API)
- **Framework:** `pytest`
- **Authentication Handling:** Handles Devise-based authentication and token injection.
- **RBAC Matrix Validation:** Automatically maps roles to permitted URLs and validates 401/403 responses for unauthorized attempts.
- **Payment Lifecycle Validation:** Tests the entire billing flow: invoice generation, payment registration (vouchers), and administrative approval logic.

## 🚀 Key Modules

- `test_dynamic_roles.py`: Crawls over 30+ endpoints per role to ensure permissions matrix matches the security spec.
- `test_complete_payment_cycle.py`: Simulates a parent logging in, finding a pending debt, attaching a mock payment voucher, and an admin approving it.
- `find_debt_robust.py`: Intelligent crawler that searches for test accounts with specific types of pending debts for isolated testing.
- `audit_school_comprehensive.py`: Full platform audit generation for specific tenants (schools).

## 🔒 Security & Data
All tests are configured to run against isolated staging/testing instances (`omega` and `edge` environments). **No real user data is exposed in this repository.** All data dumps and evidence screenshots have been excluded from the public release.

## 📜 License
MIT License.

