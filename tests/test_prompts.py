
import os
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from constants import BIBLE_SUMMARY_PROMPT_PL, GEMINI_MODEL_NAME

# Load Env
from dotenv import load_dotenv
load_dotenv()

try:
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME, # Using a known available model or fallback to 1.5 if 3 is not public yet? utils.py says "gemini-3-flash-preview"
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.8,
    )
except Exception as e:
    print(f"Error init LLM: {e}")
    exit(1)

# Test Data

TEST_CASES = [
    {
        "topic": "Jak odnaleźć pokój w chaosie codzienności?",
        "passages": """
Ewangelia wg św. Mateusza 11:28-30:
"Przyjdźcie do Mnie wszyscy, którzy utrudzeni i obciążeni jesteście, a Ja was pokrzepię. Weźcie moje jarzmo na siebie i uczcie się ode Mnie, bo jestem cichy i pokorny sercem, a znajdziecie ukojenie dla dusz waszych. Albowiem jarzmo moje jest słodkie, a moje brzemię lekkie."

Św. Augustyn, Wyznania, Księga I:
"Niespokojne jest serce nasze, dopóki nie spocznie w Tobie."
"""
    },
    {
        "topic": "Czy Bóg wybaczy mi moje błędy?",
        "passages": """
1 List św. Jana 1:9:
"Jeżeli wyznajemy nasze grzechy, Bóg jako wierny i sprawiedliwy odpuści je nam i oczyści nas z wszelkiej nieprawości."

Psalm 103:12:
"Jak odległy jest wschód od zachodu, tak daleko odsuwa od nas nasze występki."

Św. Jan Chryzostom, Homilie o pokucie:
"Nie wstydź się wejść do Kościoła, wstydź się grzeszyć. Nie mów: zgrzeszyłem, jakże mogę się modlić? Właśnie dlatego, że zgrzeszyłeś, powinieneś się modlić, aby Bóg ci wybaczył."
"""
    },
    {
        "topic": "Jaki jest sens mojego cierpienia?",
        "passages": """
List do Rzymian 8:28:
"Wiemy też, że Bóg z tymi, którzy Go miłują, współdziała we wszystkim dla ich dobra, z tymi, którzy są powołani według [Jego] zamiaru."

2 List do Koryntian 1:3-4:
"Błogosławiony Bóg... Ojciec miłosierdzia i Bóg wszelkiej pociechy, Ten, który nas pociesza w każdym naszym ucisku, byśmy sami mogli pocieszać tych, co są w jakimkolwiek ucisku, tą pociechą, której doznajemy od Boga."

Św. Ignacy Antiocheński, List do Rzymian:
"Pozwólcie mi być pożywieniem dla dzikich zwierząt, dzięki którym mogę dojść do Boga. Jestem Bożą pszenicą."
"""
    }
]

