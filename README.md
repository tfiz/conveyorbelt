# pypem
download from hypme.com 

Lets you download songs via hypemachine's listings.  It works *most* of the time.
Hypemachine is a frontend of sorts for other blogs; it doesn't host music.
Once we get the download urls we just go to the respective sites and grab the files.

Requires requests

Maybe your favorites?
```python
s = get_hype_session("some_user_name", "the_correct_password")
ls = get_hype_user_loves("some_user_name", s)
download_list(ls)
close_session(s)
```

Or maybe you just want the top 20 in the past three days?
There is no need to actually login though it may help if
you have problems with blocking. Just create a dummy session
and download.

```python
download_popular_20()
```
