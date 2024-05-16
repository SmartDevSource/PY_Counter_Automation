import time

def to_seconds(hh_mm):
    t = hh_mm.split(':')
    h, m = int(t[0]), int(t[1])
    next = (h*3600) + (m*60)

    # c = time.localtime()
    # ch, cm = c.tm_hour, c.tm_min
    # curr = (ch*3600) + (cm*60)

    return next

def round_to_half(h):
    s = h.split(':')
    hh, mm = s[0], s[1]
    round_mm = 30 if int(mm)/60 >= .5 else 0
    return f"{hh}:{round_mm:02}"