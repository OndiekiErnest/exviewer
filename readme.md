# ExViewer

## Overview

exviewer is a viewer that displays exported WhatsApp chats in a chat-style interface for easier reading.

The app uses mmap to efficiently read large chat export files.
It also uses a model/view that lazily loads the messages on demand, keeping memory usage extremely low.
