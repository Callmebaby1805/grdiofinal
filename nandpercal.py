# # import zipfile
# # from lxml import etree
# # import gradio as gr
# # import re
# # import tempfile
# # from num2words import num2words
# # # ========================
# # # Quote + Bracket handling
# # # ========================
# # OPEN_QUOTES = {"'": "'", '"': '"', "‘": "’", "“": "”"}
# # CLOSE_FOR_QUOTE = OPEN_QUOTES
# # BRACKET_PAIRS = {"(": ")", "[": "]", "{": "}", "<": ">"}
# # OPEN_BRACKETS = set(BRACKET_PAIRS.keys())
# # CLOSE_FOR_BRACKET = BRACKET_PAIRS
# # def split_by_quotes_and_brackets(text: str):
# #     """
# #     Yield (segment, is_protected).
# #     Protects text inside quotes OR brackets (supports nesting).
# #     """
# #     segments = []
# #     buf = []
# #     stack = []
# #     mode = "normal"
# #     i = 0
# #     while i < len(text):
# #         ch = text[i]
# #         if mode == "normal":
# #             if ch in OPEN_QUOTES: # entering quote
# #                 if buf:
# #                     segments.append(("".join(buf), False))
# #                     buf = []
# #                 buf.append(ch)
# #                 stack.append(CLOSE_FOR_QUOTE[ch])
# #                 mode = "quoted"
# #             elif ch in OPEN_BRACKETS: # entering bracket
# #                 if buf:
# #                     segments.append(("".join(buf), False))
# #                     buf = []
# #                 buf.append(ch)
# #                 stack.append(CLOSE_FOR_BRACKET[ch])
# #                 mode = "bracketed"
# #             else:
# #                 buf.append(ch)
# #         elif mode == "quoted":
# #             buf.append(ch)
# #             if stack and ch == stack[-1]:
# #                 stack.pop()
# #                 if not stack:
# #                     segments.append(("".join(buf), True))
# #                     buf = []
# #                     mode = "normal"
# #         elif mode == "bracketed":
# #             buf.append(ch)
# #             if stack and ch == stack[-1]:
# #                 stack.pop()
# #                 if not stack:
# #                     segments.append(("".join(buf), True))
# #                     buf = []
# #                     mode = "normal"
# #         i += 1
# #     if buf:
# #         segments.append(("".join(buf), mode != "normal"))
# #     return segments
# # # ========================
# # # Subscript Map
# # # ========================
# # SUBSCRIPT_MAP = {
# #     '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
# #     '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
# # }
# # # ========================
# # # Date Normalization (from percalchem)
# # # ========================
# # def normalize_dates_and_ranges_in_text(text, logs, counters):
# #     # Month dictionary for abbreviations and full names (case-insensitive)
# #     month_dict = {
# #         'jan': 'January', 'january': 'January',
# #         'feb': 'February', 'february': 'February',
# #         'mar': 'March', 'march': 'March',
# #         'apr': 'April', 'april': 'April',
# #         'may': 'May',
# #         'jun': 'June', 'june': 'June',
# #         'jul': 'July', 'july': 'July',
# #         'aug': 'August', 'august': 'August',
# #         'sep': 'September', 'sept': 'September', 'september': 'September',
# #         'oct': 'October', 'october': 'October',
# #         'nov': 'November', 'november': 'November',
# #         'dec': 'December', 'december': 'December',
# #     }
# #     def expand_year(year_str):
# #         if len(year_str) == 4:
# #             return year_str
# #         elif len(year_str) == 2:
# #             yy = int(year_str)
# #             if yy <= 29:
# #                 return f"20{year_str.zfill(2)}"
# #             else:
# #                 return f"19{year_str.zfill(2)}"
# #         else:
# #             return year_str
# #     def replace_range(match):
# #         y1_str = match.group(1)
# #         y2_input = match.group(2)
# #         original = match.group(0)
# #         try:
# #             y1 = int(y1_str)
# #             prefix = y1_str[:2]
# #             y2 = int(prefix + y2_input.zfill(2))
# #             if y2 < y1:
# #                 # Try next century
# #                 next_prefix = str(int(prefix) + 1)
# #                 y2 = int(next_prefix + y2_input.zfill(2))
# #                 if y2 < y1:
# #                     return original
# #             if y2 < y1:
# #                 return original
# #             # Check if same century
# #             y2_str = str(y2)
# #             if y2_str[:2] == y1_str[:2]:
# #                 y2_display = y2_str[-2:]
# #             else:
# #                 y2_display = y2_str
# #             # Use en dash
# #             replacement = f"{y1}\u2013{y2_display}"
# #             logs.append(f"{original} → {replacement}")
# #             counters["year_span"] += 1
# #             return replacement
# #         except ValueError:
# #             return original
# #     def replace_day_first(match):
# #         day_str = match.group(1)
# #         month_str = match.group(2)
# #         year_str = match.group(3)
# #         original = match.group(0)
# #         month_lower = month_str.lower()
# #         if month_lower not in month_dict:
# #             return original
# #         full_month = month_dict[month_lower]
# #         # Remove ordinal suffixes
# #         day = re.sub(r'(st|nd|rd|th)$', '', day_str, flags=re.IGNORECASE).strip()
# #         expanded_year = expand_year(year_str)
# #         replacement = f"{day} {full_month} {expanded_year}"
# #         logs.append(f"{original} → {replacement}")
# #         counters["date"] += 1
# #         return replacement
# #     def replace_month_first(match):
# #         month_str = match.group(1)
# #         day_str = match.group(2)
# #         year_str = match.group(3)
# #         original = match.group(0)
# #         month_lower = month_str.lower()
# #         if month_lower not in month_dict:
# #             return original
# #         full_month = month_dict[month_lower]
# #         # Remove ordinal suffixes
# #         day = re.sub(r'(st|nd|rd|th)$', '', day_str, flags=re.IGNORECASE).strip()
# #         expanded_year = expand_year(year_str)
# #         replacement = f"{day} {full_month} {expanded_year}"
# #         logs.append(f"{original} → {replacement}")
# #         counters["date"] += 1
# #         return replacement
# #     # Apply year ranges
# #     range_pattern = r'(\d{4})-(\d{2}|\d{4})'
# #     text = re.sub(range_pattern, replace_range, text)
# #     # Year pattern for dates
# #     year_pattern = r'(\d{2}|\d{4})'
# #     # Apply day-month-year with negative lookbehind
# #     day_first_pattern = r'(?<!\d )(\d{1,2}(?:st|nd|rd|th)?)\s*([A-Za-z]+)\s*,?\s*' + year_pattern
# #     text = re.sub(day_first_pattern, replace_day_first, text, flags=re.IGNORECASE)
# #     # Apply month-day-year with negative lookbehind
# #     month_first_pattern = r'(?<!\d )([A-Za-z]+)\s*(\d{1,2}(?:st|nd|rd|th)?)\s*,?\s*' + year_pattern
# #     text = re.sub(month_first_pattern, replace_month_first, text, flags=re.IGNORECASE)
# #     return text
# # # ========================
# # # Chemical Normalization (from percalchem)
# # # ========================
# # def normalize_chemical_in_text(text, logs, counters):
# #     def chemical_replacer(match):
# #         term = match.group(0)
# #         original = term
# #         normalized = ''.join(SUBSCRIPT_MAP.get(c, c.upper()) for c in term)
# #         if normalized != original.upper(): # Check if subscripts were present
# #             logs.append(f"{original} → {normalized}")
# #             counters["chemical"] += 1
# #         return normalized
# #     # Pattern for terms likely containing subscripts (alphanumeric with possible subscripts)
# #     chemical_pattern = r'\b([A-Za-z0-9]*[₀₁₂₃₄₅₆₇₈₉]+[A-Za-z0-9]*)\b'
# #     text = re.sub(chemical_pattern, chemical_replacer, text)
# #     # Now handle units after numbers, adding parentheses for specific common units
# #     common_units = r'GTCO2|MTCO2|KTCO2|GTCO2EQ|MTCO2EQ|KTCO2EQ'
# #     def unit_parens_replacer(match):
# #         num = match.group(1)
# #         unit = match.group(2)
# #         original = match.group(0)
# #         replacement = f"{num} ({unit})"
# #         logs.append(f"{original} → {replacement}")
# #         counters["chemical_unit"] += 1
# #         return replacement
# #     unit_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s+(' + common_units + r')\b'
# #     text = re.sub(unit_pattern, unit_parens_replacer, text)
# #     return text
# # # ========================
# # # Percentage Rewriter (from percalchem)
# # # ========================
# # def rewrite_percentages_in_text(text, logs, counters):
# #     pieces = []
# #     def percent_symbol_replacer(match):
# #         num_str = match.group(1)
# #         original = match.group(0)
# #         try:
# #             num = float(num_str)
# #             if num.is_integer():
# #                 replacement = f"{int(num)} per cent"
# #             else:
# #                 replacement = f"{num_str}%"
# #         except ValueError:
# #             replacement = original
# #         logs.append(f"{original} → {replacement}")
# #         counters["%"] += 1
# #         return replacement
# #     def percent_word_replacer(match):
# #         num_str, unit = match.group(1), match.group(2).lower()
# #         original = match.group(0)
# #         try:
# #             num = float(num_str)
# #             if num.is_integer():
# #                 replacement = f"{int(num)} per cent"
# #             else:
# #                 replacement = f"{num_str}%"
# #         except ValueError:
# #             replacement = original
# #         logs.append(f"{original} → {replacement}")
# #         if unit == "percent":
# #             counters["percent"] += 1
# #         elif unit == "percentage":
# #             counters["percentage"] += 1
# #         elif unit == "per cent":
# #             counters["per cent"] += 1
# #         return replacement
# #     for seg, is_protected in split_by_quotes_and_brackets(text):
# #         if is_protected:
# #             pieces.append(seg)
# #         else:
# #             temp = re.sub(r"(\d+(?:\.\d+)?)\s*%", percent_symbol_replacer, seg)
# #             temp = re.sub(
# #                 r"\b(\d+(?:\.\d+)?)\s*(percent|percentage|per\s+cent)\b",
# #                 percent_word_replacer,
# #                 temp,
# #                 flags=re.IGNORECASE,
# #             )
# #             pieces.append(temp)
# #     return "".join(pieces)
# # # ========================
# # # PerCalChem Rewriter (combined dates, chemical, percentages)
# # # ========================
# # def percalchem_rewrite_in_text(text, logs, counters):
# #     pieces = []
# #     for seg, is_protected in split_by_quotes_and_brackets(text):
# #         if is_protected:
# #             pieces.append(seg)
# #         else:
# #             # Normalize dates and ranges
# #             temp = normalize_dates_and_ranges_in_text(seg, logs, counters)
# #             # Normalize chemical terms
# #             temp = normalize_chemical_in_text(temp, logs, counters)
# #             # Rewrite percentages
# #             temp = rewrite_percentages_in_text(temp, logs, counters)
# #             pieces.append(temp)
# #     return "".join(pieces)
# # # ========================
# # # Number Rewriter (from number)
# # # ========================
# # def spell_number(n: str, capitalize=False) -> str:
# #     """
# #     Spell out an integer or decimal number using num2words.
# #     For decimals (e.g., '10.4'), convert to 'ten point four'.
# #     """
# #     try:
# #         if '.' in n:
# #             integer_part, decimal_part = n.split('.')
# #             integer_words = num2words(int(integer_part), lang='en')
# #             decimal_words = ' point '.join(num2words(int(d), lang='en') for d in decimal_part)
# #             result = f"{integer_words} point {decimal_words}"
# #         else:
# #             result = num2words(int(n), lang='en')
# #         return result.capitalize() if capitalize else result
# #     except ValueError:
# #         return str(n)
# # # Reverse mapping of number words to numbers for currency conversion
# # number_words_to_num = {
# #     'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
# #     'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12,
# #     'thirteen': 13, 'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
# #     'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40,
# #     'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
# #     'hundred': 100, 'thousand': 1000, 'million': 1000000, 'billion': 1000000000,
# #     'crore': 10000000, 'lakh': 100000
# # }
# # def words_to_number(word: str) -> float:
# #     """
# #     Convert a number written in words (e.g., 'five', 'two hundred', 'five hundred crores') to a float.
# #     Handles simple cases up to crore.
# #     """
# #     try:
# #         words = word.lower().split()
# #         total = 0
# #         current = 0
# #         for w in words:
# #             if w in number_words_to_num:
# #                 num = number_words_to_num[w]
# #                 if num >= 100:
# #                     if current == 0:
# #                         current = 1 # Handle cases like "hundred" alone
# #                     current *= num
# #                 else:
# #                     current += num
# #             elif w == 'and':
# #                 continue
# #             else:
# #                 break # Stop at unrecognized words
# #         total += current
# #         return float(total) if total > 0 else float(word)
# #     except (ValueError, KeyError):
# #         try:
# #             return float(word) # Fallback to float conversion
# #         except ValueError:
# #             return 0.0 # Return 0 if conversion fails
# # def format_large_number(num):
# #     if num >= 1e9:
# #         return f"{num / 1e9:.2f} billion"
# #     elif num >= 1e6:
# #         return f"{num / 1e6:.2f} million"
# #     else:
# #         return f"{num:,.2f}"
# # def number_rewrite_in_text(text, logs, counters):
# #     """
# #     - Protect decimal percentages (e.g., 8.6%) and decimal numbers (e.g., 10.4) with placeholders.
# #     - Spell out integers 1–9; keep 10+ unless at sentence start.
# #     - Any integer or decimal at sentence start → spell out (including 10+).
# #     - For decimals > 1 followed by a noun and 'is', change 'is' to 'are' (e.g., '1.25 metres is' → 'one point two five metres are').
# #     - Protect currency amounts (e.g., $300, US$five million, five hundred rupees) and convert to SGD after text conversions.
# #     - Restore placeholders at the end.
# #     """
# #     # Placeholder store shared across segments
# #     placeholder_map = {}
# #     ph_counter = 0
# #     # Exchange rates (updated average over July 30–August 26, 2025)
# #     exchange_rates = {
# #         'S$': 1.0, # SGD/SGD
# #         'US$': 1.285, # USD/SGD
# #         '€': 1.496, # EUR/SGD
# #         '£': 1.726, # GBP/SGD
# #         '¥': 0.00871, # JPY/SGD
# #         '₹': 0.01466, # INR/SGD
# #         'rupees': 0.01466, # INR/SGD
# #     }
 
