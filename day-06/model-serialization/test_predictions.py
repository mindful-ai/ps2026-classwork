import pickle

model = []
with open(r'C:\mindful-ai\sapient-ds\2025\work\day-07\model-serialization\housing_model.pkl', 'rb') as file:
    model = pickle.load(file)

print(model.predict([[100000, 15, 5, 3, 50000]]))