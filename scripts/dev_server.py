import os
import subprocess
import glob
import re
import shutil
from flask import Flask, request, jsonify, render_template_string, send_from_directory, redirect, url_for

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
# Deteksi VENV: Jika folder venv tidak ada, maka dianggap mode PRODUKSI (Web/GitHub)
VENV_EXISTS = os.path.exists(os.path.join(os.getcwd(), 'venv'))
MODE = os.environ.get("MODE", "DEVELOPMENT" if VENV_EXISTS else "PRODUCTION")
BUILD_DIR = os.path.join(os.getcwd(), '_build', 'html')

def is_local_access():
    """Cek apakah akses berasal dari localhost atau 127.0.0.1"""
    return request.remote_addr in ['127.0.0.1', 'localhost', '::1']

def get_editable_files():
    """Get list of files that can be edited/deleted"""
    ignore = ['intro.md', 'README.md', 'requirements.txt', '.nojekyll', 'markdown.md', 'markdown-notebooks.md', 'notebooks.ipynb', '_toc.yml', '_config.yml']
    files = []
    # Root files
    for f in glob.glob("*.md") + glob.glob("*.ipynb"):
        if f not in ignore: files.append(f)
    # md/ folder files
    if os.path.exists('md'):
        for f in glob.glob("md/*.md") + glob.glob("md/*.ipynb"):
            if os.path.basename(f) not in ignore: files.append(f)
    return sorted(files)

def update_toc():
    """Otomatis mengupdate _toc.yml berdasarkan isi folder md/"""
    ignore = ['intro.md', 'README.md', 'requirements.txt', '.nojekyll', 'markdown.md', 'markdown-notebooks.md', 'notebooks.ipynb']
    files = []
    # Root files
    for f in glob.glob("*.md") + glob.glob("*.ipynb"):
        if f not in ignore: files.append(f)
    # md/ folder files
    if os.path.exists('md'):
        for f in glob.glob("md/*.md") + glob.glob("md/*.ipynb"):
            if os.path.basename(f) not in ignore: files.append(f)

    # Sort logic (Numbered first, then alphabetical)
    numbered = []
    non_numbered = []
    for f in files:
        basename = os.path.basename(f)
        if re.match(r'^\d+', basename):
            numbered.append(f)
        else:
            non_numbered.append(f)
    
    non_numbered.sort()
    numbered.sort(key=lambda x: int(re.match(r'^(\d+)', os.path.basename(x)).group(1)) if re.match(r'^(\d+)', os.path.basename(x)) else 0)
    
    final_list = numbered + non_numbered
    
    toc_content = "format: jb-book\nroot: intro\nchapters:\n"
    for f in final_list:
        title = os.path.splitext(os.path.basename(f))[0].replace('-', ' ').replace('_', ' ').title()
        try:
            with open(f, 'r', encoding='utf-8') as file:
                for _ in range(10):
                    line = file.readline()
                    if line.startswith('# '):
                        title = line.replace('# ', '').strip()
                        break
        except: pass
        
        jb_path = os.path.splitext(f)[0].replace('\\', '/')
        toc_content += f"- file: {jb_path}\n  title: \"{title}\"\n"
    
    with open('_toc.yml', 'w', encoding='utf-8') as f:
        f.write(toc_content)

def build_book():
    """Menjalankan jupyter-book build secara penuh"""
    try:
        # Gunakan --all agar sidebar di SEMUA halaman terupdate saat TOC berubah
        subprocess.run(["jupyter-book", "build", "--all", "."], check=True)
        return True
    except:
        return False

# --- ROUTES ---

@app.route('/canvas')
def canvas():
    if not VENV_EXISTS or not is_local_access():
        return render_template_string(RESTRICTED_HTML), 403
    return render_template_string(CANVAS_HTML)

@app.route('/api/files')
def list_files():
    if not VENV_EXISTS or not is_local_access(): return jsonify([]), 403
    return jsonify(get_editable_files())

@app.route('/api/read')
def read_file():
    if not VENV_EXISTS or not is_local_access(): return jsonify(success=False), 403
    path = request.args.get('path')
    if not path or not os.path.exists(path):
        return jsonify(success=False, error="File not found")
    with open(path, 'r', encoding='utf-8') as f:
        return jsonify(success=True, content=f.read())

@app.route('/api/delete', methods=['POST'])
def delete_file():
    if not VENV_EXISTS or not is_local_access(): return jsonify(success=False), 403
    path = request.json.get('path')
    if not path or not os.path.exists(path):
        return jsonify(success=False, error="File not found")
    try:
        # 1. Hapus source file (.md atau .ipynb)
        os.remove(path)
        
        # 2. Hapus sisa file HTML di folder _build agar benar-benar hilang
        html_path = os.path.join('_build', 'html', os.path.splitext(path)[0] + '.html')
        if os.path.exists(html_path):
            os.remove(html_path)
        
        # 3. Update daftar isi (_toc.yml)
        update_toc()
        
        # 4. Build ulang buku
        build_book()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route('/save', methods=['POST'])
