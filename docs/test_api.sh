#!/bin/bash
# API Testing Script for FastAPI E-Commerce Backend

API_URL="http://localhost:8802"

echo "=========================================="
echo "FastAPI E-Commerce API Testing"
echo "=========================================="
echo ""

# Test 1: Health Check
echo "1. Health Check"
echo "   GET /health"
curl -s "${API_URL}/health" | python3 -m json.tool
echo ""

# Test 2: Root Health Check with Database
echo "2. Root Health Check (with database status)"
echo "   GET /"
curl -s "${API_URL}/" | python3 -m json.tool
echo ""

# Test 3: Database Stats
echo "3. Database Statistics"
echo "   GET /stats"
curl -s "${API_URL}/stats" | python3 -m json.tool
echo ""

# Test 4: Get All Products (limited)
echo "4. Get Products (first 5)"
echo "   GET /products?limit=5"
curl -s "${API_URL}/products?limit=5" | python3 -m json.tool
echo ""

# Test 5: Get Specific Product
echo "5. Get Specific Product (ID: 203)"
echo "   GET /products/203"
curl -s "${API_URL}/products/203" | python3 -m json.tool
echo ""

# Test 6: Get All Orders (limited)
echo "6. Get Orders (first 3)"
echo "   GET /orders?limit=3"
curl -s "${API_URL}/orders?limit=3" | python3 -m json.tool
echo ""

# Test 7: Get Specific Order
echo "7. Get Specific Order (ID: 70)"
echo "   GET /orders/70"
curl -s "${API_URL}/orders/70" | python3 -m json.tool
echo ""

# Test 8: Pagination Test
echo "8. Pagination Test - Products (skip=5, limit=3)"
echo "   GET /products?skip=5&limit=3"
curl -s "${API_URL}/products?skip=5&limit=3" | python3 -m json.tool
echo ""

# Test 9: 404 Test - Non-existent Product
echo "9. Error Handling - Non-existent Product (ID: 99999)"
echo "   GET /products/99999"
curl -s -w "\nHTTP Status: %{http_code}\n" "${API_URL}/products/99999" | python3 -m json.tool 2>/dev/null || echo "Product not found (expected)"
echo ""

echo "=========================================="
echo "API Testing Complete!"
echo "=========================================="
