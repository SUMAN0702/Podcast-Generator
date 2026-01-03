import gradio as gr
import os

from elevenlabs import ElevenLabs

from blog_summarizer import summarize_blog

import gradio as gr
def process_url(url):
    summary = summarize_blog(url)
    print("Blog Summary:", summary)

    # Generate podcast audio using ElevenLabs
    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    response = client.text_to_speech.convert(
        text=summary[:350],
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_flash_v2_5",
        output_format="mp3_44100_128",
    )

    audio_file = "podcast_episode.mp3"
    with open(audio_file, "wb") as f:
        for chunk in response:
            f.write(chunk)

    print("Podcast audio generated successfully.")

    return "Podcast generation completed.", summary, audio_file



with gr.Blocks() as demo:
    gr.Markdown("# AI Podcast Generator")
    gr.Markdown("Enter a blog URL to generate a podcast episode from its content")

    with gr.Row():
        url_input = gr.Textbox(label="Blog URL", placeholder="https://example.com/blog-post")

    generate_btn = gr.Button("Generate Podcast")
    status_output = gr.Textbox(label="Status", lines=1)

    with gr.Row():
        summary_output = gr.Textbox(label="Blog Summary", placeholder="The blog summary will appear here...", lines=10)    

    with gr.Row():
        audio_output = gr.Audio(label="Podcast Audio")

    generate_btn.click(
        fn=process_url,
        inputs=[url_input],
        outputs=[status_output, summary_output, audio_output],
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7777, auth=("aipodcast", "Welcome@2026"))