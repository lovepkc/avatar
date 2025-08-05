import streamlit as st
import requests
import base64
from PIL import Image
import time

# 화면 하단에 SOLASiEU CI 표시
st.markdown(body="""
                <style>
                .footer {
                            position: fixed;
                            left: 0;
                            bottom: 0;
                            width: 100%;
                            background-color: #ffffff;
                            color: #87CEEB;
                            text-align: center;
                            padding: 10px;
                            border-top: 1px solid #ccc;
                            z-index: 9999;
                        }
                </style>

                <div class="footer">
                    <img src="https://solasieu.cafe24.com/web/upload/labeldesign/logo.png" width="100">
                </div>
            """, 
            unsafe_allow_html=True)


def encode_file_base64(file_obj):
        file_obj.seek(0)  # 파일 포인터 초기화
        
        return base64.b64encode(file_obj.read()).decode("utf-8")

X_API_KEY = st.secrets["X_API_KEY"]

# 아바타 생성 함수
def create_avatar_video(name: str, portrate, voice, speech: str)->str:
    
    headers = {"X-API-Key":X_API_KEY}
    
    payload_avatar = {
        "inline_data":{
            "mime_type":"image/jpg",
            "data":encode_file_base64(portrate)
        },
        "name":name
    }
    
    avatar_id = requests.post("https://openapi.visionstory.ai/api/v1/avatar", 
                             json=payload_avatar, headers=headers).json()["data"]["avatar_id"]
    
    # print("avatar_id", avatar_id)

    payload_voice = {
        "inline_data":{
            "mime_type":"audio/mp3",
            "data":encode_file_base64(voice)
        },
        "preview_text":"안녕하세요? 만나서 반갑습니다."
    }

    voice_id = requests.post("https://openapi.visionstory.ai/api/v1/voice", 
                             json=payload_voice, headers=headers).json()["data"]["voice_id"]


    # print("voice_id", voice_id)

    payload_video = {
        "model-id":"vs_talk_v1",
        "avatar_id":avatar_id,
        "text_script":{
            "text":speech,
            "voice_id":voice_id
        },
        "aspect_ratio":"9:16",
        "resolution":"480p"
    }

    video_id = requests.post("https://openapi.visionstory.ai/api/v1/video",
                             json=payload_video, headers=headers).json()["data"]["video_id"]
    
    # print("video_id", video_id)
    
    for i in range(100):
        video_url = requests.get(f"https://openapi.visionstory.ai/api/v1/video?video_id={video_id}",
                                 headers=headers).json()["data"]["video_url"]
    
        if video_url != "":

            # print("video_url", video_url)
            return video_url
        else:
            time.sleep(3)

st.sidebar.title("Setup")

image_avatar = st.sidebar.file_uploader("🙍‍♂️아바타 사진 파일을 업로드하세요!", type=['png', 'jpg', 'jpeg'])

if image_avatar:
     st.sidebar.image(Image.open(image_avatar), width=80)

voice_avatar = st.sidebar.file_uploader("🔊아바타 음성 파일을 업로드하세요!", type=['mp3', 'm4a'])

if voice_avatar:
     st.sidebar.audio(voice_avatar, format="audio/mp3")

speech_avatar = st.sidebar.text_area(label="🔠아바타 대사를 입력하세요!",
                             value="안녕하세요? 만나서 반갑습니다. 주식회사 솔라시우에서 현재 아바타 생성 시험 중입니다.",
                             height=100,
                             max_chars=100)

if st.sidebar.button("아바타 생성하기") and image_avatar and voice_avatar:

    with st.spinner("⏳ 아바타 영상 생성 중... 잠시만 기다려주세요!"):
         video_url = create_avatar_video(name="test",
                                          portrate=image_avatar,
                                          voice=voice_avatar,
                                          speech=speech_avatar)
         
         col1, col2 = st.columns([1, 1])
         
         with col1:
            st.video(video_url, format="video/mp4", autoplay=True)