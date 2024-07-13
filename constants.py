# File paths
DB_DIR = "./data/db"
COMMENTARY_DB_DIR = "./data/commentary_db"
BIBLE_XML_FILE = "./data/engwebp_vpl.xml"

# Model names
EMBEDDING_MODEL_NAME = "hkunlp/instructor-large"
LLM_MODEL_NAME = "claude-3-5-sonnet-20240620"
MAX_TOKENS = 4096

# Query Instructions
DB_QUERY = "Represent the Religious Bible verse text for semantic search:"
COMMENTARY_DB_QUERY = "Represent the Religious bible commentary text for semantic search:"

# Prompts
BIBLE_SUMMARY_PROMPT = """
The topic for analysis is {topic}. Here are the Bible passages: {passages}.  Please provide the following:

* **Key Insights:** Summarize the main points made about the topic within these specific verses.
* **Connections:** How do the verses reinforce, complement, or potentially challenge each other's perspective on the topic?
* **Theological Significance:** How do these insights connect to the broader story of God's redemption (as seen in the gospel message) across the Old and New Testaments?
* **Practical Application:** What actions or changes in understanding might be inspired by reflecting on these passages together?
"""

COMMENTARY_SUMMARY_PROMPT = """Based on the user's search query, the topic is: {topic}
Please provide a concise summary of the key insights and interpretations offered in the following Church Fathers' commentaries on the topic above. Focus only on the content in these specific commentaries, highlighting how they contribute to understanding the scriptural texts. Include the church father and source text.
{content}"""

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

# Test Queries
DEFAULT_QUERIES = [
    "What did Jesus say about eternal life?",
    #"Divine agape and  God's love for humanity",
    #"What will happen during the end times?",
    #"What is the work and nature of the Holy Spirit in our life?",
    #"Experiencing God's presence: Comfort and renewal in the Christian life",
]

# Other constants
UNSAFE_PASSWORD = "x"
LLM_ERROR = "No API token found, so LLM support is disabled."

FATHER_NAME = "father_name"
SOURCE_TITLE = "source_title"
CHAPTER = "chapter"
