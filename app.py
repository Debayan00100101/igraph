import streamlit as st
import instaloader
import requests
import base64

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Warden", layout="centered", page_icon="📷")

st.markdown(
    "<h1 style='text-align:center;'>Warden</h1>",
    unsafe_allow_html=True
)

username = st.text_input("")

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

    except Exception as e:
        st.error("❌ Unable to load profile (private, blocked, or rate-limited).")

st.caption("@created by Debayan Das")
