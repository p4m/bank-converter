import csv
import os
import time
import re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path.home() / "BankConverter"
IN_DIR = BASE_DIR / "IN"
OUT_DIR = BASE_DIR / "OUT"
DONE_DIR = BASE_DIR / "DONE"
LOG_FILE = BASE_DIR / "log.txt"

REQUIRED_COLUMNS = {"Datum", "Bedrag", "Naam tegenpartij", "Omschrijving-1", "Betalingskenmerk"}

def log(msg: str):
    """Schrijf een tijdstempel en bericht naar log.txt én print naar console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def open_with_fallback(path):
    """Open bestand met UTF-8, val terug op Windows-1252."""
    try:
        f = open(path, newline='', encoding='utf-8-sig')
        f.readline()
        f.seek(0)
        return f
    except UnicodeDecodeError:
        try:
            f.close()
        except Exception:
            pass
        return open(path, newline='', encoding='cp1252')

_ws_re = re.compile(r'\s+', flags=re.UNICODE)
_dash_space_re = re.compile(r'\s*-\s*')
_space_punct_re = re.compile(r'\s+([.,;:])')

def normalize_whitespace(text: str) -> str:
    """Maak spaties netjes: meerdere → één, spaties rond '-' weghalen, enz."""
    if text is None:
        return ""
    text = text.replace('\xa0', ' ')
    text = _ws_re.sub(' ', text)
    text = _dash_space_re.sub('-', text)
    text = _space_punct_re.sub(r'\1', text)
    return text.strip()

def validate_csv_structure(path):
    """Controleer of CSV de verwachte kolommen bevat."""
    infile = open_with_fallback(path)
    try:
        reader = csv.DictReader(infile, delimiter=',', quotechar='"')
        headers = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - headers
        if missing:
            return False, missing
        return True, None
    finally:
        infile.close()

def convert_rabobank_csv(input_file, output_file):
    """Converteer Rabobank CSV naar 3 kolommen: Datum, Bedrag, Omschrijving."""
    infile = open_with_fallback(input_file)
    with infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile, delimiter=',', quotechar='"')
        writer = csv.writer(outfile)

        first_date = None
        for row in reader:
            datum = (row.get("Datum") or "").strip()
            if not datum:
                continue

            if first_date is None:
                first_date = datum

            parts = datum.split('-')
            if len(parts) == 3:
                datum = f"{parts[2]}/{parts[1]}/{parts[0]}"

            bedrag_raw = (row.get("Bedrag") or "")
            bedrag = bedrag_raw.replace("+", "").replace(".", "").replace(",", ".").strip()

            naam_tegenpartij = normalize_whitespace(row.get("Naam tegenpartij") or "")
            betalingskenmerk = normalize_whitespace(row.get("Betalingskenmerk") or "")
            oms1 = normalize_whitespace(row.get("Omschrijving-1") or "")

            if betalingskenmerk:
                omschrijving = normalize_whitespace(f"{naam_tegenpartij}{betalingskenmerk} {oms1}")
            else:
                omschrijving = normalize_whitespace(f"{naam_tegenpartij} {oms1}")

            writer.writerow([datum, bedrag, omschrijving])

    return first_date

def safe_filename(date_str, original_name):
    """Maak een nette bestandsnaam met datum vooraan."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        prefix = dt.strftime("%Y-%m-%d")
    except Exception:
        prefix = "onbekend"
    return f"{prefix}_{original_name}"

def watch_folder():
    """Controleer de IN-map en verwerk nieuwe CSV-bestanden."""
    log("💡 Converter actief — plaats Rabobank CSV's in ~/BankConverter/IN/")
    IN_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DONE_DIR.mkdir(parents=True, exist_ok=True)

    processed = set()

    while True:
        for file in IN_DIR.glob("*.csv"):
            if file not in processed:
                try:
                    # Controleer structuur
                    valid, missing = validate_csv_structure(file)
                    if not valid:
                        log(f"⚠️ Bestand {file.name} overgeslagen: ontbrekende kolommen {missing}")
                        os.replace(file, DONE_DIR / file.name)
                        processed.add(file)
                        continue

                    # Converteren
                    first_date = convert_rabobank_csv(file, OUT_DIR / file.name)
                    new_name = safe_filename(first_date or "onbekend", file.name)
                    new_output = OUT_DIR / new_name
                    os.replace(OUT_DIR / file.name, new_output)
                    done_path = DONE_DIR / file.name
                    os.replace(file, done_path)

                    log(f"✅ Omgezet: {file.name} → OUT/{new_name}")
                    log(f"📦 Origineel verplaatst naar DONE/{file.name}")
                    processed.add(file)

                except Exception as e:
                    log(f"⚠️ Fout bij {file.name}: {e}")
                    try:
                        os.replace(file, DONE_DIR / file.name)
                    except Exception:
                        pass
                    processed.add(file)
        time.sleep(5)

if __name__ == "__main__":
    watch_folder()
