
def read_initial_urls(path:str) -> list:
    """
    Reads the initial URLs from the initial_urls.txt file

    Args:
        path (str): relative path to the file

    Returns:
        initial_urls (list): The initial URLs from the file
        
    Raises: 
        /
    """
    with open(path, 'r') as urls_file:
        initial_urls = [file.replace("\n", "") for file in urls_file]
    
    return initial_urls

def filter_urls(urls: list, target_site: str) -> list:
    """
    Filters the URLs-List to only contain URLs to webpages with textual information and stay on the target webpage 
    
    Args:
        url (list): List of all crawled URLs
        target_site (str): Site on which the crawler should focus

    Returns:
        filtered_urls (list): All the filtered URLs that are on the same page and  
        
    Raises: 
        /
    """
    import urllib.parse
    import pathlib

    filtered_urls = []
    file_endings = ['.png', '.js', '.jpg', '.jpeg', '.gif', '.css', '.php', '.mp3']
    for url in urls:
        parsed = urllib.parse.urlsplit(url)
        url_ending = pathlib.Path(parsed.path).suffix.lower()
        if (url_ending not in file_endings) and (target_site in url):
            filtered_urls.append(url)
        
    return filtered_urls
