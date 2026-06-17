# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from llm import get_product_explanation

# app = Flask(__name__)
# CORS(app)


# @app.route("/")
# def home():
#     return "Backend is running"


# @app.route("/explain", methods=["POST"])
# def explain():
#     body = request.get_json(silent=True) or {}
#     product = body.get("product")
#     budget = body.get("budget")
#     category = body.get("category", "general")
#     compare_with = body.get("compare_with")

#     if not product or not budget:
#         return jsonify({"error": "Product and budget are required."}), 400

#     try:
#         result = get_product_explanation(product, budget, category, compare_with)
#         return jsonify(result)
#     except Exception as exc:
#         return jsonify({"error": str(exc)}), 500


# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)



from flask import Flask, request, jsonify
from flask_cors import CORS
from llm import get_product_explanation

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "Backend is running"


@app.route("/explain", methods=["POST"])
def explain():
    body = request.get_json(silent=True) or {}
    product = body.get("product")
    budget = body.get("budget")
    category = body.get("category", "general")
    compare_with = body.get("compare_with")
    compare_with_2 = body.get("compare_with_2")

    if compare_with_2:
        compare_items = []
        if isinstance(compare_with, list):
            compare_items.extend(compare_with)
        elif compare_with:
            compare_items.append(compare_with)
        compare_items.append(compare_with_2)
        compare_with = compare_items

    if not product or not budget:
        return jsonify({"error": "Product and budget are required."}), 400

    try:
        result = get_product_explanation(product, budget, category, compare_with)
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
