import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'bible.db')

def get_db_conn():
    # SQLite connections are connection-per-thread recommended or create on demand.
    # We use uri=True for read-only access to prevent locking issues.
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    return conn

def get_real_verse_nums(book_code, chapter, text_chunk):
    """
    Identifies the actual verse numbers present in a text chunk 
    by finding the chunk's position in the full chapter text.
    """
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT full_text FROM source_chapters WHERE book=? AND chapter=?", (book_code, int(chapter)))
        row = cursor.fetchone()
        if not row:
            return []
        
        full_text = row[0]
        
        # 1. Try exact match
        start_idx = full_text.find(text_chunk)
        
        if start_idx == -1:
             # Fallback: Try match first line
             first_line = text_chunk.split('\n')[0].strip()
             start_idx = full_text.find(first_line)
             if start_idx == -1:
                 return []
        
        end_idx = start_idx + len(text_chunk)
        
        # 2. Get spans for this chapter
        cursor.execute("SELECT verse, start_idx, end_idx FROM source_spans WHERE book=? AND chapter=?", (book_code, int(chapter)))
        spans = cursor.fetchall()
        
        found_verses = set()
        for v_num, v_start, v_end in spans:
            overlap_start = max(start_idx, v_start)
            overlap_end = min(end_idx, v_end)
            if overlap_start < overlap_end:
                found_verses.add(v_num)
                
        return sorted(list(found_verses))
    finally:
        conn.close()

def get_bible_text(language, book_name, chapter, verse_nums_str):
    """
    Retrieves the specific translated verses for a given book and chapter.
    """
    if not verse_nums_str:
        return None
        
    nums = [int(n) for n in verse_nums_str.split(',') if n.strip()]
    if not nums:
        return None
        
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        placeholders = ','.join('?' for _ in nums)
        query = f"SELECT text FROM bible_verses WHERE language=? AND book=? AND chapter=? AND verse IN ({placeholders}) ORDER BY verse"
        cursor.execute(query, (language, book_name, int(chapter), *nums))
        
        texts = [row[0] for row in cursor.fetchall() if row[0]]
        
        if texts:
            return " ".join(texts)
    except Exception as e:
        print(f"Error retrieving {language} text: {e}")
    finally:
        conn.close()
        
    return None
