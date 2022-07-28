Simple script that sends PDF files to an API through Post requests, and stores the response in a SQLite database.


**Parameters:**

**APIURL** = API endpoint where requests should be sent.

**DBURL** = Database url. "sqlite:///documents.sqlite" for default DB

**BASEPATH** = Where the Db will be created.

**DATAPATH** = Relative path from _BASEPATH_ for the documents to scan.

# Usage
## Command line
Set the variables above to what you need.

Run the tool from the command line
```
usage: main.py [-h] [-sync] [-number NUMBER] [-rate RATE]
optional arguments:
  -h, --help      show this help message and exit
  -sync           Sync or async operation
  -number NUMBER  Number of documents to scan
  -rate RATE      Max concurrency for asyncio
```

## Scanner

Main class of the scanner

Main method is Scan.

**Params**:

**sync**-> bool, true for sync operation (through request library), False for async (Aiohttp).

**number**-> number of documents to scan.