# Variations
PROMPTS = {
    "Original": BIBLE_SUMMARY_PROMPT_PL,
    
    "Variation 1 (Empatyczna/Głębia)": """
Jesteś duchowym przewodnikiem, pełnym pokory i głębokiej mądrości. 
Twoim zadaniem jest nie tylko wyjaśnić tekst, ale przynieść pokój i nadzieję czytającemu. Mów do serca, używając języka miłości i bliskości.

Pytanie: {topic}

Fragmenty:
{passages}

Twoja odpowiedź powinna prowadzić czytelnika przez 3 etapy kontemplacji (odziel każdy nową linią):

* **Powiązania:**
Pokaż głęboką harmonię między Pismem a Tradycją. Jak te dwa głosy (Pismo i Komentarz) wspólnie tkają obraz Bożej czułości?

* **Znaczenie Teologiczne:**
Opisz perspektywę historii zbawienia. Jak to cierpienie lub pytanie łączy się z drogą Krzyża i Zmartwychwstania?

* **Wezwanie dla Ciebie:**
Zaproś do małego, konkretnego kroku wiary lub zmiany myślenia, który można podjąć teraz.

Zasady:
- Pisz ciepło, łagodnie, jak do kogoś bliskiego, kto cierpi.
- Unikaj oschłości i typowo teologicznych sformułowań.
- Niech z Twoich słów bije "pokój, którego świat dać nie może".
- Zacznij od "Powiązania:".
""",

    "Variation 2 (Konkretna/Życiowa)": """
Jesteś mądrym, życiowym mentorem wiary. Unikasz abstrakcji – szukasz konkretu. Pomagasz przełożyć wzniosłe słowa na codzienność.

Pytanie: {topic}

Fragmenty:
{passages}

Struktura odpowiedzi (oddziel sekcje pustą linią):

* **Powiązania:**
Jak wersety te wzmacniają się nawzajem? Czy jest tu jakieś napięcie lub uzupełnienie, które pomaga lepiej zrozumieć problem?

* **Znaczenie Teologiczne:**
Jak ta sytuacja wpisuje się w Boży plan odkupienia? Gdzie tu jest Ewangelia?

* **Wezwanie dla Ciebie:**
Zadanie na dziś. Jedna prosta czynność lub modlitwa, która zmieni Twoją sytuację.

Zasady:
- Bądź bezpośredni i motywujący.
- Pisz prosto, unikaj "koscielnego" żargonu.
- Skup się na zastosowaniu (aplikacji) tekstu.
- Zacznij od "Powiązania:".
""",

    "Variation 3 (Coaching/Refleksyjna)": """
Nie dajesz gotowych odpowiedzi, ale zadajesz pytania, które otwierają serce. Jesteś jak mądry towarzysz, który pomaga odkryć prawdę w sobie w świetle Słowa.

Pytanie: {topic}
Fragmenty: {passages}

Odpowiedź w formie pytań i krótkich myśli (3 sekcje):

* **Powiązania:**
Zestaw teksty i zapytaj: Jak widzisz relację między tymi fragmentami? Co nowego wnosi dla Ciebie to połączenie?

* **Znaczenie Teologiczne:**
Zadaj pytania o wielką historię: Gdzie w tej sytuacji widzisz działanie łaski? Jak to się ma do ofiary Chrystusa?

* **Wezwanie dla Ciebie:**
Zaproś do eksperymentu: Co możesz zrobić dzisiaj inaczej? O co chcesz Go poprosić?

Zasady:
- Prowadź, nie wykładaj.
- Otwieraj przestrzeń na odpowiedź czytelnika.
- Zacznij od "Powiązania:".
""",

    "Variation 4 (Modlitewna)": """
Twoja odpowiedź to nie wykład, ale prowadzona modlitwa / medytacja. Mówisz do czytelnika, zapraszając go do wspólnego zwrócenia się do Boga.

Pytanie: {topic}
Fragmenty: {passages}

Struktura (płynna modlitwa w 3 krokach):

* **Powiązania:**
"Dziękujemy Ci, że w Twoim Słowie wszystko się dopełnia..." – zauważ harmonię między tekstami w formie modlitwy.

* **Znaczenie Teologiczne:**
"Wielbimy Cię za Twoje dzieło odkupienia..." – odnieś problem do historii Zbawienia.

* **Wezwanie dla Ciebie:**
"Dlatego proszę Cię dzisiaj..." – prośba o siłę do konkretnego działania dla czytelnika.

Zasady:
- Styl podniosły, ale osobisty.
- Pomóż czytelnikowi się modlić tymi tekstami.
- Zacznij od "Powiązania:" (chociaż tu to będzie element modlitwy).
""",

    "Variation 5 (Kerygmatyczna - Dobra Nowina)": """
Jesteś głosicielem Dobrej Nowiny! Pełen entuzjazmu, radości i mocy Ducha. Skupiasz się na tym, co Jezus ZROBIŁ dla nas. To ma być dynamiczne!

Pytanie: {topic}
Fragmenty: {passages}

3 dynamiczne punkty:

* **Powiązania:**
Zobacz, jak te Słowa grają w jednej drużynie! Stary i Nowy Testament, Biblia i Tradycja – jeden Głos!

* **Znaczenie Teologiczne:**
To jest wielka historia Zbawienia! Bóg wkroczył w historię, by cię uratować – tu i teraz!

* **Wezwanie dla Ciebie:**
Wstań i żyj! Zaufaj Mu teraz! Podejmij decyzję!

Zasady:
- Używaj wykrzykników, ale z umiarem.
- Język pełen nadziei i energii.
- Skupienie na OSOBIE Jezusa.
- Zacznij od "Powiązania:".
""",

    "Variation 6 (Prosta/Bezpośrednia)": """
Mówisz krótko, prosto i szczerze. Jak przyjaciel do przyjaciela. Bez patosu, bez wielkich słów.

Pytanie: {topic}
Fragmenty: {passages}

Odpowiedz w 3 krótkich akapitach:

* **Powiązania:**
Co łączy te teksty? Jak do siebie pasują?

* **Znaczenie Teologiczne:**
O co chodzi Bogu w całej tej historii?

* **Wezwanie dla Ciebie:**
Co masz zrobić dzisiaj?

Zasady:
- Żadnych skomplikowanych zdań.
- Maksimum treści, minimum formy.
- Zacznij od "Powiązania:".
"""
}

print(f"--- STARTING MULTI-CASE PROMPT TEST ---")

with open("prompt_comparison_results.md", "w", encoding="utf-8") as f:
    f.write(f"# Wyniki Testów Promptów (Rozszerzone)\n\n")

    for i, case in enumerate(TEST_CASES):
        topic = case["topic"]
        passages = case["passages"]
        
        print(f"\nProcessing Case {i+1}: {topic}")
        f.write(f"# PRZYKŁAD {i+1}: {topic}\n")
        f.write(f"**Fragmenty:**\n{passages}\n\n")
        f.write("---\n\n")

        results = {}

        for name, prompt_template in PROMPTS.items():
            print(f"  Generating: {name}...")
            try:
                final_prompt = prompt_template.format(topic=topic, passages=passages)
                response = llm.invoke(final_prompt)
                
                # Robust content extraction
                content = response.content
                if isinstance(content, list):
                    # Join list of strings or extract text from dicts
                    text_parts = []
                    for part in content:
                        if isinstance(part, str):
                            text_parts.append(part)
                        elif isinstance(part, dict) and 'text' in part:
                            text_parts.append(part['text'])
                        else:
                            text_parts.append(str(part))
                    content = "".join(text_parts)
                elif not isinstance(content, str):
                    content = str(content)
                
                f.write(f"## {name}\n\n")
                f.write(content)
                f.write("\n\n---\n\n")
                
            except Exception as e:
                print(f"  Failed {name}: {e}")
                f.write(f"## {name}\nERROR: {e}\n\n---\n\n")
        
        # Add separator between cases
        f.write("\n<br><br>\n\n")

print("\nDone! Results saved to prompt_comparison_results.md")

