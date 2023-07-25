Welcome to aioevents's documentation!
=====================================

aioevents is a simple event system for asyncio. It allows objects to declare 
and emit events, and users to register handlers for those events.

::

  class Spam:
      egged = Event("The spam has been egged")
  
  a_spam = Spam()

  @a_spam.egged.handler
  def on_egged(sender: Spam):
      print("An egging has occurred")

  a_spam.egged.trigger()
   

Events may have positional or keyword arguments::

   
  @a_spam.egged.handler
  def on_egged(sender: Spam, num, foo):
      print("An egging has occurred")

  s_spam.egged(42, foo='bar')

Handlers can be registered at the class level, and those will receive all instance's events::

  @Spam.egged.handler
  def on_egged(sender: Spam, num, foo):
      print("An egging has occurred")

  more_spam = Spam()  

  s_spam.egged(42, foo='bar')
  more_spam.egged(24, foo='baz')

Handlers may be regular functions or coroutines::

  @a_spam.egged.handler
  def on_egged_sync(sender, num, foo):
      print("Handling an egging")

  @a_spam.egged.handler
  async def on_egged_async(sender, num, foo):
      print("Handling an egging, asyncly")
      await asyncio.sleep(7)


Events may also be triggered on the class. In that case, no instance-level 
handlers will be called, and the first argument will be :const:`None`

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   apiref
   sample


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
