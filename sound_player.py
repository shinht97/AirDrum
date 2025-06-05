# sound_player.py
import pygame
import time

pygame.mixer.init()

sounds = {
    'HI_HAT1'    : pygame.mixer.Sound("./sounds/druuum/hi-hat_open_s.wav"),
    'HI_HAT2'    : pygame.mixer.Sound("./sounds/druuum/hi-hat_open_s.wav"),
    'SMALL_TAM'  : pygame.mixer.Sound("./sounds/druuum/low-tomtom_s.wav"),
    'LARGE_TAM'  : pygame.mixer.Sound("./sounds/druuum/hi-tomtom_s.wav"),
    'RIDE_CYMBAL': pygame.mixer.Sound("./sounds/druuum/ride_s.wav"),
    'SNARE'      : pygame.mixer.Sound("./sounds/druuum/snare-s.wav"),
    'FLOOR_TAM'  : pygame.mixer.Sound("./sounds/druuum/floar-tom_s.wav"),
    'BASE_DRUM'  : pygame.mixer.Sound("./sounds/druuum/bassD_s.wav"),
}

def play_drum(drum_name, volume=1.0):
    """해당 드럼 사운드를 지정된 볼륨으로 재생"""
    if drum_name in sounds:
        sound = sounds[drum_name]
        sound.set_volume(volume)
        sound.play()
    else:
        print(f"[Warning] Unknown drum: {drum_name}")

if __name__ == '__main__':
    print("Sound Player 테스트: 각 드럼 소리가 순차적으로 재생됩니다.")
    for name in sounds:
        print(f"Playing {name}...")
        play_drum(name)
        time.sleep(1)  # 다음 소리까지 1초 대기
    print("테스트 완료.")