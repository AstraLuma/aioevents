# aioevents

Events for asyncio (PEP 3156)

## Usage

To declare an event:

```python
from aioevents import Event

class Spam:
	egged = Event("The spam has been egged")
```

To register a handler:

```python

spam = Spam()

@spam.egged.handler
def on_egged(sender, amt):
    print("Spam got egged {} times".format(amt)")
```

Triggering an event:

```python
spam.egged(42)
```
