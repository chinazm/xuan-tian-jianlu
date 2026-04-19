#!/usr/bin/env python3
"""为玄天剑录生成背景音乐和音效。"""
import numpy as np
import os
import subprocess

SR = 44100
DURATION = 30  # 秒
OUTDIR = os.path.join(os.path.dirname(__file__), 'assets', 'music')
SFXDIR = os.path.join(os.path.dirname(__file__), 'assets', 'audio')

os.makedirs(OUTDIR, exist_ok=True)
os.makedirs(SFXDIR, exist_ok=True)

# ====== 基础工具函数 ======
def to_audio(samples):
    """将 numpy 数组归一化到 [-1, 1] 并转为 int16."""
    max_val = np.max(np.abs(samples))
    if max_val > 0:
        samples = samples / max_val * 0.9
    return (samples * 32767).astype(np.int16)

def save_ogg(samples, filename):
    """保存为 OGG 文件."""
    data = to_audio(samples)
    wav_path = filename.replace('.ogg', '.wav')
    subprocess.run(['ffmpeg', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1',
                    '-i', wav_path.replace('.wav', '_raw.bin'),
                    filename], capture_output=True)

def save_ogg_v2(samples, filename):
    """保存为 OGG 文件 - 改进版本."""
    data = to_audio(samples)
    # 写 WAV header + data
    import wave, io
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(data.tobytes())
    buf.seek(0)
    
    # 用 ffmpeg 转 OGG
    wav_tmp = '/tmp/_music_temp.wav'
    ogg_tmp = filename
    with open(wav_tmp, 'wb') as f:
        f.write(buf.read())
    
    subprocess.run(['ffmpeg', '-y', '-i', wav_tmp, '-c:a', 'libvorbis', '-q:a', '4',
                    ogg_tmp], capture_output=True, timeout=30)
    os.remove(wav_tmp)

def tone(freq, duration, vol=0.3, wave_type='sine'):
    """生成单音."""
    t = np.linspace(0, duration, int(SR * duration), False)
    if wave_type == 'sine':
        return np.sin(2 * np.pi * freq * t) * vol
    elif wave_type == 'triangle':
        return 2 * np.abs(2 * (freq * t - np.floor(0.5 + freq * t))) - 1
    elif wave_type == 'square':
        return np.sign(np.sin(2 * np.pi * freq * t)) * vol
    elif wave_type == 'sawtooth':
        return 2 * (freq * t - np.floor(0.5 + freq * t)) * vol

def pad_to_length(samples, length_sec):
    """填充到指定长度."""
    target = int(SR * length_sec)
    if len(samples) < target:
        return np.concatenate([samples, np.zeros(target - len(samples))])
    return samples[:target]

def crossfade(s1, s2, fade_dur=0.5):
    """交叉淡入淡出."""
    fade_samples = int(SR * fade_dur)
    if len(s1) < fade_samples or len(s2) < fade_samples:
        return np.concatenate([s1, s2])
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    s1[-fade_samples:] *= fade_out
    s2[:fade_samples] *= fade_in
    return np.concatenate([s1, s2])

# ====== 音符工具 ======
NOTE_FREQS = {
    'C3': 130.81, 'D3': 146.83, 'Eb3': 155.56, 'E3': 164.81, 'F3': 174.61,
    'G3': 196.00, 'Ab3': 207.65, 'A3': 220.00, 'Bb3': 233.08, 'B3': 246.94,
    'C4': 261.63, 'D4': 293.66, 'Eb4': 311.13, 'E4': 329.63, 'F4': 349.23,
    'G4': 392.00, 'Ab4': 415.30, 'A4': 440.00, 'Bb4': 466.16, 'B4': 493.88,
    'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99,
}

def melody(notes, note_dur=0.4, vol=0.2, wave_type='sine'):
    """根据音符序列生成旋律."""
    parts = []
    for note in notes:
        if note == 'R' or note is None:
            parts.append(np.zeros(int(SR * note_dur)))
        elif note in NOTE_FREQS:
            parts.append(tone(NOTE_FREQS[note], note_dur, vol, wave_type))
        else:
            parts.append(np.zeros(int(SR * note_dur)))
    return np.concatenate(parts)

