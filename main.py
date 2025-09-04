import requests

url = "https://jsonplaceholder.typicode.com/posts/1"

try:
    # Hacemos una petición GET
    response = requests.get(url)

    # Verificamos si la respuesta fue exitosa
    if response.status_code == 200:
        print("✅ Conexión exitosa")
        print("Respuesta del servidor:")
        print(response.json())  # Si el endpoint devuelve JSON
    else:
        print(f"❌ Error: {response.status_code}")
except requests.exceptions.RequestException as e:
    print("⚠️ Ocurrió un error:", e)
