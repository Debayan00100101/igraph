import streamlit as st
import instaloader
import requests
import base64
from PIL import Image
import io

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Warden", layout="centered", page_icon="📷")

st.markdown(
    "<h1 style='text-align:center;'>Warden</h1>",
    unsafe_allow_html=True
)

# ---------- INSTAGRAM CREDENTIALS FROM STREAMLIT SECRETS ----------
INSTA_USERNAME = st.secrets["insta"]["username"]  # "_yes_its_warden_"
INSTA_PASSWORD = st.secrets["insta"]["password"]  # "!@#$%^&*()_+{}:\"<>?"

# ---------- AUTO LOGIN (Hidden from UI) ----------
if 'L' not in st.session_state:
    try:
        L = instaloader.Instaloader()
        L.login(INSTA_USERNAME, INSTA_PASSWORD)
        st.session_state.L = L
        st.session_state.logged_in = True
    except:
        st.session_state.L = instaloader.Instaloader()
        st.session_state.logged_in = False

# ---------- LOGIN STATUS ----------
if st.session_state.logged_in:
    st.sidebar.success("✅ Auto-logged in!")
else:
    st.sidebar.warning("⚠️ Login failed - using anonymous mode")

username = st.text_input("")

if username.strip():
    try:
        profile = instaloader.Profile.from_username(st.session_state.L.context, username)

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
        st.markdown(f"**Private:** {'🔒 Yes' if profile.is_private else 'No'}")
        st.markdown(f"**Verified:** {'✅ Yes' if profile.is_verified else 'No'}")

        if profile.external_url:
            st.markdown(f"**External URL:** {profile.external_url}")

        st.divider()

        # ---------- POSTS SECTION ----------
        st.subheader("Recent Posts")
        
        @st.cache_data(ttl=3600)
        def get_recent_posts_cached(profile, count=12):
            return list(profile.get_posts())[:count]
        
        with st.spinner("Loading posts..."):
            posts = get_recent_posts_cached(profile, 12)

        if not posts:
            if profile.is_private:
                st.warning("🔒 Private account - login account doesn't follow this user.")
            else:
                st.warning("No posts available.")
        else:
            cols = st.columns(4)
            for idx, post in enumerate(posts):
                col_idx = idx % 4
                with cols[col_idx]:
                    try:
                        media_url = post.display_url if hasattr(post, 'display_url') else post.url
                        response = requests.get(media_url, timeout=5)
                        img = Image.open(io.BytesIO(response.content))
                        img.thumbnail((200, 200))
                        
                        st.image(img, use_column_width=True)
                        
                        caption = (post.caption or "No caption")[:50] + "..." if post.caption and len(post.caption) > 50 else (post.caption or "No caption")
                        st.caption(caption)
                        st.caption(f"📅 {post.date.strftime('%m/%d')}")
                        
                    except:
                        st.caption("Error loading post")

    except instaloader.exceptions.PrivateProfileNotFollowedException:
        st.error("❌ Private profile. Your account must follow this user first.")
    except instaloader.exceptions.ProfileNotExistsException:
        st.error("❌ Profile does not exist.")
    except Exception as e:
        st.error("❌ Unable to load profile.")

st.caption("@secrets integrated - no UI login needed")
