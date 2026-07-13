# ExViewer

## Overview

exviewer is a viewer that displays WhatsApp chat exports in a chat-style interface.

The app uses mmap to efficiently read large chat export files.
It also uses a model/view that lazily loads the messages on demand, keeping memory usage extremely low.
