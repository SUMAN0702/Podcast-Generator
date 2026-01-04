import streamlit as st
import os
from elevenlabs import ElevenLabs
from blog_summarizer import summarize_blog

# Page configuration
st.set_page_config(
    page_title="AI Podcast Generator",
    page_icon="🎙️",
    layout="centered"
)

# Authentication (simple version for Streamlit)
def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] == "aipodcast"
            and st.session_state["password"] == "Welcome@2026"
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct
        return True

def process_url(url):
    """Process blog URL and generate podcast"""
    try:
        with st.spinner("🔍 Scraping blog content..."):
            # Get summary
            summary = summarize_blog(url)
        
        # Check if there was an error in summarization
        if summary.startswith("Error:"):
            return summary, None
        
        st.success("✅ Summary generated!")
        
        # Try to get ElevenLabs API key
        try:
            elevenlabs_key = st.secrets.get("ELEVENLABS_API_KEY")
        except:
            elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        
        if not elevenlabs_key:
            return summary, None
        
        with st.spinner("🎵 Generating podcast audio..."):
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
        
        st.success("🎉 Podcast generated successfully!")
        return summary, audio_file
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        st.error(error_msg)
        return error_msg, None

# Main app
def main():
    # Title and description
    st.title("🎙️ AI Podcast Generator")
    st.markdown("Enter a blog URL to generate a podcast episode from its content")
    
    # URL input
    url = st.text_input(
        "Blog URL",
        placeholder="https://example.com/blog-post",
        help="Enter the full URL of the blog post you want to convert"
    )
    
    # Generate button
    if st.button("🚀 Generate Podcast", type="primary", use_container_width=True):
        if not url:
            st.warning("⚠️ Please enter a blog URL")
        elif not url.startswith(('http://', 'https://')):
            st.error("❌ Please enter a valid URL (must start with http:// or https://)")
        else:
            # Process the URL
            summary, audio_file = process_url(url)
            
            # Display results
            if summary and not summary.startswith("Error:"):
                st.subheader("📝 Blog Summary")
                st.text_area(
                    "Summary",
                    value=summary,
                    height=200,
                    disabled=True,
                    label_visibility="collapsed"
                )
                
                if audio_file:
                    st.subheader("🔊 Podcast Audio")
                    st.audio(audio_file, format="audio/mp3")
                    
                    # Download button
                    with open(audio_file, "rb") as f:
                        st.download_button(
                            label="⬇️ Download Podcast",
                            data=f,
                            file_name="podcast_episode.mp3",
                            mime="audio/mp3",
                            use_container_width=True
                        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Made with ❤️ using AI | 
            <a href='https://github.com/yourusername/podcast-generator'>GitHub</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    if check_password():
        main()
