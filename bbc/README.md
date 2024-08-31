<p align="center">
    <a href="https://pypi.org/project/bbc-news"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Sayad-Uddin-Tahsin/BBC-News-API/main/Assets/Dark%20Logo.png"><img alt="Logo" src="https://raw.githubusercontent.com/Sayad-Uddin-Tahsin/BBC-News-API/main/Assets/Light%20Logo.png" height=100 width=100></picture></a>
</p>

# bbc-news

The `bbc-news` Python library provides a simple and intuitive interface for accessing the BBC News API, allowing developers to fetch the latest news articles from the British Broadcasting Corporation (BBC) programmatically. This library aims to streamline the integration of BBC news content into Python applications with ease.

<a href="https://pypi.org/project/bbc-news"><img src="https://img.shields.io/pypi/status/bbc-news?label=Status&logo=pypi&logoColor=ffffff" height=22></a>
<a href="https://pypi.org/project/bbc-news"><img src="https://img.shields.io/pypi/v/bbc-news?label=PyPI Version&logo=pypi&logoColor=ffffff" height=22></a>
<a href="https://python.org"><img src="https://img.shields.io/pypi/pyversions/bbc-news?label=Python&logo=python&logoColor=ffdd54" height=22></a>

<picture><source media="(prefers-color-scheme: dark)" srcset="https://web-badge-psi.vercel.app/latency-badge?theme=dark"><img alt="Latency Badge" src="https://web-badge-psi.vercel.app/latency-badge?theme=light"></picture>

## Features
- **Easy-to-use Interface:** The library offers a straightforward interface for accessing the BBC News API.
- **Language Support:** Users can retrieve news content in over 30 languages supported by the BBC.
- **Customizable Queries:** Developers can tailor their queries to fetch news articles based on specific topics, regions, or categories.
- **Error Handling:** The library includes built-in error handling mechanisms to handle API errors gracefully.

## Installation
You can install the bbc-news library via pip:

```console
python -m pip install bbc-news
```
`bbc-news` requires Python 3.7 or later.

## Quick Start

<!-- Example: Printing Categories -->
<details open>
<summary>Printing section titles</summary>

<!-- Code: Start -->
<details open>
<summary>Code</summary>


```python
# Import the Library
import bbc

# Get the News for Chinese
news = bbc.news.get_news(bbc.Languages.Chinese)

# Get the Category Titles
categories = news.news_categories()

# Print the category titles
print(categories)

```

</details>
<!-- Code: End -->

<!-- Output: Start -->
<details>
<summary>Output</summary>

```console
['Top story - Zhongwen', '必看', '深度报道', '新闻时事 趋势动态', '知识资讯 观点角度', '特别推荐']
```

</details>
</details>

<!-- Example: Printing Category News -->
<details>
<summary>Printing category news' title, summary, image link and news link</summary>

<!-- Code: Start -->
<details open>
<summary>Code</summary>


```python
# Import the Library
import bbc

# Get the News for Bengali
news = bbc.news.get_news(bbc.Languages.Bengali)

# Get the Category Titles
categories = news.news_categories()

# Loop through the category titles
for category in categories:
    # Get the Category News
    section_news = news.news_category(category)

    # Loop through the news dictionary
    for news_dict in section_news:
        # Print the Title
        print(news_dict['title'])

        # Print the News Summary/Description according to availability  (Returns None if unavailable)
        print(news_dict['summary'])

        # Print the Image Link
        print(news_dict['image_link'])

        # Print the News Link
        print(news_dict["news_link"])
                
        # Print a Separator Line
        print("---")
```

</details>
<!-- Code: End -->

<!-- Output: Start -->
<details>
<summary>Output</summary>

