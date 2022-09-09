# [BBC Bangla API](https://BBC-Api.sy-uinuin.repl.co/news)
## BBC
BBC, British Broadcasting Corporation is a Trustable News Site. BBC has almost every languages!
[BBC Bangla](https://bbc.com/bengali) is the site for Bangladeshi People as they serves News in `Bangla`.

## API
Application Programming Interface(API) is a way for two or more computer programs to communicate with each other. It is a type of software interface, offering a service to other pieces of software. A document or standard that describes how to build or use such a connection or interface is called an API specification.

## What is this API?
BBC Bangla API is an API that serves you the News from [BBC Bangla](https://bbc.com/bengali)!

## Requirements
| Name | Version | Install Syntax |
|        ---:|     :---:     | :---       |
| [Python](https://python.org) | 3.9 | [`python.org`](https://www.python.org/downloads/release/python-390/) |
| [Flask](https://pypi.org/project/Flask/2.2.2/) | 2.2.2 | `pip install Flask==2.2.2` |
| [Request-HTML](https://pypi.org/project/requests-html/0.10.0/) | 0.10.0 | `pip install requests-html==0.10.0` |
| [Time](https://docs.python.org/3.9/library/time.html) | ------ | `builtin` |
| [Json](https://docs.python.org/3.9/library/json.html) | ------ | `builtin` |

## How to use?
Once you run the [Code](https://github.com/Sayad-Uddin-Tahsin/BBC-Bangla-API/blob/main/main.py), a piece of URL will be printed in your `Console`!
If you click the url you should get a result `{"status":"OK"}` according to [Line: 9 - 11](https://github.com/Sayad-Uddin-Tahsin/BBC-Bangla-API/blob/main/main.py#L10-L13). https://github.com/Sayad-Uddin-Tahsin/BBC-Bangla-API/blob/475e8a45260b3bbde646b10c483069511f420e33/main.py#L10-L13
If the Status says `OK` that means you've configured `Flask` perfectely! Now you just need to add `/news` after the Link printed before!
It should take some time to give the output because It need to fetch every single News of [BBC Bangla](https://bbc.com/bengali).

**NOTE: IF ANY ERROR OCCURED, FEEL FREE TO CREATE AN [ISSUE](https://github.com/Sayad-Uddin-Tahsin/BBC-Bangla-API/issues)**

## The response looks so messy?
Actually the response is given in `json` format. So, it can feel you so messy but don't worry, You can view the response after formatting that is so good to see!
Just `Paste` the response in [Json Formatter](nformatter.curiousconcept.com/#) and press `Process`, after a while it will show you the exact same result but neatly!

## API Live
The API is currently found [here](https://BBC-Api.sy-uinuin.repl.co/news/)(The News API Web). But it can be offline, Check if it is Online with [this link](https://BBC-Api.sy-uinuin.repl.co) and check if the `status` is `OK`!

> ***Don't forget to give a star on this repository!***

**Thank you**
  
  **- 09 September 2022/Tahsin**
