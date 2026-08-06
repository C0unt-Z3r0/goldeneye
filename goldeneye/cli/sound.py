"""
goldeneye/cli/sound.py
Toca o tema 007 via Windows Media Player.
"""

import os
import subprocess

THEME_MP3 = os.path.expanduser("~/goldeneye/assets/bond_theme.mp3")
THEME_WAV = "/tmp/goldeneye_bg.wav"


def play_theme():
    """Toca o tema 007."""
    # Tentar MP3 primeiro
    if os.path.exists(THEME_MP3) and os.path.getsize(THEME_MP3) > 0:
        os.system(f'cp "{THEME_MP3}" "/mnt/c/Users/Public/bond_theme.mp3" 2>/dev/null')
        subprocess.Popen(
            'powershell.exe -Command "Start-Process wmplayer -ArgumentList \'C:\\\\Users\\\\Public\\\\bond_theme.mp3\'"',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return
    
    # Fallback: WAV sintetizado
    _play_synth()


def _play_synth():
    """Toca versao sintetizada em WAV."""
    import numpy as np
    import struct

    E4, F4, G4, A4, B4 = 329.63, 349.23, 392.00, 440.00, 493.88
    C5, D5, E5, F5, G5, A5, B5 = 523.25, 587.33, 659.25, 698.46, 783.99, 880.00, 987.77
    C6, D6 = 1046.50, 1174.66

    notes = [
        (E4,0.12,0.02),(F4,0.12,0.02),(E4,0.12,0.02),(F4,0.12,0.05),
        (E4,0.12,0.02),(F4,0.12,0.02),(E4,0.12,0.02),(F4,0.12,0.05),(0,0.05,0.0),
        (D5,0.4,0.04),(0,0.06,0.0),(D5,0.08,0.02),(E5,0.16,0.02),
        (D5,0.08,0.02),(C5,0.16,0.02),(A4,0.08,0.04),(B4,0.24,0.02),(C5,0.08,0.02),
        (D5,0.16,0.02),(D5,0.08,0.02),(E5,0.16,0.02),(D5,0.08,0.02),
        (C5,0.16,0.02),(A4,0.08,0.04),(B4,0.24,0.02),(C5,0.08,0.02),(D5,0.35,0.15),
        (0,0.15,0.0),(D5,0.24,0.02),(E5,0.24,0.02),(F5,0.24,0.02),
        (E5,0.16,0.02),(D5,0.16,0.02),(C5,0.24,0.02),(A4,0.16,0.04),
        (B4,0.35,0.15),(0,0.2,0.0),(C6,0.12,0.02),(B5,0.12,0.02),
        (A5,0.12,0.02),(G5,0.24,0.04),(F5,0.24,0.04),(E5,0.24,0.04),
        (D5,0.5,0.15),(0,0.1,0.0),(D5,0.4,0.04),(0,0.06,0.0),
        (D5,0.08,0.02),(E5,0.16,0.02),(D5,0.08,0.02),(C5,0.16,0.02),
        (A4,0.08,0.04),(B4,0.24,0.02),(C5,0.08,0.02),(D5,0.16,0.02),
        (D5,0.08,0.02),(E5,0.16,0.02),(D5,0.08,0.02),(C5,0.16,0.02),
        (A4,0.08,0.04),(B4,0.24,0.02),(C5,0.08,0.02),(D5,0.4,0.04),
        (E5,0.24,0.02),(F5,0.35,0.04),(E5,0.16,0.02),(D5,0.24,0.02),
        (C5,0.16,0.02),(A4,0.16,0.04),(B4,0.24,0.02),(C5,0.12,0.02),
        (D5,0.5,0.04),(D5,0.24,0.0),(A5,0.24,0.0),(D6,0.7,0.0),
        (0,0.04,0.0),(D5,0.08,0.02),(0,0.04,0.0),(D5,0.12,0.3),
    ]

    sr = 22050
    all_samples = []
    for freq, dur, pause in notes:
        if freq > 0:
            t = np.linspace(0, dur, int(sr * dur), False)
            wave = np.sin(2*np.pi*freq*t)*0.6 + np.sin(4*np.pi*freq*t)*0.3 + np.sin(6*np.pi*freq*t)*0.15
            wave = np.tanh(wave*1.5)*0.8
            env = np.ones_like(wave)
            a = int(sr*0.008)
            r = int(sr*min(0.03, dur*0.3))
            if len(env) > a+r:
                env[:a] = np.linspace(0,1,a)
                env[-r:] = np.linspace(1,0,r)
            wave *= env
            all_samples.append((wave*32767*0.3).astype(np.int16))
        else:
            all_samples.append(np.zeros(int(sr*dur), dtype=np.int16))
        all_samples.append(np.zeros(int(sr*pause), dtype=np.int16))

    audio = np.concatenate(all_samples)
    data = audio.tobytes()
    with open(THEME_WAV, 'wb') as f:
        f.write(b'RIFF')
        f.write(struct.pack('<I', 36+len(data)))
        f.write(b'WAVE')
        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))
        f.write(struct.pack('<H', 1))
        f.write(struct.pack('<H', 1))
        f.write(struct.pack('<I', sr))
        f.write(struct.pack('<I', sr*2))
        f.write(struct.pack('<H', 2))
        f.write(struct.pack('<H', 16))
        f.write(b'data')
        f.write(struct.pack('<I', len(data)))
        f.write(data)

    os.system(f"cp {THEME_WAV} /mnt/c/Users/Public/goldeneye_bg.wav 2>/dev/null")
    subprocess.Popen(
        'powershell.exe -Command "Start-Process wmplayer -ArgumentList \'C:\\\\Users\\\\Public\\\\goldeneye_bg.wav\'"',
        shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
