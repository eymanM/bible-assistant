# File paths
DB_DIR = "./data/db"
COMMENTARY_DB_DIR = "./data/commentary_db"

# Model names
EMBEDDING_MODEL_NAME = "hkunlp/instructor-large"
OPEN_AI_LLM_MODEL_NAME = "gpt-5-mini"
OPEN_AI_LLM_MODEL_NAME_TRANSLATION = "gpt-4.1-nano"
MAX_TOKENS = 4096

# Query Instructions
DB_QUERY = "Represent the Religious Bible verse text for semantic search:"
COMMENTARY_DB_QUERY = "Represent the Religious bible commentary text for semantic search:"

# Prompts
BIBLE_SUMMARY_PROMPT = """
The topic for analysis is {topic}. Here are the Bible passages and commentaries:
{passages}

Please provide the following:
* **Key Insights:** Summarize the main points made about the topic within these specific verses.
* **Connections:** How do the verses reinforce, complement, or potentially challenge each other's perspective on the topic?
* **Theological Significance:** How do these insights connect to the broader story of God's redemption (as seen in the gospel message) across the Old and New Testaments?
* **Practical Application:** What actions or changes in understanding might be inspired by reflecting on these passages together?

Do not format the response. Give short responses.
User do not know about the included passages so do no mention about the verses.
Give a general summary of the topic and the insights from the verses in English.
"""

COMMENTARY_SUMMARY_PROMPT = """Based on the user's search query, the topic is: {topic}
Please provide a concise summary of the key insights and interpretations offered in the following Church Fathers' commentaries on the topic above. Focus only on the content in these specific commentaries, highlighting how they contribute to understanding the scriptural texts. Include the church father and source text.
{content}"""

BIBLE_SUMMARY_PROMPT_PL = """
Tematem analizy jest {topic}. Oto fragmenty Biblii i komentarze:
{passages}

Proszę o wykonanie następujących kroków:
* **Kluczowe Spostrzeżenia:** Podsumuj główne punkty dotyczące tematu w ramach tych konkretnych wersetów.
* **Powiązania:** W jaki sposób te wersety wzmacniają, uzupełniają lub potencjalnie podważają nawzajem swoje perspektywy na dany temat?
* **Znaczenie Teologiczne:** Jak te spostrzeżenia łączą się z szerszą historią Bożego odkupienia (widoczną w przesłaniu ewangelii) w Starym i Nowym Testamencie?
* **Praktyczne Zastosowanie:** Jakie działania lub zmiany w zrozumieniu mogą być inspirowane wspólną refleksją nad tymi fragmentami?

Nie formatuj odpowiedzi. Udzielaj krótkich odpowiedzi.
Użytkownik nie zna dołączonych fragmentów, więc nie wspominaj o wersetach bezpośrednio.
Podaj ogólne podsumowanie tematu i spostrzeżenia z wersetów po Polsku.
"""

COMMENTARY_SUMMARY_PROMPT_PL = """Na podstawie zapytania użytkownika, tematem jest: {topic}
Proszę o zwięzłe podsumowanie kluczowych spostrzeżeń i interpretacji zawartych w komentarzach Ojców Kościoła na powyższy temat. Skup się wyłącznie na treści tych konkretnych komentarzy, podkreślając, w jak wnoszą one wkład w zrozumienie tekstów biblijnych. Uwzględnij ojca kościoła i tekst źródłowy.
{content}"""


QUERY_TRANSLATION_PROMPT = "Translate the following Polish search query into English. Return only the translated text, nothing else. Query: {query}"

# Church Fathers
CHURCH_FATHERS = [
    "Augustine of Hippo",
    "Athanasius of Alexandria",
    "Basil of Caesarea",
    "Gregory of Nazianzus",
    "Gregory of Nyssa",
    "Cyril of Alexandria",
    "Irenaeus",
    "Cyprian",
    "Origen of Alexandria"
]

CHURCH_FATHERS_PL = {
    "Augustine of Hippo": "Augustyn z Hippony",
    "Athanasius of Alexandria": "Atanazy Wielki",
    "Basil of Caesarea": "Bazyli Wielki",
    "Gregory of Nazianzus": "Grzegorz z Nazjanzu",
    "Gregory of Nyssa": "Grzegorz z Nyssy",
    "Cyril of Alexandria": "Cyryl Aleksandryjski",
    "Irenaeus": "Ireneusz z Lyonu",
    "Cyprian": "Cyprian z Kartaginy",
    "Origen of Alexandria": "Orygenes"
}

# Other constants
LLM_ERROR = "No API token found, so LLM support is disabled."

FATHER_NAME = "father_name"
SOURCE_TITLE = "source_title"
CHAPTER = "chapter"



OT_BOOKS = {
    'GEN', 'EXO', 'LEV', 'NUM', 'DEU', 'JOS', 'JDG', 'RUT', '1SA', '2SA', '1KI', '2KI', '1CH', '2CH', 
    'EZR', 'NEH', 'EST', 'JOB', 'PSA', 'PRO', 'ECC', 'SNG', 'ISA', 'JER', 'LAM', 'EZK', 'DAN', 'HOS', 
    'JOL', 'AMO', 'OBA', 'JON', 'MIC', 'NAM', 'HAB', 'ZEP', 'HAG', 'ZEC', 'MAL'
}

NT_BOOKS = {
    'MAT', 'MRK', 'LUK', 'JHN', 'ACT', 'ROM', '1CO', '2CO', 'GAL', 'EPH', 'PHP', 'COL', '1TH', '2TH', 
    '1TI', '2TI', 'TIT', 'PHM', 'HEB', 'JAS', '1PE', '2PE', '1JN', '2JN', '3JN', 'JUD', 'REV'
}