# #     # Regex for decimal percentages (e.g., "8.6%")
# #     pct_decimal_pattern = re.compile(r"(\d+\.\d+)\s*%")
# #     # Regex for decimal numbers (e.g., "10.4", "0.4")
# #     decimal_pattern = re.compile(r"\b(\d+\.\d+)\b")
# #     # Regex for decimals > 1 followed by noun and 'is' (e.g., "1.25 metres is")
# #     plural_pattern = re.compile(r"\b([1-9]\d*\.\d+)\s+(\w+)\s+is\b", re.IGNORECASE)
# #     # Regex for prefix currency amounts (e.g., "$300", "US$five million")
# #     prefix_pattern = re.compile(r"(([$€£¥₹]|[A-Z]{1,3}\$))\s*(__DEC_\d+__|[0-9.]+|[a-zA-Z\s]+?)(?:\s+(million|billion|crore|crores|lakh|lakhs))?\b", re.IGNORECASE)
# #     # Regex for suffix currency amounts (e.g., "five hundred rupees", "five hundred crores")
# #     suffix_pattern = re.compile(r"(__DEC_\d+__|[0-9.]+|[a-zA-Z\s]+?)(?:\s+(million|billion|crore|crores|lakh|lakhs))?\s*\b(rupees|crores|lakhs)\b", re.IGNORECASE)
# #     # Regex for ranges (e.g., "1980-1999")
# #     range_pattern = re.compile(r"\b(\d+-\d+)\b")
# #     # Regex for dates (e.g., "31 January 1999", "January 31, 1999")
# #     months = r"(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
# #     date_pattern1 = re.compile(r"\b(\d{1,2}\s+" + months + r"\s+\d{4})\b", re.IGNORECASE)
# #     date_pattern2 = re.compile(r"\b(" + months + r"\s+\d{1,2}(?:,\s*)?\d{4})\b", re.IGNORECASE)
 
# #     def protect_pct_decimals(s: str) -> str:
# #         nonlocal ph_counter
# #         def _repl(m):
# #             nonlocal ph_counter
# #             ph = f"__DEC_PCT_{ph_counter}__"
# #             placeholder_map[ph] = m.group(0) # full match, e.g., "8.6%"
# #             ph_counter += 1
# #             return ph
# #         return pct_decimal_pattern.sub(_repl, s)
 
# #     def protect_decimals(s: str) -> str:
# #         nonlocal ph_counter
# #         def _repl(m):
# #             nonlocal ph_counter
# #             ph = f"__DEC_{ph_counter}__"
# #             placeholder_map[ph] = m.group(0) # full match, e.g., "10.4"
# #             ph_counter += 1
# #             return ph
# #         return decimal_pattern.sub(_repl, s)
 
# #     def protect_ranges(s: str) -> str:
# #         nonlocal ph_counter
# #         def _repl(m):
# #             nonlocal ph_counter
# #             ph = f"__RANGE_{ph_counter}__"
# #             placeholder_map[ph] = m.group(0)
# #             ph_counter += 1
# #             return ph
# #         return range_pattern.sub(_repl, s)
 
# #     def protect_dates(s: str) -> str:
# #         nonlocal ph_counter
# #         def _repl(m):
# #             nonlocal ph_counter
# #             ph = f"__DATE_{ph_counter}__"
# #             placeholder_map[ph] = m.group(0)
# #             ph_counter += 1
# #             return ph
# #         s = date_pattern1.sub(_repl, s)
# #         s = date_pattern2.sub(_repl, s)
# #         return s
 
# #     def protect_currency(s: str) -> str:
# #         nonlocal ph_counter
# #         def prefix_repl(m):
# #             nonlocal ph_counter
# #             currency = m.group(1)
# #             if currency == '$':
# #                 currency = 'US$'
# #             amount = m.group(2)
# #             magnitude = m.group(3) if len(m.groups()) >= 3 else None
# #             ph = f"__CUR_{ph_counter}__"
# #             original = m.group(0)
# #             if currency == 'S$':
# #                 # Format large S$ amounts
# #                 try:
# #                     if amount.startswith('__DEC_'):
# #                         num = float(placeholder_map[amount])
# #                     else:
# #                         num = float(amount) if amount.replace('.', '').isdigit() else words_to_number(amount)
# #                     if num == 0.0:
# #                         placeholder_map[ph] = original
# #                         ph_counter += 1
# #                         return ph
# #                     if magnitude:
# #                         magnitude_lower = magnitude.lower()
# #                         multiplier = 1_000_000 if magnitude_lower == 'million' else 1_000_000_000 if magnitude_lower == 'billion' else 10_000_000 if magnitude_lower in ['crore', 'crores'] else 100_000 if magnitude_lower in ['lakh', 'lakhs'] else 1
# #                         num *= multiplier
# #                     formatted = f"S${format_large_number(num)}"
# #                     placeholder_map[ph] = f"{currency}{' ' if currency in ['rupees'] else ''}{amount}{' ' + magnitude if magnitude else ''} ({formatted})"
# #                     logs.append(f"Currency: {original} → {placeholder_map[ph]}")
# #                     counters["currency"] += 1
# #                 except ValueError:
# #                     placeholder_map[ph] = original
# #                     logs.append(f"Currency skipped (invalid amount): {original}")
# #                 ph_counter += 1
# #                 return ph
# #             if currency in exchange_rates:
# #                 try:
# #                     if amount.startswith('__DEC_'):
# #                         num = float(placeholder_map[amount])
# #                     else:
# #                         num = float(amount) if amount.replace('.', '').isdigit() else words_to_number(amount)
# #                     if num == 0.0:
# #                         placeholder_map[ph] = original # Skip if amount is invalid
# #                         ph_counter += 1
# #                         return ph
# #                     if magnitude:
# #                         magnitude_lower = magnitude.lower()
# #                         multiplier = 1_000_000 if magnitude_lower == 'million' else 1_000_000_000 if magnitude_lower == 'billion' else 10_000_000 if magnitude_lower in ['crore', 'crores'] else 100_000 if magnitude_lower in ['lakh', 'lakhs'] else 1
# #                         num *= multiplier
# #                     sgd = num * exchange_rates[currency]
# #                     sgd_formatted = f"S${format_large_number(sgd)}"
# #                     placeholder_map[ph] = f"{currency}{' ' if currency in ['rupees'] else ''}{amount}{' ' + magnitude if magnitude else ''} ({sgd_formatted})"
# #                     logs.append(f"Currency: {original} → {placeholder_map[ph]}")
# #                     counters["currency"] += 1
# #                 except ValueError:
# #                     placeholder_map[ph] = original # Keep original if conversion fails
# #                     logs.append(f"Currency skipped (invalid amount): {original}")
# #             else:
# #                 placeholder_map[ph] = original # Keep original for unknown currencies
# #                 logs.append(f"Currency skipped (no rate): {original}")
# #             ph_counter += 1
# #             return ph
       
# #         def suffix_repl(m):
# #             nonlocal ph_counter
# #             amount = m.group(1)
# #             magnitude = m.group(2)
# #             currency_word = m.group(3)
# #             currency = currency_word.lower()
# #             original_magnitude = magnitude
# #             if currency == 'crores':
# #                 currency = 'rupees'
# #                 if not magnitude:
# #                     magnitude = 'crores'
# #             elif currency == 'lakhs':
# #                 currency = 'rupees'
# #                 if not magnitude:
# #                     magnitude = 'lakhs'
# #             ph = f"__CUR_{ph_counter}__"
# #             original = m.group(0)
# #             if currency in exchange_rates:
# #                 try:
# #                     if amount.startswith('__DEC_'):
# #                         num = float(placeholder_map[amount])
# #                     else:
# #                         num = float(amount) if amount.replace('.', '').isdigit() else words_to_number(amount)
# #                     if num == 0.0:
# #                         placeholder_map[ph] = original # Skip if amount is invalid
# #                         ph_counter += 1
# #                         return ph
# #                     if magnitude:
# #                         magnitude_lower = magnitude.lower()
# #                         multiplier = 1_000_000 if magnitude_lower == 'million' else 1_000_000_000 if magnitude_lower == 'billion' else 10_000_000 if magnitude_lower in ['crore', 'crores'] else 100_000 if magnitude_lower in ['lakh', 'lakhs'] else 1
# #                         num *= multiplier
# #                     sgd = num * exchange_rates[currency]
# #                     sgd_formatted = f"S${format_large_number(sgd)}"
# #                     placeholder_map[ph] = f"{amount}{' ' + original_magnitude if original_magnitude else ''} {currency_word} ({sgd_formatted})"
# #                     logs.append(f"Currency: {original} → {placeholder_map[ph]}")
# #                     counters["currency"] += 1
# #                 except ValueError:
# #                     placeholder_map[ph] = original # Keep original if conversion fails
# #                     logs.append(f"Currency skipped (invalid amount): {original}")
# #             else:
# #                 placeholder_map[ph] = original # Keep original for unknown currencies
# #                 logs.append(f"Currency skipped (no rate): {original}")
# #             ph_counter += 1
# #             return ph
       
# #         s = suffix_pattern.sub(suffix_repl, s)
# #         s = prefix_pattern.sub(prefix_repl, s)
# #         return s
 
# #     def restore_placeholders(s: str) -> str:
# #         for ph, val in reversed(placeholder_map.items()):
# #             s = s.replace(ph, val)
# #         return s
 
# #     # Integer replacer (does not touch decimals or percentages)
# #     def int_replacer_factory(segment_text):
# #         def replacer(match):
# #             num_str = match.group(0)
# #             try:
# #                 num = int(num_str)
# #             except ValueError:
# #                 return num_str
# #             # Spell out 1–9, keep 10+ as numerals
# #             if num <= 9:
# #                 replacement = spell_number(num_str)
# #             else:
# #                 replacement = str(num)
# #             if replacement != num_str:
# #                 logs.append(f"{num_str} → {replacement}")
# #                 counters["numbers"] += 1
# #             return replacement
# #         return replacer
 
# #     # 1) Split by quotes/brackets
# #     processed_segments = []
# #     for seg, is_protected in split_by_quotes_and_brackets(text):
# #         if is_protected:
# #             processed_segments.append(seg) # untouched
# #         else:
# #             # 2) Handle plural forms for decimals > 1
# #             tmp = plural_pattern.sub(
# #                 lambda m: f"{m.group(1)} {m.group(2)} are" if float(m.group(1)) > 1 else m.group(0), seg
# #             )
# #             if tmp != seg:
# #                 logs.append(f"{seg} → {tmp}")
# #                 counters["plural"] += 1
# #             # 3) Protect decimal percentages and decimals
# #             tmp = protect_pct_decimals(tmp)
# #             tmp = protect_decimals(tmp)
# #             # 4) Protect ranges and dates
# #             tmp = protect_ranges(tmp)
# #             tmp = protect_dates(tmp)
# #             # 5) Convert standalone integers
# #             tmp = re.sub(r"\b\d+\b", int_replacer_factory(tmp), tmp)
# #             # 6) Handle currency amounts after text conversions
# #             tmp = protect_currency(tmp)
# #             processed_segments.append(tmp)
 
# #     combined = "".join(processed_segments)
# #     # 7) Sentence-start capitalization rule for integers and decimals
# #     parts = re.split(r"([.!?]\s+)", combined)
# #     for i in range(0, len(parts), 2):
# #         sent = parts[i]
# #         if not sent:
# #             continue
# #         if sent.startswith(("__DEC_PCT_", "__DEC_", "__CUR_", "__RANGE_", "__DATE_")):
# #             continue
# #         # Match integers or decimals at sentence start
# #         m = re.match(r"^(\s*)(\d+\.\d+|\d+)\b", sent)
# #         if m:
# #             leading_ws, num_str = m.groups()
# #             try:
# #                 cap = spell_number(num_str, capitalize=True)
# #                 parts[i] = f"{leading_ws}{cap}{sent[len(leading_ws)+len(num_str):]}"
# #                 logs.append(f"Sentence start: {num_str} → {cap}")
# #                 counters["sentence_start"] += 1
# #             except ValueError:
# #                 pass
# #     result = "".join(parts)
# #     # 8) Restore all placeholders
# #     result = restore_placeholders(result)
# #     return result
# # # ========================
# # # DOCX Processing
# # # ========================
# # def process_docx(docx_file):
# #     counters = {"date": 0, "year_span": 0, "chemical": 0, "chemical_unit": 0, "%": 0, "percent": 0, "percentage": 0, "per cent": 0, "numbers": 0, "sentence_start": 0, "plural": 0, "currency": 0}
# #     logs = []
# #     # Temporary output file
# #     temp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
# #     output_path = temp_out.name
# #     temp_out.close()
# #     with zipfile.ZipFile(docx_file.name, "r") as zin:
# #         with zipfile.ZipFile(output_path, "w") as zout:
# #             for item in zin.infolist():
# #                 if item.filename != "word/document.xml":
# #                     zout.writestr(item, zin.read(item.filename))
# #                 else:
# #                     xml_content = zin.read("word/document.xml")
# #                     tree = etree.fromstring(xml_content)
# #                     ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
# #                     body = tree.find(".//w:body", ns)
# #                     if body is None:
# #                         print("No document body found in DOCX file.")
# #                         return output_path
# #                     for para in body.findall(".//w:p", ns):
# #                         # Skip TOC paragraphs
# #                         is_toc = False
# #                         for instr in para.findall(".//w:instrText", ns):
# #                             if instr.text and "TOC" in instr.text.upper():
# #                                 is_toc = True
# #                                 break
# #                         style = para.find(".//w:pStyle", ns)
# #                         if style is not None and style.get(f"{{{ns['w']}}}val", "").startswith("TOC"):
# #                             is_toc = True
# #                         if is_toc:
# #                             continue # Skip TOC paragraphs
                       
