import streamlit as st
import instaloader
import requests
import base64
import io
from PIL import Image

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Warden", layout="centered", page_icon="📷")

st.markdown(
    "<h1 style='text-align:center;'>Warden</h1>",
    unsafe_allow_html=True
)

username = st.text_input("Enter Instagram username")

if username.strip():
    try:
        # ---------- LOAD PROFILE ----------
        L = instaloader.Instaloader()
        profile = instaloader.Profile.from_username(L.context, username)

        # ---------- DOWNLOAD PFP ----------
        pfp_url = str(profile.profile_pic_url)
        response = requests.get(pfp_url, timeout=10)
        pfp_base64 = base64.b64encode(response.content).decode()

        # ---------- CIRCULAR PFP ----------
        st.markdown(
            f"""
            <div style="display:flex; justify-content:center; margin-top:20px;">
                <img src="data:image/jpeg;base64,{pfp_base64}"
                     style="
                     width:160px;
                     height:160px;
                     border-radius:50%;
                     object-fit:cover;
                     border:3px solid #ddd;
                     "/>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ---------- NAME & BIO ----------
        st.markdown(
            f"""
            <h3 style="text-align:center; margin-bottom:5px;">
                {profile.full_name}
            </h3>
            <p style="text-align:center; max-width:400px; margin:auto;">
                {profile.biography if profile.biography else "No bio"}
            </p>
            """,
            unsafe_allow_html=True
        )

        # ---------- FOLLOWERS / FOLLOWING ----------
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f"<h4 style='text-align:center;'>Followers</h4>"
                f"<p style='text-align:center; font-size:22px;'>{profile.followers}</p>",
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"<h4 style='text-align:center;'>Following</h4>"
                f"<p style='text-align:center; font-size:22px;'>{profile.followees}</p>",
                unsafe_allow_html=True
            )

        st.divider()

        # ---------- MORE INFO ----------
        st.subheader("More Info")
        st.markdown(f"**Username:** `{profile.username}`")
        st.markdown(f"**Posts:** {profile.mediacount}")
        st.markdown(f"**Private:** {profile.is_private}")
        st.markdown(f"**Verified:** {profile.is_verified}")

        if profile.external_url:
            st.markdown(f"**External URL:** {profile.external_url}")

        st.divider()

        # ---------- POSTS SECTION ----------
        st.subheader("Recent Posts")
        
        # Get recent posts (limit to avoid rate limits, adjust as needed)
        posts = profile.get_posts()
        post_list = list(posts)[:12]  # Show up to 12 recent posts

        if not post_list:
            st.warning("No posts available (private account or no posts).")
        else:
            posts_container = st.container()
            
            # Create columns for grid display (4 columns)
            cols = st.columns(4)
            
            for idx, post in enumerate(post_list):
                col_idx = idx % 4
                with cols[col_idx]:
                    try:
                        # Get main image/video thumbnail
                        if post.typename == 'GraphSidecar':
                            # Carousel post: get first node
                            node = next(post.get_sidecar_nodes())
                            media_url = node.display_url if not node.is_video else node.video_url
                        else:
                            media_url = post.url if not post.is_video else post.video_url
                        
                        # Fetch and display image
                        response = requests.get(media_url, timeout=10)
                        img = Image.open(io.BytesIO(response.content))
                        
                        # Resize for thumbnail
                        img.thumbnail((300, 300))
                        
                        st.image(img, use_column_width=True)
                        
                        # Post caption preview
                        caption = post.caption or "No caption"
                        st.caption(caption[:100] + "..." if len(caption) > 100 else caption)
                        
                        # Post date
                        st.caption(f"📅 {post.date.strftime('%Y-%m-%d')}")
                        
                    except Exception as post_error:
                        st.error("Error loading post")

    except Exception as e:
        st.error("❌ Unable to load profile (private, blocked, or rate-limited).")

    st.caption("@modified to show posts - original by Debayan Das")
