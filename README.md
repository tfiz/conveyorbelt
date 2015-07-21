# conveyorbelt
grab songs from the hype machine 

Lets you download songs via hypemachine's listings.
Get the stream urls and go to the respective sites and grab the files.

Requires requests - make http requests
         pickle - don't redownload stuff
         mutagen - edit audio tags

Maybe your favorites?
```python
import conveyb
conveyb.get_loves(some_user)
```

Or maybe you just want the top 20 in the past three days?

```python
import conveyb
conveyb.get_top20()
```

A file (default bucket.p) will be created to avoid duplicate downloads.
This name and the default folder can be changed.
