def get_products():
    url = f"{BASE_URL}/products"
    headers = {
        "api-token": API_TOKEN,
        "Accept": "application/json"
    }

    try:
        res = requests.get(url, headers=headers)

        print("STATUS:", res.status_code)
        print("RESPONSE:", res.text)

        data = res.json()

        # 👇 جرب نرجع كل شي بدون فلترة
        return data

    except Exception as e:
        print("API Error:", e)
        return []
