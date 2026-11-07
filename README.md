# Shop Module Sample

This repository contains the `shop` module extracted from a larger Django-based e-commerce project. It is provided as a code sample for hiring purposes to demonstrate my approach to modular architecture, Django structure, and code organization.

## Purpose
The primary goal of this repository is to showcase:
- Organizing shop-related functionality within a Django module.
- Implementation of models, forms, serializers, and API views.
- Logic for handling product attributes, categories, and cart operations.
- Integration of unit and API tests.

## Important Note: Running this Project
This code is **not a full, runnable project**. It is an extracted module intended for code review. 
- It lacks certain configurations, external dependencies, `media_files`, the `ai_chat` module, and global project templates.
- It is designed to be read and analyzed as a sample of coding standards, not to be deployed or run locally as a complete store.

## Key Components
The code is organized into the following areas within the `shop` directory:
- **Models:** Definitions for Products, Categories, Tags, Cart, and Product Attributes.
- **API Views & Serializers:** RESTful endpoints and data serialization for products, tags, and categories.
- **Forms:** Django forms for product and category management.
- **Services:** Helpers for category trees and category filtering.
- **Tests:** A set of tests verifying basic functionality for form logic (`tests.py`) and API filter behavior (`test_search_filters.py`).

## Cart Logic Design
In this implementation, the `add_to_cart` logic is **non-locking**. Adding a product to a cart does not reserve inventory. This design decision allows multiple users to add the same product to their carts simultaneously. Final stock validation and deduction are handled during checkout, which is not included in this code sample.

## Tests
This repository includes a set of tests to verify specific parts of the module:
- `tests.py`: Covers validation and handling of tags within product forms.
- `test_search_filters.py`: Validates the filtering logic for search queries via the API.