```console
রূপগঞ্জে গাজী টায়ার কারখানায় গিয়ে যা দেখলেন বিবিসি সংবাদদাতা
গাজী টায়ারস ফ্যাক্টরির যে ভবনে ২৫ শে অগাস্ট অগ্নিসংযোগ করা হয়েছিল সেটি পুড়ে ছাই হয়ে গেছে। ভবনটি ঝুঁকিপূর্ণ ঘোষণার পর ফায়ার সার্ভিস এর ভেতরে অভিযান বন্ধ রেখেছে। সেখানে গিয়ে বিভিন্ন জায়গায় থেমে থেমে আগুন জ্বলতে দেখা যায়।
https://ichef.bbci.co.uk/ace/ws/240/cpsprodpb/5b0d/live/acc7a540-66df-11ef-8c32-f3c2bc7494c6.jpg.webp
https://www.bbc.com/bengali/articles/clyn2eydejlo
---
'সম্পর্ক ঝালাইয়ে নজর দিল্লির'
৩১শে অগাস্ট শনিবার প্রকাশিত পত্রিকাগুলোর প্রথম পাতায় বন্যায় ক্ষয়ক্ষতি সংক্রান্ত খবর বেশ প্রাধান্য পেয়েছে সেইসাথে গুম প্রতিরোধ দিবসকে ঘিরে নানা কর্মসূচির খবর, মানবাধিকার লঙ্ঘন তদন্তে জাতিসঙ্ঘের হস্তক্ষেপ, দুর্নীতিসহ আরো নানা প্রসঙ্গ আলোচনায় রয়েছে।
https://ichef.bbci.co.uk/ace/ws/240/cpsprodpb/e21a/live/f8ac1610-6740-11ef-b970-9f202720b57a.jpg.webp
https://www.bbc.com/bengali/articles/clynrl8yzvvo
---
কালো টাকা সাদা করার বিধান বাতিল হলে কী হবে অর্থনীতিতে?
অপ্রদর্শিত অর্থের মোড়কে অবৈধভাবে অর্জিত কালো টাকা সাদা করার সুযোগ দেওয়াকে শুরু থেকেই বৈষম্যমূলক এবং অনৈতিক বলে দাবি করেছেন অর্থনীতিবিদরা।
https://ichef.bbci.co.uk/ace/ws/240/cpsprodpb/7039/live/5b0af020-66d7-11ef-b970-9f202720b57a.jpg.webp
https://www.bbc.com/bengali/articles/cr7r3xz8y12o

...
```

</details>
</details>

<!-- Example: Printing Latest News -->
<details>
<summary>Printing Latest News</summary>

<!-- Code: Start -->
<details open>
<summary>Code</summary>


```python
# Import the Library
import bbc

# Get the Latest News for Arabic
news_list = bbc.news.get_latest_news(bbc.Languages.Arabic)

# Loop through the list
for news_dict in news_list:
    # Print the Title
    print(news_dict['title'])

    # Print the News Summary/Description according to availability  (Returns None if unavailable)
    print(news_dict['summary'])

    # Print the Image Link
    print(news_dict['image_link'])

    # Print the News Link
    print(news_dict["news_link"])
            
    # Print a Separator Line
    print("---")

```

</details>
<!-- Code: End -->

<!-- Output: Start -->
<details>
<summary>Output</summary>

