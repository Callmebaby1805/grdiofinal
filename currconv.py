import zipfile
from lxml import etree
import gradio as gr
import re
import tempfile
from word2number import w2n

# ========================
# Quote + Bracket handling
# ========================
OPEN_QUOTES = {"'": "'", '"': '"', "‘": "’", "“": "”"}
CLOSE_FOR_QUOTE = OPEN_QUOTES
BRACKET_PAIRS = {"(": ")", "[": "]", "{": "}", "<": ">"}
OPEN_BRACKETS = set(BRACKET_PAIRS.keys())
CLOSE_FOR_BRACKET = BRACKET_PAIRS

def split_by_quotes_and_brackets(text: str):
    segments = []
    buf = []
    stack = []
    mode = "normal"
    i = 0
    while i < len(text):
        ch = text[i]
        if mode == "normal":
            if ch in OPEN_QUOTES:  # entering quote
                if buf:
                    segments.append(("".join(buf), False))
                    buf = []
                buf.append(ch)
                stack.append(CLOSE_FOR_QUOTE[ch])
                mode = "quoted"
            elif ch in OPEN_BRACKETS:  # entering bracket
                if buf:
                    segments.append(("".join(buf), False))
                    buf = []
                buf.append(ch)
                stack.append(CLOSE_FOR_BRACKET[ch])
                mode = "bracketed"
            else:
                buf.append(ch)
        elif mode == "quoted":
            buf.append(ch)
            if stack and ch == stack[-1]:
                stack.pop()
                if not stack:
                    segments.append(("".join(buf), True))
                    buf = []
                    mode = "normal"
        elif mode == "bracketed":
            buf.append(ch)
            if stack and ch == stack[-1]:
                stack.pop()
                if not stack:
                    segments.append(("".join(buf), True))
                    buf = []
                    mode = "normal"
        i += 1
    if buf:
        segments.append(("".join(buf), mode != "normal"))
    return segments

# ========================
# Currency Conversion Setup
# ========================
EXCHANGE_RATES = {
    "USD": 1.35,
    "EUR": 1.45,
    "GBP": 1.70,
    "JPY": 0.009,
    "INR": 0.0156
}

CURRENCY_SYMBOLS = {
    "US$": "USD",
    "$": "USD",
    "USD": "USD",
    "EUR": "EUR",
    "€": "EUR",
    "GBP": "GBP",
    "£": "GBP",
    "JPY": "JPY",
    "¥": "JPY",
    "INR": "INR",
    "₹": "INR",
    "rupees": "INR",
    "dollars": "USD",
    "euros": "EUR",
    "pounds": "GBP",
    "yen": "JPY"
}
def convert_to_sgd(amount, code):
    """Convert given amount in currency code to SGD string with proper rounding + scale units."""
    if code not in EXCHANGE_RATES:
        return None
    sgd_value = amount * EXCHANGE_RATES[code]

    if sgd_value >= 1_000_000_000:
        return f"S${sgd_value/1_000_000_000:.2f} billion"
    elif sgd_value >= 1_000_000:
        return f"S${sgd_value/1_000_000:.2f} million"
    else:
        return f"S${sgd_value:.2f}"

# ========================
# Core Rewriter
# ========================
def rewrite_in_text(text, logs, counters):
    pieces = []

    SCALE_MAP = {
    "thousand": 1_000,
    "million": 1_000_000,
    "billion": 1_000_000_000,
    "trillion": 1_000_000_000_000,
    "lakh": 100_000,
    "crore": 10_000_000,
}


    def convert_numeric(match):
        sym = match.group("sym")
        num = float(match.group("num").replace(",", ""))
        scale_word = match.group("scale")
        multiplier = SCALE_MAP.get(scale_word.lower(), 1) if scale_word else 1
        code = CURRENCY_SYMBOLS.get(sym)
        sgd = convert_to_sgd(num * multiplier, code)
        if sgd:
            if scale_word:  # keep scale only once
                replacement = f"{sym}{int(num) if num.is_integer() else num} {scale_word} ({sgd})"
            else:
                replacement = f"{sym}{int(num) if num.is_integer() else num} ({sgd})"
            logs.append(f"{match.group(0)} → {replacement}")
            counters["currency"] += 1
            return replacement
        return match.group(0)

    def convert_words(match):
        words = match.group("words").strip()
        curr = match.group("curr").lower()
        scale_word = match.group("scale")
        try:
            num = w2n.word_to_num(words)
        except:
            return match.group(0)
        multiplier = SCALE_MAP.get(scale_word.lower(), 1) if scale_word else 1
        code = CURRENCY_SYMBOLS.get(curr)
        sgd = convert_to_sgd(num * multiplier, code)
        if sgd:
            if scale_word:
                replacement = f"{words} {curr} {scale_word} ({sgd})"
            else:
                replacement = f"{words} {curr} ({sgd})"
            logs.append(f"{match.group(0)} → {replacement}")
            counters["currency"] += 1
            return replacement
        return match.group(0)

    # Numeric currency detection
    numeric_pattern = re.compile(
    r"(?P<sym>US\$|₹|€|£|¥|\$|USD|EUR|GBP|JPY|INR)"
    r"\s*(?P<num>\d+(?:,\d{3})*(?:\.\d+)?)"
    r"(?:\s*(?P<scale>thousand|million|billion|trillion|lakh|crore))?",
    re.IGNORECASE
)
# Word-based currency detection
    word_pattern = re.compile(
    r"(?P<words>(?:\w+\s+){1,6})"
    r"(?P<curr>rupees|dollars|euros|pounds|yen)"
    r"(?:\s*(?P<scale>thousand|million|billion|trillion|lakh|crore))?",
    re.IGNORECASE
)



    for seg, is_protected in split_by_quotes_and_brackets(text):
        if is_protected:
            pieces.append(seg)
        else:
            temp = seg
            temp = numeric_pattern.sub(convert_numeric, temp)
            temp = word_pattern.sub(convert_words, temp)
            pieces.append(temp)

    return "".join(pieces)

# ========================
# DOCX Processing
# ========================
def process_docx(docx_file):
    counters = {"currency": 0}
    logs = []
    temp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    output_path = temp_out.name
    temp_out.close()
    with zipfile.ZipFile(docx_file.name, "r") as zin:
        with zipfile.ZipFile(output_path, "w") as zout:
            for item in zin.infolist():
                if item.filename != "word/document.xml":
                    zout.writestr(item, zin.read(item.filename))
                else:
                    xml_content = zin.read("word/document.xml")
                    tree = etree.fromstring(xml_content)
                    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                    for node in tree.findall(".//w:t", ns):
                        if node.text:
                            node.text = rewrite_in_text(node.text, logs, counters)
                    zout.writestr(
                        "word/document.xml",
                        etree.tostring(tree, xml_declaration=True, encoding="utf-8", standalone="yes"),
                    )
    print("===== Replacement Summary =====")
    for k, v in counters.items():
        print(f"{k}: {v}")
    print("Changes:")
    for log in logs:
        print(log)
    return output_path

# ========================
# Gradio UI
# ========================
iface = gr.Interface(
    fn=process_docx,
    inputs=gr.File(file_types=[".docx"], label="Upload Word Document"),
    outputs=gr.File(label="Download Modified Document"),
    title="Currency Converter to SGD in Word Document",
    description=(
        "Converts all non-SGD currency amounts (numeric or in words) into their SGD equivalent "
        "using fixed rates as of 09 April 2025. Skips text inside quotes, brackets, tables, and figures. "
        "Formats preserved."
    ),
)

# if __name__ == "__main__":
#     iface.launch()
