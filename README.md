<p align="center">
    <a href="https://bbc-api.vercel.app"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Sayad-Uddin-Tahsin/BBC-News-API/main/Assets/Dark%20Logo.png"><img alt="Logo" src="https://raw.githubusercontent.com/Sayad-Uddin-Tahsin/BBC-News-API/main/Assets/Light%20Logo.png" height=100 width=100></picture></a>
</p>

# BBC News API
Discover the world of news through the lens of the BBC News API. With access to a rich array of news content spanning over 31 languages, this API serves as a gateway to the latest updates from the British Broadcasting Corporation (BBC). Seamlessly integrate trusted news sources into your applications, offering users a diverse and comprehensive view of current events. Empower your audience with timely and reliable information, curated by one of the most respected news organizations worldwide.

<a href="https://bbc-news-api.vercel.app"><img src="https://img.shields.io/website?url=https%3A%2F%2Fbbc-news-api.vercel.app%2Fping&up_message=Online&down_message=Offline&label=API" height=22></a>
<a href="https://bbc-news-api.vercel.app"><img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fbbc-news-api.vercel.app%2Fnews%3Flang%3Dbengali&query=%24%5B'elapsed%20time'%5D&label=Latency" height=22></a>
<a href="https://bbc-news-api.vercel.app"><img src="https://img.shields.io/github/license/Sayad-Uddin-Tahsin/BBC-News-API" height=22></a>
<a href="https://bbc-news-api.vercel.app"><img src="https://img.shields.io/badge/Supported%20Language-31-deepgreen" height=22></a>

<picture><source media="(prefers-color-scheme: dark)" srcset="https://web-badge-psi.vercel.app/visit-badge?theme=dark"><img alt="Requests Badge" src="https://web-badge-psi.vercel.app/visit-badge?theme=light"></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="https://web-badge-psi.vercel.app/latency-badge?theme=dark"><img alt="Latency Badge" src="https://web-badge-psi.vercel.app/latency-badge?theme=light"></picture>

## BBC
BBC, British Broadcasting Corporation is a Trustable News Site. It has coverage of 31 languages. 

## API
Application Programming Interface (API) is a way for two or more computer programs to communicate with each other. It is a type of software interface, offering a service to other pieces of software. A document or standard that describes how to build or use such a connection or interface is called an API specification.

## What is this API?
BBC News API is the API for serving the news from all the BBC Services according to your need. This API has a coverage of 31 Languages!

### How it works?
```mermaid
graph TD;
    yourpc["Your PC"]
    bbcweb["BBC Web"]
    api["API"]
    yourpc-- Request -->api;
    api-- Request-->bbcweb;
    bbcweb-- Response -->api;
    api-- Response -->yourpc;
```

## Documentation
The official BBC News API documentation can be found [here](http://bbc-news-api.vercel.app/documentation)

## Endpoints
Types & Languages are at [Documentation/Supported Languages](http://bbc-news-api.vercel.app/documentation#languages)

## Wrapper
### [bbc-news](https://pypi.org/project/bbc-news) for Python

<a href="https://pypi.org/project/bbc-news"><img src="https://img.shields.io/pypi/status/bbc-news?label=Status&logo=pypi&logoColor=ffffff" height=22></a>
<a href="https://pypi.org/project/bbc-news"><img src="https://img.shields.io/pypi/v/bbc-news?label=PyPI Version&logo=pypi&logoColor=ffffff" height=22></a>
<a href="https://python.org"><img src="https://img.shields.io/pypi/pyversions/bbc-news?label=Python&logo=python&logoColor=ffdd54" height=22></a>

The `bbc-news` Python wrapper provides convenient access to the BBC News API from your Python projects. It allows you to easily fetch news content and integrate it into your applications. You can install the wrapper via pip:

```sh
python -m pip install -U bbc-news
```
Example usage in Python: [Quick start with bbc-news](https://github.com/Sayad-Uddin-Tahsin/BBC-News-API/blob/main/bbc/README.md#quick-start)

## How to use?
Fetch our API URL with `GET` HTTP method! You can use any programming language to use our API. Here are code examples, how you can use our API in different language.

<!-- Python -->
<details open>
<summary><b>Python</b></summary>


<details open>
<summary>With Wrapper</summary>

```python
# pip install bbc-news

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


<details>
<summary>With requests</summary>

```py
# pip install requests
import requests

response = requests.get("https://bbc-news-api.vercel.app/news?lang=bengali").json()
print(response)
```

</details>
</details>

<!-- JavaScript (Node.js) -->
<details>

<summary>JavaScript (Node.js)</summary>

```js
const axios = require('axios');

axios.get('https://bbc-news-api.vercel.app/news?lang=chinese')
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
```
    
</details>

<!-- JavaScript (Browser) -->
<details>

<summary>JavaScript (Browser)</summary>

```py
fetch('https://bbc-news-api.vercel.app/news?lang=turkish')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.log(error));
```
    
</details>

<!-- PHP -->
<details>

<summary>PHP</summary>

```php
$response = file_get_contents('https://bbc-news-api.vercel.app/news?lang=spanish');
$data = json_decode($response);
print_r($data);
```
    
</details>

<!-- Ruby -->
<details>

<summary>Ruby</summary>

```ruby
require 'net/http'
require 'json'

uri = URI('https://bbc-news-api.vercel.app/news?lang=portuguese')
response = Net::HTTP.get(uri)
data = JSON.parse(response)
puts data
```
    
</details>

<!-- Java -->
<details>

<summary>Java</summary>

```java
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        try {
            URL url = new URL("https://bbc-news-api.vercel.app/news?lang=russian");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.connect();
            int responseCode = conn.getResponseCode();
            if (responseCode == 200) {
                Scanner scanner = new Scanner(url.openStream());
                String responseBody = scanner.useDelimiter("\\A").next();
                scanner.close();
                System.out.println(responseBody);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```
    
</details>

**NOTE: IF ANY ERROR ENCOUNTERED, FEEL FREE TO CREATE AN [ISSUE](https://github.com/Sayad-Uddin-Tahsin/BBC-Bangla-API/issues)**

## The response looks so messy?
The response you receive is in JSON format, which can appear a bit cluttered at first glance. But don’t worry — our website includes a built-in JSON formatter that makes the response much easier to read.

Simply visit the documentation page on the website and navigate to your desired endpoint (e.g., `news` or `latest`). There, you can test the API in all supported languages and view a neatly formatted version of the JSON response.

In your code, you can access values from the JSON like this:

```json
{
  "key": "value"
}
```
Just use the key to retrieve its corresponding value.
