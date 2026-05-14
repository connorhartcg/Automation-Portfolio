# Inventory Guidance & Restock Intelligence System

A spreadsheet-driven inventory intelligence system I designed to transform raw POS exports into actionable restock guidance for retail inventory operations.

This project combines automated data ingestion, normalization, consolidation logic, and highly customized inventory threshold rules to generate dynamic low-stock reporting across multiple product categories.

The goal of this system was to reduce manual inventory review time while improving purchasing visibility and restock decision-making.

---

# Overview

The workflow transforms:

1. Raw inventory exports  
2. Consolidated and normalized inventory data  
3. Dynamic restock guidance sheets  

The system was designed around real-world retail inventory behavior, where different product categories, brands, and package types require different stocking strategies.

---

# Workflow

## 📥 Step 1 — Raw Inventory Export

The process begins with a live inventory CSV export pulled from the POS system.

### Raw Data Includes
- Product names
- Categories
- Brands
- Quantities
- SKU data
- Vendor information
- Product types
- Package formats

### Automation
The inventory export process was automated using:
- Power Automate Desktop
- Browser automation
- CSV ingestion workflows

---

# 🧹 Step 2 — Consolidated Inventory Layer

The raw inventory data is transformed into a structured consolidated dataset.

### Consolidation Tasks
- Data cleanup
- Category normalization
- Product type normalization
- Vendor formatting
- Derived product metadata
- Inventory calculations
- Query-ready formatting

This layer acts as the operational backend for all downstream reporting and inventory guidance logic.

---

# 📊 Step 3 — Dynamic Restock Guidance

The final output is a dynamically generated restock sheet powered almost entirely through advanced Google Sheets QUERY logic.

The system evaluates inventory levels differently depending on:
- Product category
- Brand
- Product format
- Package size
- Vendor-specific sales behavior

---

# Example Business Logic

The guidance system uses custom inventory thresholds such as:

### Flower
- 3.5g products restock below 12 units
- Larger flower formats restock below 8 units

### Cartridges
Different brands and hardware types use entirely different thresholds:
- STIIIZY
- Coldfire
- Turn
- Boutiq
- All-in-one devices
- Standard cartridges

### Prerolls
- Multi-packs use different logic than singles
- Brand-specific thresholds applied

### Merchandise
- Puffco devices monitored separately
- Different thresholds for premium hardware

### Additional Categories
- Edibles
- Beverages
- Extracts
- Topicals
- Pills

Each category contains custom operational logic designed around actual sales behavior and purchasing patterns.

---

# Advanced QUERY System

One of the core components of this project is a highly customized Google Sheets QUERY formula that dynamically generates actionable inventory guidance from consolidated inventory data.

The formula performs:
- Conditional category filtering
- Brand-specific threshold evaluation
- Multi-condition logical grouping
- Product-type differentiation
- Automated sorting and prioritization

### Core Capabilities
- Nested conditional logic
- Dynamic filtering
- Brand-aware inventory thresholds
- Package-type interpretation
- Real-time restock guidance generation

---

# Technical Highlights

## Key Technical Concepts
- Spreadsheet engineering
- Advanced QUERY architecture
- Workflow automation
- Data normalization
- Operational reporting systems
- Inventory intelligence logic
- Conditional filtering systems
- Retail operations tooling

---

# Technologies Used

- Google Sheets
- QUERY formulas
- Array formulas
- Power Automate Desktop
- CSV processing workflows
- Browser automation
- Spreadsheet-based reporting systems

---

# Design Philosophy

Rather than building a generic low-stock alert system, this project was designed around the reality that different products move at different speeds and require different operational thresholds.

The objective was to create:
- Actionable reporting instead of raw data
- Smarter purchasing visibility
- Faster inventory review workflows
- Reduced manual analysis
- Operationally-aware inventory guidance

---

# Example Workflow Screenshots

This repository includes screenshots demonstrating:
- Raw inventory exports
- Consolidated data transformations
- Dynamic restock guidance outputs
- Query-driven inventory filtering systems

---

# Notes

Portfolio versions of this project have been sanitized to remove:
- Proprietary business information
- Internal vendor data
- Live inventory figures
- Sensitive operational details

# Additional Operational Features

Beyond restock guidance, the system also functions as a centralized inventory operations dashboard used for day-to-day sales floor management.

---

# 🛒 Sales Floor Guidance System

The spreadsheet dynamically tracks which products are currently placed on the sales floor and which products are still available in backstock.

### Features
- “Not On Floor” product guidance
- Available replacement product suggestions
- Dynamic floor inventory visibility
- Category-aware replacement filtering
- Automated quantity lookups

This allows staff to quickly identify products that:
- are available for display
- are low on the floor
- need replacement
- are not yet represented on the sales floor

---

# ⚡ Priority Processing Guidance

The system also includes operational guidance for intake and processing prioritization.

### Workflow Support
- Highlights products requiring immediate attention
- Surfaces inventory gaps
- Assists with rapid restocking decisions
- Helps prioritize incoming product processing

This reduced the need for manually reviewing large inventory exports during busy intake periods.

---

# 📆 Oldest Product Tracking

The dashboard includes views designed to surface older inventory requiring prioritization.

### Purpose
- Improve inventory turnover
- Reduce aging product buildup
- Assist with promotional planning
- Improve operational visibility

This allowed inventory teams to make more informed decisions around:
- promotions
- sales prioritization
- shelf placement
- vendor management

---

# 🗂️ Visual Drawer Management Interface

One of the most operationally-focused components of the project is a visual spreadsheet-based GUI used to manage 94 physical product drawers on the sales floor.

The interface acts as a lightweight inventory management layer directly inside Google Sheets.

---

# Drawer Dashboard Features

Each drawer visually displays:
- Current product
- Product category
- Inventory quantity
- Stock status
- Threshold-based highlighting

### Visual Indicators
Drawers automatically change color depending on inventory levels and operational thresholds, allowing staff to quickly identify:
- Low stock
- Healthy inventory
- Empty drawers
- Priority restock areas

---

# 🔄 Dynamic Product Replacement System

The drawer management system also allows staff to dynamically replace drawer inventory directly from the spreadsheet interface.

### Replacement Workflow

Each drawer contains selectable dropdown options such as:
- Manual Change
- Indica Options
- Hybrid Options
- Sativa Options

When a category is selected:
1. The sheet dynamically filters all products not already on the sales floor
2. Available replacement products are displayed
3. Selecting a product automatically updates the drawer assignment
4. Associated inventory quantities populate dynamically
5. The visual dashboard updates immediately

---

# Intelligent Product Availability Logic

The replacement system prevents duplicate floor assignments by only displaying:
- available inventory
- products not already assigned to active drawers

This created a streamlined workflow for:
- rotating inventory
- replacing sold-through products
- updating sales floor layouts
- maintaining category balance across drawers

---

# Operational Impact

This system significantly improved:
- sales floor visibility
- inventory rotation workflows
- restock efficiency
- intake prioritization
- operational awareness
- drawer management speed

The project evolved beyond a reporting sheet into a lightweight operational inventory management platform built entirely within Google Sheets and automation tooling.