def chord(freqs, duration, vol=0.1):
    """生成和弦."""
    return sum(tone(f, duration, vol) for f in freqs) / len(freqs)

def pad_chords(chord_progression, chord_dur=2.0, vol=0.08):
    """生成持续和弦伴奏."""
    parts = []
    for ch in chord_progression:
        parts.append(chord(ch, chord_dur, vol))
    result = np.concatenate(parts)
    return pad_to_length(result, DURATION)

# ====== 音乐曲目 ======
def gen_town_theme():
    """青石镇 - 温馨宁静的小镇音乐."""
    beats = np.zeros(SR * DURATION)
    # 主旋律 - 中国风五声音阶
    mel_notes = ['C4','D4','E4','G4','A4','G4','E4','D4',
                 'C4','E4','G4','A4','G4','E4','D4','C4',
                 'A3','C4','D4','E4','D4','C4','A3','G3',
                 'A3','C4','E4','D4','C4','A3','G3','A3']
    m = melody(mel_notes, 0.5, 0.15)
    m = pad_to_length(m, DURATION)
    
    # 和弦伴奏
    chords = pad_chords([
        [130.81, 164.81, 196.00], [146.83, 196.00, 246.94],
        [164.81, 220.00, 261.63], [196.00, 246.94, 293.66],
    ], 2.0, 0.06)
    
    return m * 0.7 + chords * 0.3

def gen_boss_battle():
    """Boss战 - 紧张激烈的战斗音乐."""
    beats = np.zeros(SR * DURATION)
    # 快速紧张旋律 - 小调
    mel_notes = ['C4','C4','Eb4','F4','G4','G4','F4','Eb4',
                 'D4','D4','F4','G4','Ab4','Ab4','G4','F4',
                 'Eb4','Eb4','G4','Ab4','Bb4','Bb4','Ab4','G4',
                 'F4','G4','Ab4','Bb4','C5','Bb4','Ab4','G4']
    m = melody(mel_notes, 0.25, 0.2, 'square')
    m = pad_to_length(m, DURATION)
    
    # 低音伴奏
    bass = pad_chords([
        [65.41, 77.78, 98.00], [69.30, 82.41, 110.00],
        [73.42, 87.31, 116.54], [77.78, 98.00, 130.81],
    ], 1.0, 0.12)
    
    # 鼓点模拟
    drum = np.zeros(SR * DURATION)
    for i in range(0, DURATION * 4, 4):  # 4拍/秒
        t = int(SR * i / 4)
        dur = int(SR * 0.05)
        if t + dur < len(drum):
            drum[t:t+dur] = np.random.randn(dur) * 0.3 * np.linspace(1, 0, dur)
    
    return m * 0.4 + bass * 0.3 + drum * 0.3

def gen_snow_field():
    """雪地 - 空灵冰冷的氛围音乐."""
    # 高音区缓慢旋律
    mel_notes = ['E5','D5','C5','G4',None,'A4','G4','E4',
                 'D5','C5','A4','G4',None,'A4','G4','E4',
                 'C5','D5','E5','D5',None,'C5','D5','E5',
                 'G4','A4','G4','E4',None,'D4','E4','G4']
    m = melody(mel_notes, 0.6, 0.12)
    m = pad_to_length(m, DURATION)
    
    # 空灵和弦
    chords = pad_chords([
        [164.81, 196.00, 246.94, 329.63], [146.83, 174.61, 220.00, 293.66],
        [130.81, 164.81, 196.00, 261.63], [110.00, 130.81, 164.81, 220.00],
    ], 3.0, 0.04)
    
    return m * 0.8 + chords * 0.5

