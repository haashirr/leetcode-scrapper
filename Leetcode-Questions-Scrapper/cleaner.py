import fnmatch # Required for pattern matching

unclean_links = []  # List to store the lines(links) of the file

# Store all the links from txt file into list object.
# Open the file
with open("lc_links_unclean.txt", "r") as file:
    # Read each line one by one
    for line in file:
        # Process the line
        unclean_links.append(line)  # Add line as link to the list

# Remove the links in which a certain pattern is there eg:"/problems/*/solution"
def remove_links_with_pattern(links, pattern):
    clean_links = []
    for link in links:
        if pattern not in link:
            clean_links.append("https://leetcode.com"+link)
        else:
            print("Removed: " + link)
    return clean_links


pattern = "/solution"
links = remove_links_with_pattern(unclean_links, pattern)
print("Now total no of clean links: "+ str(len(links)))
# Remove duplicate links (if any by chance)
links = list(set(links))

# Open a file to write the results (links) to
# Used "w" instead of "a" so that each time link_cleaner.py runs it wont add to existing links in the file
with open('lc_links_cleann.txt', 'w') as f: 
    # Iterate over each link in your final list of links
    for link in links:
        # Write each link to the file, followed by a newline
        f.write(link)