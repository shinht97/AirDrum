import cv2
import mediapipe as mp
import numpy as np
from sound_player import play_drum_with_volume
from utils import get_hand_center

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)

# 타격 기준선 (Y축)
snare_y_threshold = 0.5

prev_state = {"Left": False, "Right": False}
prev_pos   = {"Left": None, "Right": None}

print("에어드럼 시작! 손을 움직여보세요.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks and result.multi_handedness:
        for hand_landmarks, hand_info in zip(result.multi_hand_landmarks, result.multi_handedness):
            label = hand_info.classification[0].label  # 'Left' or 'Right'
            x, y, z = get_hand_center(hand_landmarks.landmark)

            # 화면 픽셀 좌표로 변환
            px, py = int(x * w), int(y * h)

            # 손 중심에 원 그리기
            cv2.circle(frame, (px, py), 10, (0, 255, 0), -1)

            # 속도 계산 (X/Y 이동량만 사용)
            prev = prev_pos[label]
            velocity = 0.0
            if prev is not None:
                dx = x - prev[0]
                dy = y - prev[1]
                velocity = np.sqrt(dx*dx + dy*dy)
            prev_pos[label] = (x, y, z)

            # 볼륨 결정 (속도 기반)
            volume = min(max(velocity * 100, 0.2), 1.0)

            # 기준선 아래로 내려오면 타격
            if y > snare_y_threshold:
                if not prev_state[label]:
                    drum_type = 'snare' if label == 'Right' else 'hihat'
                    # play_drum_with_volume(drum_type, volume)
                    
                    print(drum_type, volume)
                    prev_state[label] = True
            else:
                prev_state[label] = False

            # (선택) 좌표 텍스트 표시
            cv2.putText(frame,
                        f"{label}: ({px},{py})",
                        (px + 15, py - 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 1)

    cv2.imshow("Air Drum - Hand Position Only", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC 종료
        break

cap.release()
cv2.destroyAllWindows()
