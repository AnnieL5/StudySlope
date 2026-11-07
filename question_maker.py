import os
import dotenv
from groq import Groq

async def question_maker(pdf_file):
    """
    pdf_file: FastAPI UploadFile object
    """

    # Load environment variables
    dotenv.load_dotenv(".env")

    # Initialize Groq client
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Save the uploaded PDF temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await pdf_file.read()
        tmp.write(content)
        tmp_path = tmp.name

    # Load and split PDF
    loader = PyPDFLoader(tmp_path)
    docs = loader.load()

    splitter = TokenTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    combined_text = "\n".join([chunk.page_content for chunk in chunks[:10]])

    # Prompt for flashcards - modified to ensure JSON output
    prompt = f"""
    You are an expert tutor creating study flashcards.
    Create 10 flashcards from the following notes.
    
    Return ONLY a JSON array with this exact format:
    [
      {{"question": "question text here", "answer": "answer text here"}},
      {{"question": "question text here", "answer": "answer text here"}}
    ]
    
    Do not include any other text, explanations, or markdown formatting.
  
    Notes:
    {combined_text}
    """

    # Query Groq
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a tutor that makes clear and accurate flashcards. Return only valid JSON arrays, no markdown or extra text.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=800,
    )

    flashcards_text = response.choices[0].message.content.strip()

    # Remove markdown code blocks if present
    flashcards_text = re.sub(r"```json\s*|\s*```", "", flashcards_text)

    # Parse the JSON response
    try:
        flashcards_list = json.loads(flashcards_text)
    except json.JSONDecodeError as e:
        print(f"Failed to parse flashcards: {e}")
        print(f"Response was: {flashcards_text}")
        flashcards_list = []

    # Initialize SM-2 parameters for each new card
    for card in flashcards_list:
        card["n"] = 0
        card["ef"] = 2.5
        card["interval"] = 0
        card["due_date"] = datetime.now().strftime("%Y-%m-%d")

    # Save flashcards to set.json properly
    try:
        with open("set.json", "r") as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.extend(flashcards_list)

    with open("set.json", "w") as f:
        json.dump(existing_data, f, indent=2)

    print("\nFlashcards Generated:\n")
    print(json.dumps(flashcards_list, indent=2))

    # Clean up temp file
    os.remove(tmp_path)

    return flashcards_list