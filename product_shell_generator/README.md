# Product Shell Generator

An automated product shell creation system I designed to accelerate POS onboarding workflows for rapidly changing cannabis inventory environments.

The cannabis retail industry introduces a constant stream of new products, strains, hardware variations, and limited releases. Because of this, new product shells must be created continuously in the POS and inventory system.

This project automates much of that process by transforming purchaser PO tracking data into structured product shell entries inside the POS platform.

---

# Overview

The workflow begins with purchaser-maintained PO tracking sheets containing incoming product information.

The system then:
1. Reads structured PO data from Google Sheets
2. Normalizes product information
3. Generates standardized naming structures
4. Automates POS form entry using Power Automate Desktop
5. Creates product shells directly in the inventory system

---

# Business Context

The retail environment this system was designed for contains:
- Over 20,000 total product SKUs historically created
- Roughly 2,000 active in-store SKUs at any given time
- Constant incoming product rotations
- Frequent vendor and strain changes
- Rapid inventory turnover

Manual shell creation at this scale was repetitive, time-consuming, and highly error-prone.

The objective of this system was to reduce onboarding friction while improving naming consistency and operational speed.

---

# Workflow Architecture

## 📥 Purchaser PO Tracking Input

Purchasers manually maintain incoming product information inside Google Sheets.

### Typical Data Includes
- Brand
- Product name
- Strain
- Weight
- Category
- Product type
- Vendor information
- Pricing details
- Special product descriptors

---

# 🧹 Product Normalization Layer

The system applies formatting and normalization logic to standardize product naming conventions.

### Example Formatting Goals
- Consistent weight formatting
- Brand normalization
- Strain formatting
- Category consistency
- Removal of duplicate naming patterns
- Standardized SKU naming structures

---

# ⚙️ POS Automation Workflow

Once the data is prepared, Power Automate Desktop performs automated form entry directly into the POS system.

### Automated Actions
- Navigation through POS interfaces
- Form population
- Field mapping
- Product shell submission
- Sequential product creation workflows

---

# 🏷️ Standardized Product Naming

The system generates structured naming formats designed to improve:
- Inventory consistency
- Searchability
- Reporting quality
- Online menu organization
- Downstream automation compatibility

### Example Output Structure

```text
Brand - Strain - Product Type - Weight - Special Attributes
```

---

# Key Features

## Dynamic Product Handling
Designed to accommodate:
- Constant product rotations
- New strain releases
- Limited drops
- Vendor naming inconsistencies
- Expanding SKU counts

---

# Error Reduction

The automation significantly reduced:
- Manual typing errors
- Naming inconsistencies
- Duplicate shell creation
- Missing metadata
- Category mismatches

---

# Operational Benefits

The system improved:
- Intake speed
- Inventory onboarding
- Data consistency
- POS organization
- Workflow scalability
- Product searchability

It also reduced repetitive administrative work for inventory and intake teams.

---

# Technologies Used

- Google Sheets
- Power Automate Desktop
- Spreadsheet formulas
- Browser automation
- POS workflow automation
- Data normalization systems

---

# Design Philosophy

This project focused heavily on operational scalability.

Rather than treating product shell creation as isolated manual entry tasks, the system approaches inventory onboarding as a repeatable data pipeline:
1. Structured input
2. Data normalization
3. Automated execution
4. Consistent output

The result is a lightweight automation system capable of supporting large-scale and constantly changing retail inventory environments.

---

# Example Repository Assets

This repository may include:
- Workflow screenshots
- Example PO tracker sheets
- Product normalization examples
- POS automation demonstrations
- Before/after workflow comparisons

---

# Notes

Portfolio versions of this project have been sanitized to remove:
- Proprietary product data
- Vendor-sensitive information
- Live operational credentials
- Internal pricing information
- Production POS access details