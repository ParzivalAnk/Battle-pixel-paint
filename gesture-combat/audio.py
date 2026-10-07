import math
import struct
import pygame

def generate_tone(freq, duration_sec, volume=0.3, wave_type='sine', decay=True):
    sample_rate = 44100
    n_samples = int(sample_rate * duration_sec)
    buf = bytearray()
    
    for i in range(n_samples):
        t = i / sample_rate
        env = (1.0 - t / duration_sec) if decay else 1.0
        
        if wave_type == 'sine':
            val = math.sin(2.0 * math.pi * freq * t)
        elif wave_type == 'square':
            val = 1.0 if math.sin(2.0 * math.pi * freq * t) >= 0 else -1.0
        elif wave_type == 'noise':
            import random
            val = random.uniform(-1.0, 1.0)
        elif wave_type == 'bell':
            val = 0.6 * math.sin(2.0 * math.pi * freq * t) + 0.4 * math.sin(4.0 * math.pi * freq * t)
        elif wave_type == 'sweep_down':
            cur_freq = freq * (1.0 - 0.7 * (t / duration_sec))
            val = math.sin(2.0 * math.pi * cur_freq * t)
        else:
            val = math.sin(2.0 * math.pi * freq * t)
            
        sample = int(val * env * volume * 32767)
        sample = max(-32767, min(32767, sample))
        buf.extend(struct.pack('<h', sample)) # 16-bit mono PCM
        
    return pygame.mixer.Sound(buffer=bytes(buf))

class SoundFX:
    def __init__(self):
        self.enabled = False
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.enabled = True
            self.s_slash = generate_tone(320, 0.12, volume=0.25, wave_type='sweep_down')
            self.s_hit = generate_tone(140, 0.15, volume=0.35, wave_type='square')
            self.s_crit = generate_tone(880, 0.25, volume=0.4, wave_type='bell')
            self.s_parry = generate_tone(1200, 0.3, volume=0.45, wave_type='bell')
            self.s_fumble = generate_tone(85, 0.22, volume=0.35, wave_type='square')
            self.s_dash = generate_tone(550, 0.18, volume=0.3, wave_type='sweep_down')
        except Exception as e:
            print(f"Audio init fallback: {e}")

    def play(self, name):
        if not self.enabled:
            return
        snd = getattr(self, f"s_{name}", None)
        if snd:
            snd.play()

if __name__ == '__main__':
    pygame.init()
    sfx = SoundFX()
    print("Testing sound generator: OK!")
