# position check for drum place for camera
# 화면상의 드럼 영역(좌상, 우하 좌표) 정의

DRUMS = {
    "HI_HAT1"   : [[75, 55], [395, 375]],
    "HI_HAT2"   : [[75, 385], [395, 705]],
    "SMALL_TAM" : [[505, 65], [850, 410]],
    "LARGE_TAM" : [[930, 65], [1275, 410]],
    "RIDE_CYMBAL" : [[1395, 150], [1850, 605]],
    "SNARE"     : [[360, 660], [705, 1005]],
    "FLOOR_TAM" : [[1375, 615], [1825, 1065]],
    "BASE_DRUM" : [[740, 480], [1325, 1065]],
}

def drumPlaceCheck():
    import cv2
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

    print(f"Camera width: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")
    print(f"Camera height: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    print("after set")
    print(f"Camera width: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")
    print(f"Camera height: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")

    cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Frame', 960, 540)

    while True:
        ret, frame = cap.read()
        
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # Flip the frame horizontally
            
        for drum, pos in DRUMS.items():
            cv2.putText(frame, drum, (pos[0][0], pos[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.rectangle(frame, pos[0], pos[1], (0, 0, 255), 2)
        
        cv2.imshow('Frame', frame)

        if cv2.waitKey(1) == ord('q'):
            break
        
    cv2.destroyAllWindows()
    cap.release()
        
if __name__ == "__main__":
    drumPlaceCheck()
