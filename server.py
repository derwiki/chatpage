from flask import Flask, request, redirect
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

    with open('index.html', 'r') as f:
        file_content = f.read()

    # Construct OpenAI request with the input text as prompt
    prompt = f"""Change the code in index.html according to the prompt. Your response should only include html and nothing to escape the code.

Prompt:
{text}

index.html:
{file_content}
"""
    response = openai.ChatCompletion.create(
        model='gpt-4',  # so slow
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=4000,
        temperature=0.0
    )

    response_content = response.choices[0].message['content'].strip()

    # Get the generated code and replace it in index.html
    with open('index.html', 'w') as f:
        f.write(response_content)

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
