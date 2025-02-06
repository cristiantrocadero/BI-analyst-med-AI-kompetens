# Description: This script is the fourth script in the pipeline. 
# It imports the output from the previous scripts and uses the ML model 
# to predict the categories of the new articles. It then combines the predictions 
# with the final list of articles and validates the final structure with a JSON 
# schema. The final list is saved as 'validDict' for further processing.

import RssFeedNewArticle_2
import MLModelMLC_3
import FullRSSList_1_2

import jsonschema

def main():
    MLModelMLC_3.main() # Run the ML model training script
    categories = MLModelMLC_3.categories # Import the categories
    vectorizer = MLModelMLC_3.vectorizer # Import the vectorizer
    best_clf_pipeline = MLModelMLC_3.best_clf_pipeline # Import the best classifier pipeline

    RssFeedNewArticle_2.main() # Run the RSS feed script (also runs the RssArticles_1 script inside, so posts are available)
    printdepositlist = RssFeedNewArticle_2.printdepositlist # Import the printdepositlist

    FullRSSList_1_2.main()  # Run the FullRSSList script (needs posts from RssArticles_1, activated from RssFeedNewArticle_2)
    MyTheFinalList = FullRSSList_1_2.MyTheFinalList # Import the MyTheFinalList
    
    print('-----Starting MLModelReturns_4.py-----')

    # 1. Extract text from 'printdepositlist' (title + summary)
    print("Extracting title+summary from 'printdepositlist'...")
    my_text = printdepositlist  # Assuming this is a list of combined title + summary strings

    # 2. Remove empty strings
    my_text_no_empty = [t for t in my_text if t.strip() != ""]

    # 3. Transform text using vectorizer
    print("Transforming text with vectorizer...")
    my_text_transformed = vectorizer.transform(my_text_no_empty)

    # 4. Predict categories with the model
    print("Predicting categories with the model...")
    predictions = best_clf_pipeline.predict_proba(my_text_transformed)

    # 5. Assign categories based on a threshold
    print("Assigning categories based on a threshold...")
    threshold = 0.3
    results = {}  # dict of text -> list of predicted categories
    for idx, pvector in enumerate(predictions):
        text = my_text_no_empty[idx]
        predicted_categories = [categories[i] for i, prob in enumerate(pvector) if prob >= threshold]
        results[text] = predicted_categories

    # 6. Combine 'results' with 'MyTheFinalList'
    print("Combining the predictions with the final list...")
    combinedList = []
    for idx, item in enumerate(MyTheFinalList):
        title, summary, link, published = item
        text = f"{title} {summary}"
        predicted_topics = results.get(text, [])
        combinedList.append([title, summary, link, published, predicted_topics])

    # 7. Create a final list with dictionaries
    key_list = ['title', 'summary', 'link', 'published', 'topic']
    finalDict = [dict(zip(key_list, v)) for v in combinedList]

    # 8. Validate final structure with JSON schema (optional)
    print("Validating final structure with JSON schema...")
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "summary": {"type": "string"},
            "link": {"type": "string"},
            "published": {"type": "string"},
            "topic": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["title", "summary", "link", "published", "topic"]
    }

    valid_list = []
    for item in finalDict:
        try:
            jsonschema.validate(instance=item, schema=schema)
            valid_list.append(item)
        except jsonschema.exceptions.ValidationError as e:
            print(f"Validation error for item {item}: {e}")

    # 9. Export the validated list as 'validDict'
    global validDict  # To allow saving it later
    validDict = valid_list
    print(f"Number of valid dictionaries: {len(valid_list)}")
    #print("Validated dictionary:", validDict)
    print(f"First Article (Verify appearance): {validDict[0]}")

# Run the script
if __name__ == "__main__":
    main()