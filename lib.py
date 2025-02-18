import csv

def detect_delimiter(file_path, encoding):
    with open(file_path, mode="r", encoding=encoding) as file:
        sample = file.read(2048)
        sniffer = csv.Sniffer()
        return sniffer.sniff(sample, delimiters="|,;:\t").delimiter

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw = file.read(4)  # Read first few bytes

    # Check for BOM
    if raw.startswith(b'\xef\xbb\xbf'):  # UTF-8 BOM
        return "utf-8-sig"
    elif raw.startswith(b'\xff\xfe') or raw.startswith(b'\xfe\xff'):  # UTF-16 BOM
        return "utf-16"
    elif raw.startswith(b'\xff\xfe\x00\x00') or raw.startswith(b'\x00\x00\xfe\xff'):  # UTF-32 BOM
        return "utf-32"
    else:
        return "utf-8"  # Default if no BOM is found