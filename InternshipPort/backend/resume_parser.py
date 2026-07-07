import os
import PyPDF2
import pandas as pd
import spacy

from spacy.matcher import PhraseMatcher


# LOAD SPACY MODEL

nlp = spacy.load(
    "en_core_web_sm"
)


# LOAD SKILLS DATABASE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
skills_path = os.path.join(BASE_DIR, "datasets", "skills_dataset.csv")
skills_df = pd.read_csv(skills_path)

SKILLS_DB = skills_df[
    "Skills"
].dropna().str.lower().tolist()


# CREATE PHRASE MATCHER

matcher = PhraseMatcher(
    nlp.vocab,
    attr="LOWER"
)

patterns = [

    nlp.make_doc(skill)

    for skill in SKILLS_DB
]

matcher.add(
    "SKILLS",
    patterns
)


# EXTRACT TEXT FROM PDF

def extract_resume_text(file_path):

    text = ""

    with open(file_path, "rb") as file:

        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:

            extracted_text = page.extract_text()

            if extracted_text:

                text += extracted_text

    return text


# EXTRACT SKILLS USING NLP

def extract_skills(text):

    doc = nlp(text)

    matches = matcher(doc)

    found_skills = set()

    for match_id, start, end in matches:

        skill = doc[start:end].text

        found_skills.add(
            skill.lower()
        )

    return list(found_skills)

