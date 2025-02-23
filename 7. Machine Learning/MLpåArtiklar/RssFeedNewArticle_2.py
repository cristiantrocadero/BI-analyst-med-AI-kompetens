# This scripts receives the posts 
# (Rss extracted news articles from the NEWRsArticles.py file)
# it is then cleans and structures them to be imported by NEWMLModelMLC.py

import RssArticles_1

def OnlyTitlesandSummaries(posts):
    """
    Extracts only the title and summary from the articles fetched in RssArticles_1.py.
    Args:
        posts (list): List of dictionaries containing article details.
    Returns:
        list: A list of dictionaries containing titles and summaries.
    """
    only_titles_and_summaries = []
    for x in posts:
        tempdict = {
            "title": x.get("title", ""),
            "summary": x.get("summary", ""),
            "link": x.get("link", ""),
            "published": x.get("published", "")
        }
        only_titles_and_summaries.append(tempdict)
    return only_titles_and_summaries

def TitleAndSummaryList(only_titles_and_summaries):
    """
    This function takes a list of dictionaries (each containing 'title' 
    and 'summary') and creates a nested list, where each inner list has 
    exactly one combined string: "title summary".
    
    Args:
        only_titles_and_summaries (list): List of dictionaries 
                                          (each has 'title' and 'summary').

    Returns:
        title_and_summary_list (list): A nested list where each sub-list 
                                       contains a single combined string.
    """
    # Initialize an empty list that will hold nested lists
    title_and_summary_list = []
    
    # Loop through each dictionary in the provided list
    for item in only_titles_and_summaries:
        # Combine the title and summary into one string
        combined = item["title"] + " " + item["summary"]
        
        # Append the combined text as a single-element list
        title_and_summary_list.append([combined])
    
    # Return the nested list
    return title_and_summary_list

def PrintDeposit(title_and_summary_list):
    """
    This function flattens the nested list returned by TitleAndSummaryList. 
    Each sub-list might look like ["Title Summary"], and we want a single 
    one-dimensional list like ["Title Summary", "Another Title Summary", ...].
    
    Args:
        title_and_summary_list (list): Nested list of single-element lists 
                                       containing "title summary" strings.

    Returns:
        flattened_list (list): A one-dimensional list of combined strings.
    """
    # Initialize an empty list to hold our flattened strings
    flattened_list = []
    
    # Loop through each sub-list in the nested list
    for item in title_and_summary_list:
        
        # Each 'item' itself might be something like ["Title Summary"]
        for value in item:
            # Add each string to our flattened_list
            flattened_list.append(value)
    
    # Return the flattened list of strings
    return flattened_list

def main():
    """
    Main function to process articles and print the results.
    """
    RssArticles_1.main() # Run the RssArticles_1 script
    posts = RssArticles_1.posts

    print('-----Starting RssFeedNewArticle_2.py-----')

    # 1. Extract only the 'title' and 'summary' keys (handling missing ones)
    Only_the_titles_Summaries = OnlyTitlesandSummaries(posts)
        
    # 2. Build a nested list combining the title and summary into one string
    The_Title_Summary_List = TitleAndSummaryList(Only_the_titles_Summaries)
        
    # 3. Flatten the nested list into a single list of strings
    global printdepositlist
    printdepositlist = PrintDeposit(The_Title_Summary_List)
    #print("Flattened Deposit List:")
    #print(printdepositlist)

    print(f"Total Articles Processed: {len(printdepositlist)}")
    if len(printdepositlist) > 0:
        print(f"First Article: {printdepositlist[0]}")

if __name__ == "__main__":
    main()
