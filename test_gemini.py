from google import genai

client = genai.Client(api_key="AIzaSyAt0konMQV4qlttEovrYkcRbjz5hoO4xi8")

response = client.models.generate_content(
 model="gemini-3-flash-preview",
 contents="Say hello"
)

print(response.text)