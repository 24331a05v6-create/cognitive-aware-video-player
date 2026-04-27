from google import genai

client = genai.Client(api_key="AIzaSyAhvd-xGGwj3v-m4FNyeMn6ZU68V9ae3XI")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Say hello"
)

print(response.text)