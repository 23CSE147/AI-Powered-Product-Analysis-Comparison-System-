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
    body = request.json
    product = body.get("product")
    budget = body.get("budget")

    result = get_product_explanation(product, budget)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)