import numpy as np
from numpy import asarray, zeros, place, nan, mod, pi, extract, log, sqrt, exp, cos, sin, polyval, polyint
from struct import pack
import pyaudio


def sawtooth(t, width=1):
    t, w = asarray(t), asarray(width)
    w = asarray(w + (t - t))
    t = asarray(t + (w - w))
    if t.dtype.char in ['fFdD']:
        ytype = t.dtype.char
    else:
        ytype = 'd'
    y = zeros(t.shape, ytype)

    # width must be between 0 and 1 inclusive
    mask1 = (w > 1) | (w < 0)
    place(y, mask1, nan)

    # take t modulo 2*pi
    tmod = mod(t, 2 * pi)

    # on the interval 0 to width*2*pi function is
    #  tmod / (pi*w) - 1
    mask2 = (1 - mask1) & (tmod < w * 2 * pi)
    tsub = extract(mask2, tmod)
    wsub = extract(mask2, w)
    place(y, mask2, tsub / (pi * wsub) - 1)

    # on the interval width*2*pi to 2*pi function is
    #  (pi*(w+1)-tmod) / (pi*(1-w))

    mask3 = (1 - mask1) & (1 - mask2)
    tsub = extract(mask3, tmod)
    wsub = extract(mask3, w)
    place(y, mask3, (pi * (wsub + 1) - tsub) / (pi * (1 - wsub)))
    return y


def oscillator(fq, ph, t, a):
    phase_inc = 2.0*np.pi*fq/fs;
    synth_time=np.int(fs*t);
    signal=[]
    for i in range(0, synth_time):
        signal.append(a*sawtooth(ph))
        ph = ph + phase_inc;
    #place the phaser between the 0 and 2pi range
    ph = np.mod(ph, 2.0*np.pi);
    return signal, ph


def BPF(sig, fc):
    Q=10;
    N=len(sig)
    omega = 2 * pi * fc / fs;
    alpha = sin(omega)/(2*Q);
    B = [sin(omega)/2, 0, -sin(omega)/2];
    A = [1 + alpha, -2 * cos(omega), 1 - alpha];
    filt_sig=np.zeros(N);
    
    xmem1 = 0;
    xmem2 = 0;
    ymem1 = 0;
    ymem2 = 0;

    b0 = B[0] / A[0];
    b1 = B[1] / A[0];
    b2 = B[2] / A[0];
    a1 = A[1] / A[0];
    a2 = A[2] / A[0];


    for j in range(0, N):

        filt_sig[j] =b0*sig[j] + b1*xmem1 + b2*xmem2 - a1*ymem1 - a2*ymem2;
    
        xmem2 = xmem1;
        xmem1 = sig[j];
        ymem2 = ymem1;
        ymem1 = filt_sig[j];

    return filt_sig




f=150;
amp=0.9;
time = 0.5;
fs = 44100;
phase=0.0;


#Vowel Formants hertz F1 and F2 AEIOU table - PT_BR (Brazil)

#A
f1=800;
f2=1250;

sig_osc, phase=oscillator(f, phase, time, amp);
biquad_filt_Af1=BPF(sig_osc, f1);
biquad_filt_Af2=BPF(sig_osc, f2);

vowel_A=biquad_filt_Af2+biquad_filt_Af1


#E
f1=600;
f2=1600;

sig_osc, phase=oscillator(f, phase, time, amp);
biquad_filt_Ef1=BPF(sig_osc, f1);
biquad_filt_Ef2=BPF(sig_osc, f2);

vowel_E=biquad_filt_Ef2+biquad_filt_Ef1



#I
f1=300;
f2=2400;

sig_osc, phase=oscillator(f, phase, time, amp);
biquad_filt_If1=BPF(sig_osc, f1);
biquad_filt_If2=BPF(sig_osc, f2);

vowel_I=biquad_filt_If2+biquad_filt_If1



#Ó
f1=500;
#f1=550;
f2=700;

sig_osc, phase=oscillator(f, phase, time, amp);
biquad_filt_Of1=BPF(sig_osc, f1);
biquad_filt_Of2=BPF(sig_osc, f2);

vowel_O=biquad_filt_Of2+biquad_filt_Of1



#U
f1=300;
f2=750;

sig_osc, phase=oscillator(f, phase, time, amp);
biquad_filt_Uf1=BPF(sig_osc, f1);
biquad_filt_Uf2=BPF(sig_osc, f2);

vowel_U =biquad_filt_Uf2+biquad_filt_Uf1




ALL_vowels = 0.6 * np.concatenate([vowel_A,vowel_E,vowel_I,vowel_O,vowel_U])
ALL_vowels = np.clip(ALL_vowels, -1, 1)


# Initialize PyAudio
pyaud = pyaudio.PyAudio()


# Open stream
stream = pyaud.open(format =  pyaudio.paFloat32,
               channels = 1,
               rate = fs,
               output = True)



print("Playing AEIOU...")

out = pack("%df"%len(ALL_vowels), *(ALL_vowels))
stream.write(out)



#speak OI(hi in portuguese)

#O
f1=500;
f2=800;

time = 0.5;

sig_osc, phase=oscillator(f, phase, time, amp);
biquad_filt_Of1=BPF(sig_osc, f1);
biquad_filt_Of2=BPF(sig_osc, f2);

vowel_O=biquad_filt_Of2+biquad_filt_Of1


#I
f1=300;
f2=2400;

time = 0.7;

sig_osc, phase=oscillator(f, phase, time, amp);
biquad_filt_If1=BPF(sig_osc, f1);
biquad_filt_If2=BPF(sig_osc, f2);

vowel_I=biquad_filt_If2+biquad_filt_If1


HI = 0.6 * np.concatenate([vowel_O,vowel_I])
HI = np.clip(HI, -1, 1)

print("Playing OIII...")

out = pack("%df"%len(HI), *(HI))
stream.write(out)

stream.close()
pyaud.terminate()

