import connexion
import six

from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.inline_response2003 import InlineResponse2003  # noqa: E501
from swagger_server.models.inline_response2006 import InlineResponse2006  # noqa: E501
from swagger_server.models.products_list_response import ProductsListResponse  # noqa: E501
from swagger_server import util

from swagger_server.db import products_collection
from swagger_server.models.product import Product
from datetime import datetime, timezone
from math import ceil
from bson import ObjectId


# GET /api/products/categories
def api_categories_get():  # noqa: E501
    try:
        categories = products_collection.distinct("category")
        result = []
        
        for category in categories:
            count = products_collection.count_documents({"category": category})
            result.append({
                "category": category,
                "count": count
            })

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
    try:
        page = page or 1
        per_page = limit or 20
        
        if page < 1:
            return {"status": "error", "message": "Page must be greater than 0"}, 400
        if per_page < 1 or per_page > 100:
            return {"status": "error", "message": "Items per page must be between 1 and 100"}, 400
        
        query = {}

        if category:
            query["category"] = category
        if brand:
            query["brand"] = brand
        if sku:
            query["sku"] = sku
        if status:
            if status not in ["active", "inactive", "discontinued"]:
                return {"status": "error", "message": "Invalid status. Must be: active, inactive, or discontinued"}, 400
            query["status"] = status
        if min_price is not None or max_price is not None:
            query["price"] = {}
            if min_price is not None:
                if min_price < 0:
                    return {"status": "error", "message": "min_price must be >= 0"}, 400
                query["price"]["$gte"] = float(min_price)
            if max_price is not None:
                if max_price < 0:
                    return {"status": "error", "message": "max_price must be >= 0"}, 400
                query["price"]["$lte"] = float(max_price)
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
            ]

        sort_spec = [("created_at", -1)]  # Default sort by created date descending
        if sort == "name":
            sort_spec = [("name", 1)]
        elif sort == "price_asc":
            sort_spec = [("price", 1)]
        elif sort == "price_desc":
            sort_spec = [("price", -1)]
        elif sort == "updated_at":
            sort_spec = [("updated_at", -1)]
        elif sort == "created_at":
            sort_spec = [("created_at", -1)]

        # Execute query with pagination
        skip = (page - 1) * per_page
        cursor = products_collection.find(query).sort(sort_spec).skip(skip).limit(per_page)
        total_count = products_collection.count_documents(query)
        total_pages = ceil(total_count / per_page) if total_count > 0 else 1

        items = []
        for doc in cursor:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
            doc["links"] = {
                "self": {"href": f"/api/products/{doc['id']}", "method": "GET"},
                "update": {"href": f"/api/products/{doc['id']}", "method": "PUT"},
                "delete": {"href": f"/api/products/{doc['id']}", "method": "DELETE"}
            }
            items.append(Product.from_dict(doc))

        resp = ProductsListResponse(
            status="success",
            message="Retrieved all products successfully",
            data=items,
            links={
                "self": {"href": f"/api/products?page={page}&per_page={per_page}", "method": "GET"},
                "create": {"href": "/api/products", "method": "POST"},
                "prev": {"href": f"/api/products?page={page-1}&per_page={per_page}", "method": "GET"} if page > 1 else None,
                "next": {"href": f"/api/products?page={page+1}&per_page={per_page}", "method": "GET"} if page < total_pages else None,
                "first": {"href": f"/api/products?page=1&per_page={per_page}", "method": "GET"},
                "last": {"href": f"/api/products?page={total_pages}&per_page={per_page}", "method": "GET"}
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


# GET /api/products/{product_id}
def api_products_product_id_get(product_id):  # noqa: E501
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


# GET /api/products/sku/{sku}
def api_products_sku_sku_get(sku):  # noqa: E501
    try:
        if not sku or not sku.strip():
            return {"status": "error", "message": "SKU is required"}, 400

        product = products_collection.find_one({"sku": sku})
        
        if not product:
            return {"status": "error", "message": "Product not found"}, 404

        product["id"] = str(product["_id"])
        product.pop("_id", None)

        return {
            "status": "success",
            "message": "Product retrieved successfully",
            "data": product,
            "links": {
                "self": {"href": f"/api/products/sku/{sku}", "method": "GET"},
                "by_id": {"href": f"/api/products/{product['id']}", "method": "GET"},
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