# #                         # Skip paragraphs inside tables or figures for number rewrites (as per number.py)
# #                         if para.getparent().tag.endswith("tbl") or para.find(".//w:drawing", ns) is not None:
# #                             continue
                       
# #                         # Process text nodes
# #                         for node in para.findall(".//w:t", ns):
# #                             if node.text:
# #                                 # First apply percalchem transformations
# #                                 node.text = percalchem_rewrite_in_text(node.text, logs, counters)
# #                                 # Then apply number transformations
# #                                 node.text = number_rewrite_in_text(node.text, logs, counters)
# #                     zout.writestr(
# #                         "word/document.xml",
# #                         etree.tostring(tree, xml_declaration=True, encoding="utf-8", standalone="yes"),
# #                     )
# #     # Summary
# #     print("===== Replacement Summary =====")
# #     for k, v in counters.items():
# #         print(f"{k}: {v}")
# #     print(f"TOTAL replacements: {sum(counters.values())}")
# #     print("================================")
# #     print("Changes:")
# #     for log in logs:
# #         print(log)
# #     return output_path
# # # ========================
# # # Gradio UI
# # # ========================
# # iface = gr.Interface(
# #     fn=process_docx,
# #     inputs=gr.File(file_types=[".docx"], label="Upload Word Document"),
# #     outputs=gr.File(label="Download Modified Document"),
# #     title="Normalize Dates, Chemical Terms, Percentages, and Rewrite Numbers in Word Document",
# #     description=(
# #         "Normalizes dates, year ranges, chemical terms (e.g., CO₂ → CO2, GtCO₂ → GTCO2, 2,607 GtCO₂ → 2,607 (GTCO2)), rewrites percentages (integers → 'per cent', decimals → '%'), "
# #         "and rewrites numbers (1–9 spelled out, 10+ numerals, sentence-start spelled out, decimals to words, plural verbs for >1, currency to SGD in parens). "
# #         "Dates: e.g., '31st December, 2023' → '31 December 2023', '31 jan 99' → '31 January 1999'. "
# #         "Year spans: e.g., '1914-18' → '1914–18', '1986-2000' → '1986–2000'. "
# #         "Chemical: Replaces subscripts, capitalizes, adds parens for units. "
# #         "Numbers: e.g., 10.4 → ten point four (or Ten at sentence start), 1.25 metres is → one point two five metres are. "
# #         "Currency: e.g., US$5 → US$5 (S$6.43), using averages July 30–Aug 26, 2025. "
# #         "Skips in quotes/brackets, tables/figures/TOC. Preserves formatting. Logs replacements."
# #     ),
# # )
# # if __name__ == "__main__":
# #     iface.launch()

# import zipfile
# from lxml import etree
# import gradio as gr
# import re
# import tempfile
# from num2words import num2words
# # ========================
# # Quote + Bracket handling
# # ========================
# OPEN_QUOTES = {"'": "'", '"': '"', "‘": "’", "“": "”"}
# CLOSE_FOR_QUOTE = OPEN_QUOTES
# BRACKET_PAIRS = {"(": ")", "[": "]", "{": "}", "<": ">"}
# OPEN_BRACKETS = set(BRACKET_PAIRS.keys())
# CLOSE_FOR_BRACKET = BRACKET_PAIRS
# def split_by_quotes_and_brackets(text: str):
#     """
#     Yield (segment, is_protected).
#     Protects text inside quotes OR brackets (supports nesting).
#     """
#     segments = []
#     buf = []
#     stack = []
#     mode = "normal"
#     i = 0
#     while i < len(text):
#         ch = text[i]
#         if mode == "normal":
#             if ch in OPEN_QUOTES: # entering quote
#                 if buf:
#                     segments.append(("".join(buf), False))
#                     buf = []
#                 buf.append(ch)
#                 stack.append(CLOSE_FOR_QUOTE[ch])
#                 mode = "quoted"
#             elif ch in OPEN_BRACKETS: # entering bracket
#                 if buf:
#                     segments.append(("".join(buf), False))
#                     buf = []
#                 buf.append(ch)
#                 stack.append(CLOSE_FOR_BRACKET[ch])
#                 mode = "bracketed"
#             else:
#                 buf.append(ch)
#         elif mode == "quoted":
#             buf.append(ch)
#             if stack and ch == stack[-1]:
#                 stack.pop()
#                 if not stack:
#                     segments.append(("".join(buf), True))
#                     buf = []
#                     mode = "normal"
#         elif mode == "bracketed":
#             buf.append(ch)
#             if stack and ch == stack[-1]:
#                 stack.pop()
#                 if not stack:
#                     segments.append(("".join(buf), True))
#                     buf = []
#                     mode = "normal"
#         i += 1
#     if buf:
#         segments.append(("".join(buf), mode != "normal"))
#     return segments
# # ========================
# # Subscript Map
# # ========================
# SUBSCRIPT_MAP = {
#     '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
#     '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
# }
# # ========================
# # Date Normalization (from percalchem)
# # ========================
# def normalize_dates_and_ranges_in_text(text, logs, counters):
#     # Month dictionary for abbreviations and full names (case-insensitive)
#     month_dict = {
#         'jan': 'January', 'january': 'January',
#         'feb': 'February', 'february': 'February',
#         'mar': 'March', 'march': 'March',
#         'apr': 'April', 'april': 'April',
#         'may': 'May',
#         'jun': 'June', 'june': 'June',
#         'jul': 'July', 'july': 'July',
#         'aug': 'August', 'august': 'August',
#         'sep': 'September', 'sept': 'September', 'september': 'September',
#         'oct': 'October', 'october': 'October',
#         'nov': 'November', 'november': 'November',
#         'dec': 'December', 'december': 'December',
#     }
#     def expand_year(year_str):
#         if len(year_str) == 4:
#             return year_str
#         elif len(year_str) == 2:
#             yy = int(year_str)
#             if yy <= 29:
#                 return f"20{year_str.zfill(2)}"
#             else:
#                 return f"19{year_str.zfill(2)}"
#         else:
#             return year_str
#     def replace_range(match):
#         y1_str = match.group(1)
#         y2_input = match.group(2)
#         original = match.group(0)
#         try:
#             y1 = int(y1_str)
#             prefix = y1_str[:2]
#             y2 = int(prefix + y2_input.zfill(2))
#             if y2 < y1:
#                 # Try next century
#                 next_prefix = str(int(prefix) + 1)
#                 y2 = int(next_prefix + y2_input.zfill(2))
#                 if y2 < y1:
#                     return original
#             if y2 < y1:
#                 return original
#             # Check if same century
#             y2_str = str(y2)
#             if y2_str[:2] == y1_str[:2]:
#                 y2_display = y2_str[-2:]
#             else:
#                 y2_display = y2_str
#             # Use en dash
#             replacement = f"{y1}\u2013{y2_display}"
#             logs.append(f"{original} → {replacement}")
#             counters["year_span"] += 1
#             return replacement
#         except ValueError:
#             return original
#     def replace_day_first(match):
#         day_str = match.group(1)
#         month_str = match.group(2)
#         year_str = match.group(3)
#         original = match.group(0)
#         month_lower = month_str.lower()
#         if month_lower not in month_dict:
#             return original
#         full_month = month_dict[month_lower]
#         # Remove ordinal suffixes
#         day = re.sub(r'(st|nd|rd|th)$', '', day_str, flags=re.IGNORECASE).strip()
#         expanded_year = expand_year(year_str)
#         replacement = f"{day} {full_month} {expanded_year}"
#         logs.append(f"{original} → {replacement}")
#         counters["date"] += 1
#         return replacement
#     def replace_month_first(match):
#         month_str = match.group(1)
#         day_str = match.group(2)
#         year_str = match.group(3)
#         original = match.group(0)
#         month_lower = month_str.lower()
#         if month_lower not in month_dict:
#             return original
#         full_month = month_dict[month_lower]
#         # Remove ordinal suffixes
#         day = re.sub(r'(st|nd|rd|th)$', '', day_str, flags=re.IGNORECASE).strip()
#         expanded_year = expand_year(year_str)
#         replacement = f"{day} {full_month} {expanded_year}"
#         logs.append(f"{original} → {replacement}")
#         counters["date"] += 1
#         return replacement
#     # Apply year ranges
#     range_pattern = r'(\d{4})-(\d{2}|\d{4})'
#     text = re.sub(range_pattern, replace_range, text)
#     # Year pattern for dates
#     year_pattern = r'(\d{2}|\d{4})'
#     # Apply day-month-year with negative lookbehind
#     day_first_pattern = r'(?<!\d )(\d{1,2}(?:st|nd|rd|th)?)\s*([A-Za-z]+)\s*,?\s*' + year_pattern
#     text = re.sub(day_first_pattern, replace_day_first, text, flags=re.IGNORECASE)
#     # Apply month-day-year with negative lookbehind
#     month_first_pattern = r'(?<!\d )([A-Za-z]+)\s*(\d{1,2}(?:st|nd|rd|th)?)\s*,?\s*' + year_pattern
#     text = re.sub(month_first_pattern, replace_month_first, text, flags=re.IGNORECASE)
#     return text
# # ========================
# # Chemical Normalization (from percalchem)
# # ========================
# def normalize_chemical_in_text(text, logs, counters):
#     def chemical_replacer(match):
#         term = match.group(0)
#         original = term
#         normalized = ''.join(SUBSCRIPT_MAP.get(c, c.upper()) for c in term)
#         if normalized != original.upper(): # Check if subscripts were present
#             logs.append(f"{original} → {normalized}")
#             counters["chemical"] += 1
#         return normalized
#     # Pattern for terms likely containing subscripts (alphanumeric with possible subscripts)
#     chemical_pattern = r'\b([A-Za-z0-9]*[₀₁₂₃₄₅₆₇₈₉]+[A-Za-z0-9]*)\b'
#     text = re.sub(chemical_pattern, chemical_replacer, text)
#     # Now handle units after numbers, adding parentheses for specific common units
#     common_units = r'GTCO2|MTCO2|KTCO2|GTCO2EQ|MTCO2EQ|KTCO2EQ'
#     def unit_parens_replacer(match):
#         num = match.group(1)
#         unit = match.group(2)
#         original = match.group(0)
#         replacement = f"{num} ({unit})"
#         logs.append(f"{original} → {replacement}")
#         counters["chemical_unit"] += 1
#         return replacement
#     unit_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s+(' + common_units + r')\b'
#     text = re.sub(unit_pattern, unit_parens_replacer, text)
#     return text
# # ========================
# # Percentage Rewriter (from percalchem)
# # ========================
# def rewrite_percentages_in_text(text, logs, counters):
#     pieces = []
#     def percent_symbol_replacer(match):
#         num_str = match.group(1)
#         original = match.group(0)
#         try:
#             num = float(num_str)
#             if num.is_integer():
#                 replacement = f"{int(num)} per cent"
#             else:
#                 replacement = f"{num_str}%"
#         except ValueError:
#             replacement = original
#         logs.append(f"{original} → {replacement}")
#         counters["%"] += 1
#         return replacement
#     def percent_word_replacer(match):
#         num_str, unit = match.group(1), match.group(2).lower()
#         original = match.group(0)
#         try:
#             num = float(num_str)
#             if num.is_integer():
#                 replacement = f"{int(num)} per cent"
#             else:
#                 replacement = f"{num_str}%"
#         except ValueError:
#             replacement = original
#         logs.append(f"{original} → {replacement}")
#         if unit == "percent":
#             counters["percent"] += 1
#         elif unit == "percentage":
#             counters["percentage"] += 1
#         elif unit == "per cent":
#             counters["per cent"] += 1
#         return replacement
#     for seg, is_protected in split_by_quotes_and_brackets(text):
#         if is_protected:
#             pieces.append(seg)
#         else:
#             temp = re.sub(r"(\d+(?:\.\d+)?)\s*%", percent_symbol_replacer, seg)
#             temp = re.sub(
#                 r"\b(\d+(?:\.\d+)?)\s*(percent|percentage|per\s+cent)\b",
#                 percent_word_replacer,
#                 temp,
#                 flags=re.IGNORECASE,
#             )
#             pieces.append(temp)
#     return "".join(pieces)
# # ========================
# # PerCalChem Rewriter (combined dates, chemical, percentages)
# # ========================
# def percalchem_rewrite_in_text(text, logs, counters):
#     pieces = []
#     for seg, is_protected in split_by_quotes_and_brackets(text):
#         if is_protected:
#             pieces.append(seg)
#         else:
#             # Normalize dates and ranges
#             temp = normalize_dates_and_ranges_in_text(seg, logs, counters)
#             # Normalize chemical terms
#             temp = normalize_chemical_in_text(temp, logs, counters)
#             # Rewrite percentages
#             temp = rewrite_percentages_in_text(temp, logs, counters)
#             pieces.append(temp)
#     return "".join(pieces)
# # ========================
# # Number Rewriter (from number)
# # ========================
# def spell_number(n: str, capitalize=False) -> str:
#     """
#     Spell out an integer or decimal number using num2words.
#     For decimals (e.g., '10.4'), convert to 'ten point four'.
#     """
#     try:
#         if '.' in n:
#             integer_part, decimal_part = n.split('.')
#             integer_words = num2words(int(integer_part), lang='en')
#             decimal_words = ' point '.join(num2words(int(d), lang='en') for d in decimal_part)
#             result = f"{integer_words} point {decimal_words}"
#         else:
#             result = num2words(int(n), lang='en')
#         return result.capitalize() if capitalize else result
#     except ValueError:
#         return str(n)
# # Reverse mapping of number words to numbers for currency conversion
# number_words_to_num = {
#     'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
#     'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12,
#     'thirteen': 13, 'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
#     'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40,
#     'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
#     'hundred': 100, 'thousand': 1000, 'million': 1000000, 'billion': 1000000000,
#     'trillion': 1000000000000, 'crore': 10000000, 'lakh': 100000
# }
# def words_to_number(word: str) -> float:
#     """
#     Convert a number written in words (e.g., 'five', 'two hundred', 'five hundred crores') to a float.
#     Handles simple cases up to crore.
#     """
#     try:
#         words = word.lower().split()
#         total = 0
#         current = 0
#         for w in words:
#             if w in number_words_to_num:
#                 num = number_words_to_num[w]
#                 if num >= 100:
#                     if current == 0:
#                         current = 1 # Handle cases like "hundred" alone
#                     current *= num
#                 else:
#                     current += num
#             elif w == 'and':
#                 continue
#             else:
#                 break # Stop at unrecognized words
#         total += current
#         return float(total) if total > 0 else float(word)
#     except (ValueError, KeyError):
#         try:
#             return float(word) # Fallback to float conversion
#         except ValueError:
#             return 0.0 # Return 0 if conversion fails
# def format_large_number(num):
#     if num >= 1e12:
#         return f"{num / 1e12:.2f} trillion"
#     elif num >= 1e9:
#         return f"{num / 1e9:.2f} billion"
#     elif num >= 1e6:
#         return f"{num / 1e6:.2f} million"
#     else:
#         return f"{num:,.2f}"
# def number_rewrite_in_text(text, logs, counters):
#     """
#     - Protect decimal percentages (e.g., 8.6%) and decimal numbers (e.g., 10.4) with placeholders.
#     - Spell out integers 1–9; keep 10+ unless at sentence start.
#     - Any integer or decimal at sentence start → spell out (including 10+).
#     - For decimals > 1 followed by a noun and 'is', change 'is' to 'are' (e.g., '1.25 metres is' → 'one point two five metres are').
#     - Protect currency amounts (e.g., $300, US$five million, five hundred rupees) and convert to SGD after text conversions.
#     - Restore placeholders at the end.
#     """
#     # Placeholder store shared across segments
#     placeholder_map = {}
#     ph_counter = 0
#     # Exchange rates (updated average over July 30–August 26, 2025)
#     exchange_rates = {
#         'S$': 1.0, # SGD/SGD
#         'US$': 1.285, # USD/SGD
#         '€': 1.496, # EUR/SGD
#         '£': 1.726, # GBP/SGD
#         '¥': 0.00871, # JPY/SGD
#         '₹': 0.01466, # INR/SGD
#         'rupees': 0.01466, # INR/SGD
#     }
 
