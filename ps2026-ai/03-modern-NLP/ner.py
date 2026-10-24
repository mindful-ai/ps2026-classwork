from transformers import pipeline

# Load the pre-trained NER model
ner_pipeline = pipeline(
    "ner",
    model="dslim/bert-base-NER",
    aggregation_strategy="simple"
)

# Example text
text = "Ratan Tata was the chairman of the Tata Group"

# Run NER
results = ner_pipeline(text)

print(results)
