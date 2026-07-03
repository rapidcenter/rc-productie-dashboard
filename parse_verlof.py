#!/usr/bin/env python3
# Leest een Nmbrs iCal-feed en maakt er verlof.json van voor de 7 medewerkers.
# Gebruik: python3 parse_verlof.py feed.ics verlof.json
import sys, json, re
from datetime import date, timedelta

NAMES = ["Ticho Zomer","Maxym Ebeling","Nigel Stikker","Guido Saimbang",
         "Bram van Vliet","Geert van der Wouden","Niels van der Werff"]

def field(block, key):
    m = re.search(r'^'+key+r'[^:\r\n]*:(.*)$', block, re.M)
    return m.group(1).strip() if m else ''

def to_ymd(s):
    s = s.strip()[:8]
    return s[0:4]+'-'+s[4:6]+'-'+s[6:8]

def to_date(s):
    s = s.strip()[:8]
    return date(int(s[0:4]), int(s[4:6]), int(s[6:8]))

def person_of(desc):
    d = desc.replace('\\n', '\n').replace('\\,', ',')
    return d.split('\n')[0].strip()

def half_of(text):
    s = text.lower()
    if re.search(r'ochtend|voor 12|voor de middag', s): return 'am'
    if re.search(r'middag|na 12|vanaf 12|om 1[2-8][:\. ]|12:00|13:00|14:00|15:00', s): return 'pm'
    return None

def parse(text):
    leave = {n: [] for n in NAMES}
    for block in re.findall(r'BEGIN:VEVENT(.*?)END:VEVENT', text, re.S):
        desc = field(block, 'DESCRIPTION'); summ = field(block, 'SUMMARY')
        ds = field(block, 'DTSTART'); de = field(block, 'DTEND')
        if not ds or not de: continue
        name = person_of(desc)
        if name not in leave: continue
        try:
            d0 = to_date(ds); d1 = to_date(de)
        except Exception:
            continue
        entry = [to_ymd(ds), to_ymd(de)]
        # halve dag alleen bij een enkele dag (DTEND = DTSTART + 1)
        if (d1 - d0).days == 1:
            h = half_of(summ + ' ' + desc)
            if h: entry.append(h)
        leave[name].append(entry)
    return leave

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'feed.ics'
    out = sys.argv[2] if len(sys.argv) > 2 else 'verlof.json'
    text = open(src, encoding='utf-8', errors='replace').read()
    leave = parse(text)
    obj = {"generated": date.today().isoformat(), "names": NAMES, "leave": leave}
    open(out, 'w', encoding='utf-8').write(json.dumps(obj, ensure_ascii=False))
    tot = sum(len(v) for v in leave.values())
    print("verlof.json geschreven:", tot, "verlof-items over", len([n for n in NAMES if leave[n]]), "medewerkers")

if __name__ == '__main__':
    main()