def gen_mountain_theme():
    """山景 - 壮阔悠扬的主题."""
    mel_notes = ['G3','C4','E4','G4','A4','G4','E4','C4',
                 'D4','G4','B4','D5','B4','G4','D4','G3',
                 'C4','E4','G4','A4','G4','E4','D4','C4',
                 'A3','C4','D4','E4','D4','C4','A3','G3']
    m = melody(mel_notes, 0.5, 0.15)
    m = pad_to_length(m, DURATION)
    
    chords = pad_chords([
        [196.00, 246.94, 293.66], [196.00, 246.94, 329.63],
        [146.83, 196.00, 246.94], [164.81, 207.65, 246.94],
    ], 2.0, 0.07)
    
    return m * 0.6 + chords * 0.4

def gen_tomb_hall():
    """古墓 - 阴森神秘的音乐."""
    mel_notes = ['A3','C4','Eb4','G4',None,'F4','Eb4','C4',
                 'B3','D4','F4','A4',None,'G4','F4','D4',
                 'A3','B3','C4','D4','Eb4','D4','C4','B3',
                 'A3','C4','Eb4','F4',None,'Eb4','C4','A3']
    m = melody(mel_notes, 0.5, 0.1)
    m = pad_to_length(m, DURATION)
    
    chords = pad_chords([
        [110.00, 130.81, 155.56], [98.00, 116.54, 146.83],
        [123.47, 146.83, 174.61], [110.00, 130.81, 164.81],
    ], 2.5, 0.05)
    
    return m * 0.7 + chords * 0.5

def gen_bamboo_fog():
    """竹林迷雾 - 幽静神秘."""
    mel_notes = ['D4','F4','A4','D5',None,'C5','A4','F4',
                 'G4','Bb4','D5','G5',None,'F5','D5','Bb4',
                 'A4','C5','D5','F5',None,'E5','D5','C5',
                 'G4','A4','C5','D5',None,'C5','A4','G4']
    m = melody(mel_notes, 0.45, 0.12)
    m = pad_to_length(m, DURATION)
    
    chords = pad_chords([
        [146.83, 174.61, 220.00], [130.81, 164.81, 196.00],
        [110.00, 146.83, 174.61], [130.81, 155.56, 196.00],
    ], 2.0, 0.05)
    
    return m * 0.7 + chords * 0.4

def gen_peak_theme():
    """山峰 - 高远开阔."""
    mel_notes = ['E4','G4','B4','E5',None,'D5','B4','G4',
                 'C5','E5','G5','C6',None,'B5','G5','E5',
                 'A4','C5','E5','A5',None,'G5','E5','C5',
                 'G4','B4','D5','G5',None,'F5','D5','B4']
    m = melody(mel_notes, 0.4, 0.14)
    m = pad_to_length(m, DURATION)
    
    chords = pad_chords([
        [164.81, 207.65, 246.94], [196.00, 246.94, 293.66],
        [130.81, 164.81, 196.00], [146.83, 196.00, 220.00],
    ], 2.0, 0.06)
    
    return m * 0.6 + chords * 0.4

def gen_sect_morning():
    """门派清晨 - 清新明朗."""
    mel_notes = ['C4','E4','G4','C5','G4','E4','C4','G3',
                 'D4','F4','A4','D5','A4','F4','D4','A3',
                 'E4','G4','B4','E5','B4','G4','E4','B3',
                 'C4','D4','E4','G4','A4','G4','E4','C4']
    m = melody(mel_notes, 0.4, 0.13)
    m = pad_to_length(m, DURATION)
    
    chords = pad_chords([
        [130.81, 164.81, 196.00], [146.83, 174.61, 220.00],
        [164.81, 207.65, 246.94], [196.00, 246.94, 293.66],
    ], 1.5, 0.06)
    
    return m * 0.6 + chords * 0.4

