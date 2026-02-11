from flask import Flask, render_template, request, send_file
from io import BytesIO
import gifgen

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
	name = request.form.get('name', 'ANONYMOUS')
	idnum = request.form.get('idnum', '000-000')
	reason = request.form.get('reason', 'No reason provided')
	stamp = request.form.get('stamp', 'DENIED')

	bio = gifgen.generate_citation_gif(name, idnum, reason, stamp)
	bio.seek(0)
	return send_file(bio, mimetype='image/gif', as_attachment=False, download_name='citation.gif')


if __name__ == '__main__':
	app.run(host='127.0.0.1', port=5000, debug=True)

