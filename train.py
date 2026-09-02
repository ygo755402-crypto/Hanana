import json
from database import create_database, import_file, all_text
from brain import Brain

create_database()
import_file()

documents = all_text()
brain = Brain(documents)

index = {
    "documents": documents,
    "idf": brain.idf
}

with open("brain.json", "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False)

print("Data imported into knowledge.db")
print("Brain index built and saved to brain.json")
print("Documents:", len(documents))
