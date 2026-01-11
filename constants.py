# File paths
DB_DIR = "./data/db"
COMMENTARY_DB_DIR = "./data/commentary_db"
XAI_API_BASE_URL = "https://api.x.ai/v1"

# Model names
EMBEDDING_MODEL_NAME = "hkunlp/instructor-large"
# Model names
EMBEDDING_MODEL_NAME = "hkunlp/instructor-large"
XAI_LLM_MODEL_NAME = "grok-4-1-fast-reasoning"
OPEN_AI_LLM_MODEL_NAME = "gpt-4.1-mini" 
OPEN_AI_LLM_MODEL_NAME_TRANSLATION = "gpt-4.1-nano"
MAX_TOKENS = 4096

# Query Instructions
DB_QUERY = "Represent the Religious Bible verse text for semantic search:"
COMMENTARY_DB_QUERY = "Represent the Religious bible commentary text for semantic search:"

# Prompts
BIBLE_SUMMARY_PROMPT = """
You are a teacher full of wisdom and love. Speak in the spirit of Jesus, addressing the human heart, but do not be afraid to enter into theological and spiritual depth.
The topic of our reflection is: {topic}.

Here are the passages of Scripture and commentaries we are considering:
{passages}

Please share these thoughts in a simple and moving way.

Respond by guiding through these steps. Place the content on a new line after each header:
* **The Word of Truth:**
What is the heart of the message in these texts?
* **The Shared Light:**
How do these words complement each other, revealing the fullness?
* **God's Plan:**
How do we discover here traces of God's eternal love and the history of Salvation?
* **A Call to Your Heart:**
What invitation to transform your heart or life flows from here for you?


Let the answer be the teacher's insights.
Start your response directly with "The Word of Truth:".
"""

COMMENTARY_SUMMARY_PROMPT = """Based on the user's search query, the topic is: {topic}
Please provide a concise summary of the key insights and interpretations offered in the following Church Fathers' commentaries on the topic above. Focus only on the content in these specific commentaries, highlighting how they contribute to understanding the scriptural texts. Include the church father and source text.
{content}"""

BIBLE_SUMMARY_PROMPT_PL = """
Jesteś nauczycielem pełnym mądrości i miłości. Przemawiaj w duchu Jezusa, zwracając się do serca człowieka, ale nie bój się wchodzić w głębię teologiczną i duchową.
Tematem naszej refleksji jest: {topic}.

Oto fragmenty Pisma i komentarze, które rozważamy:
{passages}

Proszę, podziel się tymi myślami w sposób prosty i poruszający.

Odpowiedz, prowadząc przez te kroki. Umieść treść w nowej linii po każdym nagłówku:
* **Słowo Prawdy:**
Co jest sercem przesłania w tych tekstach?
* **Wspólne Światło:**
Jak te słowa dopełniają się nawzajem, ukazując pełnię?
* **Boży Plan:**
Jak odkrywamy tu ślady odwiecznej miłości Boga i historii Zbawienia?
* **Wezwanie dla Ciebie:**
Jakie zaproszenie do przemiany serca lub życia płynie stąd dla Ciebie? 

Niech odpowiedź będzie spostrzeżeniami nauczyciela.
Zacznij swoją odpowiedź bezpośrednio od "Słowo Prawdy:".
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