def save():
    if not VENV_EXISTS or not is_local_access(): return jsonify(success=False), 403
    data = request.json
    filename = data.get('filename')
    content = data.get('content')
    
    # Check if this is an update to an existing file with a full path
    is_edit = '/' in filename or '\\' in filename or os.path.exists(filename)
    
    if not is_edit:
        # Automatic Numbering Logic
        files = get_editable_files()
        max_num = -1
        for f in files:
            match = re.search(r'(\d+)', os.path.basename(f))
            if match:
                num = int(match.group(1))
                if num > max_num: max_num = num
        
        # Check if the user already started with a number
        if not re.match(r'^\d+', filename):
            next_num = max_num + 1
            prefix = f"{next_num:02d}_"
            filename = prefix + filename.replace(' ', '-')
        
        if not filename.endswith('.md'): filename += '.md'
        target_path = os.path.join('md', filename)
    else:
        target_path = filename

    os.makedirs(os.path.dirname(target_path) or '.', exist_ok=True)
    
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    update_toc()
    if build_book():
        # Karena build selesai, kita berikan redirect ke halaman yang baru/diupdate
        clean_path = target_path.replace('.md', '').replace('.ipynb', '')
        page_url = f"/{clean_path}.html"
        return jsonify(success=True, redirect=page_url, path=target_path)
    return jsonify(success=False, error="Build failed")

@app.route('/')
def home():
    if not os.path.exists(os.path.join(BUILD_DIR, 'index.html')):
        return redirect(url_for('canvas'))
    return send_from_directory(BUILD_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(BUILD_DIR, path)):
        return send_from_directory(BUILD_DIR, path)
    if os.path.exists(os.path.join(BUILD_DIR, path + '.html')):
        return send_from_directory(BUILD_DIR, path + '.html')
    return "File Not Found", 404

# --- UI TEMPLATE ---

RESTRICTED_HTML = r"""
<!DOCTYPE html>
<html>
<head>
    <title>Access Denied</title>
    <style>
        body { background: #0d1117; color: #c9d1d9; display: flex; align-items: center; justify-content: center; height: 100vh; font-family: sans-serif; text-align: center; }
        .box { padding: 40px; border: 1px solid #30363d; border-radius: 12px; background: #161b22; max-width: 400px; }
        h1 { color: #f85149; }
        p { line-height: 1.6; }
        .footer { margin-top: 20px; font-size: 12px; color: #8b949e; }
    </style>
</head>
<body>
    <div class="box">
        <h1>Akses Dibatasi</h1>
        <p>Markdown Canvas hanya bisa diakses via <b>Localhost</b> dengan environment <b>VENV</b> aktif.</p>
        <p>Fitur editor dimatikan untuk versi web publik demi keamanan data.</p>
        <div class="footer">Silakan jalankan <code>bash run.sh dev</code> di komputer lokal Anda.</div>
    </div>
</body>
</html>
"""