```console
كيف كانت الأوضاع داخل مخيم جنين أثناء مداهمة الجيش الإسرائيلي؟
كانت الشوراع داخل المخيم خالية، وحتى سيارات الإسعاف كانت تسير وفقاً لتوجيهات محددة، وتعرضت للتفتيش.
https://ichef.bbci.co.uk/ace/ws/240/cpsprodpb/f580/live/8b704870-66da-11ef-8c32-f3c2bc7494c6.jpg.webp
https://www.bbc.com/arabic/articles/c1l57yz7r40o
---
ماذا نعرف عن خطة التطعيم ضد شلل الأطفال في غزة؟
ستبدأ سلسلة من "التوقف الإنساني" عن القتال في غزة يوم الأحد، بهدف تمكين مئات الآلاف من الأطفال من تلقي لقاح شلل الأطفال.
https://ichef.bbci.co.uk/ace/ws/240/cpsprodpb/cc93/live/f32bc090-66fb-11ef-a006-fb0775301171.jpg.webp
https://www.bbc.com/arabic/articles/c5yp5wqvge4o
---
المقاتلون الروس يغادرون بوركينا فاسو للمساعدة في حرب أوكرانيا
المقاتلون الروس يغادرون بوركينا فاسو لمساعدة القوات الروسية في صد الهجمات الأوكرنية على منطقة كورسك،.
https://ichef.bbci.co.uk/ace/ws/240/cpsprodpb/3030/live/36e81670-6702-11ef-8c32-f3c2bc7494c6.jpg.webp
https://www.bbc.com/arabic/articles/c04930zve6wo

...
```

</details>
</details>

<!-- Example: Printing News of English -->
<details>
<summary>Printing News (English)</summary>

<!-- Code: Start -->
<details open>
<summary>Code</summary>


```python
# Import the Library
import bbc

# Get the Latest News for English
news = bbc.news.get_news(bbc.Languages.English)

# Get the Category Titles
categories = news.news_categories()

# Loop through the category titles
for category in categories:
    # Get the Category News
    section_news = news.news_category(category)

    # Loop through the news dictionary
    for news_dict in section_news:
        # Print the Title
        print(news_dict['title'])

        # Print the News Summary/Description according to availability  (Returns None if unavailable)
        print(news_dict['summary'])

        # Print the News Image according to availability (Returns None if unavailable)
        print(news_dict['image_link'])
        
        # Print the News Link
        print(news_dict["news_link"])
        
        # Print a Blank Line
        print("---")

```

</details>
<!-- Code: End -->

<!-- Output: Start -->
<details>
<summary>Output</summary>

```console
Israel and Hezbollah exchange heavy fire in major escalation
Hezbollah says it fired hundreds of rockets after Israel says it launched pre-emptive strikes on Sunday morning.
https://ichef.bbci.co.uk/news/240/cpsprodpb/c16f/live/604e1f70-6354-11ef-8665-19cd0ac0261f.jpg.webp
https://bbc.com/news/articles/cq6rzvyz9p6o
---
Matthew Perry's death reveals Hollywood's ketamine 'wild west'
Doctors say ketamine has become "super easy" to get through a network of online clinics that exploit government loopholes.
https://ichef.bbci.co.uk/news/240/cpsprodpb/11ab/live/fa8ebf00-617d-11ef-8c32-f3c2bc7494c6.jpg.webp
https://bbc.com/news/articles/czrgp7pj4g2o
---
Israel and Hezbollah exchange heavy fire in major escalation
Hezbollah says it fired hundreds of rockets after Israel says it launched pre-emptive strikes on Sunday morning.
https://ichef.bbci.co.uk/news/240/cpsprodpb/c16f/live/604e1f70-6354-11ef-8665-19cd0ac0261f.jpg.webp
https://bbc.com/news/articles/cq6rzvyz9p6o
---
Matthew Perry's death reveals Hollywood's ketamine 'wild west'
Doctors say ketamine has become "super easy" to get through a network of online clinics that exploit government loopholes.
https://ichef.bbci.co.uk/news/240/cpsprodpb/11ab/live/fa8ebf00-617d-11ef-8c32-f3c2bc7494c6.jpg.webp
https://bbc.com/news/articles/czrgp7pj4g2o

...
...
...
```

</details>
</details>

## Contributing
Contributions to the bbc-news Python library are welcome! If you encounter any issues, have suggestions for improvements, or would like to contribute new features, feel free to open an issue or submit a pull request on the [GitHub repository](https://github.com/Sayad-Uddin-Tahsin/BBC-News-API).

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/Sayad-Uddin-Tahsin/BBC-News-API/blob/main/LICENSE) file for details.
