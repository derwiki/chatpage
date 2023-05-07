from flask import Flask, request
import openai

openai.api_key = "insert_your_api_key"

app = Flask(__name__)

@app.route('/change', methods=['POST'])
def handle_change():
    text = request.form.get('change-input')

    # Construct OpenAI request with the input text as prompt
    prompt = f"Change the code in index.html: {text}"
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    # Get the generated code and replace it in index.html
    generated_code = response.choices[0].text
    with open('index.html', 'r') as f:
        file_content = f.read()
        updated_content = file_content.replace('<!-- OLD CODE HERE -->', generated_code)
    with open('index.html', 'w') as f:
        f.write(updated_content)

    return 'Code updated successfully!'

if __name__ == '__main__':
    app.run(debug=True)