#     # Regex for decimal percentages (e.g., "8.6%")
#     pct_decimal_pattern = re.compile(r"(\d+\.\d+)\s*%")
#     # Regex for decimal numbers (e.g., "10.4", "0.4")
#     decimal_pattern = re.compile(r"\b(\d+\.\d+)\b")
#     # Regex for decimals > 1 followed by noun and 'is' (e.g., "1.25 metres is")
#     plural_pattern = re.compile(r"\b([1-9]\d*\.\d+)\s+(\w+)\s+is\b", re.IGNORECASE)
#     # Regex for prefix currency amounts (e.g., "$300", "US$five million")
#     prefix_pattern = re.compile(r"(([$€£¥₹]|[A-Z]{1,3}\$))\s*(__DEC_\d+__|[0-9.]+|[a-zA-Z\s]+?)(?:\s+(million|billion|trillion|crore|crores|lakh|lakhs))?\b", re.IGNORECASE)
#     # Regex for suffix currency amounts (e.g., "five hundred rupees", "five hundred crores")
#     suffix_pattern = re.compile(r"(__DEC_\d+__|[0-9.]+|[a-zA-Z\s]+?)(?:\s+(million|billion|trillion|crore|crores|lakh|lakhs))?\s*\b(rupees|crores|lakhs)\b", re.IGNORECASE)
#     # Regex for ranges (e.g., "1980-1999")
#     range_pattern = re.compile(r"\b(\d+-\d+)\b")
#     # Regex for dates (e.g., "31 January 1999", "January 31, 1999")
#     months = r"(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
#     date_pattern1 = re.compile(r"\b(\d{1,2}\s+" + months + r"\s+\d{4})\b", re.IGNORECASE)
#     date_pattern2 = re.compile(r"\b(" + months + r"\s+\d{1,2}(?:,\s*)?\d{4})\b", re.IGNORECASE)
 
#     def protect_pct_decimals(s: str) -> str:
#         nonlocal ph_counter
#         def _repl(m):
#             nonlocal ph_counter
#             ph = f"__DEC_PCT_{ph_counter}__"
#             placeholder_map[ph] = m.group(0) # full match, e.g., "8.6%"
#             ph_counter += 1
#             return ph
#         return pct_decimal_pattern.sub(_repl, s)
 
#     def protect_decimals(s: str) -> str:
#         nonlocal ph_counter
#         def _repl(m):
#             nonlocal ph_counter
#             ph = f"__DEC_{ph_counter}__"
#             placeholder_map[ph] = m.group(0) # full match, e.g., "10.4"
#             ph_counter += 1
#             return ph
#         return decimal_pattern.sub(_repl, s)
 
#     def protect_ranges(s: str) -> str:
#         nonlocal ph_counter
#         def _repl(m):
#             nonlocal ph_counter
#             ph = f"__RANGE_{ph_counter}__"
#             placeholder_map[ph] = m.group(0)
#             ph_counter += 1
#             return ph
#         return range_pattern.sub(_repl, s)
 
#     def protect_dates(s: str) -> str:
#         nonlocal ph_counter
#         def _repl(m):
#             nonlocal ph_counter
#             ph = f"__DATE_{ph_counter}__"
#             placeholder_map[ph] = m.group(0)
#             ph_counter += 1
#             return ph
#         s = date_pattern1.sub(_repl, s)
#         s = date_pattern2.sub(_repl, s)
#         return s
 
#     def protect_currency(s: str) -> str:
#         nonlocal ph_counter
#         def prefix_repl(m):
#             nonlocal ph_counter
#             currency = m.group(1)
#             if currency == '$':
#                 currency = 'US$'
#             amount = m.group(2)
#             magnitude = m.group(3) if len(m.groups()) >= 3 else None
#             ph = f"__CUR_{ph_counter}__"
#             original = m.group(0)
#             if currency == 'S$':
#                 # Format large S$ amounts
#                 try:
#                     if amount.startswith('__DEC_'):
#                         num = float(placeholder_map[amount])
#                     else:
#                         num = float(amount) if amount.replace('.', '').isdigit() else words_to_number(amount)
#                     if num == 0.0:
#                         placeholder_map[ph] = original
#                         ph_counter += 1
#                         return ph
#                     if magnitude:
#                         magnitude_lower = magnitude.lower()
#                         multiplier = 1_000_000 if magnitude_lower == 'million' else 1_000_000_000 if magnitude_lower == 'billion' else 1_000_000_000_000 if magnitude_lower == 'trillion' else 10_000_000 if magnitude_lower in ['crore', 'crores'] else 100_000 if magnitude_lower in ['lakh', 'lakhs'] else 1
#                         num *= multiplier
#                     formatted = f"S${format_large_number(num)}"
#                     placeholder_map[ph] = f"{currency}{' ' if currency in ['rupees'] else ''}{amount}{' ' + magnitude if magnitude else ''} ({formatted})"
#                     logs.append(f"Currency: {original} → {placeholder_map[ph]}")
#                     counters["currency"] += 1
#                 except ValueError:
#                     placeholder_map[ph] = original
#                     logs.append(f"Currency skipped (invalid amount): {original}")
#                 ph_counter += 1
#                 return ph
#             if currency in exchange_rates:
#                 try:
#                     if amount.startswith('__DEC_'):
#                         num = float(placeholder_map[amount])
#                     else:
#                         num = float(amount) if amount.replace('.', '').isdigit() else words_to_number(amount)
#                     if num == 0.0:
#                         placeholder_map[ph] = original # Skip if amount is invalid
#                         ph_counter += 1
#                         return ph
#                     if magnitude:
#                         magnitude_lower = magnitude.lower()
#                         multiplier = 1_000_000 if magnitude_lower == 'million' else 1_000_000_000 if magnitude_lower == 'billion' else 1_000_000_000_000 if magnitude_lower == 'trillion' else 10_000_000 if magnitude_lower in ['crore', 'crores'] else 100_000 if magnitude_lower in ['lakh', 'lakhs'] else 1
#                         num *= multiplier
#                     sgd = num * exchange_rates[currency]
#                     sgd_formatted = f"S${format_large_number(sgd)}"
#                     placeholder_map[ph] = f"{currency}{' ' if currency in ['rupees'] else ''}{amount}{' ' + magnitude if magnitude else ''} ({sgd_formatted})"
#                     logs.append(f"Currency: {original} → {placeholder_map[ph]}")
#                     counters["currency"] += 1
#                 except ValueError:
#                     placeholder_map[ph] = original # Keep original if conversion fails
#                     logs.append(f"Currency skipped (invalid amount): {original}")
#             else:
#                 placeholder_map[ph] = original # Keep original for unknown currencies
#                 logs.append(f"Currency skipped (no rate): {original}")
#             ph_counter += 1
#             return ph
       
#         def suffix_repl(m):
#             nonlocal ph_counter
#             amount = m.group(1)
#             magnitude = m.group(2)
#             currency_word = m.group(3)
#             currency = currency_word.lower()
#             original_magnitude = magnitude
#             if currency == 'crores':
#                 currency = 'rupees'
#                 if not magnitude:
#                     magnitude = 'crores'
#             elif currency == 'lakhs':
#                 currency = 'rupees'
#                 if not magnitude:
#                     magnitude = 'lakhs'
#             ph = f"__CUR_{ph_counter}__"
#             original = m.group(0)
#             if currency in exchange_rates:
#                 try:
#                     if amount.startswith('__DEC_'):
#                         num = float(placeholder_map[amount])
#                     else:
#                         num = float(amount) if amount.replace('.', '').isdigit() else words_to_number(amount)
#                     if num == 0.0:
#                         placeholder_map[ph] = original # Skip if amount is invalid
#                         ph_counter += 1
#                         return ph
#                     if magnitude:
#                         magnitude_lower = magnitude.lower()
#                         multiplier = 1_000_000 if magnitude_lower == 'million' else 1_000_000_000 if magnitude_lower == 'billion' else 1_000_000_000_000 if magnitude_lower == 'trillion' else 10_000_000 if magnitude_lower in ['crore', 'crores'] else 100_000 if magnitude_lower in ['lakh', 'lakhs'] else 1
#                         num *= multiplier
#                     sgd = num * exchange_rates[currency]
#                     sgd_formatted = f"S${format_large_number(sgd)}"
#                     placeholder_map[ph] = f"{amount}{' ' + original_magnitude if original_magnitude else ''} {currency_word} ({sgd_formatted})"
#                     logs.append(f"Currency: {original} → {placeholder_map[ph]}")
#                     counters["currency"] += 1
#                 except ValueError:
#                     placeholder_map[ph] = original # Keep original if conversion fails
#                     logs.append(f"Currency skipped (invalid amount): {original}")
#             else:
#                 placeholder_map[ph] = original # Keep original for unknown currencies
#                 logs.append(f"Currency skipped (no rate): {original}")
#             ph_counter += 1
#             return ph
       
#         s = suffix_pattern.sub(suffix_repl, s)
#         s = prefix_pattern.sub(prefix_repl, s)
#         return s
 
#     def restore_placeholders(s: str) -> str:
#         for ph, val in reversed(placeholder_map.items()):
#             s = s.replace(ph, val)
#         return s
 
#     # Integer replacer (does not touch decimals or percentages)
#     def int_replacer_factory(segment_text):
#         def replacer(match):
#             num_str = match.group(0)
#             try:
#                 num = int(num_str)
#             except ValueError:
#                 return num_str
#             # Spell out 1–9, keep 10+ as numerals
#             if num <= 9:
#                 replacement = spell_number(num_str)
#             else:
#                 replacement = str(num)
#             if replacement != num_str:
#                 logs.append(f"{num_str} → {replacement}")
#                 counters["numbers"] += 1
#             return replacement
#         return replacer
 
