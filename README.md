Simple script that sends PDF files to an API through Post requests, and stores the response in a SQLite database.


**Parameters:**

**APIURL** = API endpoint where requests should be sent.

**DBURL** = Database url. "sqlite:///documents.sqlite" for default DB

**BASEPATH** = Where the Db will be created.

**DATAPATH** = Relative path from _BASEPATH_ for the documents to scan.

**CONCURRENCY** = 5 Max concurrency Aiohttp should use. Only used in async mode.


#Scanner
Main class of the scanner

Main method is Scan. 

**Params**:

**sync**-> bool, true for sync operation (trough request library), False for async (Aiohttp).

**number**-> number of documents to scan.
