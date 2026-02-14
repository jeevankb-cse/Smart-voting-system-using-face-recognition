# clean_data.py
import os

DATA_DIR = "data"
FILES_TO_DELETE = [
    "faces_data.pkl",
    "names.pkl",
    "Votes.csv",
    "voted_hashes.txt"
]

deleted = 0
for fname in FILES_TO_DELETE:
    path = os.path.join(DATA_DIR, fname)
    if os.path.exists(path):
        os.remove(path)
        print(f"Deleted: {path}")
        deleted += 1
    else:
        print(f"Not found: {path}")

if deleted == 0:
    print("Nothing to delete — already clean.")
else:
    print(f"\n✅ Cleaned {deleted} files. All registered faces, Aadhaar IDs, and votes removed.")
