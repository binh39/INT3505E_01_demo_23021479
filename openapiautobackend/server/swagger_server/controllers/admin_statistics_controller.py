import connexion
import six
from functools import wraps

from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.statistics import Statistics  # noqa: E501
from swagger_server import util

from swagger_server.db import products_collection
from datetime import datetime, timezone
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


# GET /api/statistics
@admin_required
def api_statistics_get():  # noqa: E501
    try:
        # Get all products from database
        all_products = list(products_collection.find())
        total_products = len(all_products)
        total_quantity = sum(p.get("quantity", 0) for p in all_products)
        total_value = sum(p.get("price", 0) * p.get("quantity", 0) for p in all_products)
        
        active_products = sum(1 for p in all_products if p.get("status") == "active")
        inactive_products = sum(1 for p in all_products if p.get("status") == "inactive")
        discontinued_products = sum(1 for p in all_products if p.get("status") == "discontinued")
        
        out_of_stock = sum(1 for p in all_products if p.get("quantity", 0) == 0)
        low_stock = sum(1 for p in all_products if 0 < p.get("quantity", 0) < 10)
        
        inventory_stats = {
            "total_products": total_products,
            "total_quantity": total_quantity,
            "total_value": round(total_value, 2),
            "active_products": active_products,
            "inactive_products": inactive_products,
            "discontinued_products": discontinued_products,
            "out_of_stock": out_of_stock,
            "low_stock": low_stock
        }
        
        categories_dict = {}
        for product in all_products:
            category = product.get("category", "Unknown")
            if category not in categories_dict:
                categories_dict[category] = {
                    "count": 0,
                    "total_value": 0
                }
            categories_dict[category]["count"] += 1
            categories_dict[category]["total_value"] += product.get("price", 0) * product.get("quantity", 0)
        
        category_breakdown = []
        for category, stats in categories_dict.items():
            category_breakdown.append({
                "category": category,
                "count": stats["count"],
                "total_value": round(stats["total_value"], 2)
            })
        
        category_breakdown.sort(key=lambda x: x["count"], reverse=True)
        
        categories_stats = {
            "total_categories": len(categories_dict),
            "category_breakdown": category_breakdown
        }
        
        # Top 10 highest value products (price * quantity)
        products_with_value = []
        for product in all_products:
            product_value = product.get("price", 0) * product.get("quantity", 0)
            products_with_value.append({
                "id": str(product.get("_id")),
                "sku": product.get("sku", ""),
                "name": product.get("name", ""),
                "price": product.get("price", 0),
                "quantity": product.get("quantity", 0),
                "total_value": round(product_value, 2)
            })
        
        # Sort by total_value descending and take top 10
        products_with_value.sort(key=lambda x: x["total_value"], reverse=True)
        top_products = products_with_value[:10]
        
        # Get user info from token
        token_info = connexion.context.get('token_info', {})
        requested_by = token_info.get('username', 'unknown')
        
        response = {
            "status": "success",
            "message": "Statistics retrieved successfully",
            "data": {
                "inventory": inventory_stats,
                "categories": categories_stats,
                "top_products": top_products
            },
            "links": {
                "self": {"href": "/api/statistics", "method": "GET"},
                "products": {"href": "/api/products", "method": "GET"},
                "categories": {"href": "/api/products/categories", "method": "GET"}
            },
            "meta": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "requested_by": requested_by
            }
        }
        
        return response, 200
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Internal server error: {str(e)}",
            "data": None,
            "links": None,
            "meta": {
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }, 500
