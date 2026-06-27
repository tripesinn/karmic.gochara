import os
import sys
from google.cloud import firestore

# Insert path to load local modules
sys.path.insert(0, '/Users/jero87/karmic.gochara')

def main():
    # Initialize Firestore client using ADC
    project_id = os.environ.get("PROJECT_ID", "karmic-gochara-cloud")
    print(f"Connecting to project '{project_id}'...")
    db = firestore.Client(project=project_id)
    
    # Verify collection and document read/write
    test_email = "test_firestore_speed@example.com"
    doc_ref = db.collection("users").document(test_email)
    
    print("Writing test profile...")
    import time
    start = time.time()
    doc_ref.set({
        "pseudo": "test_speed",
        "email": test_email,
        "name": "Test Speed",
        "plan": "pro",
        "syntheses_count": 0
    })
    write_duration = (time.time() - start) * 1000
    print(f"✅ Write completed in {write_duration:.2f} ms")
    
    print("Reading test profile...")
    start = time.time()
    doc = doc_ref.get()
    read_duration = (time.time() - start) * 1000
    if doc.exists:
        print(f"✅ Read completed in {read_duration:.2f} ms")
        print("Data:", doc.to_dict())
    else:
        print("❌ Document not found")
        
    print("Deleting test profile...")
    doc_ref.delete()
    print("Done!")

if __name__ == '__main__':
    main()
