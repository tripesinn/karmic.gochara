---
name: karmic-gochara-agent
description: A specialized agent for the karmic.gochara application, assisting with development, testing, and deployment across web and mobile platforms. Use when working on new features, bug fixes, or maintenance tasks related to karmic.gochara.
---

# Karmic Gochara Agent

## Overview

This skill enables specialized assistance for the karmic.gochara application, providing deep knowledge of its codebase, conventions, and workflows. It can help with various tasks, including feature development, bug fixing, testing, and deployment procedures for both web and Android platforms.

## Core Capabilities

This agent provides expertise in the following areas:

### 1. Feature Development
Assistance with implementing new features, following existing architectural patterns and coding conventions.

### 2. Bug Fixing
Guidance and execution of bug fixes, including root cause analysis and verification.

### 3. Testing
Understanding and running existing test suites, and creating new tests for added or modified functionality.

### 4. Deployment
Knowledge of deployment procedures for web and mobile (Android) platforms, including asset management and build processes.

## Resources

This skill includes example resource directories that demonstrate how to organize different types of bundled resources:

### scripts/
Executable code that can be run directly to perform specific operations.

**Examples from other skills:**
- PDF skill: fill_fillable_fields.cjs, extract_form_field_info.cjs - utilities for PDF manipulation
- CSV skill: normalize_schema.cjs, merge_datasets.cjs - utilities for tabular data manipulation

**Appropriate for:** Node.cjs scripts (cjs), shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by Gemini CLI for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform Gemini CLI's process and thinking.

**Examples from other skills:**
- Product management: communication.md, context_building.md - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Gemini CLI should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the output Gemini CLI produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---