def gen_demon_valley():
    """魔谷 - 黑暗压抑."""
    mel_notes = ['C3','Eb3','G3','C4',None,'B3','G3','Eb3',
                 'D3','F3','Ab3','D4',None,'C4','Ab3','F3',
                 'Eb3','G3','B3','Eb4',None,'D4','B3','G3',
                 'F3','Ab3','C4','F4',None,'Eb4','C4','Ab3']
    m = melody(mel_notes, 0.5, 0.12, 'sawtooth')
    m = pad_to_length(m, DURATION)
    
    chords = pad_chords([
        [65.41, 77.78, 98.00], [73.42, 87.31, 103.83],
        [77.78, 98.00, 123.47], [87.31, 103.83, 130.81],
    ], 2.0, 0.1)
    
    return m * 0.4 + chords * 0.5

def gen_demon_mid():
    """魔谷深处 - 更黑暗."""
    mel_notes = ['A2','C3','Eb3','G3',None,'B2','D3','F3',
                 'A3','C4','Eb4','G4',None,'F4','Eb4','C4',
                 'G3','B3','D4','F4',None,'E4','D4','B3',
                 'A3','C4','Eb4','G4',None,'F4','Eb4','D4']
    m = melody(mel_notes, 0.45, 0.1, 'triangle')
    m = pad_to_length(m, DURATION)
    
    chords = pad_chords([
        [55.00, 65.41, 82.41], [61.74, 73.42, 92.50],
        [49.00, 58.27, 73.42], [55.00, 65.41, 77.78],
    ], 2.5, 0.08)
    
    return m * 0.5 + chords * 0.5

def gen_ice_valley():
    """冰谷 - 寒冷空灵."""
    mel_notes = ['E5','G5','A5','B5',None,'A5','G5','E5',
                 'D5','F5','A5','D6',None,'C6','A5','F5',
                 'G5','B5','D6','G6',None,'F6','D6','B5',
                 'A5','C6','E6','A6',None,'G6','E6','C6']
    m = melody(mel_notes, 0.35, 0.1)
    m = pad_to_length(m, DURATION)
    
    chords = pad_chords([
        [164.81, 196.00, 246.94, 329.63], [146.83, 174.61, 220.00, 293.66],
        [130.81, 164.81, 196.00, 261.63], [110.00, 130.81, 164.81, 220.00],
    ], 2.5, 0.04)
    
    return m * 0.8 + chords * 0.5

def gen_dragon_den():
    """龙巢 - 威严震撼."""
    mel_notes = ['G3','B3','D4','G4',None,'F4','D4','B3',
                 'A3','C4','E4','A4',None,'G4','E4','C4',
                 'D4','F4','A4','D5',None,'C5','A4','F4',
                 'G3','B3','D4','G4',None,'A4','G4','D4']
    m = melody(mel_notes, 0.4, 0.15, 'triangle')
    m = pad_to_length(m, DURATION)
    
    chords = pad_chords([
        [98.00, 123.47, 146.83], [110.00, 130.81, 164.81],
        [73.42, 98.00, 116.54], [98.00, 123.47, 146.83],
    ], 1.5, 0.08)
    
    # 鼓点
    drum = np.zeros(SR * DURATION)
    for i in range(0, int(DURATION * 2), 2):
        t = int(SR * i / 2)
        dur = int(SR * 0.15)
        if t + dur < len(drum):
            drum[t:t+dur] = np.sin(np.linspace(0, 20, dur)) * 0.2 * np.linspace(1, 0, dur)
    
    return m * 0.5 + chords * 0.4 + drum * 0.3

def gen_hall_music():
    """大厅音乐 - 庄严."""
    mel_notes = ['C4','E4','G4','C5','B4','G4','E4','C4',
                 'F4','A4','C5','F5','E5','C5','A4','F4',
                 'G4','B4','D5','G5','F5','D5','B4','G4',
                 'C4','D4','E4','G4','A4','G4','E4','C4']
    m = melody(mel_notes, 0.45, 0.12)
    m = pad_to_length(m, DURATION)
    
    chords = pad_chords([
        [130.81, 164.81, 196.00], [174.61, 220.00, 261.63],
        [196.00, 246.94, 293.66], [130.81, 155.56, 196.00],
    ], 2.0, 0.06)
    
    return m * 0.6 + chords * 0.4

