import gradio as gr
import os
from footnote_corrector import DocxFootnoteProcessor

def process_docx(file_obj):
    if file_obj is None:
        return None
    
    # Input and output paths
    input_path = file_obj.name
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_corrected{ext}"

    try:
        # Run the processor
        proc = DocxFootnoteProcessor(input_path=input_path, output_path=output_path)
        newfile = proc.process()
        return newfile
    except Exception as e:
        return str(e)

with gr.Blocks() as demo:
    gr.Markdown("## 📑 Footnote Corrector")
    with gr.Row():
        inp = gr.File(label="Upload DOCX file", file_types=[".docx"])
        out = gr.File(label="Download Corrected DOCX")

    run_btn = gr.Button("Process Document")

    run_btn.click(fn=process_docx, inputs=inp, outputs=out)