#     # 1) Split by quotes/brackets
#     processed_segments = []
#     for seg, is_protected in split_by_quotes_and_brackets(text):
#         if is_protected:
#             processed_segments.append(seg) # untouched
#         else:
#             # 2) Handle plural forms for decimals > 1
#             tmp = plural_pattern.sub(
#                 lambda m: f"{m.group(1)} {m.group(2)} are" if float(m.group(1)) > 1 else m.group(0), seg
#             )
#             if tmp != seg:
#                 logs.append(f"{seg} → {tmp}")
#                 counters["plural"] += 1
#             # 3) Protect decimal percentages and decimals
#             tmp = protect_pct_decimals(tmp)
#             tmp = protect_decimals(tmp)
#             # 4) Protect ranges and dates
#             tmp = protect_ranges(tmp)
#             tmp = protect_dates(tmp)
#             # 5) Convert standalone integers
#             tmp = re.sub(r"\b\d+\b", int_replacer_factory(tmp), tmp)
#             # 6) Handle currency amounts after text conversions
#             tmp = protect_currency(tmp)
#             processed_segments.append(tmp)
 
#     combined = "".join(processed_segments)
#     # 7) Sentence-start capitalization rule for integers and decimals
#     parts = re.split(r"([.!?]\s+)", combined)
#     for i in range(0, len(parts), 2):
#         sent = parts[i]
#         if not sent:
#             continue
#         if sent.startswith(("__DEC_PCT_", "__DEC_", "__CUR_", "__RANGE_", "__DATE_")):
#             continue
#         # Match integers or decimals at sentence start
#         m = re.match(r"^(\s*)(\d+\.\d+|\d+)\b", sent)
#         if m:
#             leading_ws, num_str = m.groups()
#             try:
#                 cap = spell_number(num_str, capitalize=True)
#                 parts[i] = f"{leading_ws}{cap}{sent[len(leading_ws)+len(num_str):]}"
#                 logs.append(f"Sentence start: {num_str} → {cap}")
#                 counters["sentence_start"] += 1
#             except ValueError:
#                 pass
#     result = "".join(parts)
#     # 8) Restore all placeholders
#     result = restore_placeholders(result)
#     return result
# # ========================
# # DOCX Processing
# # ========================
# def process_docx(docx_file):
#     counters = {"date": 0, "year_span": 0, "chemical": 0, "chemical_unit": 0, "%": 0, "percent": 0, "percentage": 0, "per cent": 0, "numbers": 0, "sentence_start": 0, "plural": 0, "currency": 0}
#     logs = []
#     # Temporary output file
#     temp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
#     output_path = temp_out.name
#     temp_out.close()
#     with zipfile.ZipFile(docx_file.name, "r") as zin:
#         with zipfile.ZipFile(output_path, "w") as zout:
#             for item in zin.infolist():
#                 if item.filename != "word/document.xml":
#                     zout.writestr(item, zin.read(item.filename))
#                 else:
#                     xml_content = zin.read("word/document.xml")
#                     tree = etree.fromstring(xml_content)
#                     ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
#                     body = tree.find(".//w:body", ns)
#                     if body is None:
#                         print("No document body found in DOCX file.")
#                         return output_path
#                     for para in body.findall(".//w:p", ns):
#                         # Skip TOC paragraphs
#                         is_toc = False
#                         for instr in para.findall(".//w:instrText", ns):
#                             if instr.text and "TOC" in instr.text.upper():
#                                 is_toc = True
#                                 break
#                         style = para.find(".//w:pStyle", ns)
#                         if style is not None and style.get(f"{{{ns['w']}}}val", "").startswith("TOC"):
#                             is_toc = True
#                         if is_toc:
#                             continue # Skip TOC paragraphs
                       
#                         # Skip paragraphs inside tables or figures for number rewrites (as per number.py)
#                         if para.getparent().tag.endswith("tbl") or para.find(".//w:drawing", ns) is not None:
#                             continue
                       
#                         # Process text nodes
#                         for node in para.findall(".//w:t", ns):
#                             if node.text:
#                                 # First apply percalchem transformations
#                                 node.text = percalchem_rewrite_in_text(node.text, logs, counters)
#                                 # Then apply number transformations
#                                 node.text = number_rewrite_in_text(node.text, logs, counters)
#                     zout.writestr(
#                         "word/document.xml",
#                         etree.tostring(tree, xml_declaration=True, encoding="utf-8", standalone="yes"),
#                     )
#     # Summary
#     print("===== Replacement Summary =====")
#     for k, v in counters.items():
#         print(f"{k}: {v}")
#     print(f"TOTAL replacements: {sum(counters.values())}")
#     print("================================")
#     print("Changes:")
#     for log in logs:
#         print(log)
#     return output_path
# # ========================
# # Gradio UI
# # ========================
# iface = gr.Interface(
#     fn=process_docx,
#     inputs=gr.File(file_types=[".docx"], label="Upload Word Document"),
#     outputs=gr.File(label="Download Modified Document"),
#     title="Normalize Dates, Chemical Terms, Percentages, and Rewrite Numbers in Word Document",
#     description=(
#         "Normalizes dates, year ranges, chemical terms (e.g., CO₂ → CO2, GtCO₂ → GTCO2, 2,607 GtCO₂ → 2,607 (GTCO2)), rewrites percentages (integers → 'per cent', decimals → '%'), "
#         "and rewrites numbers (1–9 spelled out, 10+ numerals, sentence-start spelled out, decimals to words, plural verbs for >1, currency to SGD in parens). "
#         "Dates: e.g., '31st December, 2023' → '31 December 2023', '31 jan 99' → '31 January 1999'. "
#         "Year spans: e.g., '1914-18' → '1914–18', '1986-2000' → '1986–2000'. "
#         "Chemical: Replaces subscripts, capitalizes, adds parens for units. "
#         "Numbers: e.g., 10.4 → ten point four (or Ten at sentence start), 1.25 metres is → one point two five metres are. "
#         "Currency: e.g., US$5 → US$5 (S$6.43), using averages July 30–Aug 26, 2025. "
#         "Skips in quotes/brackets, tables/figures/TOC. Preserves formatting. Logs replacements."
#     ),
# )
# if __name__ == "__main__":
#     iface.launch()
# import zipfile
# from lxml import etree
# import gradio as gr
# import re
# import tempfile
# from num2words import num2words
# # ========================
# # Quote + Bracket handling
# # ========================
# OPEN_QUOTES = {"'": "'", '"': '"', "‘": "’", "“": "”"}
# CLOSE_FOR_QUOTE = OPEN_QUOTES
# BRACKET_PAIRS = {"(": ")", "[": "]", "{": "}", "<": ">"}
# OPEN_BRACKETS = set(BRACKET_PAIRS.keys())
# CLOSE_FOR_BRACKET = BRACKET_PAIRS
# def split_by_quotes_and_brackets(text: str):
#     """
#     Yield (segment, is_protected).
#     Protects text inside quotes OR brackets (supports nesting).
#     """
#     segments = []
#     buf = []
#     stack = []
#     mode = "normal"
#     i = 0
#     while i < len(text):
#         ch = text[i]
#         if mode == "normal":
#             if ch in OPEN_QUOTES: # entering quote
#                 if buf:
#                     segments.append(("".join(buf), False))
#                     buf = []
#                 buf.append(ch)
#                 stack.append(CLOSE_FOR_QUOTE[ch])
#                 mode = "quoted"
#             elif ch in OPEN_BRACKETS: # entering bracket
#                 if buf:
#                     segments.append(("".join(buf), False))
#                     buf = []
#                 buf.append(ch)
#                 stack.append(CLOSE_FOR_BRACKET[ch])
#                 mode = "bracketed"
#             else:
#                 buf.append(ch)
#         elif mode == "quoted":
#             buf.append(ch)
#             if stack and ch == stack[-1]:
#                 stack.pop()
#                 if not stack:
#                     segments.append(("".join(buf), True))
#                     buf = []
#                     mode = "normal"
#         elif mode == "bracketed":
#             buf.append(ch)
#             if stack and ch == stack[-1]:
#                 stack.pop()
#                 if not stack:
#                     segments.append(("".join(buf), True))
#                     buf = []
#                     mode = "normal"
#         i += 1
#     if buf:
#         segments.append(("".join(buf), mode != "normal"))
#     return segments
# # ========================
# # Subscript Map
# # ========================
# SUBSCRIPT_MAP = {
#     '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
#     '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
# }
# # ========================
# # Date Normalization (from percalchem)
# # ========================
# def normalize_dates_and_ranges_in_text(text, logs, counters):
#     # Month dictionary for abbreviations and full names (case-insensitive)
#     month_dict = {
#         'jan': 'January', 'january': 'January',
#         'feb': 'February', 'february': 'February',
#         'mar': 'March', 'march': 'March',
#         'apr': 'April', 'april': 'April',
#         'may': 'May',
#         'jun': 'June', 'june': 'June',
#         'jul': 'July', 'july': 'July',
#         'aug': 'August', 'august': 'August',
#         'sep': 'September', 'sept': 'September', 'september': 'September',
#         'oct': 'October', 'october': 'October',
#         'nov': 'November', 'november': 'November',
#         'dec': 'December', 'december': 'December',
#     }
#     def expand_year(year_str):
#         if len(year_str) == 4:
#             return year_str
#         elif len(year_str) == 2:
#             yy = int(year_str)
#             if yy <= 29:
#                 return f"20{year_str.zfill(2)}"
#             else:
#                 return f"19{year_str.zfill(2)}"
#         else:
#             return year_str
#     def replace_range(match):
#         y1_str = match.group(1)
#         y2_input = match.group(2)
#         original = match.group(0)
#         try:
#             y1 = int(y1_str)
#             prefix = y1_str[:2]
#             y2 = int(prefix + y2_input.zfill(2))
#             if y2 < y1:
#                 # Try next century
#                 next_prefix = str(int(prefix) + 1)
#                 y2 = int(next_prefix + y2_input.zfill(2))
#                 if y2 < y1:
#                     return original
#             if y2 < y1:
#                 return original
#             # Check if same century
#             y2_str = str(y2)
#             if y2_str[:2] == y1_str[:2]:
#                 y2_display = y2_str[-2:]
#             else:
#                 y2_display = y2_str
#             # Use en dash
#             replacement = f"{y1}\u2013{y2_display}"
#             logs.append(f"{original} → {replacement}")
#             counters["year_span"] += 1
#             return replacement
#         except ValueError:
#             return original
#     def replace_day_first(match):
#         day_str = match.group(1)
#         month_str = match.group(2)
#         year_str = match.group(3)
#         original = match.group(0)
#         month_lower = month_str.lower()
#         if month_lower not in month_dict:
#             return original
#         full_month = month_dict[month_lower]
#         # Remove ordinal suffixes
#         day = re.sub(r'(st|nd|rd|th)$', '', day_str, flags=re.IGNORECASE).strip()
#         expanded_year = expand_year(year_str)
#         replacement = f"{day} {full_month} {expanded_year}"
#         logs.append(f"{original} → {replacement}")
#         counters["date"] += 1
#         return replacement
#     def replace_month_first(match):
#         month_str = match.group(1)
#         day_str = match.group(2)
#         year_str = match.group(3)
#         original = match.group(0)
#         month_lower = month_str.lower()
#         if month_lower not in month_dict:
#             return original
#         full_month = month_dict[month_lower]
#         # Remove ordinal suffixes
#         day = re.sub(r'(st|nd|rd|th)$', '', day_str, flags=re.IGNORECASE).strip()
#         expanded_year = expand_year(year_str)
#         replacement = f"{day} {full_month} {expanded_year}"
#         logs.append(f"{original} → {replacement}")
#         counters["date"] += 1
#         return replacement
#     # Apply year ranges
#     range_pattern = r'(\d{4})-(\d{2}|\d{4})'
#     text = re.sub(range_pattern, replace_range, text)
#     # Year pattern for dates
#     year_pattern = r'(\d{2}|\d{4})'
#     # Apply day-month-year with negative lookbehind
#     day_first_pattern = r'(?<!\d )(\d{1,2}(?:st|nd|rd|th)?)\s*([A-Za-z]+)\s*,?\s*' + year_pattern
#     text = re.sub(day_first_pattern, replace_day_first, text, flags=re.IGNORECASE)
#     # Apply month-day-year with negative lookbehind
#     month_first_pattern = r'(?<!\d )([A-Za-z]+)\s*(\d{1,2}(?:st|nd|rd|th)?)\s*,?\s*' + year_pattern
#     text = re.sub(month_first_pattern, replace_month_first, text, flags=re.IGNORECASE)
#     return text
# # ========================
# # Chemical Normalization (from percalchem)
# # ========================
# def normalize_chemical_in_text(text, logs, counters):
#     def chemical_replacer(match):
#         term = match.group(0)
#         original = term
#         normalized = ''.join(SUBSCRIPT_MAP.get(c, c.upper()) for c in term)
#         if normalized != original.upper(): # Check if subscripts were present
#             logs.append(f"{original} → {normalized}")
#             counters["chemical"] += 1
#         return normalized
#     # Pattern for terms likely containing subscripts (alphanumeric with possible subscripts)
#     chemical_pattern = r'\b([A-Za-z0-9]*[₀₁₂₃₄₅₆₇₈₉]+[A-Za-z0-9]*)\b'
#     text = re.sub(chemical_pattern, chemical_replacer, text)
#     # Now handle units after numbers, adding parentheses for specific common units
#     common_units = r'GTCO2|MTCO2|KTCO2|GTCO2EQ|MTCO2EQ|KTCO2EQ'
#     def unit_parens_replacer(match):
#         num = match.group(1)
#         unit = match.group(2)
#         original = match.group(0)
#         replacement = f"{num} ({unit})"
#         logs.append(f"{original} → {replacement}")
#         counters["chemical_unit"] += 1
#         return replacement
#     unit_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s+(' + common_units + r')\b'
#     text = re.sub(unit_pattern, unit_parens_replacer, text)
#     return text
# # ========================
# # Percentage Rewriter (from percalchem)
# # ========================
# def rewrite_percentages_in_text(text, logs, counters):
#     pieces = []
#     def percent_symbol_replacer(match):
#         num_str = match.group(1)
#         original = match.group(0)
#         try:
#             num = float(num_str)
#             if num.is_integer():
#                 replacement = f"{int(num)} per cent"
#             else:
#                 replacement = f"{num_str}%"
#         except ValueError:
#             replacement = original
#         logs.append(f"{original} → {replacement}")
#         counters["%"] += 1
#         return replacement
#     def percent_word_replacer(match):
#         num_str, unit = match.group(1), match.group(2).lower()
#         original = match.group(0)
#         try:
#             num = float(num_str)
#             if num.is_integer():
#                 replacement = f"{int(num)} per cent"
#             else:
#                 replacement = f"{num_str}%"
#         except ValueError:
#             replacement = original
#         logs.append(f"{original} → {replacement}")
#         if unit == "percent":
#             counters["percent"] += 1
#         elif unit == "percentage":
#             counters["percentage"] += 1
#         elif unit == "per cent":
#             counters["per cent"] += 1
#         return replacement
#     for seg, is_protected in split_by_quotes_and_brackets(text):
#         if is_protected:
#             pieces.append(seg)
#         else:
#             temp = re.sub(r"(\d+(?:\.\d+)?)\s*%", percent_symbol_replacer, seg)
#             temp = re.sub(
#                 r"\b(\d+(?:\.\d+)?)\s*(percent|percentage|per\s+cent)\b",
#                 percent_word_replacer,
#                 temp,
#                 flags=re.IGNORECASE,
#             )
#             pieces.append(temp)
#     return "".join(pieces)
# # ========================
# # PerCalChem Rewriter (combined dates, chemical, percentages)
# # ========================
# def percalchem_rewrite_in_text(text, logs, counters):
#     pieces = []
#     for seg, is_protected in split_by_quotes_and_brackets(text):
#         if is_protected:
#             pieces.append(seg)
#         else:
#             # Normalize dates and ranges
#             temp = normalize_dates_and_ranges_in_text(seg, logs, counters)
#             # Normalize chemical terms
#             temp = normalize_chemical_in_text(temp, logs, counters)
#             # Rewrite percentages
#             temp = rewrite_percentages_in_text(temp, logs, counters)
#             pieces.append(temp)
#     return "".join(pieces)
# # ========================
# # Number Rewriter (from number)
# # ========================
# def spell_number(n: str, capitalize=False) -> str:
#     """
#     Spell out an integer or decimal number using num2words.
#     For decimals (e.g., '10.4'), convert to 'ten point four'.
#     """
#     try:
#         if '.' in n:
#             integer_part, decimal_part = n.split('.')
#             integer_words = num2words(int(integer_part), lang='en')
#             decimal_words = ' point '.join(num2words(int(d), lang='en') for d in decimal_part)
#             result = f"{integer_words} point {decimal_words}"
#         else:
#             result = num2words(int(n), lang='en')
#         return result.capitalize() if capitalize else result
#     except ValueError:
#         return str(n)
# # Reverse mapping of number words to numbers for currency conversion
# number_words_to_num = {
#     'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
#     'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12,
#     'thirteen': 13, 'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
#     'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40,
#     'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
#     'hundred': 100, 'thousand': 1000, 'million': 1000000, 'billion': 1000000000,
#     'trillion': 1000000000000, 'crore': 10000000, 'lakh': 100000
# }
# def words_to_number(word: str) -> float:
#     """
#     Convert a number written in words (e.g., 'five', 'two hundred', 'five hundred crores') to a float.
#     Handles simple cases up to crore.
#     """
#     try:
#         words = word.lower().split()
#         total = 0
#         current = 0
#         for w in words:
#             if w in number_words_to_num:
#                 num = number_words_to_num[w]
#                 if num >= 100:
#                     if current == 0:
#                         current = 1 # Handle cases like "hundred" alone
#                     current *= num
#                 else:
#                     current += num
#             elif w == 'and':
#                 continue
#             else:
#                 break # Stop at unrecognized words
#         total += current
#         return float(total) if total > 0 else float(word)
#     except (ValueError, KeyError):
#         try:
#             return float(word) # Fallback to float conversion
#         except ValueError:
#             return 0.0 # Return 0 if conversion fails
# def format_large_number(num):
#     if num >= 1e12:
#         return f"{num / 1e12:.2f} trillion"
#     elif num >= 1e9:
#         return f"{num / 1e9:.2f} billion"
#     elif num >= 1e6:
#         return f"{num / 1e6:.2f} million"
#     else:
#         return f"{num:,.2f}"
# def number_rewrite_in_text(text, logs, counters):
#     """
#     - Protect decimal percentages (e.g., 8.6%) and decimal numbers (e.g., 10.4) with placeholders.
#     - Spell out integers 1–9; keep 10+ unless at sentence start.
#     - Any integer or decimal at sentence start → spell out (including 10+).
#     - For decimals > 1 followed by a noun and 'is', change 'is' to 'are' (e.g., '1.25 metres is' → 'one point two five metres are').
#     - Protect currency amounts (e.g., $300, US$five million, five hundred rupees) and convert to SGD after text conversions.
#     - Restore placeholders at the end.
#     """
#     # Placeholder store shared across segments
#     placeholder_map = {}
#     ph_counter = 0
#     # Exchange rates (updated average over July 30–August 26, 2025)
#     exchange_rates = {
#         'S$': 1.0, # SGD/SGD
#         'US$': 1.285, # USD/SGD
#         '€': 1.496, # EUR/SGD
#         '£': 1.726, # GBP/SGD
#         '¥': 0.00871, # JPY/SGD
#         '₹': 0.01466, # INR/SGD
#         'rupees': 0.01466, # INR/SGD
#     }
 
