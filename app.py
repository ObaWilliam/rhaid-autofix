
import gradio as gr
import os, zipfile, tempfile, shutil, json, subprocess, sys, pathlib

HERE = os.path.dirname(__file__)
RHAID_SRC = os.path.join(HERE, "rhaid_src")

def ensure_rhaid():
    # add local source to path (vendored minimal cli)
    if RHAID_SRC not in sys.path:
        sys.path.insert(0, RHAID_SRC)

def extract_zip(zf, dest):
    with zipfile.ZipFile(zf, "r") as z:
        z.extractall(dest)

def make_zip(src_dir, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(src_dir):
            for f in files:
                ab = os.path.join(root, f)
                rel = os.path.relpath(ab, src_dir)
                z.write(ab, rel)

def clone_repo(repo_url, dest):
    try:
        subprocess.check_call(["git", "clone", "--depth", "1", repo_url, dest])
        return True, None
    except Exception as e:
        return False, str(e)

def run_rhaid(folder, mode, args):
    # call the vendored CLI
    ensure_rhaid()
    from rhaid_autofix import main as rhaid_main
    # Patch argv
    sys_argv = sys.argv
    try:
        sys.argv = ["rhaid_autofix.py", "--path", folder, "--mode", mode, "--json"] + (args.split() if args else [])
        from io import StringIO
        import contextlib
        buf = StringIO()
        with contextlib.redirect_stdout(buf):
            rhaid_main()
        out = buf.getvalue()
        try:
            data = json.loads(out)
        except Exception:
            data = {"raw": out}
        return data
    finally:
        sys.argv = sys_argv

def serve(zip_file, repo_url, mode, extra_args):
    td = tempfile.mkdtemp(prefix="rhaid_")
    if zip_file is not None:
        try:
            extract_zip(zip_file, td)
        except Exception as e:
            return {"error": f"Failed to extract ZIP: {e}"}, None
    elif repo_url:
        ok, err = clone_repo(repo_url, td)
        if not ok:
            return {"error": f"Failed to clone repo: {err}"}, None
    else:
        return {"error": "Please upload a ZIP or provide a repo URL."}, None
    try:
        data = run_rhaid(td, mode, extra_args or "")
    except Exception as e:
        return {"error": f"Rhaid failed: {e}"}, None
    out_zip = os.path.join(td, "rhaid_result.zip")
    make_zip(td, out_zip)
    return data, out_zip


with gr.Blocks() as demo:
    gr.Markdown("# Rhaid Autofix — run on a ZIP or Git repo")
    auth = gr.Textbox(label="Access Token (optional)", type="password")
    with gr.Row():
        up = gr.File(label="Project ZIP (.zip)", file_types=[".zip"])
        repo = gr.Textbox(label="Git Repo URL", placeholder="https://github.com/user/repo.git")
        mode = gr.Dropdown(choices=["scan", "fix"], value="scan", label="Mode")
    rules = gr.Textbox(label="Rules (e.g. +format:*,+json:*)", value="")
    extra = gr.Textbox(label="Extra args", value="--use-cache")
    run = gr.Button("Run")
    out_json = gr.JSON(label="Rhaid output")
    out_zip = gr.File(label="Result ZIP")
    def serve_with_auth(zip_file, repo_url, mode, rules, extra_args, token):
        args = extra_args or ""
        if rules:
            args += f" --rules {rules}"
        # Optionally use token for private repo access (future)
        return serve(zip_file, repo_url, mode, args)
    run.click(serve_with_auth, [up, repo, mode, rules, extra, auth], [out_json, out_zip])

if __name__ == "__main__":
    demo.launch()
