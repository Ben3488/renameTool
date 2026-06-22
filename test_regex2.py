import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Simulate actual filenames from the user's NAS
# Pattern: NN.1080p.HD国语中字无水印[最新电影电视剧www.xxx.com].mkv
test_filenames = [
    "01.1080p.HD国语中字无水印[最新电影电视剧www.abc.com].mkv",
    "02.1080p.HD国语中字无水印[最新电影电视剧www.abc.com].mkv",
    "03.1080p.HD国语中字无水印[最新电影电视剧www.abc.com].mkv",
    "10.1080p.HD国语中字无水印[最新电影电视剧www.abc.com].mkv",
    "24.1080p.HD国语中字无水印[最新电影电视剧www.abc.com].mkv",
    # Other common formats
    "Show.Name.S01E02.1080p.mkv",
    "Show.Name.EP03.1080p.mkv",
    "劇名.第04集.1080p.mkv",
    "劇名 - 05 - 1080p.mkv",
    "E06.1080p.mkv",
    # Edge cases - should NOT match random numbers
    "1080p.sample.mkv",
]

# Current patterns
ep_patterns = [
    re.compile(r'[Ss]\d{1,2}[Ee](\d{1,2})'),
    re.compile(r'(?:^|[^a-zA-Z0-9])[Ee][Pp]?(\d{1,2})(?:[^a-zA-Z0-9]|$)'),
    re.compile(r'第\s*(\d{1,2})\s*[集話话期]'),
    re.compile(r'^(\d{1,2})(?:[^a-zA-Z0-9]|$)'),
    re.compile(r'(?:^|[^a-zA-Z0-9])(\d{1,2})(?:[^a-zA-Z0-9]|$)')
]

# Improved patterns - strip extension first, then match
ep_patterns_v2 = [
    # 1. S01E02 format (highest priority)
    re.compile(r'[Ss]\d{1,2}[Ee](\d{1,3})'),
    # 2. EP02 or E02 format
    re.compile(r'(?:^|[^a-zA-Z0-9])[Ee][Pp]?(\d{1,3})(?:[^a-zA-Z0-9]|$)'),
    # 3. Chinese format: 第04集
    re.compile(r'第\s*(\d{1,3})\s*[集話话期]'),
    # 4. Filename starts with episode number: "01.xxx" or "01 xxx"
    re.compile(r'^(\d{1,3})(?:\.|[ _\-])'),
    # 5. Dash/space separated number: " - 05 - " or ".05."
    re.compile(r'(?:^|[\.\-_ ])(\d{1,3})(?:[\.\-_ ]|$)'),
]

def extract_episode(filename, patterns):
    """Extract episode number from filename (without extension)."""
    name_no_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
    for i, pattern in enumerate(patterns):
        match = pattern.search(name_no_ext)
        if match:
            num = int(match.group(1))
            # Skip obviously wrong numbers (like 1080, 720, 480, 2160, etc.)
            if num in (1080, 720, 480, 2160, 264, 265, 50):
                continue
            return num, i
    return None, -1

print("=" * 70)
print("Testing CURRENT patterns (v1):")
print("=" * 70)
for fn in test_filenames:
    ep, idx = extract_episode(fn, ep_patterns)
    print(f"  Pattern#{idx} | EP={str(ep):>4s} | {fn}")

print()
print("=" * 70)
print("Testing IMPROVED patterns (v2):")
print("=" * 70)
for fn in test_filenames:
    ep, idx = extract_episode(fn, ep_patterns_v2)
    print(f"  Pattern#{idx} | EP={str(ep):>4s} | {fn}")
