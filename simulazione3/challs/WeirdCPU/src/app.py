from flask import Flask, render_template, request
import requests
import io
import os
from waf import filter_program
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024

FPGA_SERVICE_ADDRESS = os.getenv('FPGA_SERVICE_ADDRESS')
FPGA_TEAM_TOKEN = os.getenv('FPGA_TEAM_TOKEN')
MAX_PROGRAM_LENGTH = 1024


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run', methods=['POST'])
def run():
    if 'program' not in request.files:
        return {'ok': False, 'error': 'Missing program'}

    f = request.files['program']
    
    program = f.stream.read()

    if len(program) > MAX_PROGRAM_LENGTH:
        return {'ok': False, 'error': 'Program too long'}

    if len(program) == 0:
        return {'ok': False, 'error': 'Program empty'}

    filtered_program = filter_program(program)
    if filtered_program is None:
        return {'ok': False, 'error': 'Prevented execution'}

    try:
        response = requests.post(f'{FPGA_SERVICE_ADDRESS}/run', headers={
            'FPGA-Team-Token': FPGA_TEAM_TOKEN
        }, files={
            'program': io.BytesIO(program)
        })

        return response.json()
    except:
        return {'ok': False, 'error': 'Error contacting FPGA Service'}


if __name__ == '__main__':
    app.run(debug=True)
