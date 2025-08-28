# app.py
from __future__ import annotations
import os
import io
import shutil
import tempfile
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr

import gradio as gr

# Load environment variables from either ".env" or "env (1)"
try:
    from dotenv import load_dotenv
    load_dotenv()            # .env
    load_dotenv("env (1)")   # env (1)
except Exception:
    pass

# Import your pipeline (tTesting.py must be in the same folder)
from tTesting import TextCorrector
from langchain_anthropic import ChatAnthropic


# --- helper to run your async .process(...) cleanly ---
import asyncio
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    if loop.is_running():
        import threading
        res = {"val": None, "err": None}
        def _runner():
            try:
                res["val"] = asyncio.run(coro)
            except Exception as e:
                res["err"] = e
        t = threading.Thread(target=_runner, daemon=True)
        t.start(); t.join()
        if res["err"]:
            raise res["err"]
        return res["val"]
    else:
        return loop.run_until_complete(coro)


def process_docx(file_obj):
    if file_obj is None:
        return None, "Please upload a .docx file."

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None, "Missing ANTHROPIC_API_KEY in environment (.env or 'env (1)'))."

    # prepare temp workspace
    tmpdir = Path(tempfile.mkdtemp(prefix="ttesting_"))
    inp = tmpdir / Path(file_obj.name).name
    out = tmpdir / (inp.stem + "_corrected.docx")
    shutil.copy2(file_obj.name if hasattr(file_obj, "name") else file_obj, inp)

    # build LLM
    llm = ChatAnthropic(
        model="claude-3-5-haiku-20241022",
        temperature=0.1,
        api_key=api_key,
    )

    # run pipeline and capture logs
    log_buf = io.StringIO()
    try:
        with redirect_stdout(log_buf), redirect_stderr(log_buf):
            corrector = TextCorrector(llm)
            run_async(corrector.process(str(inp), str(out)))

        if not out.exists():
            return None, "Processing finished but no output file was produced."

        # hand back a stable path for Gradio to serve
        return str(out), log_buf.getvalue()

    except Exception as e:
        import traceback
        return None, f"[ERROR] {e}\n\n{traceback.format_exc()}\n\nLogs:\n{log_buf.getvalue()}"


# --------- Gradio UI (minimal) ----------
with gr.Blocks(title="ISAS Copyediting") as demo:
    gr.Markdown("# ISAS Copyediting")
    file_in = gr.File(label="Upload .docx", file_types=[".docx"], type="filepath")
    run_btn = gr.Button("Run", variant="primary")
    file_out = gr.File(label="Download corrected .docx")
    logs = gr.Textbox(label="Logs", lines=12)

    run_btn.click(fn=process_docx, inputs=[file_in], outputs=[file_out, logs])

