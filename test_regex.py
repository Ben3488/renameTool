import re

EP_PATTERNS = [
    re.compile(r'[Ss]\d{1,2}[Ee](\d{1,2})'),
    re.compile(r'(?:^|[^a-zA-Z0-9])[Ee][Pp]?(\d{1,2})(?:[^a-zA-Z0-9]|$)'),
    re.compile(r'第\s*(\d{1,2})\s*[集話话期]'),
    re.compile(r'^(\d{1,2})(?:[^a-zA-Z0-9]|$)'),
    re.compile(r'(?:^|[^a-zA-Z0-9])(\d{1,2})(?:[^a-zA-Z0-9]|$)')
]

def extract_episode(filename):
    for pattern in EP_PATTERNS:
        match = pattern.search(filename)
        if match:
            return match.group(1)
    return None

test_cases = [
    "01.1080p.HD国语中字无水印[最新电影",
    "02.1080p.HD国语中字无水印[最新电影",
    "10.1080p.HD国语中字无水印[最新电影",
    "24.1080p.HD国语中字无水印[最新电影",
    "Show.Name.S01E02.1080p.mkv",
    "Show.Name.EP03.1080p.mkv",
    "劇名.第04集.1080p.mkv",
    "劇名 - 05 - 1080p.mkv",
    "Show.Name.1080p.50fps.E06.mkv",
    "1080p.07.mkv"
]

for tc in test_cases:
    print(f"{ascii(tc)} => {ascii(extract_episode(tc))}")
