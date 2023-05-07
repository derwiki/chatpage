from flask import Flask, request
import openai

import os

openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)
app = Flask(__name__, static_url_path='', static_folder='')



@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')


@app.route('/change', methods=['POST'])
def handle_change():
    text = request.form.get('change-input')

    # Construct OpenAI request with the input text as prompt
    prompt = f"Change the code in index.html: {text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
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
