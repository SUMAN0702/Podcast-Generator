import gradio as gr
import os

from elevenlabs import ElevenLabs
from blog_summarizer import summarize_blog

def process_url(url):
    """Process blog URL and generate podcast"""
    try:
        # Get summary
        summary = summarize_blog(url)
        print("Blog Summary:", summary)
        
        # Check if there was an error in summarization
        if summary.startswith("Error:"):
            return summary, summary, None
        
        # Try to get ElevenLabs API key from Streamlit secrets or environment
        try:
            import streamlit as st
            elevenlabs_key = st.secrets.get("ELEVENLABS_API_KEY")
        except:
            elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        
        if not elevenlabs_key:
            return "Summary generated but audio failed: ELEVENLABS_API_KEY not found", summary, None
        
        # Generate podcast audio using ElevenLabs
        client = ElevenLabs(api_key=elevenlabs_key)

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
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(error_msg)
        return error_msg, "", None


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
    # Get port from environment (for Streamlit Cloud) or use default
    port = int(os.getenv("PORT", 7860))
    
    # For Streamlit Cloud, don't specify server_name and use environment port
    try:
        # Try launching with auto port detection
        demo.launch(
            auth=("aipodcast", "Welcome@2026"),
            server_name="0.0.0.0",
            share=False
        )
    except:
        # Fallback for cloud environments
        demo.launch(auth=("aipodcast", "Welcome@2026"))
