# utils.py

def get_hand_centers(landmarks_list, handedness_list):
    """
    MediaPipe 결과에서 각 손의 (label, x, y, z)를 normalized 좌표로 뽑아 반환.
    landmarks_list: result.multi_hand_landmarks
    handedness_list: result.multi_handedness
    """
    hands = []
    
    for lm_list, hand_info in zip(landmarks_list, handedness_list):
        
        label = hand_info.classification[0].label  # 'Left' or 'Right'
        
        xs = [lm.x for lm in lm_list.landmark]
        ys = [lm.y for lm in lm_list.landmark]
        zs = [lm.z for lm in lm_list.landmark]
        
        hands.append({
            'label': label,
            'x': sum(xs)/len(xs),
            'y': sum(ys)/len(ys),
            'z': sum(zs)/len(zs),
        })
        
    return hands