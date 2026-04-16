def get_products():
    url = f"{BASE_URL}/products"
    headers = {
        "api-token": API_TOKEN,
        "Accept": "application/json"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()

        print("DEBUG:", data)  # مهم

        # 👇 هون التصحيح
        if not data.get("err"):
            return data.get("data", {}).get("products", [])

        return []

    except Exception as e:
        print("API ERROR:", e)
        return []