#     # Regex for decimal percentages (e.g., "8.6%")
#     pct_decimal_pattern = re.compile(r"(\d+\.\d+)\s*%")
#     # Regex for decimal numbers (e.g., "10.4", "0.4")
#     decimal_pattern = re.compile(r"\b(\d+\.\d+)\b")
#     # Regex for decimals > 1 followed by noun and 'is' (e.g., "1.25 metres is")
#     plural_pattern = re.compile(r"\b([1-9]\d*\.\d+)\s+(\w+)\s+is\b", re.IGNORECASE)
#     # Regex for prefix currency amounts (e.g., "$300", "US$five million")
#     prefix_pattern = re.compile(r"(([$€£¥₹]|[A-Z]{1,3}\$))\s*(__DEC_\d+__|[0-9.]+|[a-zA-Z\s]+?)\s*(million|billion|trillion|crore|crores|lakh|lakhs)?\b", re.IGNORECASE)
#     # Regex for suffix currency amounts (e.g., "five hundred rupees", "five hundred crores")
#     suffix_pattern = re.compile(r"(__DEC_\d+__|[0-9.]+|[a-zA-Z\s]+?)\s*(million|billion|trillion|crore|crores|lakh|lakhs)?\s*\b(rupees|crores|lakhs)\b", re.IGNORECASE)
#     # Regex for ranges (e.g., "1980-1999")
#     range_pattern = re.compile(r"\b(\d+-\d+)\b")
#     # Regex for dates (e.g., "31 January 1999", "January 31, 1999")
#     months = r"(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
#     date_pattern1 = re.compile(r"\b(\d{1,2}\s+" + months + r"\s+\d{4})\b", re.IGNORECASE)
#     date_pattern2 = re.compile(r"\b(" + months + r"\s+\d{1,2}(?:,\s*)?\d{4})\b", re.IGNORECASE)
 
#     def protect_pct_decimals(s: str) -> str:
#         nonlocal ph_counter
#         def _repl(m):
#             nonlocal ph_counter
#             ph = f"__DEC_PCT_{ph_counter}__"
#             placeholder_map[ph] = m.group(0) # full match, e.g., "8.6%"
#             ph_counter += 1
#             return ph
#         return pct_decimal_pattern.sub(_repl, s)
 
#     def protect_decimals(s: str) -> str:
#         nonlocal ph_counter
#         def _repl(m):
#             nonlocal ph_counter
#             ph = f"__DEC_{ph_counter}__"
#             placeholder_map[ph] = m.group(0) # full match, e.g., "10.4"
#             ph_counter += 1
#             return ph
#         return decimal_pattern.sub(_repl, s)
 
#     def protect_ranges(s: str) -> str:
#         nonlocal ph_counter
#         def _repl(m):
#             nonlocal ph_counter
#             ph = f"__RANGE_{ph_counter}__"
#             placeholder_map[ph] = m.group(0)
#             ph_counter += 1
#             return ph
#         return range_pattern.sub(_repl, s)
 
#     def protect_dates(s: str) -> str:
#         nonlocal ph_counter
#         def _repl(m):
#             nonlocal ph_counter
#             ph = f"__DATE_{ph_counter}__"
#             placeholder_map[ph] = m.group(0)
#             ph_counter += 1
#             return ph
#         s = date_pattern1.sub(_repl, s)
#         s = date_pattern2.sub(_repl, s)
#         return s
 
#     def protect_currency(s: str) -> str:
#         nonlocal ph_counter
#         def prefix_repl(m):
#             nonlocal ph_counter
#             currency = m.group(1)
#             if currency == '$':
#                 currency = 'US$'
#             amount = m.group(2)
#             magnitude = m.group(3) if m.group(3) else None
#             ph = f"__CUR_{ph_counter}__"
#             original = m.group(0)
#             if currency == 'S$':
#                 # Format large S$ amounts
#                 try:
#                     if amount.startswith('__DEC_'):
#                         num = float(placeholder_map[amount])
#                     else:
#                         num = float(amount) if amount.replace('.', '').isdigit() else words_to_number(amount)
#                     if num == 0.0:
#                         placeholder_map[ph] = original
#                         ph_counter += 1
#                         return ph
#                     if magnitude:
#                         magnitude_lower = magnitude.lower()
#                         multiplier = 1_000_000 if magnitude_lower == 'million' else 1_000_000_000 if magnitude_lower == 'billion' else 1_000_000_000_000 if magnitude_lower == 'trillion' else 10_000_000 if magnitude_lower in ['crore', 'crores'] else 100_000 if magnitude_lower in ['lakh', 'lakhs'] else 1
#                         num *= multiplier
#                     formatted = f"S${format_large_number(num)}"
#                     placeholder_map[ph] = f"{currency}{' ' if currency in ['rupees'] else ''}{amount}{' ' + magnitude if magnitude else ''} ({formatted})"
#                     logs.append(f"Currency: {original} → {placeholder_map[ph]}")
#                     counters["currency"] += 1
#                 except ValueError:
#                     placeholder_map[ph] = original
#                     logs.append(f"Currency skipped (invalid amount): {original}")
#                 ph_counter += 1
#                 return ph
#             if currency in exchange_rates:
#                 try:
#                     if amount.startswith('__DEC_'):
#                         num = float(placeholder_map[amount])
#                     else:
#                         num = float(amount) if amount.replace('.', '').isdigit() else words_to_number(amount)
#                     if num == 0.0:
#                         placeholder_map[ph] = original # Skip if amount is invalid
#                         ph_counter += 1
#                         return ph
#                     if magnitude:
#                         magnitude_lower = magnitude.lower()
#                         multiplier = 1_000_000 if magnitude_lower == 'million' else 1_000_000_000 if magnitude_lower == 'billion' else 1_000_000_000_000 if magnitude_lower == 'trillion' else 10_000_000 if magnitude_lower in ['crore', 'crores'] else 100_000 if magnitude_lower in ['lakh', 'lakhs'] else 1
#                         num *= multiplier
#                     sgd = num * exchange_rates[currency]
#                     sgd_formatted = f"S${format_large_number(sgd)}"
#                     placeholder_map[ph] = f"{currency}{' ' if currency in ['rupees'] else ''}{amount}{' ' + magnitude if magnitude else ''} ({sgd_formatted})"
#                     logs.append(f"Currency: {original} → {placeholder_map[ph]}")
#                     counters["currency"] += 1
#                 except ValueError:
#                     placeholder_map[ph] = original # Keep original if conversion fails
#                     logs.append(f"Currency skipped (invalid amount): {original}")
#             else:
#                 placeholder_map[ph] = original # Keep original for unknown currencies
#                 logs.append(f"Currency skipped (no rate): {original}")
#             ph_counter += 1
#             return ph
       