def gen_quiet_room():
    """安静房间 - 轻柔."""
    mel_notes = ['E4','G4','A4','G4',None,'E4','D4','C4',
                 'A3','C4','D4','C4',None,'A3','G3','A3',
                 'C4','D4','E4','D4',None,'C4','A3','G3',
                 'A3','C4','E4','D4',None,'C4','A3','G3']
    m = melody(mel_notes, 0.55, 0.08)
    m = pad_to_length(m, DURATION)
    
    chords = pad_chords([
        [164.81, 207.65, 246.94], [146.83, 174.61, 220.00],
        [130.81, 164.81, 196.00], [146.83, 174.61, 220.00],
    ], 3.0, 0.04)
    
    return m * 0.7 + chords * 0.5

def gen_sect_entrance():
    """门派入口 - 庄严迎接."""
    mel_notes = ['G3','C4','E4','G4','A4','G4','E4','C4',
                 'D4','G4','B4','D5','B4','G4','D4','G3',
                 'A3','C4','E4','A4','G4','E4','C4','A3',
                 'G3','A3','B3','C4','D4','C4','A3','G3']
    m = melody(mel_notes, 0.4, 0.14)
    m = pad_to_length(m, DURATION)
    
    chords = pad_chords([
        [196.00, 246.94, 293.66], [196.00, 246.94, 329.63],
        [220.00, 261.63, 329.63], [196.00, 233.08, 293.66],
    ], 2.0, 0.06)
    
    return m * 0.6 + chords * 0.4

def gen_tomb_entrance():
    """古墓入口 - 神秘."""
    mel_notes = ['D3','F3','A3','D4',None,'C4','A3','F3',
                 'G3','Bb3','D4','G4',None,'F4','D4','Bb3',
                 'A3','C4','D4','F4',None,'E4','D4','C4',
                 'G3','A3','C4','D4',None,'C4','A3','G3']
    m = melody(mel_notes, 0.5, 0.1)
    m = pad_to_length(m, DURATION)
    
    chords = pad_chords([
        [73.42, 87.31, 110.00], [65.41, 77.78, 98.00],
        [55.00, 69.30, 82.41], [65.41, 77.78, 98.00],
    ], 2.5, 0.05)
    
    return m * 0.7 + chords * 0.5

def gen_tomb_deep():
    """古墓深处 - 幽暗."""
    mel_notes = ['A2','C3','Eb3','A3',None,'G3','Eb3','C3',
                 'D3','F3','Ab3','D4',None,'C4','Ab3','F3',
                 'Eb3','G3','Bb3','Eb4',None,'D4','Bb3','G3',
                 'A3','C4','Eb4','A4',None,'G4','Eb4','C4']
    m = melody(mel_notes, 0.6, 0.08, 'triangle')
    m = pad_to_length(m, DURATION)
    
    chords = pad_chords([
        [55.00, 65.41, 82.41], [73.42, 87.31, 110.00],
        [77.78, 98.00, 123.47], [55.00, 69.30, 87.31],
    ], 3.0, 0.05)
    
    return m * 0.6 + chords * 0.6

def gen_snow_field_ambient():
    """雪地环境音 - 风声效果."""
    noise = np.random.randn(SR * DURATION) * 0.05
    # 低通滤波模拟风声
    filtered = np.convolve(noise, np.ones(100) / 100, mode='same')
    
    mel = np.zeros(SR * DURATION)
    mel_notes = ['E5',None,'D5',None,'C5',None,'A4',None,
                 'G4',None,'A4',None,'C5',None,'D5',None]
    m = melody(mel_notes, 1.0, 0.06)
    m = pad_to_length(m, DURATION)
    
    return filtered * 0.5 + m * 0.5

# ====== 音效 ======
def gen_sfx_attack():
    """攻击音效."""
    t = np.linspace(0, 0.2, int(SR * 0.2), False)
    s = np.sin(2 * np.pi * 440 * t) * np.exp(-t * 20) * 0.3
    s += np.sin(2 * np.pi * 880 * t) * np.exp(-t * 30) * 0.1
    return s

