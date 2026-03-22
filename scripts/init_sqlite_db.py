import sqlite3
import json
import os
import xml.etree.ElementTree as ET
import collections

DB_PATH = os.path.join('data', 'bible.db')

def init_db():
    if os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} already exists. Deleting it to start fresh.")
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table for Bible translations (English, Polish)
    cursor.execute('''
        CREATE TABLE bible_verses (
            language TEXT,
            book TEXT,
            chapter INTEGER,
            verse INTEGER,
            text TEXT
        )
    ''')
    
    # Table for full chapter texts (used for mapping source XML)
    cursor.execute('''
        CREATE TABLE source_chapters (
            book TEXT,
            chapter INTEGER,
            full_text TEXT
        )
    ''')
    
    # Table for spanning info of source XML
    cursor.execute('''
        CREATE TABLE source_spans (
            book TEXT,
            chapter INTEGER,
            verse INTEGER,
            start_idx INTEGER,
            end_idx INTEGER
        )
    ''')
    
    # Indexes
    cursor.execute('CREATE INDEX idx_bible_verses ON bible_verses(language, book, chapter, verse)')
    cursor.execute('CREATE INDEX idx_source_chapters ON source_chapters(book, chapter)')
    cursor.execute('CREATE INDEX idx_source_spans ON source_spans(book, chapter)')
    
    conn.commit()
    return conn

def load_bible_data(conn, language_code, filename):
    file_path = os.path.join('data', filename)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Loading {language_code} from {filename}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    cursor = conn.cursor()
    count = 0
    
    for book in data.get('books', []):
        book_name = book.get('name')
        if not book_name: continue
        
        for chapter in book.get('chapters', []):
            try:
                chapter_num = int(chapter.get('chapter', 0))
            except ValueError:
                continue
                
            for verse in chapter.get('verses', []):
                try:
                    verse_num = int(verse.get('verse', 0))
                except ValueError:
                    continue
                    
                text = verse.get('text', '')
                cursor.execute(
                    'INSERT INTO bible_verses (language, book, chapter, verse, text) VALUES (?, ?, ?, ?, ?)',
                    (language_code, book_name, chapter_num, verse_num, text)
                )
                count += 1
                
    conn.commit()
    print(f"Inserted {count} verses for {language_code}.")


def load_source_data(conn, filename):
    file_path = os.path.join('data', filename)
    if not os.path.exists(file_path):
        print(f"Source file not found: {file_path}")
        return

    print(f"Loading source data from {filename}...")
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    verses_by_chapter = collections.defaultdict(list)
    
    for verse in root.findall("v"):
        book = verse.attrib["b"]
        chapter = int(verse.attrib["c"])
        verse_num = int(verse.attrib["v"])
        text = verse.text if verse.text else ""
        verses_by_chapter[(book, chapter)].append((verse_num, text))

    cursor = conn.cursor()
    chapters_count = 0
    spans_count = 0
    
    for (book, chapter), verses in verses_by_chapter.items():
        verses.sort(key=lambda x: x[0])
        
        full_text = ""
        current_idx = 0
        
        for verse_num, text in verses:
            start = current_idx
            snippet = f"{text}\n"
            end = current_idx + len(snippet)
            
            cursor.execute(
                'INSERT INTO source_spans (book, chapter, verse, start_idx, end_idx) VALUES (?, ?, ?, ?, ?)',
                (book, chapter, verse_num, start, end)
            )
            spans_count += 1
            
            full_text += snippet
            current_idx = end
        
        cursor.execute(
            'INSERT INTO source_chapters (book, chapter, full_text) VALUES (?, ?, ?)',
            (book, chapter, full_text)
        )
        chapters_count += 1
        
    conn.commit()
    print(f"Inserted {chapters_count} chapters and {spans_count} spans for source data.")


if __name__ == '__main__':
    # Ensure data directory exists
    if not os.path.exists('data'):
        os.makedirs('data')
        
    conn = init_db()
    
    # Load JSON Bibles
    load_bible_data(conn, 'pl', 'polish_bible.json')
    load_bible_data(conn, 'en', 'english_bible.json')
    
    # Load Source XML
    load_source_data(conn, 'engwebp_vpl.xml')
    
    conn.close()
    print("Database initialization complete.")
