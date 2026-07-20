# ExViewer

## Overview

exviewer is a viewer that displays exported WhatsApp chats in a chat-style interface for easier reading.

The app uses mmap to efficiently read large chat export files.
It also uses a PyQt6 model/view that lazily loads the messages on demand, keeping memory usage extremely low.

## Setup

### Windows installer

For Windows users, download and install the [installer](https://github.com/OndiekiErnest/exviewer/blob/Ernesto/exviewer%2064-bit.exe) above.

NOTE: The installer is not signed, so it may trigger antivirus warnings.

### From source

To build from source, run the following commands in your environment:

```bash
git clone https://github.com/OndiekiErnest/exviewer.git
```

```bash
cd exviewer
```

```bash
pip install -r requirements.txt
```

```bash
py main.py
```
