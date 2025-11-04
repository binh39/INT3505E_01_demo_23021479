import connexion
import six
from functools import wraps

from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.inline_response2003 import InlineResponse2003  # noqa: E501
from swagger_server.models.inline_response2004 import InlineResponse2004  # noqa: E501
from swagger_server.models.inline_response2005 import InlineResponse2005  # noqa: E501
from swagger_server.models.inline_response2006 import InlineResponse2006  # noqa: E501
from swagger_server.models.inline_response201 import InlineResponse201  # noqa: E501
from swagger_server.models.products_list_response import ProductsListResponse  # noqa: E501
from swagger_server.models.update_product_request import UpdateProductRequest  # noqa: E501
from swagger_server.models.create_product_request import CreateProductRequest
from swagger_server import util

from swagger_server.db import products_collection
from swagger_server.models.product import Product
from datetime import datetime, timezone
from math import ceil
from bson import ObjectId


def admin_required(f):
    """Decorator to check if user has admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token_info = connexion.context.get('token_info')
        if not token_info or token_info.get('role') != 'admin':
            return {"status": "error", "message": "Admin access required"}, 403
        return f(*args, **kwargs)
    return decorated_function

# GET /api/products/categories
def api_categories_get():  # noqa: E501
    """Get all product categories"""
    try:
        categories = products_collection.distinct("category")
        result = [{"category": c, "count": products_collection.count_documents({"category": c})} for c in categories]

        return {
            "status": "success",
            "message": "Categories retrieved successfully",
            "data": result,
            "links": {
                "self": {"href": "/api/products/categories", "method": "GET"},
                "products": {"href": "/api/products", "method": "GET"}
            },
            "meta": {
                "total_categories": len(categories),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }, 200
    except Exception as e:
        return {"status": "error", "message": f"Internal server error: {str(e)}"}, 500

# GET /api/products
def api_products_get(page=None, limit=None, category=None, brand=None, sku=None, status=None, min_price=None, max_price=None, search=None, sort=None):  # noqa: E501
    """Get all products with pagination and filtering"""
    try:
        page = page or 1
        per_page = limit or 20
        query = {}

        if category:
            query["category"] = category
        if brand:
            query["brand"] = brand
        if sku:
            query["sku"] = sku
        if status:
            query["status"] = status
        if min_price is not None or max_price is not None:
            query["price"] = {}
            if min_price is not None:
                query["price"]["$gte"] = float(min_price)
            if max_price is not None:
                query["price"]["$lte"] = float(max_price)
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
            ]

        sort_spec = [("created_at", -1)]
        if sort == "name":
            sort_spec = [("name", 1)]
        elif sort == "price_asc":
            sort_spec = [("price", 1)]
        elif sort == "price_desc":
            sort_spec = [("price", -1)]
        elif sort == "updated_at":
            sort_spec = [("updated_at", -1)]

        skip = (page - 1) * per_page
        cursor = products_collection.find(query).sort(sort_spec).skip(skip).limit(per_page)
        total_count = products_collection.count_documents(query)
        total_pages = ceil(total_count / per_page)

        items = []
        for doc in cursor:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
            # Add HATEOAS links to each product
            doc["links"] = {
                "self": {"href": f"/api/products/{doc['id']}", "method": "GET"},
                "update": {"href": f"/api/products/{doc['id']}", "method": "PUT"},
                "delete": {"href": f"/api/products/{doc['id']}", "method": "DELETE"}
            }
            items.append(Product.from_dict(doc))

        resp = ProductsListResponse(
            status="success",
            message="Products retrieved successfully",
            data=items,
            links={
                "self": {"href": f"/api/products?page={page}", "method": "GET"},
                "create": {"href": "/api/products", "method": "POST"},
                "prev": {"href": f"/api/products?page={page-1}", "method": "GET"} if page > 1 else None,
                "next": {"href": f"/api/products?page={page+1}", "method": "GET"} if page < total_pages else None,
                "first": {"href": "/api/products?page=1", "method": "GET"},
                "last": {"href": f"/api/products?page={total_pages}", "method": "GET"}
            },
            meta={
                "total_count": total_count,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
        return resp, 200
    except Exception as e:
        return {"status": "error", "message": f"Internal server error: {str(e)}"}, 500

# POST /api/products
@admin_required
def api_products_post(body):  # noqa: E501
    """Create new product (Admin only)"""
    try:
        if body is None:
            return {"status": "error", "message": "Missing request body"}, 400

        if isinstance(body, dict):
            data = body
        else:
            data = body.to_dict()
        
        # Validate required fields
        required_fields = ["sku", "name", "category", "price"]
        for field in required_fields:
            if not data.get(field):
                return {
                    "status": "error", 
                    "message": f"{field} is required",
                    "meta": {"required_fields": required_fields}
                }, 400
        
        # Validate price >= 0
        if data.get("price", 0) < 0:
            return {"status": "error", "message": "Price must be greater than or equal to 0"}, 400
        
        # Validate quantity >= 0
        if data.get("quantity", 0) < 0:
            return {"status": "error", "message": "Quantity must be greater than or equal to 0"}, 400

        # Validate SKU uniqueness
        if products_collection.find_one({"sku": data.get("sku")}):
            return {"status": "error", "message": "Product with this SKU already exists"}, 409

        now = datetime.now(timezone.utc).isoformat()
        data["created_at"] = now
        data["updated_at"] = now
        data["status"] = data.get("status", "active")
        data["currency"] = data.get("currency", "USD")
        data["quantity"] = data.get("quantity", 0)

        result = products_collection.insert_one(data)
        data["id"] = str(result.inserted_id)
        data.pop("_id", None)

        return {
            "status": "success",
            "message": "Product created successfully",
            "data": data,
            "links": {
                "self": {"href": f"/api/products/{data['id']}", "method": "GET"},
                "update": {"href": f"/api/products/{data['id']}", "method": "PUT"},
                "delete": {"href": f"/api/products/{data['id']}", "method": "DELETE"},
                "all_products": {"href": "/api/products", "method": "GET"}
            },
            "meta": {
                "created_at": now,
                "created_by": connexion.context.get('token_info', {}).get('username', 'unknown')
            }
        }, 201
    except Exception as e:
        return {"status": "error", "message": f"Internal server error: {str(e)}"}, 500

# DELETE /api/products/{product_id}
@admin_required
def api_products_product_id_delete(product_id):  # noqa: E501
    """Delete product (Admin only) - Soft delete by setting status to discontinued"""
    try:
        try:
            obj_id = ObjectId(product_id)
        except Exception:
            return {"status": "error", "message": "Invalid product ID format"}, 400

        product = products_collection.find_one({"_id": obj_id})
        if not product:
            return {"status": "error", "message": "Product not found"}, 404
        
        # Check if already discontinued
        if product.get("status") == "discontinued":
            return {"status": "error", "message": "Product already discontinued"}, 400

        now = datetime.now(timezone.utc).isoformat()
        result = products_collection.update_one(
            {"_id": obj_id},
            {"$set": {"status": "discontinued", "updated_at": now}}
        )
        
        if result.modified_count == 0:
            return {"status": "error", "message": "Failed to delete product"}, 500

        # Get updated product
        updated_product = products_collection.find_one({"_id": obj_id})
        updated_product["id"] = str(updated_product["_id"])
        updated_product.pop("_id", None)

        return {
            "status": "success",
            "message": "Product deleted successfully",
            "data": updated_product,
            "links": {
                "all_products": {"href": "/api/products", "method": "GET"}
            },
            "meta": {
                "deleted_at": now,
                "deleted_by": connexion.context.get('token_info', {}).get('username', 'unknown')
            }
        }, 200
    except Exception as e:
        return {"status": "error", "message": f"Internal server error: {str(e)}"}, 500

# GET /api/products/{product_id}
def api_products_product_id_get(product_id):  # noqa: E501
    """Get product details by ID"""
    try:
        try:
            obj_id = ObjectId(product_id)
        except Exception:
            return {"status": "error", "message": "Invalid product ID format"}, 400

        product = products_collection.find_one({"_id": obj_id})
        
        if not product:
            return {"status": "error", "message": "Product not found"}, 404

        product["id"] = str(product["_id"])
        product.pop("_id", None)

        return {
            "status": "success",
            "message": "Product retrieved successfully",
            "data": product,
            "links": {
                "self": {"href": f"/api/products/{product['id']}", "method": "GET"},
                "update": {"href": f"/api/products/{product['id']}", "method": "PUT"},
                "delete": {"href": f"/api/products/{product['id']}", "method": "DELETE"},
                "all_products": {"href": "/api/products", "method": "GET"}
            },
            "meta": {
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }, 200
    except Exception as e:
        return {"status": "error", "message": f"Internal server error: {str(e)}"}, 500

# PUT /api/products/{product_id}
@admin_required
def api_products_product_id_put(body, product_id):  # noqa: E501
    """Update product information (Admin only)"""
    try:
        if body is None:
            return {"status": "error", "message": "Missing request body"}, 400

        try:
            obj_id = ObjectId(product_id)
        except Exception:
            return {"status": "error", "message": "Invalid product ID format"}, 400
        
        # Check if product exists
        existing_product = products_collection.find_one({"_id": obj_id})
        if not existing_product:
            return {"status": "error", "message": "Product not found"}, 404

        if isinstance(body, dict):
            data = body
        else:
            data = body.to_dict()

        # Remove None values to avoid overwriting with null
        data = {k: v for k, v in data.items() if v is not None}
        
        # Validate price >= 0 if provided
        if "price" in data and data["price"] < 0:
            return {"status": "error", "message": "Price must be greater than or equal to 0"}, 400
        
        # Validate quantity >= 0 if provided
        if "quantity" in data and data["quantity"] < 0:
            return {"status": "error", "message": "Quantity must be greater than or equal to 0"}, 400
        
        now = datetime.now(timezone.utc).isoformat()
        data["updated_at"] = now

        result = products_collection.update_one({"_id": obj_id}, {"$set": data})

        if result.matched_count == 0:
            return {"status": "error", "message": "Product not found"}, 404

        updated = products_collection.find_one({"_id": obj_id})
        updated["id"] = str(updated["_id"])
        updated.pop("_id", None)

        return {
            "status": "success",
            "message": "Product updated successfully",
            "data": updated,
            "links": {
                "self": {"href": f"/api/products/{updated['id']}", "method": "GET"},
                "delete": {"href": f"/api/products/{updated['id']}", "method": "DELETE"},
                "all_products": {"href": "/api/products", "method": "GET"}
            },
            "meta": {
                "updated_at": now,
                "updated_by": connexion.context.get('token_info', {}).get('username', 'unknown')
            }
        }, 200
    except Exception as e:
        return {"status": "error", "message": f"Internal server error: {str(e)}"}, 500