def gen_sfx_hit():
    """受击音效."""
    t = np.linspace(0, 0.15, int(SR * 0.15), False)
    s = np.sin(2 * np.pi * 200 * t) * np.exp(-t * 25) * 0.3
    s += np.random.randn(len(t)) * 0.05 * np.exp(-t * 25)
    return s

def gen_sfx_pickup():
    """拾取物品音效."""
    t = np.linspace(0, 0.3, int(SR * 0.3), False)
    s = np.sin(2 * np.pi * 523 * t) * np.exp(-t * 8) * 0.2
    s += np.sin(2 * np.pi * 659 * (t - 0.1)) * np.exp(-(t-0.1) * 8) * 0.2 * (t > 0.1)
    return s

def gen_sfx_levelup():
    """升级音效."""
    s = np.zeros(int(SR * 0.6))
    notes = [523, 659, 784, 1047]
    for i, freq in enumerate(notes):
        t = np.linspace(0, 0.15, int(SR * 0.15), False)
        seg = np.sin(2 * np.pi * freq * t) * np.exp(-t * 5) * 0.2
        start = int(i * SR * 0.12)
        if start + len(seg) < len(s):
            s[start:start+len(seg)] += seg
    return s

def gen_sfx_footstep():
    """脚步声."""
    t = np.linspace(0, 0.1, int(SR * 0.1), False)
    s = np.random.randn(len(t)) * 0.1 * np.exp(-t * 30)
    return s

# ====== 主程序 ======
def main():
    tracks = [
        ('town_theme.ogg', gen_town_theme, '青石镇'),
        ('boss_battle.ogg', gen_boss_battle, 'Boss战'),
        ('snow_field.ogg', gen_snow_field, '雪地'),
        ('mountain_theme.ogg', gen_mountain_theme, '山峰'),
        ('tomb_hall.ogg', gen_tomb_hall, '古墓大厅'),
        ('bamboo_fog.ogg', gen_bamboo_fog, '竹林迷雾'),
        ('peak_theme.ogg', gen_peak_theme, '山峰主题'),
        ('sect_morning.ogg', gen_sect_morning, '门派清晨'),
        ('demon_valley.ogg', gen_demon_valley, '魔谷'),
        ('demon_mid.ogg', gen_demon_mid, '魔谷深处'),
        ('ice_valley.ogg', gen_ice_valley, '冰谷'),
        ('dragon_den.ogg', gen_dragon_den, '龙巢'),
        ('hall_music.ogg', gen_hall_music, '大厅'),
        ('quiet_room.ogg', gen_quiet_room, '安静房间'),
        ('sect_entrance.ogg', gen_sect_entrance, '门派入口'),
        ('tomb_entrance.ogg', gen_tomb_entrance, '古墓入口'),
        ('tomb_deep.ogg', gen_tomb_deep, '古墓深处'),
    ]
    
    sfx_tracks = [
        ('attack.ogg', gen_sfx_attack, '攻击'),
        ('hit.ogg', gen_sfx_hit, '受击'),
        ('pickup.ogg', gen_sfx_pickup, '拾取'),
        ('levelup.ogg', gen_sfx_levelup, '升级'),
        ('footstep.ogg', gen_sfx_footstep, '脚步'),
    ]
    
    print(f"生成 {len(tracks)} 首背景音乐...")
    for fname, gen_func, desc in tracks:
        path = os.path.join(OUTDIR, fname)
        print(f"  [{desc}] {fname}")
        samples = gen_func()
        save_ogg_v2(samples, path)
        print(f"    -> {path}")
    
    print(f"\n生成 {len(sfx_tracks)} 个音效...")
    for fname, gen_func, desc in sfx_tracks:
        path = os.path.join(SFXDIR, fname)
        print(f"  [{desc}] {fname}")
        samples = gen_func()
        save_ogg_v2(samples, path)
        print(f"    -> {path}")
    
    print("\n完成!")

if __name__ == '__main__':
    main()
