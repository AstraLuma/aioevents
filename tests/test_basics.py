def test_basics(mocker):
    from aioevents import Event

    class Spam:
        egged = Event("The spam has been egged")

    spam = Spam()

    inst_handler = mocker.stub('inst_handler')
    cls_handler = mocker.stub('cls_handler')

    spam.egged.handler(inst_handler)
    Spam.egged.handler(cls_handler)

    spam.egged()

    assert inst_handler.call_count == 1
    assert cls_handler.call_count == 1
