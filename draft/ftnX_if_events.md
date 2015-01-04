
Reliable Event:

1. Step prepare with provided [or default] timeout
2. Do some associated logic
3. Fire event

Reliable event delivery:

1. If fired delivery as "CONFIRMED"
2. Otherwise, wait timeout and fire as "INCOMPLETE" - receivers knows that
    events requires validation