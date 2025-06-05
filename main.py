import cv2
import mediapipe as mp
from drum_place import DRUMS
from sound_player import play_drum
from utils import get_hand_centers

# 색상 정의 (BGR)
COLOR_BLACK = (0, 0, 0)
COLOR_RED   = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_WHITE = (255, 255, 255)

# Threshold
Z_DISABLE_THRESHOLD = -0.6  # 몸 전체가 너무 가까우면 비활성화
Z_HIT_THRESHOLD     = -0.012  # 손이 이보다 가까우면 타격
Z_BACK_THRESHOLD    = -0.008  # 손이 충분히 뒤로 간 상태로 인식
COOLDOWN_FRAMES = 2

# 출력 창 설정
WINDOW_NAME = "Air Drum"
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540

# 손 위치 디버그 출력 여부
SHOW_HAND_INFO = True

# 상태 저장
prev_hit  = {drum: False for drum in DRUMS}
cooldowns = {drum: 0     for drum in DRUMS}
hand_ready = {}  # 손이 뒤로 갔다가 앞으로 오는 것을 확인하기 위한 상태

# MediaPipe 초기화
mp_hands = mp.solutions.hands
mp_pose  = mp.solutions.pose
hands    = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
pose     = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, WINDOW_WIDTH, WINDOW_HEIGHT)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Pose & Hands 처리
    pose_result = pose.process(rgb)
    hand_result = hands.process(rgb)

    # 평균 거리 초기화
    avg_body_z = None
    disabled = False

    # 1. 몸 전체 depth 계산 (손 제외)
    hand_indices = {13, 14, 15, 16, 17, 18, 19, 20, 21, 22}
    if pose_result.pose_landmarks:
        z_list = [
            lm.z for idx, lm in enumerate(pose_result.pose_landmarks.landmark)
            if lm.visibility > 0.5 and idx not in hand_indices
        ]
        if z_list:
            avg_body_z = sum(z_list) / len(z_list)
            if avg_body_z <= Z_DISABLE_THRESHOLD:
                disabled = True

    # 2. 손 위치 및 z 수집
    hands_info = []
    if hand_result.multi_hand_landmarks and hand_result.multi_handedness:
        hands_info = get_hand_centers(
            hand_result.multi_hand_landmarks,
            hand_result.multi_handedness
        )

    # 손 위치 및 depth 시각화 (옵션)
    if SHOW_HAND_INFO:
        for hand in hands_info:
            px, py = int(hand['x'] * w), int(hand['y'] * h)
            pz = hand['z']
            cv2.circle(frame, (px, py), 8, (255, 255, 0), -1)
            cv2.putText(frame, f"{pz:.4f}", (px + 10, py - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 2)

    # 3. 드럼 처리
    for drum, ((x1, y1), (x2, y2)) in DRUMS.items():
        color = COLOR_BLACK

        if cooldowns[drum] > 0:
            cooldowns[drum] -= 1
        if cooldowns[drum] == 0:
            prev_hit[drum] = False

        if disabled:
            color = COLOR_BLACK
        else:
            for hand in hands_info:
                label = hand['label']
                px, py = int(hand['x'] * w), int(hand['y'] * h)
                pz = hand['z']

                if label not in hand_ready:
                    hand_ready[label] = False

                if pz > Z_BACK_THRESHOLD:
                    hand_ready[label] = True  # 손이 충분히 뒤로 갔다고 인식

                if x1 <= px <= x2 and y1 <= py <= y2:
                    if hand_ready[label] and pz <= Z_HIT_THRESHOLD:
                        if not prev_hit[drum]:
                            play_drum(drum)
                            prev_hit[drum]  = True
                            cooldowns[drum] = COOLDOWN_FRAMES
                            color = COLOR_GREEN
                            hand_ready[label] = False  # 재진입 대기
                        else:
                            color = COLOR_RED
                    else:
                        color = COLOR_RED
                    break
            else:
                color = COLOR_RED

        # 시각화
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness=3)
        cv2.putText(frame, drum, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR_WHITE, 2)

    # 평균 거리 시각화
    if avg_body_z is not None:
        cv2.putText(frame,
                    f"Avg Body Z: {avg_body_z:.2f}",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 0), 2)

    cv2.imshow(WINDOW_NAME, frame)
    if cv2.waitKey(1) & 0xFF in (27, ord('q')):
        break

cap.release()
cv2.destroyAllWindows()
