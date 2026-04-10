# Design A Search Autocomplete System

**14**

# Design A Search Autocomplete System

When searching on Google or shopping at Amazon, as you type in the search box, one or more matches for the search term are presented to you. This feature is referred to as autocomplete, typeahead, search-as-you-type, or incremental search. Figure 1 presents an example of a Google search showing a list of autocompleted results when “dinner” is typed into the search box. Search autocomplete is an important feature of many products. This leads us to the interview question: design a search autocomplete system, also called “design top k” or “design top k most searched queries”.

![Image represents a Google search results page.  At the top, the Google logo is prominently displayed. Below it, a search bar contains the partial search query '[dinner|'.  Beneath the search bar, a list of auto-suggested search queries appears, each prefixed with a magnifying glass icon: 'dinner ideas,' 'dinner recipes,' 'dinner near me,' 'dinner,' 'dinnerly,' 'dinner in spanish,' 'dinner nearby,' 'dinner tonight,' 'dinner rolls,' and 'dinnerware sets.'  At the bottom of the search results box are two buttons: 'Google Search' and 'I'm Feeling Lucky.' A small microphone icon is present in the top right corner of the search bar, suggesting voice search functionality. Finally, a small text link at the very bottom reads 'Report inappropriate predictions,' providing a mechanism for user feedback.  No information flows visibly between components; the image depicts a static snapshot of the search interface before a search is initiated.](images/figure-13-1-KCZCT7DP.png)

Figure 1

## Step 1 - Understand the problem and establish design scope

The first step to tackle any system design interview question is to ask enough questions to clarify requirements. Here is an example of candidate-interviewer interaction:

**Candidate**: Is the matching only supported at the beginning of a search query or in the middle as well?  
**Interviewer**: Only at the beginning of a search query.

**Candidate**: How many autocomplete suggestions should the system return?  
**Interviewer**: 5

**Candidate**: How does the system know which 5 suggestions to return?  
**Interviewer**: This is determined by popularity, decided by the historical query frequency.

**Candidate**: Does the system support spell check?  
**Interviewer**: No, spell check or autocorrect is not supported.

**Candidate**: Are search queries in English?  
**Interviewer**: Yes. If time allows at the end, we can discuss multi-language support.

**Candidate**: Do we allow capitalization and special characters?  
**Interviewer**: No, we assume all search queries have lowercase alphabetic characters.

**Candidate**: How many users use the product?  
**Interviewer**: 10 million DAU.

**Requirements**

Here is a summary of the requirements:

* Fast response time: As a user types a search query, autocomplete suggestions must show up fast enough. An article about Facebook’s autocomplete system [1] reveals that the system needs to return results within 100 milliseconds. Otherwise it will cause stuttering.
* Relevant: Autocomplete suggestions should be relevant to the search term.
* Sorted: Results returned by the system must be sorted by popularity or other ranking models.
* Scalable: The system can handle high traffic volume.
* Highly available: The system should remain available and accessible when part of the system is offline, slows down, or experiences unexpected network errors.

### Back of the envelope estimation

* Assume 10 million daily active users (DAU).
* An average person performs 10 searches per day.
* 20 bytes of data per query string:
* Assume we use ASCII character encoding. 1 character = 1 byte
* Assume a query contains 4 words, and each word contains 5 characters on average.
* That is 4 x 5 = 20 bytes per query.
* For every character entered into the search box, a client sends a request to the backend for autocomplete suggestions. On average, 20 requests are sent for each search query. For example, the following 6 requests are sent to the backend by the time you finish typing “dinner”.

  search?q=d

  search?q=di

  search?q=din

  search?q=dinn

  search?q=dinne

  search?q=dinner
* ~24,000 query per second (QPS) = 10,000,000 users \* 10 queries / day \* 20 characters / 24 hours / 3600 seconds.
* Peak QPS = QPS \* 2 = ~48,000
* Assume 20% of the daily queries are new. 10 million \* 10 queries / day \* 20 byte per query \* 20% = 0.4 GB. This means 0.4GB of new data is added to storage daily.

## Step 2 - Propose high-level design and get buy-in

At the high-level, the system is broken down into two:

* Data gathering service: It gathers user input queries and aggregates them in real-time. Real-time processing is not practical for large data sets; however, it is a good starting point. We will explore a more realistic solution in deep dive.
* Query service: Given a search query or prefix, return 5 most frequently searched terms.

### Data gathering service

Let us use a simplified example to see how data gathering service works. Assume we have a frequency table that stores the query string and its frequency as shown in Figure 2. In the beginning, the frequency table is empty. Later, users enter queries “twitch”, “twitter”, “twitter,” and “twillo” sequentially. Figure 2 shows how the frequency table is updated.

![Image represents a high-level system design diagram illustrating data partitioning or sharding based on query parameters.  The diagram shows five vertical sections separated by dashed lines. The leftmost section is labeled 'QueryFrequency,' representing a source or input of queries. The remaining four sections represent different partitions or shards, each labeled with 'query: [platform]' where the platform is either 'twitch,' 'twitter' (appearing twice), or 'twillo.'  Each of these platform-specific sections contains a label 'QueryFrequency[platform]1...' suggesting that each shard stores query frequency data related to a specific platform.  There are no explicit connections drawn between the sections, implying that the data is independently managed within each shard based on the query parameter (platform).  The 'QueryFrequency' section on the left likely represents the initial query input, which is then routed or distributed to the appropriate shard based on the platform specified in the query.  The ellipsis ('...') in the shard labels suggests that there might be more partitions than those shown.](images/figure-13-2-5FQ3SDWF.svg)

Figure 2

### Query service

Assume we have a frequency table as shown in Table 1. It has two fields.

* Query: it stores the query string.
* Frequency: it represents the number of times a query has been searched.

| **Query** | **Frequency** |
| --- | --- |
| twitter | 35 |
| twitch | 29 |
| twilight | 25 |
| twin peak | 21 |
| twitch prime | 18 |
| twitter search | 14 |
| twillo | 10 |
| twin peak sf | 8 |

Table 1

When a user types “tw” in the search box, the following top 5 searched queries are displayed (Figure 3), assuming the frequency table is based on Table 1.

![The image represents a simple autocomplete suggestion box.  At the top, a light gray rectangular text box displays 'tw|' as the user's partial input. Below this input box is a table with five rows, each containing a potential autocomplete suggestion.  These suggestions are: 'twitter', 'twitch', 'twilight', 'twin peak', and 'twitch prime'.  There are no visible connections or information flow besides the implied relationship that the suggestions in the table are related to the partial input 'tw|' in the text box above.  The suggestions are presented as a list, implying a ranking or order of relevance, though no explicit ranking mechanism is shown.](images/figure-13-3-P3IEBIJH.png)

Figure 3

To get top 5 frequently searched queries, execute the following SQL query:

![Image represents a SQL query.  The query selects all columns (`SELECT *`) from a table named `frequency_table`.  A `WHERE` clause filters the results to include only rows where the `query` column starts with the string 'prefix' (using the `LIKE 'prefix%'` operator). The results are then `ORDER`ed in descending order (`DESC`) based on the `frequency` column. Finally, the `LIMIT` clause restricts the output to the top 5 rows, effectively returning the 5 most frequent queries starting with 'prefix'.  The keywords `SELECT`, `FROM`, `WHERE`, `LIKE`, `ORDER BY`, `DESC`, and `LIMIT` are highlighted in blue, indicating their significance as SQL commands.](images/figure-13-4-QFNBMQOX.svg)

Figure 4

This is an acceptable solution when the data set is small. When it is large, accessing the database becomes a bottleneck. We will explore optimizations in deep dive.

## Step 3 - Design deep dive

In the high-level design, we discussed data gathering service and query service. The high-level design is not optimal, but it serves as a good starting point. In this section, we will dive deep into a few components and explore optimizations as follows:

* Trie data structure
* Data gathering service
* Query service
* Scale the storage
* Trie operations

### Trie data structure

Relational databases are used for storage in the high-level design. However, fetching the top 5 search queries from a relational database is inefficient. The data structure trie (prefix tree) is used to overcome the problem. As trie data structure is crucial for the system, we will dedicate significant time to design a customized trie. Please note that some of the ideas are from articles [2] and [3].

Understanding the basic trie data structure is essential for this interview question. However, this is more of a data structure question than a system design question. Besides, many online materials explain this concept. In this chapter, we will only discuss an overview of the trie data structure and focus on how to optimize the basic trie to improve response time.

Trie (pronounced “try”) is a tree-like data structure that can compactly store strings. The name comes from the word re**trie**val, which indicates it is designed for string retrieval operations. The main idea of trie consists of the following:

* A trie is a tree-like data structure.
* The root represents an empty string.
* Each node stores a character and has 26 children, one for each possible character. To save space, we do not draw empty links.
* Each tree node represents a single word or a prefix string.

Figure 5 shows a trie with search queries “tree”, “try”, “true”, “toy”, “wish”, “win”. Search queries are highlighted with a thicker border.

![Image represents a directed acyclic graph (DAG) structured as a tree.  A root node, labeled 'root,' points to two child nodes, 't' and 'w.' Node 't' further branches into 'tr' and 'to,' while 'w' leads to 'wi.'  Node 'tr' has three children: 'tre,' 'tru,' and 'try.'  'tre' points to a leaf node 'tree,' and 'tru' points to a leaf node 'true.'  Both 'tree' and 'true' are highlighted with a teal border. Similarly, 'to' has two children: 'toy' (teal bordered) and an unlabeled node. Node 'wi' branches into 'wis' and 'win,' with 'win' having a teal border.  'wis' points to a leaf node 'wish' (teal bordered).  All arrows indicate the direction of flow from parent to child node.  The teal-bordered leaf nodes suggest a possible categorization or highlighting of specific terminal nodes within the overall tree structure.](images/figure-13-5-6HIZZOES.svg)

Figure 5

Basic trie data structure stores characters in nodes. To support sorting by frequency, frequency info needs to be included in nodes. Assume we have the following frequency table.

| **Query** | **Frequency** |
| --- | --- |
| tree | 10 |
| try | 29 |
| true | 35 |
| toy | 14 |
| wish | 25 |
| win | 50 |

Table 2

After adding frequency info to nodes, updated trie data structure is shown in Figure 6.

![Image represents a directed acyclic graph (DAG) or tree structure, labeled 'root' at its apex.  The root node points to two child nodes, 't' and 'w'. Node 't' further branches into 'tr', 'to'. Node 'tr' has three children: 'tre', 'tru', and 'try:29'.  'tre' points to 'tree:10', 'tru' points to 'true:35', and 'try:29' is a leaf node. Node 'to' has one child, 'toy:14', which is also a leaf node. Node 'w' points to 'wi', which branches into 'wis' and 'win:50'. 'wis' points to 'wish:25', while 'win:50' is a leaf node.  The leaf nodes ('tree:10', 'true:35', 'try:29', 'toy:14', 'wish:25', 'win:50') contain alphanumeric data, suggesting a hierarchical data structure where values are associated with the leaf nodes.  All connections are represented by arrows indicating the direction of flow from parent to child nodes.  The nodes are rectangular boxes, with leaf nodes having a sea-green border to distinguish them from internal nodes.](images/figure-13-6-M5EZD5SL.svg)

Figure 6

How does autocomplete work with trie? Before diving into the algorithm, let us define some terms.

* *p*: length of a prefix
* *n:* total number of nodes in a trie
* c: number of children of a given node

Steps to get top *k* most searched queries are listed below:

1. Find the prefix. Time complexity: *O(p)*.

2. Traverse the subtree from the prefix node to get all valid children. A child is valid if it can form a valid query string. Time complexity: *O(c)*

3. Sort the children and get top *k*. Time complexity: *O(clogc)*

Let us use an example as shown in Figure 7 to explain the algorithm. Assume *k* equals to 2 and a user types “tr” in the search box. The algorithm works as follows:

* Step 1: Find the prefix node “tr”.
* Step 2: Traverse the subtree to get all valid children. In this case, nodes [tree: 10], [true: 35], [try: 29] are valid.
* Step 3: Sort the children and get top 2. [true: 35] and [try: 29] are the top 2 queries with prefix “tr”.

![Image represents a tree-like data structure, possibly a Trie or a similar hierarchical data organization.  The topmost node is labeled 'root' and points to two child nodes, 't' and 'w'.  Node 't' further branches into 'tr' and 'to'.  'tr' has three children: 'tre', 'tru', and 'try: 29' (the ': 29' suggests a value associated with the node).  'tre' has a child 'tree: 10', and 'tru' has a child 'true: 35'.  Nodes 'try: 29', 'tree: 10', and 'true: 35' are enclosed within a dashed, teal-colored boundary, labeled with '2'.  Below this boundary, 'Top 2: [true: 35, try: 29]' indicates these two nodes are selected as top 2.  Node 'to' has a child 'toy: 14'.  Node 'w' branches into 'wi', which further branches into 'wis' and 'win: 50'.  'wis' has a child 'wish: 25'.  Thick blue arrows highlight a path from 'root' to 't' and then to 'tr', numbered '1'.  A purple arrow points from 'true: 35' to the 'Top 2' label, numbered '3'.  The overall structure depicts a hierarchical relationship between nodes, with leaf nodes containing numerical values.](images/figure-13-7-KXYAA5K3.svg)

Figure 7

The time complexity of this algorithm is the sum of time spent on each step mentioned above: ***O(p) + O(c) + O(clogc)***

The above algorithm is straightforward. However, it is too slow because we need to traverse the entire trie to get top *k* results in the worst-case scenario. Below are two optimizations:

1. Limit the max length of a prefix

2. Cache top search queries at each node

Let us look at these optimizations one by one.

#### Limit the max length of a prefix

Users rarely type a long search query into the search box. Thus, it is safe to say *p* is a small integer number, say 50. If we limit the length of a prefix, the time complexity for “Find the prefix” can be reduced from *O(p)* to *O(small constant),* aka *O(1)*.

#### Cache top search queries at each node

To avoid traversing the whole trie, we store top *k* most frequently used queries at each node. Since 5 to 10 autocomplete suggestions are enough for users, *k* is a relatively small number. In our specific case, only the top 5 search queries are cached.

By caching top search queries at every node, we significantly reduce the time complexity to retrieve the top 5 queries. However, this design requires a lot of space to store top queries at every node. Trading space for time is well worth it as fast response time is very important.

Figure 8 shows the updated trie data structure. Top 5 queries are stored on each node. For example, the node with prefix “be” stores the following: [best: 35, bet: 29, bee: 20, be: 15, beer: 10].

![Image represents a tree-like data structure, possibly a decision tree or a representation of hierarchical data.  A root node, labeled 'root,' sits at the top, branching down into two main nodes: 'b' and 'w'. Node 'b' contains the text '[best: 35, bet: 29, bee: 20, be...]' and branches further into 'be: 15', and '[buy: 14]'. Node 'w' contains the text '[win: 11]' and branches into 'wi' which also contains '[win: 11]'.  Node 'be: 15' further branches into '[bee: 20, beer: 10]', 'bee: 20', '[best: 35]', and 'bet: 29'.  'bee: 20' has a child node 'beer: 10'. 'bes' has a child node 'best: 35'.  'bu' has a child node 'buy: 14'. 'wi' has a child node 'win: 11'. Dashed teal boxes enclose groups of related nodes, suggesting logical groupings within the data.  The text within the nodes and boxes appears to represent key-value pairs or data attributes, possibly related to betting or a similar context.  The bottom-most node, 'best: 35', includes a message indicating the viewer's inability to fully render the SVG format.](images/figure-13-8-4HDDZCTY.svg)

Figure 8

Let us revisit the time complexity of the algorithm after applying those two optimizations:

1. Find the prefix node. Time complexity: *O(1)*

2. Return top *k*. Since top *k* queries are cached, the time complexity for this step is *O(1)*.

As the time complexity for each of the steps is reduced to *O(1)*, our algorithm takes only *O(1)* to fetch top *k* queries.

### Data gathering service

In our previous design, whenever a user types a search query, data is updated in real-time. This approach is not practical for the following two reasons:

* Users may enter billions of queries per day. Updating the trie on every query significantly slows down the query service.
* Top suggestions may not change much once the trie is built. Thus, it is unnecessary to update the trie frequently.

To design a scalable data gathering service, we examine where data comes from and how data is used. Real-time applications like Twitter require up to date autocomplete suggestions. However, autocomplete suggestions for many Google keywords might not change much on a daily basis.

Despite the differences in use cases, the underlying foundation for data gathering service remains the same because data used to build the trie is usually from analytics or logging services.

Figure 9 shows the redesigned data gathering service. Each component is examined one by one.

![Image represents a data processing pipeline.  It begins with 'Analytics Logs,' depicted as a file icon labeled 'LOG,' which feeds into 'Aggregators,' represented by three vertically stacked green boxes symbolizing multiple aggregator units.  The aggregated data from the aggregators is then stored in 'Aggregated Data,' shown as three blue database icons.  This aggregated data is subsequently processed by 'Workers,' also represented by three green boxes, which update a 'Trie DB' (three blue database icons) weekly.  Finally, a 'Trie Cache' (three stacked blue boxes labeled 'CACHE') receives a weekly snapshot of the data from the 'Trie DB.'  The arrows indicate the direction of data flow, showing how raw logs are processed, aggregated, stored, further processed by workers, and finally cached for faster access.  The text 'Update weekly' explicitly labels the weekly update process from the workers to the Trie DB.](images/figure-13-9-O7NXHK4L.svg)

Figure 9

**Analytics Logs.** It stores raw data about search queries. Logs are append-only and are not indexed. Table 3 shows an example of the log file.

| **query** | **time** |
| --- | --- |
| tree | 2019-10-01 22:01:01 |
| try | 2019-10-01 22:01:05 |
| tree | 2019-10-01 22:01:30 |
| toy | 2019-10-01 22:02:22 |
| tree | 2019-10-02 22:02:42 |
| try | 2019-10-03 22:03:03 |

Table 3

**Aggregators.** The size of analytics logs is usually very large, and data is not in the right format. We need to aggregate data so it can be easily processed by our system.

Depending on the use case, we may aggregate data differently. For real-time applications such as Twitter, we aggregate data in a shorter time interval as real-time results are important. On the other hand, aggregating data less frequently, say once per week, might be good enough for many use cases. During an interview session, verify whether real-time results are important. We assume trie is rebuilt weekly.

#### Aggregated Data.

Table 4 shows an example of aggregated weekly data. “time” field represents the start time of a week. “frequency” field is the sum of the occurrences for the corresponding query in that week.

| **query** | **time** | **frequency** |
| --- | --- | --- |
| tree | 2019-10-01 | 12000 |
| tree | 2019-10-08 | 15000 |
| tree | 2019-10-15 | 9000 |
| toy | 2019-10-01 | 8500 |
| toy | 2019-10-08 | 6256 |
| toy | 2019-10-15 | 8866 |

Table 4

**Workers.** Workers are a set of servers that perform asynchronous jobs at regular intervals. They build the trie data structure and store it in Trie DB.

**Trie Cache.** Trie Cache is a distributed cache system that keeps trie in memory for fast read. It takes a weekly snapshot of the DB.

**Trie DB.** Trie DB is the persistent storage. Two options are available to store the data:

1. Document store: Since a new trie is built weekly, we can periodically take a snapshot of it, serialize it, and store the serialized data in the database. Document stores like MongoDB [4] are good fits for serialized data.

2. Key-value store: A trie can be represented in a hash table form [4] by applying the following logic:

* Every prefix in the trie is mapped to a key in a hash table.
* Data on each trie node is mapped to a value in a hash table.

Figure 10 shows the mapping between the trie and hash table.

![Image represents a hierarchical tree-like structure, possibly depicting a data structure or algorithm.  A root node (an empty rectangle labeled 'root') points downwards to a node labeled 'b', enclosed in a dashed teal rectangle containing the text '[be: 15, bee: 20,...]'.  Node 'b' points to a node 'be: 15', also within a dashed teal rectangle with similar content '[be: 15, bee: 20,...]'.  'be: 15' connects to two lower nodes: 'bee: 20' (within a dashed teal rectangle '[bee: 20, beer: 10]') and 'bes' (within a dashed teal rectangle '[best: 35]').  'bee: 20' points to a leaf node 'beer: 10', and 'bes' points to a leaf node 'best: 35'.  Dashed arrows extend from each leaf node and from 'be: 15' and 'b' to the right, suggesting data output or further processing.  The top right corner displays 'KeyValueb[be: 15, bee: 20, beer: 10, bes...]', possibly indicating the overall data set.  The bottom right corner shows a browser compatibility message: 'Viewer does not support full SVG 1.1'.  The structure suggests a key-value store or a similar data organization where keys ('be', 'bee', 'bes') map to values (numerical data).](images/figure-13-10-JX4JXRHK.svg)

Figure 10

In Figure 10, each trie node on the left is mapped to the *<key, value>* pair on the right. If you are unclear how key-value stores work, refer to the "Design a key-value store" chapter.

### Query service

In the high-level design, query service calls the database directly to fetch the top 5 results. Figure 11 shows the improved design as previous design is inefficient.

![Image represents a system architecture diagram illustrating the flow of requests from a user to a database.  The diagram begins with a 'User' block containing icons for a 'Web browser' and a 'Mobile app,' both of which send requests (labeled '1') to a 'Load balancer.' The load balancer distributes these requests (labeled '2') to a cluster of 'API servers.'  These API servers then access a 'Trie Cache' (labeled '3'), which consists of three individual cache units. If the requested data is not found in the Trie Cache, the API servers access a 'Trie DB' (labeled '4') to retrieve it.  The numbered arrows indicate the sequential flow of requests and data retrieval, showing how the system manages user requests through load balancing, caching, and database access.](images/figure-13-11-S7BTGS2A.png)

Figure 11

1. A search query is sent to the load balancer.

2. The load balancer routes the request to API servers.

3. API servers get trie data from Trie Cache and construct autocomplete suggestions for the client.

4. In case the data is not in Trie Cache, we replenish data back to the cache. This way, all subsequent requests for the same prefix are returned from the cache. A cache miss can happen when a cache server is out of memory or offline.

Query service requires lightning-fast speed. We propose the following optimizations:

* AJAX request. For web applications, browsers usually send AJAX requests to fetch autocomplete results. The main benefit of AJAX is that sending/receiving a request/response does not refresh the whole web page.
* Browser caching. For many applications, autocomplete search suggestions may not change much within a short time. Thus, autocomplete suggestions can be saved in browser cache to allow subsequent requests to get results from the cache directly. Google search engine uses the same cache mechanism. Figure 12 shows the response header when you type “system design interview” on the Google search engine. As you can see, Google caches the results in the browser for 1 hour. Please note: “private” in cache-control means results are intended for a single user and must not be cached by a shared cache. “max-age=3600” means the cache is valid for 3600 seconds, aka, an hour.

![Image represents a screenshot of a network request and response within a developer tool, likely from a browser.  The top section displays the request details: the URL `https://www.google.com/complete/search?q&cp=0&client=psy-ab&xssi-t&gs_ri-gws-wiz&hl=en&authuser=0&pq-system design interview` indicates a GET request to Google's autocomplete search API, with various parameters specifying the client, language, and potentially a query related to 'system design interview'. The request method is GET, the remote address is `[2607:f8b0:4005:807::2004]:443` (an IPv6 address and port), and the status code is 200 (OK), indicating a successful request.  The HTTP version is 2.0. Below, the 'Response headers' section shows metadata about the response, including `cache-control` (private, max-age 3600 seconds), `content-disposition` (attachment, filename 'f.txt'), `content-encoding` (br - Brotli compression), `content-type` (application/json; charset=UTF-8), date and expiry timestamps, the server ('gws'), security headers (`strict-transport-security`), and other headers like `X-Firefox-Spdy`, `x-frame-options`, and `x-xss-protection`.  The size of the response is indicated as 615 bytes.  The `alt-svc` header suggests alternative service options, specifically QUIC.](images/figure-13-12-IKMFWP5J.svg)

Figure 12

* Data sampling: For a large-scale system, logging every search query requires a lot of processing power and storage. Data sampling is important. For instance, only 1 out of every *N* requests is logged by the system.

### Trie operations

Trie is a core component of the autocomplete system. Let us look at how trie operations (create, update, and delete) work.

#### Create

Trie is created by workers using aggregated data. The source of data is from Analytics Log/DB.

#### Update

There are two ways to update the trie.

Option 1: Update the trie weekly. Once a new trie is created, the new trie replaces the old one.

Option 2: Update individual trie node directly. We try to avoid this operation because it is slow. However, if the size of the trie is small, it is an acceptable solution. When we update a trie node, its ancestors all the way up to the root must be updated because ancestors store top queries of children. Figure 13 shows an example of how the update operation works. On the left side, the search query “beer” has the original value 10. On the right side, it is updated to 30. As you can see, the node and its ancestors have the “beer” value updated to 30.

![Image represents two identical tree-like structures, each depicting a hierarchical data structure.  Both structures originate from a root node labeled 'root' and branch down. The first level below the root contains a node labeled 'b' enclosed within a dashed teal rectangle annotated with '[best: 35, beer: 20,...]'.  This node points to a second-level node labeled 'be: 15', also within a similar dashed teal rectangle with the same annotation.  From 'be: 15', three branches extend to third-level nodes. One node is labeled 'bee: 20' and is enclosed in a dashed teal rectangle annotated with '[bee: 20, beer, 10]'. This node further points to a leaf node 'beer: 10'. Another branch from 'be: 15' leads to a node labeled 'bes' within a dashed teal rectangle annotated with '[best: 35]', which points to a leaf node 'best: 35'. The final branch from 'be: 15' connects to a node labeled 'bee: 20' within a dashed teal rectangle annotated with '[best: 35]'. The second tree structure mirrors the first, with identical labels, annotations, and connections.  The annotations within the dashed rectangles appear to represent data associated with each node, possibly key-value pairs.](images/figure-13-13-IHQGNBZV.svg)

Figure 13

#### Delete

We have to remove hateful, violent, sexually explicit, or dangerous autocomplete suggestions. We add a filter layer (Figure 14) in front of the Trie Cache to filter out unwanted suggestions. Having a filter layer gives us the flexibility of removing results based on different filter rules. Unwanted suggestions are removed physically from the database asynchronically so the correct data set will be used to build trie in the next update cycle.

![Image represents a system architecture diagram illustrating data flow from API servers through a filter layer to a Trie cache.  On the left, a dashed-line box labeled 'API servers' contains three vertically stacked, light-green rectangular icons representing multiple API servers. A solid blue arrow points right from this box to a central, black, funnel-shaped icon labeled 'Filter Layer,' indicating data is passed from the API servers to this filtering stage.  Another solid blue arrow extends right from the filter layer to a blue, rounded-rectangle box labeled 'Trie Cache.' Inside the Trie Cache box, three stacked, smaller blue rectangles, each labeled 'CACHE,' represent multiple cache instances. The overall flow depicts data originating from the API servers, undergoing filtering, and finally being stored in the distributed Trie cache for efficient retrieval.](images/figure-13-14-TDM2D22J.png)

Figure 14

### Scale the storage

Now that we have developed a system to bring autocomplete queries to users, it is time to solve the scalability issue when the trie grows too large to fit in one server.

Since English is the only supported language, a naive way to shard is based on the first character. Here are some examples.

* If we need two servers for storage, we can store queries starting with ‘*a*’ to ‘*m*’ on the first server, and ‘*n*’ to ‘*z*’ on the second server.
* If we need three servers, we can split queries into ‘*a*’ to ‘*i*’, ‘*j*’ to ‘*r*’ and ‘*s*’ to ‘*z*’.

Following this logic, we can split queries up to 26 servers because there are 26 alphabetic characters in English. Let us define sharding based on the first character as first level sharding. To store data beyond 26 servers, we can shard on the second or even at the third level. For example, data queries that start with ‘*a*’ can be split into 4 servers: ‘*aa-ag*’, ‘*ah-an*’, ‘*ao-au*’, and ‘*av-az’*.

At the first glance this approach seems reasonable, until you realize that there are a lot more words that start with the letter ‘*c*’ than ‘*x*’. This creates uneven distribution.

To mitigate the data imbalance problem, we analyze historical data distribution pattern and apply smarter sharding logic as shown in Figure 15. The shard map manager maintains a lookup database for identifying where rows should be stored. For example, if there are a similar number of historical queries for ‘*s*’ and for ‘*u*’, ‘*v*’, ‘*w*’, ‘*x*’, ‘*y*’ and ‘*z*’ combined, we can maintain two shards: one for ‘s’ and one for ‘u’ to ‘z’.

![Image represents a simplified database sharding architecture.  The diagram shows three main components: a group of 'Web servers' (represented by three green vertical rectangles within a dashed box), a 'Shard map manager' (a single blue cylinder in a rounded rectangle), and a set of 'Databases' (three blue cylinders labeled 'Shard 1', 'Shard 2', and 'Shard ...', also within a rounded rectangle).  The web servers initiate the process by sending a request ('What shard is it?') labeled '1' to the Shard map manager. This manager determines which database shard contains the requested data.  Then, the web servers receive a response from the Shard map manager and send a second request ('Retrieve data from shard') labeled '2' to the appropriate database shard to retrieve the data.  The arrows indicate the direction of information flow between these components.](images/figure-13-15-6H4WZOA6.svg)

Figure 15

## Step 4 - Wrap up

After you finish the deep dive, your interviewer might ask you some follow up questions.

Interviewer: How do you extend your design to support multiple languages?

To support other non-English queries, we store Unicode characters in trie nodes. If you are not familiar with Unicode, here is the definition: “an encoding standard covers all the characters for all the writing systems of the world, modern and ancient” [5].

Interviewer: What if top search queries in one country are different from others?

In this case, we might build different tries for different countries. To improve the response time, we can store tries in CDNs.

Interviewer: How can we support the trending (real-time) search queries?

Assuming a news event breaks out, a search query suddenly becomes popular. Our original design will not work because:

* Offline workers are not scheduled to update the trie yet because this is scheduled to run on weekly basis.
* Even if it is scheduled, it takes too long to build the trie.

Building a real-time search autocomplete is complicated and is beyond the scope of this course so we will only give a few ideas:

* Reduce the working data set by sharding.
* Change the ranking model and assign more weight to recent search queries.
* Data may come as streams, so we do not have access to all the data at once. Streaming data means data is generated continuously. Stream processing requires a different set of systems: Apache Hadoop MapReduce [6], Apache Spark Streaming [7], Apache Storm [8], Apache Kafka [9], etc. Because all those topics require specific domain knowledge, we are not going into detail here.

Congratulations on getting this far! Now give yourself a pat on the back. Good job!

## Reference materials

[1] The Life of a Typeahead Query:  
<https://www.facebook.com/notes/facebook-engineering/the-life-of-a-typeahead-query/389105248919/>

[2] How We Built Prefixy: A Scalable Prefix Search Service for Powering Autocomplete:  
<https://medium.com/@prefixyteam/how-we-built-prefixy-a-scalable-prefix-search-service-for-powering-autocomplete-c20f98e2eff1>

[3] Prefix Hash Tree An Indexing Data Structure over Distributed Hash Tables:  
<https://people.eecs.berkeley.edu/~sylvia/papers/pht.pdf>

[4] MongoDB wikipedia: <https://en.wikipedia.org/wiki/MongoDB>

[5] Unicode frequently asked questions: <https://www.unicode.org/faq/basic_q.html>

[6] Apache hadoop: <https://hadoop.apache.org/>

[7] Spark streaming: <https://spark.apache.org/streaming/>

[8] Apache storm: <https://storm.apache.org/>

[9] Apache kafka: <https://kafka.apache.org/documentation/>