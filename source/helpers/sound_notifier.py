import simpleaudio as sa
import os
import multiprocessing

AUDIO_DIR = '/home/ilusha/Music'


def target():
    WAVE_PATH = os.path.join(AUDIO_DIR, 'coin.wav')
    wave_obj = sa.WaveObject.from_wave_file(WAVE_PATH)
    while True:
        play_obj = wave_obj.play()
        play_obj.wait_done()


def sound_notifier():
    p = multiprocessing.Process(target=target)
    p.start()
    input('Please, enter an any key to switch off this signal!!!!!!!!')
    p.terminate()


if __name__ == '__main__':
    sound_notifier()
