import os
import subprocess
import glob
import re
import shutil
import logging
from flask import Flask, request, jsonify, render_template_string, send_from_directory, redirect, url_for

# Silence Flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# --- CONFIG & DETECTION ---
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_EXISTS = os.path.exists(os.path.join(ROOT_DIR, 'venv'))
MODE = os.environ.get("MODE", "DEVELOPMENT" if VENV_EXISTS else "PRODUCTION")
BUILD_DIR = os.path.join(ROOT_DIR, '_build', 'html')

def is_local_access():
    """Cek apakah akses berasal dari localhost atau 127.0.0.1"""
    # Cek IP remote
    remote = request.remote_addr
    # Cek Host header (untuk jaga-jaga kalau remote_addr terdistorsi)
    host = request.host.split(':')[0]
    return remote in ['127.0.0.1', 'localhost', '::1'] or host in ['127.0.0.1', 'localhost']

# --- UI TEMPLATES ---

RESTRICTED_HTML = r"""
<!DOCTYPE html>
<html>
<head>
    <title>Access Denied</title>
    <style>
        body { background: #0d1117; color: #c9d1d9; display: flex; align-items: center; justify-content: center; height: 100vh; font-family: sans-serif; text-align: center; margin: 0; }
        .box { padding: 40px; border: 1px solid #30363d; border-radius: 12px; background: #161b22; max-width: 450px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); }
        h1 { color: #f85149; margin-top: 0; }
        p { line-height: 1.6; font-size: 1.1rem; }
        code { background: #0d1117; padding: 2px 6px; border-radius: 4px; color: #58a6ff; }
        .footer { margin-top: 25px; font-size: 0.9rem; color: #8b949e; border-top: 1px solid #30363d; padding-top: 15px; }
    </style>
</head>
<body>
    <div class="box">
        <h1>Akses Dibatasi</h1>
        <p>Fitur <b>Markdown Canvas</b> hanya tersedia dalam mode <b>Development / Offline</b>.</p>
        <p>Server mendeteksi bahwa VENV tidak ditemukan atau akses berasal dari luar localhost.</p>
        <div class="footer">
            Silakan jalankan script berikut di komputer lokal Anda:<br>
            <code>./run.sh dev</code>
        </div>
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
            try {
                const res = await fetch('/api/files');
                if(!res.ok) throw new Error("Restricted");
                const files = await res.json();
                fileList.innerHTML = files.map(f => {
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
            } catch (e) {
                fileList.innerHTML = '<div style="padding:15px;color:#f85149;font-size:12px;">Access Restricted</div>';
            }
        }

        async function openFile(path) {
            const res = await fetch(`/api/read?path=${encodeURIComponent(path)}`);
            const data = await res.json();
            if(data.success) {
                currentFilePath = path;
                editor.value = data.content;
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
            const newCursor = start + before.length + insertVal.length + after.length;
            editor.setSelectionRange(newCursor, newCursor);
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
                    filenameInput.value = data.path.split('/').pop()
                                              .replace(/^\d+_/, '')
                                              .replace(/\.(md|ipynb)$/, '');
                    await loadFiles();
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

# --- LOGIC HELPERS ---

def get_editable_files():
    # Files that should NEVER be seen/edited
    blacklist = ['README.md', 'requirements.txt', '.nojekyll', '_toc.yml', '_config.yml', 'run.bat', 'run.sh']
    files = []
    
    # Root: allow intro.md to be edited
    for f in glob.glob("*.md"):
        if f not in blacklist:
            files.append(f)
            
    # md/ folder: add everything .md/.ipynb
    md_dir = os.path.join(ROOT_DIR, 'md')
    if os.path.exists(md_dir):
        for f in glob.glob(os.path.join(md_dir, "*.md")) + glob.glob(os.path.join(md_dir, "*.ipynb")):
            rel_path = os.path.relpath(f, ROOT_DIR).replace('\\', '/')
            files.append(rel_path)
            
    return sorted(list(set(files)))

def update_toc():
    ignore = ['README.md', 'requirements.txt', '.nojekyll', 'markdown.md', 'markdown-notebooks.md', 'notebooks.ipynb']
    files = []
    # Root
    for f in glob.glob("*.md") + glob.glob("*.ipynb"):
        if f not in ignore: 
            files.append(f)
    # md/
    md_dir = os.path.join(ROOT_DIR, 'md')
    if os.path.exists(md_dir):
        for f in glob.glob(os.path.join(md_dir, "*.md")) + glob.glob(os.path.join(md_dir, "*.ipynb")):
            if os.path.basename(f) not in ignore:
                files.append(os.path.relpath(f, ROOT_DIR))

    # Sort
    numbered = []
    non_numbered = []
    for f in files:
        basename = os.path.basename(f)
        if re.match(r'^\d+', basename): numbered.append(f)
        else: non_numbered.append(f)
    
    non_numbered.sort()
    numbered.sort(key=lambda x: int(re.match(r'^(\d+)', os.path.basename(x)).group(1)) if re.match(r'^(\d+)', os.path.basename(x)) else 0)
    final_list = numbered + non_numbered
    
    toc_content = "format: jb-book\nroot: intro\nchapters:\n"
    for f in final_list:
        # Skip root file from chapters list
        if f.replace('\\', '/') == 'md/intro.md' or f.replace('\\', '/') == 'intro.md':
            continue
            
        real_path = os.path.join(ROOT_DIR, f)
        title = os.path.splitext(os.path.basename(f))[0].replace('-', ' ').replace('_', ' ').title()
        try:
            with open(real_path, 'r', encoding='utf-8') as file:
                for _ in range(10):
                    line = file.readline()
                    if line.startswith('# '):
                        title = line.replace('# ', '').strip()
                        break
        except: pass
        
        jb_path = os.path.splitext(f.replace('\\', '/'))[0]
        toc_content += f"- file: {jb_path}\n  title: \"{title}\"\n"
    
    with open(os.path.join(ROOT_DIR, '_toc.yml'), 'w', encoding='utf-8') as f:
        f.write(toc_content)

def build_book():
    try:
        # Hard cleanup of build folder to prevent cache issues
        if os.path.exists(os.path.join(ROOT_DIR, '_build')):
            shutil.rmtree(os.path.join(ROOT_DIR, '_build'), ignore_errors=True)
            
        jb_bin = os.path.join(ROOT_DIR, 'venv', 'Scripts', 'jupyter-book.exe') if os.name == 'nt' else os.path.join(ROOT_DIR, 'venv', 'bin', 'jupyter-book')
        cmd = [jb_bin if os.path.exists(jb_bin) else "jupyter-book", "build", "--all", ROOT_DIR]
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        print(f"Build failed: {e}")
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
    abs_path = os.path.join(ROOT_DIR, path)
    if not path or not os.path.exists(abs_path):
        return jsonify(success=False, error="File not found")
    with open(abs_path, 'r', encoding='utf-8') as f:
        return jsonify(success=True, content=f.read())

@app.route('/api/delete', methods=['POST'])
def delete_file():
    if not VENV_EXISTS or not is_local_access(): return jsonify(success=False), 403
    path = request.json.get('path')
    abs_path = os.path.join(ROOT_DIR, path)
    if not path or not os.path.exists(abs_path):
        return jsonify(success=False, error="File not found")
    try:
        os.remove(abs_path)
        # Cleanup HTML build
        html_path = os.path.join(BUILD_DIR, os.path.splitext(path)[0] + '.html')
        if os.path.exists(html_path): os.remove(html_path)
        update_toc()
        build_book()
        return jsonify(success=True)
    except Exception as e: return jsonify(success=False, error=str(e))

@app.route('/save', methods=['POST'])
def save():
    if not VENV_EXISTS or not is_local_access(): return jsonify(success=False), 403
    data = request.json
    filename = data.get('filename')
    content = data.get('content')
    
    # Is it an existing relative path or a new filename?
    if '/' in filename or os.path.exists(os.path.join(ROOT_DIR, filename)):
        target_path = os.path.join(ROOT_DIR, filename)
    else:
        # New file auto-numbering
        files = get_editable_files()
        max_num = -1
        for f in files:
            match = re.search(r'(\d+)', os.path.basename(f))
            if match:
                num = int(match.group(1)); max_num = max(max_num, num)
        
        if not re.match(r'^\d+', filename) and filename.lower() != 'intro':
            filename = f"{(max_num + 1):02d}_" + filename.replace(' ', '-')
        
        if not filename.endswith('.md'): filename += '.md'
        target_path = os.path.join(ROOT_DIR, 'md', filename)

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    update_toc()
    if build_book():
        rel_path = os.path.relpath(target_path, ROOT_DIR).replace('\\', '/')
        clean_path = os.path.splitext(rel_path)[0]
        return jsonify(success=True, redirect=f"/{clean_path}.html", path=rel_path)
    return jsonify(success=False, error="Build failed")

@app.route('/')
def home():
    idx = os.path.join(BUILD_DIR, 'index.html')
    if not os.path.exists(idx):
        if VENV_EXISTS and is_local_access():
            return redirect(url_for('canvas'))
        return render_template_string(RESTRICTED_HTML), 403
    return send_from_directory(BUILD_DIR, 'index.html')

@app.route('/canvas.html')
def canvas_html():
    """Di dev mode: redirect ke canvas asli. Di prod: tampil restricted."""
    if VENV_EXISTS and is_local_access():
        return redirect(url_for('canvas'))
    return render_template_string(RESTRICTED_HTML), 403

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(BUILD_DIR, path)):
        return send_from_directory(BUILD_DIR, path)
    if os.path.exists(os.path.join(BUILD_DIR, path + '.html')):
        return send_from_directory(BUILD_DIR, path + '.html')
    return "File Not Found", 404

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5000
    if MODE == "DEVELOPMENT":
        print(f"\nDEV SERVER ACTIVE")
        print(f"Book: http://localhost:{port}")
        print(f"Canvas: http://localhost:{port}/canvas\n")
    else:
        print(f"\nPRODUCTION MODE (Access Restricted)")
    app.run(host=host, port=port, debug=False)