CANVAS_HTML = r"""
<!DOCTYPE html>
<html>
<head>
    <title>Markdown Canvas</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.2.0/github-markdown.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { 
            --bg: #000000; 
            --panel: #000000; 
            --accent: #58a6ff; 
            --text: #c9d1d9; 
            --border: #30363d;
            --toolbar: #000000;
            --input-bg: #0d1117;
            --sidebar-w: 250px;
        }
        body { margin:0; font-family: 'Inter', -apple-system, sans-serif; background: var(--bg); color: var(--text); overflow: hidden; display: flex; flex-direction: column; height: 100vh; }
        
        .header { height: 50px; background: var(--panel); display: flex; align-items: center; justify-content: space-between; padding: 0 15px; border-bottom: 1px solid var(--border); z-index: 10; }
        .logo { font-weight: 700; color: #fff; font-size: 1.1rem; display: flex; align-items: center; gap: 8px; }
        
        .main-layout { display: flex; flex: 1; overflow: hidden; }
        
        /* Sidebar */
        .sidebar { width: var(--sidebar-w); background: var(--panel); border-right: 1px solid var(--border); display: flex; flex-direction: column; overflow-y: auto; }
        .sidebar-header { padding: 12.5px 15px; font-size: 11px; font-weight: 600; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid var(--border); }
        .file-list { flex: 1; }
        .file-item { padding: 10px 15px; font-size: 13px; cursor: pointer; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(48, 54, 61, 0.5); transition: 0.2s; }
        .file-item:hover { background: #161b22; }
        .file-item.active { background: #161b22; border-left: 3px solid var(--accent); padding-left: 12px; }
        .file-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
        .file-actions { display: none; gap: 8px; margin-left: 10px; }
        .file-item:hover .file-actions { display: flex; }
        .action-btn { color: #8b949e; transition: 0.2s; cursor: pointer; }
        .action-btn:hover { color: #f85149; }

        /* Workspace */
        .workspace { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
        .toolbar { background: var(--toolbar); padding: 5px 15px; display: flex; gap: 5px; border-bottom: 1px solid var(--border); align-items: center; }
        .tool-btn { background: transparent; color: var(--text); border: none; padding: 6px 10px; border-radius: 4px; cursor: pointer; transition: 0.2s; font-size: 13px; }
        .tool-btn:hover { background: #30363d; color: #fff; }
        .divider { width: 1px; height: 16px; background: #30363d; margin: 0 8px; }

        .container { display: flex; flex: 1; overflow: hidden; }
        .editor-pane, .preview-pane { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
        .editor-pane { border-right: 1px solid var(--border); }
        
        textarea { flex: 1; background: var(--bg); color: #e6edf3; border: none; padding: 25px; font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 15px; line-height: 1.7; outline: none; resize: none; }
        
        .preview-pane { background: var(--bg); overflow-y: auto; }
        .markdown-body { padding: 40px !important; line-height: 1.6; background: transparent !important; color: #c9d1d9 !important; }
        .markdown-body h1, .markdown-body h2, .markdown-body h3 { border-bottom-color: var(--border) !important; color: #f0f6fc !important; }
        .markdown-body code { background-color: rgba(110, 118, 129, 0.4) !important; color: #e6edf3 !important; }
        .markdown-body pre { background-color: #161b22 !important; border: 1px solid var(--border) !important; }

        /* Inputs & Buttons */
        #filename-input { background: var(--input-bg); border: 1px solid var(--border); color: #fff; padding: 6px 12px; border-radius: 6px; width: 250px; outline: none; font-size: 13px; }
        .btn { padding: 6px 15px; border-radius: 6px; font-weight: 600; cursor: pointer; transition: 0.2s; border: 1px solid transparent; font-size: 13px; display: inline-flex; align-items: center; gap: 6px; }
        .btn-primary { background: var(--accent); color: #000; }
        .btn-outline { background: #21262d; color: #c9d1d9; border-color: var(--border); text-decoration: none; }
        
        /* Loading Overlay */
        #loading-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); z-index: 9999; flex-direction: column; align-items: center; justify-content: center; }
        .spinner { width: 40px; height: 40px; border: 4px solid #161b22; border-top-color: var(--accent); border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px; }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: var(--bg); }
        ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 4px; }
    </style>
</head>
<body>
    <div id="loading-overlay">
        <div class="spinner"></div>
        <div id="loading-text">Building Project...</div>
    </div>

    <div class="header">
        <div class="logo"><i class="fab fa-markdown"></i> Markdown Editor</div>
        <div style="display: flex; align-items: center; gap: 12px;">
            <input type="text" id="filename-input" placeholder="Filename (e.g. setup-materi)">
            <button class="btn btn-outline" onclick="newFile()">New File</button>
            <a href="/" class="btn btn-outline" target="_blank">View Book</a>
            <button class="btn btn-primary" onclick="save()">Save & Build</button>
        </div>
    </div>

    <div class="main-layout">
        <div class="sidebar">
            <div class="sidebar-header">Files</div>
            <div id="file-list" class="file-list"></div>
        </div>
        
        <div class="workspace">
            <div class="toolbar">
                <button class="tool-btn" onclick="insertFormat('h1')">H1</button>
                <button class="tool-btn" onclick="insertFormat('h2')">H2</button>
                <div class="divider"></div>
                <button class="tool-btn" onclick="insertFormat('bold')"><i class="fas fa-bold"></i></button>
                <button class="tool-btn" onclick="insertFormat('italic')"><i class="fas fa-italic"></i></button>
                <div class="divider"></div>
                <button class="tool-btn" onclick="insertFormat('list')"><i class="fas fa-list-ul"></i></button>
                <button class="tool-btn" onclick="insertFormat('code')"><i class="fas fa-code"></i></button>
                <button class="tool-btn" onclick="insertFormat('image')"><i class="fas fa-image"></i></button>
            </div>

            <div class="container">
                <div class="editor-pane">
                    <textarea id="editor" placeholder="# Write content here..." oninput="updatePreview()" spellcheck="false"></textarea>
                </div>
                <div class="preview-pane">
                    <div id="preview" class="markdown-body"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const editor = document.getElementById('editor');
        const preview = document.getElementById('preview');
        const filenameInput = document.getElementById('filename-input');
        const fileList = document.getElementById('file-list');
        const loadingOverlay = document.getElementById('loading-overlay');
        const loadingText = document.getElementById('loading-text');
        let currentFilePath = null;

        function showLoading(text) {
            loadingText.innerText = text || "Building Project...";
            loadingOverlay.style.display = 'flex';
        }
        function hideLoading() {
            loadingOverlay.style.display = 'none';
        }

        async function loadFiles() {
            const res = await fetch('/api/files');
            if(!res.ok) return;
            const files = await res.json();
            fileList.innerHTML = files.map(f => {
                // Bersihkan nama untuk tampilan: hapus path, hapus angka di depan, hapus ekstensi
                const displayName = f.split('/').pop()
                                     .replace(/^\d+_/, '')
                                     .replace(/\.(md|ipynb)$/, '');
                
                return `
                    <div class="file-item ${f === currentFilePath ? 'active' : ''}" onclick="openFile('${f}')">
                        <span class="file-name"><i class="far fa-file-alt"></i> ${displayName}</span>
                        <div class="file-actions">
                            <i class="fas fa-trash-alt action-btn" onclick="event.stopPropagation(); deleteFile('${f}')"></i>
                        </div>
                    </div>
                `;
            }).join('');
        }

        async function openFile(path) {
            const res = await fetch(`/api/read?path=${encodeURIComponent(path)}`);
            const data = await res.json();
            if(data.success) {
                currentFilePath = path;
                editor.value = data.content;
                // Tampilkan nama bersih di input box (tanpa md/, tanpa angka, tanpa ekstensi)
                filenameInput.value = path.split('/').pop()
                                          .replace(/^\d+_/, '')
                                          .replace(/\.(md|ipynb)$/, '');
                updatePreview();
                loadFiles();
            }
        }

        async function deleteFile(path) {
            if(!confirm(`Delete ${path}?`)) return;
            showLoading("Deleting & Rebuilding...");
            try {
                const res = await fetch('/api/delete', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ path })
                });
                const data = await res.json();
                if(data.success) {
                    if(currentFilePath === path) newFile();
                    await loadFiles();
                } else {
                    alert("Error: " + data.error);
                }
            } finally {
                hideLoading();
            }
        }

        function newFile() {
            currentFilePath = null;
            editor.value = "";
            filenameInput.value = "";
            updatePreview();
            loadFiles();
        }

        function updatePreview() {
            preview.innerHTML = marked.parse(editor.value || "*Content preview will appear here...*");
        }

        function insertFormat(type) {
            const start = editor.selectionStart;
            const end = editor.selectionEnd;
            const text = editor.value;
            const selected = text.substring(start, end);
            let before = "", after = "", placeholder = "text";
            
            switch(type) {
                case 'bold': before = "**"; after = "**"; break;
                case 'italic': before = "*"; after = "*"; break;
                case 'h1': before = "# "; placeholder = "Title"; break;
                case 'h2': before = "## "; placeholder = "Subtitle"; break;
                case 'list': before = "- "; break;
                case 'code': before = "```\n"; after = "\n```"; break;
                case 'image': before = "!["; after = "](https://)"; placeholder = "alt"; break;
            }

            const insertVal = selected || placeholder;
            editor.value = text.substring(0, start) + before + insertVal + after + text.substring(end);
            editor.focus();
            updatePreview();
        }

        async function save() {
            const filename = filenameInput.value.trim();
            const content = editor.value;
            if(!filename || !content) return alert("Required!");

            showLoading("Saving & Building...");
            try {
                const res = await fetch('/save', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ 
                        filename: currentFilePath || filename, 
                        content 
                    })
                });
                const data = await res.json();
                if(data.success) {
                    currentFilePath = data.path;
                    // Bersihkan input box setelah save
                    filenameInput.value = data.path.split('/').pop()
                                              .replace(/^\d+_/, '')
                                              .replace(/\.(md|ipynb)$/, '');
                    await loadFiles();
                    // Auto redirect ke halaman hasil build setelah save selesai
                    window.location.href = data.redirect;
                } else {
                    alert("Error: " + data.error);
                }
            } finally {
                hideLoading();
            }
        }

        loadFiles();
        updatePreview();
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    if MODE == "DEVELOPMENT":
        print("\nDEV SERVER ACTIVE!")
        print("Book Link: http://127.0.0.1:5000")
        print("Canvas Link: http://127.0.0.1:5000/canvas\n")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("Production Mode Active.")
        app.run(host='0.0.0.0', port=5000, debug=False)
