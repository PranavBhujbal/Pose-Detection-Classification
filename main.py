
import streamlit as st
import mediapipe as mp
import cv2
import numpy as np
import tempfile
import time
from PIL import Image
import csv
import os
import pickle

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

DEMO_VIDEO = 'demo.mp4'

st.title('Pose detection and classification')
#for sidebar and margin
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 350px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 350px;
        margin-left: -350px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title('Pose detection and classification')
st.sidebar.subheader('Parameters')

@st.cache()#caching below function
def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image
    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized

app_mode = st.sidebar.selectbox('Choose the App mode',
['About App','Run on Video']
)

if app_mode =='About App':
    st.markdown('In this application we are using **MediaPipe** for creating a Face Mesh. **StreamLit** is to create the Web Graphical User Interface (GUI) ')
    st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 400px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 400px;
        margin-left: -400px;
    }
    </style>
    """,
    unsafe_allow_html=True,
    )


    st.markdown('''
          # About  \n
          This project implementation demonstrates human pose estimation and classification. It requires an advanced human skeleton extraction approach along with machine learning classification methods to recognize daily events precisely.\n
In this project, we use new technology such as MediaPipe Holistic model which provides pose, face, and hand landmark detection models which parses the frames obtained through real-time device feed using OpenCV through our MediaPipe Holistic model and provide a total of 501 landmarks(face - 468 and pose - 33) which is exported as coordinates to a CSV file upon which we train a custom multi-class classification model to understand the relationship between the class and coordinates to classify and detect custom body language pose. 
The machine learning classification algorithms implemented in this paper are random forest, linear regression, ridge classifier, and gradient boosting classifier 
          
            ''')
elif app_mode =='Run on Video':

    st.set_option('deprecation.showfileUploaderEncoding', False)

    use_webcam = st.sidebar.button('Use Webcam')
    record = st.sidebar.checkbox("Record Video")
    if record:
        st.checkbox("Recording", value=True)

    st.sidebar.markdown('---')
    st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 400px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 400px;
        margin-left: -400px;
    }
    </style>
    """,
    unsafe_allow_html=True,
        )
    
    detection_confidence = st.sidebar.slider('Min Detection Confidence', min_value =0.0,max_value = 1.0,value = 0.5)
    tracking_confidence = st.sidebar.slider('Min Tracking Confidence', min_value = 0.0,max_value = 1.0,value = 0.5)

    st.sidebar.markdown('---')

    st.markdown(' ## Output')

    stframe = st.empty()
    video_file_buffer = st.sidebar.file_uploader("Upload a video", type=[ "mp4", "mov",'avi','asf', 'm4v' ])
    tfflie = tempfile.NamedTemporaryFile(delete=False)


    if not video_file_buffer:
        if use_webcam:
            FRAME_WINDOW = st.image([])
            cap = cv2.VideoCapture(0)
             _, frame = camera.read()
             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
             FRAME_WINDOW.image(frame)
            
        else:
            cap = cv2.VideoCapture(DEMO_VIDEO)
            tfflie.name = DEMO_VIDEO
    
    else:
        tfflie.write(video_file_buffer.read())
        cap = cv2.VideoCapture(tfflie.name)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_input = int(cap.get(cv2.CAP_PROP_FPS))

    #codec = cv2.VideoWriter_fourcc(*FLAGS.output_format)
    codec = cv2.VideoWriter_fourcc('V','P','0','9')
    out = cv2.VideoWriter('output1.mp4', codec, fps_input, (width, height))

    st.sidebar.text('Input Video')
    st.sidebar.video(tfflie.name)
    fps = 0
    i = 0


    kpi1, kpi2 = st.columns(2)

    with kpi1:
        st.markdown("**FrameRate**")
        kpi1_text = st.markdown("0")

    with kpi2:
        st.markdown("**Image Width**")
        kpi2_text = st.markdown("0")

    st.markdown("<hr/>", unsafe_allow_html=True)

    import pandas as pd
    from sklearn.model_selection import train_test_split

    data = pd.read_csv('coordss.csv')
    X = data.drop('class', axis=1)  # Features
    y = data['class']
    with open('body_language(rf).pkl', 'rb') as f:
        model = pickle.load(f)


    with mp_holistic.Holistic(
    min_detection_confidence=detection_confidence,
    min_tracking_confidence=tracking_confidence
    ) as holistic:
        prevTime = 0

        while cap.isOpened():
            i +=1
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(frame)

            frame.flags.writeable = True
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            mp_drawing.draw_landmarks(frame, results.face_landmarks, mp_holistic.FACEMESH_TESSELATION,
                                      mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
                                      mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1)
                                      )

            mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
                                      mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2)
                                      )


            mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                                      mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2)
                                      )


            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
                                      mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                      )

            # Export coordinates
            try:
                # Extract Pose landmarks
                pose = results.pose_landmarks.landmark
                pose_row = list(
                    np.array(
                        [[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in pose]).flatten())

                # Extract Face landmarks
                face = results.face_landmarks.landmark
                face_row = list(
                    np.array(
                        [[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in face]).flatten())

                # Concate rows
                row = pose_row + face_row

                # Make Detections
                X = pd.DataFrame([row])
                body_language_class = model.predict(X)[0]
                body_language_prob = model.predict_proba(X)[0]
                print(body_language_class, body_language_prob)

                # Get status box
                cv2.rectangle(frame, (0, 0), (250, 60), (245, 117, 16), -1)

                # Display Probability
                cv2.putText(frame, 'PROB'
                            , (15, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(frame, str(round(body_language_prob[np.argmax(body_language_prob)], 2))
                            , (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                # Display Class
                if (round(body_language_prob[np.argmax(body_language_prob)], 2) > 0.65):
                    cv2.putText(frame, 'CLASS'
                                , (95, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                    cv2.putText(frame, body_language_class.split(' ')[0]
                                , (90, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    # Grab ear coords
                    coords = tuple(np.multiply(
                        np.array(
                            (results.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_EAR].x,
                             results.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_EAR].y))
                        , [640, 480]).astype(int))

                    cv2.rectangle(frame,(coords[0], coords[1] + 5),(coords[0] + len(body_language_class) * 20, coords[1] - 30),(245, 117, 16), -1)
                    cv2.putText(frame, body_language_class, coords,cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            except:
                pass


            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

            currTime = time.time()
            fps = 1 / (currTime - prevTime)
            prevTime = currTime
            if record:
                #st.checkbox("Recording", value=True)
                out.write(frame)
            #Dashboard
            kpi1_text.write(f"<h1 style='text-align: center; color: red;'>{int(fps)}</h1>", unsafe_allow_html=True)

            kpi2_text.write(f"<h1 style='text-align: center; color: red;'>{width}</h1>", unsafe_allow_html=True)

            frame = cv2.resize(frame,(0,0),fx = 0.8 , fy = 0.8)
            frame = image_resize(image = frame, width = 640)
            stframe.image(frame,channels = 'BGR',use_column_width=True)

    st.text('Video Processed')

    output_video = open('output1.mp4','rb')
    out_bytes = output_video.read()
    st.video(out_bytes)

    cap.release()
    out. release()
