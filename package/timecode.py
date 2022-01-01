
def tc_to_frame(hh, mm, ss, ff, frame_rate):
    return ff + (ss + mm*60 + hh*3600) * frame_rate


def frame_to_tc(fn, framerate):
    ff = fn % framerate
    s = fn // framerate
    return (s // 3600, s // 60 % 60, s % 60, ff)

def frame_to_tc_02(fn, framerate):
    ff = fn % framerate
    s = fn // framerate
    h= int(s // 3600)
    m= int(s // 60 % 60)

    H = str(h)
    if len(H)<2:
        H = '0' + H
    M = str(m)
    if len(M)<2:
        M = '0'+M
    S = str(int(s % 60))
    if len(S)<2:
        S = '0'+S
    F = str(ff)
    if len(F)<2:
        F = '0'+F

    return f"{H}:{M}:{S}:{F}"
    #return f"{h}:{m}:{int(s % 60)}:{int(ff)}"


def tc_split(timecode):
    a = timecode.split(':')
    if len(a) < 4:
        return False
    return int(a[0]), int(a[1]),int(a[2]),int(a[3])

def tc_str_to_frames(timecode, framerate):
    a = timecode.split(':')
    if len(a) < 4:
        return False
    return tc_to_frame(int(a[0]), int(a[1]), int(a[2]), int(a[3]), framerate)


if __name__ == '__main__':
   print(frame_to_tc(2462, 24))
   print(tc_to_frame(hh =0,mm=0,ss=1,ff=0,frame_rate=24))

