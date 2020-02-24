import os, json, re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from html.parser import HTMLParser
SCRAPE_URL = r'https://www.pluralsight.com/search?categories=course&sort=title'
RAW_URL = r'https://www.pluralsight.com/courses/'
HTML_FILE = os.path.join("data", "search_results.html")
JSON_OUTPUT_FILE = os.path.join("data", "courses.json")

def load_html():
    driver = webdriver.Firefox()
    driver.get(SCRAPE_URL)
    load_more_results = r'jQuery(".button--secondary").click()'

    for i in range(1000):
        driver.execute_script(load_more_results)

    with open(os.path.join('data', 'search_results.html'), 'wt') as f:
        f.write(driver.page_source)

    driver.close()

def lookaround_tags(start_tag, end_tag):
    # Contruct regular expression
    lookbehind = r'(?<=' + start_tag + r')'
    lookahead = r'(?=' + end_tag + r')'
    wildcard = r'.*?'
    regex = "%s%s%s"%(lookbehind,wildcard,lookahead)

    # Compile it and return
    lookaround = re.compile(regex)
    return lookaround

def store_dict_as_json(dictionary, filepath):
    path = os.path.dirname(filepath)
    if not os.path.exists(path):
        os.mkdir(path)
    with open(filepath, 'wt') as f:
        json.dump(dictionary, f, sort_keys=True, indent=4)

def outer_search_result(HTML_FILE, class_name):
    read_state=False; track=0; search_snippets=[]
    with open(HTML_FILE, 'rt') as f:
        for line in f.readlines():
            if re.search(r'class=' + r'"' + class_name + r'"', line):
                read_state = True
                search_result = []
            
            if read_state:
                search_result.append(line)
                n_open = len(re.findall(r'<div', line))
                n_close = len(re.findall(r'/div>', line))
                track+=n_open;   track-=n_close
                if track == 0:
                    read_state = False
                    search_snippets.append(''.join(search_result))
    return search_snippets

def scrape_and_store_courses():
    # Search results encapsulation
    search_tag=r'<div class="search-result__title">'
    div_tag=r'</div>'
    result_lookaround = lookaround_tags(search_tag, div_tag)

    # Encapsulation within search results
    quote = r'"';      gt = r'>';     a_tag = r'</a>'
    courseid_lookaround = lookaround_tags(RAW_URL, quote)
    title_lookaround = lookaround_tags(gt, a_tag)

    # Parse data/search_results.html and put course data in a dicionary
    course_dict = {}
    with open(HTML_FILE, 'rt') as f:
        for line in f.readlines():
            search_line = result_lookaround.search(line)
            if search_line:
                title_tag = search_line.group()
                courseid = courseid_lookaround.search(title_tag)
                if courseid:
                    courseid = courseid.group()
                    title = title_lookaround.search(title_tag).group()
                    course_dict[courseid] = title
    
    print(course_dict)
    # Store dictionary as a json file
    store_dict_as_json(course_dict, JSON_OUTPUT_FILE)

def populate_dict(course_results):
    courses = {}
    for course in course_results:
        url_tag = course.find_element_by_class_name("cludo-result")
        this_url = url_tag.get_attribute('href')
        name = url_tag.text
        author = course.find_element_by_class_name("search-result__author").text
        level = course.find_element_by_class_name("search-result__level").text
        date = course.find_element_by_class_name("search-result__date").text
        length = course.find_element_by_class_name("search-result__length").text
        try:
            rating = course.find_element_by_class_name("search-result__rating").text
        except NoSuchElementException:
            rating = "none"
        
        thiscourse = {}
        thiscourse["url"] = this_url.strip()
        thiscourse["name"] = name.strip()
        thiscourse["author"] = author.split('by ')[-1]
        thiscourse["level"] = level.strip()
        thiscourse["date"] = date.strip()
        thiscourse["length"] = length.strip()
        thiscourse["rating"] = rating.strip()

        course_id = this_url.split('/')[-1]
        course_id = str(course_id.strip())
        courses[course_id] = thiscourse
        print('Done processing',course_id)
    return courses


if __name__ == "__main__":
    scrape_and_store_courses()