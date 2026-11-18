"""3.2.4 Gradio demo: shows every agent's output for one request."""
import json


def build_app(system):
    import gradio as gr

    def run(file_obj, image_path, request, use_critique):
        path = file_obj or image_path  # the File box accepts broken/empty files for the failure demo
        st = system.run(request, path, use_critique=use_critique)
        gallery = [(g["image_path"], f"attempt {g['attempt']}") for g in st.generations]
        timings = [{"agent": t.agent, "seconds": t.seconds, "error": (t.error or "")[:200]} for t in st.trace]
        return (st.final_image_path or None, f"**Status:** {st.status}  \n**Route:** {st.route or '-'}  \n{st.message}",
                st.planner, st.vision, st.prompts, st.generations, st.critiques, gallery, timings,
                json.dumps(st.to_dict(), indent=1, default=str)[:20000])

    with gr.Blocks(title="DATA 266 - Multimodal Multi-Agent System") as demo:
        gr.Markdown("## Planner -> Vision -> Prompt Engineering -> Image Generation -> Critique")
        with gr.Row():
            with gr.Column():
                img = gr.Image(type="filepath", label="Input image (optional)")
                f = gr.File(type="filepath", label="...or upload any file (for broken-file tests)")
                req = gr.Textbox(label="Request", placeholder="e.g. Turn this into a watercolor painting")
                crit = gr.Checkbox(value=True, label="Use critique loop")
                btn = gr.Button("Run", variant="primary")
            with gr.Column():
                out_img = gr.Image(label="Final image")
                msg = gr.Markdown()
        with gr.Accordion("1. Planner", open=True):
            p = gr.JSON()
        with gr.Accordion("2. Vision Understanding", open=True):
            v = gr.JSON()
        with gr.Accordion("3. Prompt Engineering (per attempt)", open=True):
            pe = gr.JSON()
        with gr.Accordion("4. Image Generation (per attempt)", open=True):
            g = gr.JSON()
            gal = gr.Gallery(label="All attempts", columns=3, height=260)
        with gr.Accordion("5. Critique (per attempt)", open=True):
            c = gr.JSON()
        with gr.Accordion("Timing and full JSON trace", open=False):
            tm = gr.JSON()
            tr = gr.Code(language="json")
        btn.click(run, [f, img, req, crit], [out_img, msg, p, v, pe, g, c, gal, tm, tr])
    return demo


if __name__ == "__main__":  # python -m src.p3.app
    from .orchestrator import MultiAgentSystem
    build_app(MultiAgentSystem()).launch(share=True)