BOOK_NAMES = {
    'GEN': 'Genesis',
    'EXO': 'Exodus',
    'LEV': 'Leviticus',
    'NUM': 'Numbers',
    'DEU': 'Deuteronomy',
    'JOS': 'Joshua',
    'JDG': 'Judges',
    'RUT': 'Ruth',
    '1SA': '1 Samuel',
    '2SA': '2 Samuel',
    '1KI': '1 Kings',
    '2KI': '2 Kings',
    '1CH': '1 Chronicles',
    '2CH': '2 Chronicles',
    'EZR': 'Ezra',
    'NEH': 'Nehemiah',
    'EST': 'Esther',
    'JOB': 'Job',
    'PSA': 'Psalms',
    'PRO': 'Proverbs',
    'ECC': 'Ecclesiastes',
    'SNG': 'Song of Solomon',
    'ISA': 'Isaiah',
    'JER': 'Jeremiah',
    'LAM': 'Lamentations',
    'EZK': 'Ezekiel',
    'DAN': 'Daniel',
    'HOS': 'Hosea',
    'JOL': 'Joel',
    'AMO': 'Amos',
    'OBA': 'Obadiah',
    'JON': 'Jonah',
    'MIC': 'Micah',
    'NAM': 'Nahum',
    'HAB': 'Habakkuk',
    'ZEP': 'Zephaniah',
    'HAG': 'Haggai',
    'ZEC': 'Zechariah',
    'MAL': 'Malachi',
    'MAT': 'Matthew',
    'MRK': 'Mark',
    'LUK': 'Luke',
    'JHN': 'John',
    'ACT': 'Acts',
    'ROM': 'Romans',
    '1CO': '1 Corinthians',
    '2CO': '2 Corinthians',
    'GAL': 'Galatians',
    'EPH': 'Ephesians',
    'PHP': 'Philippians',
    'COL': 'Colossians',
    '1TH': '1 Thessalonians',
    '2TH': '2 Thessalonians',
    '1TI': '1 Timothy',
    '2TI': '2 Timothy',
    'TIT': 'Titus',
    'PHM': 'Philemon',
    'HEB': 'Hebrews',
    'JAS': 'James',
    '1PE': '1 Peter',
    '2PE': '2 Peter',
    '1JN': '1 John',
    '2JN': '2 John',
    '3JN': '3 John',
    'JUD': 'Jude',
    'REV': 'Revelation'
}

BOOK_NAMES_PL = {
    'GEN': 'Rodzaju',
    'EXO': 'Wyjścia',
    'LEV': 'Kapłańska',
    'NUM': 'Liczb',
    'DEU': 'Powtórzonego Prawa',
    'JOS': 'Jozuego',
    'JDG': 'Sędziów',
    'RUT': 'Rut',
    '1SA': '1 Samuela',
    '2SA': '2 Samuela',
    '1KI': '1 Królewska',
    '2KI': '2 Królewska',
    '1CH': '1 Kronik',
    '2CH': '2 Kronik',
    'EZR': 'Ezdrasza',
    'NEH': 'Nehemiasza',
    'EST': 'Estery',
    'JOB': 'Hioba',
    'PSA': 'Psalmów',
    'PRO': 'Przysłów',
    'ECC': 'Kaznodziei',
    'SNG': 'Pieśń nad Pieśniami',
    'ISA': 'Izajasza',
    'JER': 'Jeremiasza',
    'LAM': 'Lamentacje',
    'EZK': 'Ezechiela',
    'DAN': 'Daniela',
    'HOS': 'Ozeasza',
    'JOL': 'Joela',
    'AMO': 'Amosa',
    'OBA': 'Abdiasza',
    'JON': 'Jonasza',
    'MIC': 'Micheasza',
    'NAM': 'Nahuma',
    'HAB': 'Habakuka',
    'ZEP': 'Sofoniasza',
    'HAG': 'Aggeusza',
    'ZEC': 'Zachariasza',
    'MAL': 'Malachiasza',
    'MAT': 'Mateusza',
    'MRK': 'Marka',
    'LUK': 'Łukasza',
    'JHN': 'Jana',
    'ACT': 'Dzieje Apostolskie',
    'ROM': 'Rzymian',
    '1CO': '1 Koryntian',
    '2CO': '2 Koryntian',
    'GAL': 'Galatów',
    'EPH': 'Efezjan',
    'PHP': 'Filipian',
    'COL': 'Kolosan',
    '1TH': '1 Tesaloniczan',
    '2TH': '2 Tesaloniczan',
    '1TI': '1 Tymoteusza',
    '2TI': '2 Tymoteusza',
    'TIT': 'Tytusa',
    'PHM': 'Filemona',
    'HEB': 'Hebrajczyków',
    'JAS': 'Jakuba',
    '1PE': '1 Piotra',
    '2PE': '2 Piotra',
    '1JN': '1 Jana',
    '2JN': '2 Jana',
    '3JN': '3 Jana',
    'JUD': 'Judy',
    'REV': 'Apokalipsa Świętego Jana'
}

COMMENTARY_TRANSLATION_PROMPT = """
You are a helpful assistant that translates theological texts from English to Polish.
Translate the following list of commentary excerpts into Polish.
Input is a JSON list of strings. Output MUST be a list of strings with the exact same number of elements as the input.
Maintain the order.
Maintain the theological meaning, tone, and historical context.
Input: {texts}
"""