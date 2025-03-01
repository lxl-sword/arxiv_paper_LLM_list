import feedparser
import datetime
import os
from urllib.parse import quote  # 用于 URL 编码

def arxiv_search(query, max_results=20):
    base_url = 'http://export.arxiv.org/api/query?'
    #encoded_query = quote(query)
    search_url = (f'search_query={query}&start=0&max_results={max_results}'
                  f'&sortBy={'submittedDate'}&sortOrder={'descending'}')
    response = feedparser.parse(base_url + search_url)
    return response.entries

def arxiv_search_today(query, max_results=20):
    base_url = 'http://export.arxiv.org/api/query?'
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    query_with_date = f'({query})+AND+submittedDate:[{today}0000+TO+{today}2359]'
    encoded_query = query_with_date
    search_url = f'search_query={encoded_query}&start=0&max_results={max_results}'
    response = feedparser.parse(base_url + search_url)
    print(f"🔍 Found {len(response.entries)} papers submitted today.")
    return response.entries

def arxiv_search_previous_day(query, max_results=20):
    base_url = 'http://export.arxiv.org/api/query?'
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    query_with_date = f'({query})+AND+submittedDate:[{yesterday_str}0000+TO+{yesterday_str}2359]'
    encoded_query = query_with_date
    search_url = f'search_query={encoded_query}&start=0&max_results={max_results}'
    response = feedparser.parse(base_url + search_url)
    print(f"🔍 Found {len(response.entries)} papers submitted on {yesterday_str}.")
    return response.entries


def save_results_as_html(entries, topic):
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    os.makedirs("docs", exist_ok=True)
    filename = f"docs/arxiv_{topic}_{today}.html"
   
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"<!DOCTYPE html>\n<html lang='en'>\n<head>\n<meta charset='UTF-8'>\n<title>{topic} - {today}</title>\n")
        f.write(f"<link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>\n")
        f.write(f"<link href='https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap' rel='stylesheet'>\n")
        f.write(f"<link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'>\n")
        f.write(f"<style>\n")
        f.write("body {\n")       
        f.write(f"font-family: 'Roboto', sans-serif;\n")  
        f.write(f"background-color: #f5f7fa;\n")  
        f.write(f"padding: 20px;\n")  
        f.write("}\n")  
        f.write(".card {\n")  
        f.write(f"    border-radius: 10px;\n")  
        f.write(f"    box-shadow: 0 4px 8px rgba(0,0,0,0.1);\n")  
        f.write("}\n")  
        f.write(".card-title {\n")  
        f.write(f"    font-weight: 700;\n")  
        f.write("}\n")  
        f.write(".card:hover {\n")  
        f.write(f"    transform: scale(1.02);\n")  
        f.write(f"    transition: 0.3s ease-in-out;\n")  
        f.write("}\n")  
        f.write(f"</style>\n</head>\n<body>\n") 
        f.write(f"<div class='container'>\n")
        f.write(f"<h1 class='text-center my-4'><i class='fas fa-book'></i>{topic} - {today}</h1>\n")
        f.write(f"<div class='row'>\n")


        if not entries:
            f.write("<p>❌ No papers found for today.</p>\n")
        else:
            for entry in entries:
                full_url = entry.id
                arxiv_id=full_url.split('/abs/')[-1]
                date = datetime.datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ")
                authors = ', '.join(author.name for author in entry.authors)
                f.write(f"<div class='col-md-6 mb-4'>\n")
                f.write(f"<div class='card'>\n")
                f.write(f"<div class='card-body'>\n")
                f.write(f"<h4 class='card-title'><a href='{entry.link}' target='_blank'>{entry.title}</a></h5>\n")
                f.write(f"<h5 class='card-subtitle mb-2 text-muted'>Authors:{authors}</h6>\n")
                f.write(f"<h6 class='card-subtitle mb-2 text-muted'>Date:{date}</h6>\n")
                f.write(f"<p class='card-text'>{entry.summary}</p>\n")
                f.write("</div>\n</div>\n</div>\n")
                
        f.write("</div>\n</div>\n")
        f.write(f"<script src='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'></script>\n")
        f.write("</body>\n</html>")
    
    update_index(today,topic)
    print(f"✅ Results saved to {filename}")
    

def update_index(latest_date,topic):
    index_file = "docs/index.html"
    if not os.path.exists(index_file):
        with open(index_file, "w", encoding="utf-8") as f:
            f.write("<!DOCTYPE html>\n<html>\n<head>\n<title>arXiv Archive</title>\n</head>\n<body>\n")
            f.write("<h1>📚 arXiv Paper Archive</h1>\n")
            f.write("<ul>\n")
            f.write("</ul>\n")
            f.write("</body>\n</html>")

    with open(index_file, "r", encoding="utf-8") as f:
        content = f.read()

    new_entry = f'<li><a href="arxiv_{topic}_{latest_date}.html">{topic} {latest_date} Papers</a></li>\n'
    if new_entry not in content:
        content = content.replace("<ul>\n", f"<ul>\n{new_entry}")

    with open(index_file, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    max_num=15000
    query = 'all:LLM+AND+all:"reinforcement%20learning"'
    results = arxiv_search(query, max_results=max_num)
    save_results_as_html(results,"LLM-RL")
    query = 'all:LLM+AND+all:planning'
    results = arxiv_search(query, max_results=max_num)
    save_results_as_html(results,"LLM-planning")
    query = 'all:LLM+AND+all:agent'
    results = arxiv_search(query, max_results=max_num)
    save_results_as_html(results,"LLM-agent")