#         def suffix_repl(m):
#             nonlocal ph_counter
#             amount = m.group(1)
#             magnitude = m.group(2) if m.group(2) else None
#             currency_word = m.group(3)
#             if currency_word is None:
#                 return m.group(0)
#             currency = currency_word.lower()
#             original_magnitude = magnitude
#             if currency == 'crores':
#                 currency = 'rupees'
#                 if not magnitude:
#                     magnitude = 'crores'
#             elif currency == 'lakhs':
#                 currency = 'rupees'
#                 if not magnitude:
#                     magnitude = 'lakhs'
#             ph = f"__CUR_{ph_counter}__"
#             original = m.group(0)
#             if currency in exchange_rates:
#                 try:
#                     if amount.startswith('__DEC_'):
#                         num = float(placeholder_map[amount])
#                     else:
#                         num = float(amount) if amount.replace('.', '').isdigit() else words_to_number(amount)
#                     if num == 0.0:
#                         placeholder_map[ph] = original # Skip if amount is invalid
#                         ph_counter += 1
#                         return ph
#                     if magnitude:
#                         magnitude_lower = magnitude.lower()
#                         multiplier = 1_000_000 if magnitude_lower == 'million' else 1_000_000_000 if magnitude_lower == 'billion' else 1_000_000_000_000 if magnitude_lower == 'trillion' else 10_000_000 if magnitude_lower in ['crore', 'crores'] else 100_000 if magnitude_lower in ['lakh', 'lakhs'] else 1
#                         num *= multiplier
#                     sgd = num * exchange_rates[currency]
#                     sgd_formatted = f"S${format_large_number(sgd)}"
#                     placeholder_map[ph] = f"{amount}{' ' + original_magnitude if original_magnitude else ''} {currency_word} ({sgd_formatted})"
#                     logs.append(f"Currency: {original} → {placeholder_map[ph]}")
#                     counters["currency"] += 1
#                 except ValueError:
#                     placeholder_map[ph] = original # Keep original if conversion fails
#                     logs.append(f"Currency skipped (invalid amount): {original}")
#             else:
#                 placeholder_map[ph] = original # Keep original for unknown currencies
#                 logs.append(f"Currency skipped (no rate): {original}")
#             ph_counter += 1
#             return ph
       
#         s = suffix_pattern.sub(suffix_repl, s)
#         s = prefix_pattern.sub(prefix_repl, s)
#         return s
 
#     def restore_placeholders(s: str) -> str:
#         for ph, val in reversed(placeholder_map.items()):
#             s = s.replace(ph, val)
#         return s
 
#     # Integer replacer (does not touch decimals or percentages)
#     def int_replacer_factory(segment_text):
#         def replacer(match):
#             num_str = match.group(0)
#             try:
#                 num = int(num_str)
#             except ValueError:
#                 return num_str
#             # Spell out 1–9, keep 10+ as numerals
#             if num <= 9:
#                 replacement = spell_number(num_str)
#             else:
#                 replacement = str(num)
#             if replacement != num_str:
#                 logs.append(f"{num_str} → {replacement}")
#                 counters["numbers"] += 1
#             return replacement
#         return replacer
 
#     # 1) Split by quotes/brackets
#     processed_segments = []
#     for seg, is_protected in split_by_quotes_and_brackets(text):
#         if is_protected:
#             processed_segments.append(seg) # untouched
#         else:
#             # 2) Handle plural forms for decimals > 1
#             tmp = plural_pattern.sub(
#                 lambda m: f"{m.group(1)} {m.group(2)} are" if float(m.group(1)) > 1 else m.group(0), seg
#             )
#             if tmp != seg:
#                 logs.append(f"{seg} → {tmp}")
#                 counters["plural"] += 1
#             # 3) Protect decimal percentages and decimals
#             tmp = protect_pct_decimals(tmp)
#             tmp = protect_decimals(tmp)
#             # 4) Protect ranges and dates
#             tmp = protect_ranges(tmp)
#             tmp = protect_dates(tmp)
#             # 5) Convert standalone integers
#             tmp = re.sub(r"\b\d+\b", int_replacer_factory(tmp), tmp)
#             # 6) Handle currency amounts after text conversions
#             tmp = protect_currency(tmp)
#             processed_segments.append(tmp)
 
#     combined = "".join(processed_segments)
#     # 7) Sentence-start capitalization rule for integers and decimals
#     parts = re.split(r"([.!?]\s+)", combined)
#     for i in range(0, len(parts), 2):
#         sent = parts[i]
#         if not sent:
#             continue
#         if sent.startswith(("__DEC_PCT_", "__DEC_", "__CUR_", "__RANGE_", "__DATE_")):
#             continue
#         # Match integers or decimals at sentence start
#         m = re.match(r"^(\s*)(\d+\.\d+|\d+)\b", sent)
#         if m:
#             leading_ws, num_str = m.groups()
#             try:
#                 cap = spell_number(num_str, capitalize=True)
#                 parts[i] = f"{leading_ws}{cap}{sent[len(leading_ws)+len(num_str):]}"
#                 logs.append(f"Sentence start: {num_str} → {cap}")
#                 counters["sentence_start"] += 1
#             except ValueError:
#                 pass
#     result = "".join(parts)
#     # 8) Restore all placeholders
#     result = restore_placeholders(result)
#     return result
# # ========================
# # DOCX Processing
# # ========================
# def process_docx(docx_file):
#     counters = {"date": 0, "year_span": 0, "chemical": 0, "chemical_unit": 0, "%": 0, "percent": 0, "percentage": 0, "per cent": 0, "numbers": 0, "sentence_start": 0, "plural": 0, "currency": 0}
#     logs = []
#     # Temporary output file
#     temp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
#     output_path = temp_out.name
#     temp_out.close()
#     with zipfile.ZipFile(docx_file.name, "r") as zin:
#         with zipfile.ZipFile(output_path, "w") as zout:
#             for item in zin.infolist():
#                 if item.filename != "word/document.xml":
#                     zout.writestr(item, zin.read(item.filename))
#                 else:
#                     xml_content = zin.read("word/document.xml")
#                     tree = etree.fromstring(xml_content)
#                     ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
#                     body = tree.find(".//w:body", ns)
#                     if body is None:
#                         print("No document body found in DOCX file.")
#                         return output_path
#                     for para in body.findall(".//w:p", ns):
#                         # Skip TOC paragraphs
#                         is_toc = False
#                         for instr in para.findall(".//w:instrText", ns):
#                             if instr.text and "TOC" in instr.text.upper():
#                                 is_toc = True
#                                 break
#                         style = para.find(".//w:pStyle", ns)
#                         if style is not None and style.get(f"{{{ns['w']}}}val", "").startswith("TOC"):
#                             is_toc = True
#                         if is_toc:
#                             continue # Skip TOC paragraphs
                       
#                         # Skip paragraphs inside tables or figures for number rewrites (as per number.py)
#                         if para.getparent().tag.endswith("tbl") or para.find(".//w:drawing", ns) is not None:
#                             continue
                       
#                         # Process text nodes
#                         para_text = ''
#                         for node in para.findall(".//w:t", ns):
#                             if node.text:
#                                 para_text += node.text
#                         # Apply transformations to the entire paragraph text
#                         para_text = percalchem_rewrite_in_text(para_text, logs, counters)
#                         para_text = number_rewrite_in_text(para_text, logs, counters)
#                         # Split back into text nodes if necessary, but for simplicity, assume single node or update the first
#                         first_text_node = para.find(".//w:t", ns)
#                         if first_text_node is not None:
#                             first_text_node.text = para_text
#                     zout.writestr(
#                         "word/document.xml",
#                         etree.tostring(tree, xml_declaration=True, encoding="utf-8", standalone="yes"),
#                     )
#     # Summary
#     print("===== Replacement Summary =====")
#     for k, v in counters.items():
#         print(f"{k}: {v}")
#     print(f"TOTAL replacements: {sum(counters.values())}")
#     print("================================")
#     print("Changes:")
#     for log in logs:
#         print(log)
#     return output_path
# # ========================
# # Gradio UI
# # ========================
# iface = gr.Interface(
#     fn=process_docx,
#     inputs=gr.File(file_types=[".docx"], label="Upload Word Document"),
#     outputs=gr.File(label="Download Modified Document"),
#     title="Normalize Dates, Chemical Terms, Percentages, and Rewrite Numbers in Word Document",
#     description=(
#         "Normalizes dates, year ranges, chemical terms (e.g., CO₂ → CO2, GtCO₂ → GTCO2, 2,607 GtCO₂ → 2,607 (GTCO2)), rewrites percentages (integers → 'per cent', decimals → '%'), "
#         "and rewrites numbers (1–9 spelled out, 10+ numerals, sentence-start spelled out, decimals to words, plural verbs for >1, currency to SGD in parens). "
#         "Dates: e.g., '31st December, 2023' → '31 December 2023', '31 jan 99' → '31 January 1999'. "
#         "Year spans: e.g., '1914-18' → '1914–18', '1986-2000' → '1986–2000'. "
#         "Chemical: Replaces subscripts, capitalizes, adds parens for units. "
#         "Numbers: e.g., 10.4 → ten point four (or Ten at sentence start), 1.25 metres is → one point two five metres are. "
#         "Currency: e.g., US$5 → US$5 (S$6.43), using averages July 30–Aug 26, 2025. "
#         "Skips in quotes/brackets, tables/figures/TOC. Preserves formatting. Logs replacements."
#     ),
# )
# if __name__ == "__main__":
#     iface.launch()
import zipfile
from lxml import etree
import gradio as gr
import re
import tempfile
from num2words import num2words
# ========================
# Quote + Bracket handling
# ========================
OPEN_QUOTES = {"'": "'", '"': '"', "‘": "’", "“": "”"}
CLOSE_FOR_QUOTE = OPEN_QUOTES
BRACKET_PAIRS = {"(": ")", "[": "]", "{": "}", "<": ">"}
OPEN_BRACKETS = set(BRACKET_PAIRS.keys())
CLOSE_FOR_BRACKET = BRACKET_PAIRS
def split_by_quotes_and_brackets(text: str):
    """
    Yield (segment, is_protected).
    Protects text inside quotes OR brackets (supports nesting).
    """
    segments = []
    buf = []
    stack = []
    mode = "normal"
    i = 0
    while i < len(text):
        ch = text[i]
        if mode == "normal":
            if ch in OPEN_QUOTES: # entering quote
                if buf:
                    segments.append(("".join(buf), False))
                    buf = []
                buf.append(ch)
                stack.append(CLOSE_FOR_QUOTE[ch])
                mode = "quoted"
            elif ch in OPEN_BRACKETS: # entering bracket
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
# Subscript Map
# ========================
SUBSCRIPT_MAP = {
    '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
    '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
}
# ========================
# Date Normalization (from percalchem)
# ========================
def normalize_dates_and_ranges_in_text(text, logs, counters):
    # Month dictionary for abbreviations and full names (case-insensitive)
    month_dict = {
        'jan': 'January', 'january': 'January',
        'feb': 'February', 'february': 'February',
        'mar': 'March', 'march': 'March',
        'apr': 'April', 'april': 'April',
        'may': 'May',
        'jun': 'June', 'june': 'June',
        'jul': 'July', 'july': 'July',
        'aug': 'August', 'august': 'August',
        'sep': 'September', 'sept': 'September', 'september': 'September',
        'oct': 'October', 'october': 'October',
        'nov': 'November', 'november': 'November',
        'dec': 'December', 'december': 'December',
    }
    def expand_year(year_str):
        if len(year_str) == 4:
            return year_str
        elif len(year_str) == 2:
            yy = int(year_str)
            if yy <= 29:
                return f"20{year_str.zfill(2)}"
            else:
                return f"19{year_str.zfill(2)}"
        else:
            return year_str
    def replace_range(match):
        y1_str = match.group(1)
        y2_input = match.group(2)
        original = match.group(0)
        try:
            y1 = int(y1_str)
            prefix = y1_str[:2]
            y2 = int(prefix + y2_input.zfill(2))
            if y2 < y1:
                # Try next century
                next_prefix = str(int(prefix) + 1)
                y2 = int(next_prefix + y2_input.zfill(2))
                if y2 < y1:
                    return original
            if y2 < y1:
                return original
            # Check if same century
            y2_str = str(y2)
            if y2_str[:2] == y1_str[:2]:
                y2_display = y2_str[-2:]
            else:
                y2_display = y2_str
            # Use en dash
            replacement = f"{y1}\u2013{y2_display}"
            logs.append(f"{original} → {replacement}")
            counters["year_span"] += 1
            return replacement
        except ValueError:
            return original
    def replace_day_first(match):
        day_str = match.group(1)
        month_str = match.group(2)
        year_str = match.group(3)
        original = match.group(0)
        month_lower = month_str.lower()
        if month_lower not in month_dict:
            return original
        full_month = month_dict[month_lower]
        # Remove ordinal suffixes
        day = re.sub(r'(st|nd|rd|th)$', '', day_str, flags=re.IGNORECASE).strip()
        expanded_year = expand_year(year_str)
        replacement = f"{day} {full_month} {expanded_year}"
        logs.append(f"{original} → {replacement}")
        counters["date"] += 1
        return replacement
    def replace_month_first(match):
        month_str = match.group(1)
        day_str = match.group(2)
        year_str = match.group(3)
        original = match.group(0)
        month_lower = month_str.lower()
        if month_lower not in month_dict:
            return original
        full_month = month_dict[month_lower]
        # Remove ordinal suffixes
        day = re.sub(r'(st|nd|rd|th)$', '', day_str, flags=re.IGNORECASE).strip()
        expanded_year = expand_year(year_str)
        replacement = f"{day} {full_month} {expanded_year}"
        logs.append(f"{original} → {replacement}")
        counters["date"] += 1
        return replacement
    # Apply year ranges
    range_pattern = r'(\d{4})-(\d{2}|\d{4})'
    text = re.sub(range_pattern, replace_range, text)
    # Year pattern for dates
    year_pattern = r'(\d{2}|\d{4})'
    # Apply day-month-year with negative lookbehind
    day_first_pattern = r'(?<!\d )(\d{1,2}(?:st|nd|rd|th)?)\s*([A-Za-z]+)\s*,?\s*' + year_pattern
    text = re.sub(day_first_pattern, replace_day_first, text, flags=re.IGNORECASE)
    # Apply month-day-year with negative lookbehind
    month_first_pattern = r'(?<!\d )([A-Za-z]+)\s*(\d{1,2}(?:st|nd|rd|th)?)\s*,?\s*' + year_pattern
    text = re.sub(month_first_pattern, replace_month_first, text, flags=re.IGNORECASE)
    return text
