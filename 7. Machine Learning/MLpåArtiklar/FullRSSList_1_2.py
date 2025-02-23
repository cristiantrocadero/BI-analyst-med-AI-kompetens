# Description: This script extracts necessary fields 
# (title, summary, link, published) from posts and returns a list of dictionaries.
import RssArticles_1 
from datetime import datetime
import pandas as pd

def gettingNecessaryList(posts):
    """
    Extracts necessary fields (title, summary, link, published) from posts
    and returns a list of dictionaries.

    Args:
        posts (list): List of RSS articles, each as a dictionary.

    Returns:
        list: A list of dictionaries with filtered and necessary fields.
    """
    allitems = []

    for x in posts:
        try:
            tempdict = {
                "title": x.get("title", ""),
                "summary": x.get("summary", ""),
                "link": x.get("link", ""),
                "published": x.get("published", ""),
            }
            allitems.append(tempdict)
        except Exception as e:
            print(f"Error processing post: {e}")
    
    return allitems

def format_date(date_str):
    """
    Converts an RSS date string to the format YYYY-MM-DD HH:MM:SS.

    Args:
        date_str (str): The date string from the RSS feed.

    Returns:
        str: A formatted date string or None if parsing fails.
    """
    if not date_str or pd.isna(date_str):
        return None

    date_str = date_str.replace("GMT", "+0000")

    date_formats = [
        "%a, %d %b %Y %H:%M:%S %z",  # Example: "Mon, 05 Feb 2025 13:00:00 +0000"
        "%Y-%m-%dT%H:%M:%S%z"         # Example: "2025-02-05T13:00:00+0000"
    ]

    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

    print("Unknown format, could not parse:", date_str)
    return None

def ThefinalList(AllItemsX):
    """
    Converts AllItemsX into a final 2D list, ensuring 'published' is formatted.

    Args:
        AllItemsX (list): List of dictionaries with RSS article data.

    Returns:
        list: A list of lists with [title, summary, link, published].
    """
    finalList = []

    for item in AllItemsX:
        title = item.get("title", "")
        summary = item.get("summary", "")
        link = item.get("link", "")
        published = format_date(item.get("published", ""))

        if published:  # Only include items with valid published dates
            finalList.append([title, summary, link, published])
    
    return finalList

def main():
    """
    Main function to orchestrate the process of extracting and formatting RSS data.
    """
    posts = RssArticles_1.posts

    print('-----Starting FullRSSList_1_2.py-----')

    # Extract necessary fields from the raw RSS posts
    print("Extracting necessary fields from posts...")
    all_items = gettingNecessaryList(posts)

    # Create the final list with formatted dates
    print("Creating the final list...")
    final_list = ThefinalList(all_items)

    # Print the final list and its length
    #print(final_list)
    print(f"Number of valid posts: {len(final_list)}")

    # Expose the final list as a global variable for other scripts
    global MyTheFinalList
    MyTheFinalList = final_list

# Entry point for the script
if __name__ == "__main__":
    main()
