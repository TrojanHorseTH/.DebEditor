# app.py
from flask import Flask, request, jsonify, send_file
import os, tempfile, tarfile, shutil

app = Flask(__name__)
UPLOAD_FOLDER = tempfile.mkdtemp()
current_file_path = None
current_extract_path = None

@app.route("/upload", methods=["POST"])
def upload():
    global current_file_path, current_extract_path
    f = request.files.get("debfile")
    if not f: return jsonify(success=False)
    current_file_path = os.path.join(UPLOAD_FOLDER, f.filename)
    f.save(current_file_path)

    # Extract .deb
    extract_path = os.path.join(UPLOAD_FOLDER, "extracted")
    if os.path.exists(extract_path): shutil.rmtree(extract_path)
    os.makedirs(extract_path)

    # A .deb is an ar archive
    os.system(f"ar x {current_file_path} -C {extract_path}")
    control_tar = os.path.join(extract_path, "control.tar.gz")
    control_contents = ""
    if os.path.exists(control_tar):
        with tarfile.open(control_tar, "r:gz") as tar:
            for member in tar.getmembers():
                if member.isfile():
                    control_contents += f.read(member).decode() + "\n"
    current_extract_path = extract_path
    return jsonify(success=True, contents=control_contents)

@app.route("/edit", methods=["POST"])
def edit():
    data = request.json
    contents = data.get("contents", "")
    # Replace control.tar.gz with new contents
    # TODO: implement properly
    return jsonify(success=True)

@app.route("/export")
def export():
    # TODO: rebuild .deb from extracted folder
    return send_file(current_file_path or "dummy.deb", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