# ========================
# Chemical Normalization (from percalchem)
# ========================
def normalize_chemical_in_text(text, logs, counters):
    def chemical_replacer(match):
        term = match.group(0)
        original = term
        normalized = ''.join(SUBSCRIPT_MAP.get(c, c.upper()) for c in term)
        if normalized != original.upper(): # Check if subscripts were present
            logs.append(f"{original} → {normalized}")
            counters["chemical"] += 1
        return normalized
    # Pattern for terms likely containing subscripts (alphanumeric with possible subscripts)
    chemical_pattern = r'\b([A-Za-z0-9]*[₀₁₂₃₄₅₆₇₈₉]+[A-Za-z0-9]*)\b'
    text = re.sub(chemical_pattern, chemical_replacer, text)
    # Now handle units after numbers, adding parentheses for specific common units
    common_units = r'GTCO2|MTCO2|KTCO2|GTCO2EQ|MTCO2EQ|KTCO2EQ'
    def unit_parens_replacer(match):
        num = match.group(1)
        unit = match.group(2)
        original = match.group(0)
        replacement = f"{num} ({unit})"
        logs.append(f"{original} → {replacement}")
        counters["chemical_unit"] += 1
        return replacement
    unit_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s+(' + common_units + r')\b'
    text = re.sub(unit_pattern, unit_parens_replacer, text)
    return text
# ========================
# Percentage Rewriter (from percalchem)
# ========================
def rewrite_percentages_in_text(text, logs, counters):
    pieces = []
    def percent_symbol_replacer(match):
        num_str = match.group(1)
        original = match.group(0)
        try:
            num = float(num_str)
            if num.is_integer():
                replacement = f"{int(num)} per cent"
            else:
                replacement = f"{num_str}%"
        except ValueError:
            replacement = original
        logs.append(f"{original} → {replacement}")
        counters["%"] += 1
        return replacement
    def percent_word_replacer(match):
        num_str, unit = match.group(1), match.group(2).lower()
        original = match.group(0)
        try:
            num = float(num_str)
            if num.is_integer():
                replacement = f"{int(num)} per cent"
            else:
                replacement = f"{num_str}%"
        except ValueError:
            replacement = original
        logs.append(f"{original} → {replacement}")
        if unit == "percent":
            counters["percent"] += 1
        elif unit == "percentage":
            counters["percentage"] += 1
        elif unit == "per cent":
            counters["per cent"] += 1
        return replacement
    for seg, is_protected in split_by_quotes_and_brackets(text):
        if is_protected:
            pieces.append(seg)
        else:
            temp = re.sub(r"(\d+(?:\.\d+)?)\s*%", percent_symbol_replacer, seg)
            temp = re.sub(
                r"\b(\d+(?:\.\d+)?)\s*(percent|percentage|per\s+cent)\b",
                percent_word_replacer,
                temp,
                flags=re.IGNORECASE,
            )
            pieces.append(temp)
    return "".join(pieces)
# ========================
# PerCalChem Rewriter (combined dates, chemical, percentages)
# ========================
def percalchem_rewrite_in_text(text, logs, counters):
    pieces = []
    for seg, is_protected in split_by_quotes_and_brackets(text):
        if is_protected:
            pieces.append(seg)
        else:
            # Normalize dates and ranges
            temp = normalize_dates_and_ranges_in_text(seg, logs, counters)
            # Normalize chemical terms
            temp = normalize_chemical_in_text(temp, logs, counters)
            # Rewrite percentages
            temp = rewrite_percentages_in_text(temp, logs, counters)
            pieces.append(temp)
    return "".join(pieces)
# ========================
# Number Rewriter (from number)
# ========================
def spell_number(n: str, capitalize=False) -> str:
    """
    Spell out an integer or decimal number using num2words.
    For decimals (e.g., '10.4'), convert to 'ten point four'.
    """
    try:
        if '.' in n:
            integer_part, decimal_part = n.split('.')
            integer_words = num2words(int(integer_part), lang='en')
            decimal_words = ' point '.join(num2words(int(d), lang='en') for d in decimal_part)
            result = f"{integer_words} point {decimal_words}"
        else:
            result = num2words(int(n), lang='en')
        return result.capitalize() if capitalize else result
    except ValueError:
        return str(n)
def number_rewrite_in_text(text, logs, counters):
    """
    - Protect decimal percentages (e.g., 8.6%) and decimal numbers (e.g., 10.4) with placeholders.
    - Spell out integers 1–9; keep 10+ unless at sentence start.
    - Any integer or decimal at sentence start → spell out (including 10+).
    - For decimals > 1 followed by a noun and 'is', change 'is' to 'are' (e.g., '1.25 metres is' → 'one point two five metres are').
    - Restore placeholders at the end.
    """
    # Placeholder store shared across segments
    placeholder_map = {}
    ph_counter = 0
    # Regex for decimal percentages (e.g., "8.6%")
    pct_decimal_pattern = re.compile(r"(\d+\.\d+)\s*%")
    # Regex for decimal numbers (e.g., "10.4", "0.4")
    decimal_pattern = re.compile(r"\b(\d+\.\d+)\b")
    # Regex for decimals > 1 followed by noun and 'is' (e.g., "1.25 metres is")
    plural_pattern = re.compile(r"\b([1-9]\d*\.\d+)\s+(\w+)\s+is\b", re.IGNORECASE)
    # Regex for ranges (e.g., "1980-1999")
    range_pattern = re.compile(r"\b(\d+-\d+)\b")
    # Regex for dates (e.g., "31 January 1999", "January 31, 1999")
    months = r"(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    date_pattern1 = re.compile(r"\b(\d{1,2}\s+" + months + r"\s+\d{4})\b", re.IGNORECASE)
    date_pattern2 = re.compile(r"\b(" + months + r"\s+\d{1,2}(?:,\s*)?\d{4})\b", re.IGNORECASE)
    def protect_pct_decimals(s: str) -> str:
        nonlocal ph_counter
        def _repl(m):
            nonlocal ph_counter
            ph = f"__DEC_PCT_{ph_counter}__"
            placeholder_map[ph] = m.group(0) # full match, e.g., "8.6%"
            ph_counter += 1
            return ph
        return pct_decimal_pattern.sub(_repl, s)
    def protect_decimals(s: str) -> str:
        nonlocal ph_counter
        def _repl(m):
            nonlocal ph_counter
            ph = f"__DEC_{ph_counter}__"
            placeholder_map[ph] = m.group(0) # full match, e.g., "10.4"
            ph_counter += 1
            return ph
        return decimal_pattern.sub(_repl, s)
    def protect_ranges(s: str) -> str:
        nonlocal ph_counter
        def _repl(m):
            nonlocal ph_counter
            ph = f"__RANGE_{ph_counter}__"
            placeholder_map[ph] = m.group(0)
            ph_counter += 1
            return ph
        return range_pattern.sub(_repl, s)
    def protect_dates(s: str) -> str:
        nonlocal ph_counter
        def _repl(m):
            nonlocal ph_counter
            ph = f"__DATE_{ph_counter}__"
            placeholder_map[ph] = m.group(0)
            ph_counter += 1
            return ph
        s = date_pattern1.sub(_repl, s)
        s = date_pattern2.sub(_repl, s)
        return s
    def restore_placeholders(s: str) -> str:
        for ph, val in reversed(placeholder_map.items()):
            s = s.replace(ph, val)
        return s
    # Integer replacer (does not touch decimals or percentages)
    def int_replacer_factory(segment_text):
        def replacer(match):
            num_str = match.group(0)
            try:
                num = int(num_str)
            except ValueError:
                return num_str
            # Spell out 1–9, keep 10+ as numerals
            if num <= 9:
                replacement = spell_number(num_str)
            else:
                replacement = str(num)
            if replacement != num_str:
                logs.append(f"{num_str} → {replacement}")
                counters["numbers"] += 1
            return replacement
        return replacer
    # 1) Split by quotes/brackets
    processed_segments = []
    for seg, is_protected in split_by_quotes_and_brackets(text):
        if is_protected:
            processed_segments.append(seg) # untouched
        else:
            # 2) Handle plural forms for decimals > 1
            tmp = plural_pattern.sub(
                lambda m: f"{m.group(1)} {m.group(2)} are" if float(m.group(1)) > 1 else m.group(0), seg
            )
            if tmp != seg:
                logs.append(f"{seg} → {tmp}")
                counters["plural"] += 1
            # 3) Protect decimal percentages and decimals
            tmp = protect_pct_decimals(tmp)
            tmp = protect_decimals(tmp)
            # 4) Protect ranges and dates
            tmp = protect_ranges(tmp)
            tmp = protect_dates(tmp)
            # 5) Convert standalone integers
            tmp = re.sub(r"\b\d+\b", int_replacer_factory(tmp), tmp)
            processed_segments.append(tmp)
    combined = "".join(processed_segments)
    # 7) Sentence-start capitalization rule for integers and decimals
    parts = re.split(r"([.!?]\s+)", combined)
    for i in range(0, len(parts), 2):
        sent = parts[i]
        if not sent:
            continue
        if sent.startswith(("__DEC_PCT_", "__DEC_", "__RANGE_", "__DATE_")):
            continue
        # Match integers or decimals at sentence start
        m = re.match(r"^(\s*)(\d+\.\d+|\d+)\b", sent)
        if m:
            leading_ws, num_str = m.groups()
            try:
                cap = spell_number(num_str, capitalize=True)
                parts[i] = f"{leading_ws}{cap}{sent[len(leading_ws)+len(num_str):]}"
                logs.append(f"Sentence start: {num_str} → {cap}")
                counters["sentence_start"] += 1
            except ValueError:
                pass
    result = "".join(parts)
    # 8) Restore all placeholders
    result = restore_placeholders(result)
    return result
# ========================
# DOCX Processing
# ========================
def process_docx(docx_file):
    counters = {"date": 0, "year_span": 0, "chemical": 0, "chemical_unit": 0, "%": 0, "percent": 0, "percentage": 0, "per cent": 0, "numbers": 0, "sentence_start": 0, "plural": 0}
    logs = []
    # Temporary output file
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
                    body = tree.find(".//w:body", ns)
                    if body is None:
                        print("No document body found in DOCX file.")
                        return output_path
                    for para in body.findall(".//w:p", ns):
                        # Skip TOC paragraphs
                        is_toc = False
                        for instr in para.findall(".//w:instrText", ns):
                            if instr.text and "TOC" in instr.text.upper():
                                is_toc = True
                                break
                        style = para.find(".//w:pStyle", ns)
                        if style is not None and style.get(f"{{{ns['w']}}}val", "").startswith("TOC"):
                            is_toc = True
                        if is_toc:
                            continue # Skip TOC paragraphs
                      
                        # Skip paragraphs inside tables or figures for number rewrites (as per number.py)
                        if para.getparent().tag.endswith("tbl") or para.find(".//w:drawing", ns) is not None:
                            continue
                      
                        # Process text nodes
                        for node in para.findall(".//w:t", ns):
                            if node.text:
                                # First apply percalchem transformations
                                node.text = percalchem_rewrite_in_text(node.text, logs, counters)
                                # Then apply number transformations
                                node.text = number_rewrite_in_text(node.text, logs, counters)
                    zout.writestr(
                        "word/document.xml",
                        etree.tostring(tree, xml_declaration=True, encoding="utf-8", standalone="yes"),
                    )
    # Summary
    print("===== Replacement Summary =====")
    for k, v in counters.items():
        print(f"{k}: {v}")
    print(f"TOTAL replacements: {sum(counters.values())}")
    print("================================")
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
    title="Normalize Dates, Chemical Terms, Percentages, and Rewrite Numbers in Word Document",
    description=(
        "Normalizes dates, year ranges, chemical terms (e.g., CO₂ → CO2, GtCO₂ → GTCO2, 2,607 GtCO₂ → 2,607 (GTCO2)), rewrites percentages (integers → 'per cent', decimals → '%'), "
        "and rewrites numbers (1–9 spelled out, 10+ numerals, sentence-start spelled out, decimals to words, plural verbs for >1). "
        "Dates: e.g., '31st December, 2023' → '31 December 2023', '31 jan 99' → '31 January 1999'. "
        "Year spans: e.g., '1914-18' → '1914–18', '1986-2000' → '1986–2000'. "
        "Chemical: Replaces subscripts, capitalizes, adds parens for units. "
        "Numbers: e.g., 10.4 → ten point four (or Ten at sentence start), 1.25 metres is → one point two five metres are. "
        "Skips in quotes/brackets, tables/figures/TOC. Preserves formatting. Logs replacements."
    ),
)
# if __name__ == "__main__":
#     iface.launch()