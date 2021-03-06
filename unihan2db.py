import os
import re
import sqlite3

SOURCE_DIR = 'data/source'
READINGS_FILE = 'Unihan_Readings.txt'
VARIANTS_FILE = 'Unihan_Variants.txt'
DICTIONARYLIKE_FILE = 'Unihan_DictionaryLikeData.txt'

DERIVED_DIR = 'data/derived'
DB_FILE = 'unihan.db'

def process_simple(left, middle, right):
    return (codepoint2chr(left), middle, right)

def process_variants(left, middle, right):
    try:
        l, m, r = right.partition('<')
        return (codepoint2chr(left), middle, codepoints2chr(right))
    except ValueError as e:
        print('Error: ' + str(e))
        print('\t'.join((left, middle, right)))

FILES = [
    ['Unihan_Readings.txt', 'readings', process_simple],
    ['Unihan_Variants.txt', 'variants', process_variants],
    ['Unihan_DictionaryLikeData.txt', 'dictionary_like_data', process_simple],
    ['Unihan_DictionaryIndices.txt', 'dictionary_indices', process_simple],
    ['Unihan_IRGSources.txt', 'irg_sources', process_simple],
    ['Unihan_NumericValues.txt', 'numeric_values', process_simple],
    ['Unihan_OtherMappings.txt', 'other_mappings', process_simple],
    ['Unihan_RadicalStrokeCounts.txt', 'radical_stroke_counts', process_simple],
]

codepointRE = re.compile('U\+[0-9A-F]+')

def codepoint2chr(codepoint):
    return chr(int(codepoint[2:], 16))

def codepoints2chr(text):
    return codepointRE.sub(lambda match: codepoint2chr(match.group(0)), text)

def read_file(process_fn, source_dir=SOURCE_DIR, readings_file=READINGS_FILE):
    reading_rows = []
    with open(os.path.join(source_dir, readings_file), 'r') as infile:
        for line in infile:
            if line.startswith('U+'):
                line = line.strip()
                left, middle, right = line.split('\t')
                reading_rows.append(process_fn(left, middle, right))
    return reading_rows

def write_data(reading_rows, table_name, derived_dir=DERIVED_DIR, db_file=DB_FILE):
    with sqlite3.connect(os.path.join(derived_dir, db_file)) as conn:
        conn.execute('''DROP TABLE IF EXISTS %s''' % table_name)
        conn.execute('''CREATE TABLE %s(character text, attribute text, reading text)''' % table_name)
        for reading_row in reading_rows:
            conn.execute('''INSERT INTO %s VALUES (?, ?, ?)''' % table_name, reading_row)


if __name__ == '__main__':
    for filename, table_name, process_fn in FILES:
        rows = read_file(process_fn, SOURCE_DIR, filename)
        write_data(rows, table_name)

