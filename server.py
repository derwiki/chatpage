import logging
import sys
import uuid

from flask import Flask, request, redirect, render_template
import openai

import os

openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

log = logging.getLogger(__file__)
log.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

log.addHandler(handler)


def get_or_create_session_id() -> str:
    if get_session_id := request.args.get('session_id'):
        return get_session_id
    else:
        return str(uuid.uuid4())


def session_template_filename(s: str) -> str:
    return f'index-{s}.html'


def template_filename_for_reading(session_id: str) -> str:
    return session_template_filename(session_id) if session_template_exists(session_id) else 'index.html'


def session_template_exists(session_id: str) -> bool:
    return os.path.exists(f'templates/{session_template_filename(session_id)}')


@app.route('/', methods=['GET'])
def index():
    session_id = get_or_create_session_id()
    log.info("index %s", {session_id: session_id})
    return render_template(template_filename_for_reading(session_id), session_id=session_id)


@app.route('/change', methods=['POST'])
def handle_change():
    text = request.form.get('change-input')
    session_id = get_or_create_session_id()
    log.info("handle_change %s", {"session_id": session_id, "text": text})

    with open(template_filename_for_reading(session_id), 'r') as f:
        file_content = f.read()

    # TODO(derwiki) construct in haml to save tokens
    # Construct OpenAI request with the input text as prompt
    prompt = f"""Change the code in index.html according to the prompt.
Your response should only include html and nothing to escape the code.
Make sure the new index.html is less than the token limit.
The new code must include the POST form with the change-input text field.
    
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
    log.info("handle_change response_content:\n%s", response_content)

    # Get the generated code and replace it in index-{session_id}.html
    with open(f'templates/{session_template_filename(session_id)}', 'w') as f:
        f.write(response_content)

    return redirect(f'/?session_id={session_id}')


if __name__ == '__main__':
    app.run(debug=os.getenv('ENV') == 'production')
