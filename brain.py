import math
import re

STOP = {
    "কি","কী","কে","কেন","কোথায়","কোথায়","কখন","কিভাবে","কীভাবে",
    "হয়","হয়","হলো","হল","এর","এবং","একটি","এক","তে","থেকে",
    "নাম","বল","বলুন","আমার","তুমি","আপনি","হয়েছে","হয়েছে",
    "আছে","ছিল","টায়","টা","জন","টি","নাকি","নাকিও"
}

SUFFIXES = ["র", "ের", "কে", "তে", "টি", "টা", "গুলো", "গুলি", "য়", "ে"]

def stem_bengali(word):
    for suffix in SUFFIXES:
        if word.endswith(suffix) and len(word) > len(suffix) + 1:
            return word[:-len(suffix)]
    return word

def tokens(text):
    raw = re.findall(r"[\w\u0980-\u09FF]+", text.lower())
    out = []
    for w in raw:
        if w not in STOP and len(w) > 1:
            w = stem_bengali(w)
            out.append(w)
    return out

def normalize(text):
    return set(tokens(text))

class Brain:
    def __init__(self, documents):
        self.documents = documents
        self.doc_sets = [(doc_id, text, normalize(text)) for doc_id, text in documents]

        df = {}
        for _, _, words in self.doc_sets:
            for w in words:
                df[w] = df.get(w, 0) + 1

        n = max(1, len(self.doc_sets))
        self.idf = {
            w: math.log((n + 1) / (freq + 1)) + 1
            for w, freq in df.items()
        }

    def rank(self, question, limit=3):
        q = normalize(question)
        if not q:
            return []

        scored = []
        for doc_id, text, words in self.doc_sets:
            overlap = q & words
            if not overlap:
                continue

            score = sum(self.idf.get(w, 1.0) for w in overlap)
            score += 0.5 * len(overlap)

            scored.append((score, doc_id, text))

        scored.sort(reverse=True)
        return scored[:limit]

    def answer(self, question):
        results = self.rank(question)

        if not results:
            return None, 0.0, []

        best_score, _, best_text = results[0]

        q_words = normalize(question)
        max_possible_score = sum(self.idf.get(w, 1.0) for w in q_words) + (0.5 * len(q_words))
        
        if max_possible_score > 0:
            confidence = min(0.99, max(0.0, best_score / max_possible_score))
        else:
            confidence = 0.0

        return best_text, confidence, results
