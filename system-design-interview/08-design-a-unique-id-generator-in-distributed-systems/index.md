# Design A Unique ID Generator In Distributed Systems

**08**

# Design A Unique ID Generator In Distributed Systems

In this chapter, you are asked to design a unique ID generator in distributed systems. Your first thought might be to use a primary key with the *auto\_increment* attribute in a traditional database. However, *auto\_increment* does not work in a distributed environment because a single database server is not large enough and generating unique IDs across multiple databases with minimal delay is challenging.

Here are a few examples of unique IDs:

![Image represents a simplified conceptual diagram illustrating a database table or a similar data structure.  The diagram shows a single column labeled 'user_id' containing a list of numerical user identifiers.  The column is enclosed within a dashed rectangular border, suggesting a table structure.  Each row within the border represents a single record, with each record containing a unique, long numerical user ID.  The IDs are presented as sequential entries, vertically stacked, implying a possible ordering or indexing mechanism.  There are no explicit connections to other tables or components shown; the diagram focuses solely on the structure and content of the 'user_id' column, which appears to store a series of distinct user identification numbers.  No other attributes or columns are visible, and there's no indication of any relationships with other data elements.](images/figure-7-1-VGKGPLH3.svg)

Figure 1

## Step 1 - Understand the problem and establish design scope

Asking clarification questions is the first step to tackle any system design interview question. Here is an example of candidate-interviewer interaction:

**Candidate**: What are the characteristics of unique IDs?  
**Interviewer**: IDs must be unique and sortable.

**Candidate**: For each new record, does ID increment by 1?  
**Interviewer**: The ID increments by time but not necessarily only increments by 1. IDs created in the evening are larger than those created in the morning on the same day.

**Candidate**: Do IDs only contain numerical values?  
**Interviewer**: Yes, that is correct.

**Candidate**: What is the ID length requirement?  
**Interviewer**: IDs should fit into 64-bit.

**Candidate**: What is the scale of the system?  
**Interviewer**: The system should be able to generate 10,000 IDs per second.

Above are some of the sample questions that you can ask your interviewer. It is important to understand the requirements and clarify ambiguities. For this interview question, the requirements are listed as follows:

* IDs must be unique.
* IDs are numerical values only.
* IDs fit into 64-bit.
* IDs are ordered by date.
* Ability to generate over 10,000 unique IDs per second.

## Step 2 - Propose high-level design and get buy-in

Multiple options can be used to generate unique IDs in distributed systems. The options we considered are:

* Multi-master replication
* Universally unique identifier (UUID)
* Ticket server
* Twitter snowflake approach

Let us look at each of them, how they work, and the pros/cons of each option.

### Multi-master replication

As shown in Figure 2, the first approach is multi-master replication.

![Image represents a system architecture diagram showing two MySQL databases connected to a cluster of web servers.  Two rectangular boxes labeled 'My SQL' represent the two separate MySQL database instances.  From each MySQL instance, arrows point towards a larger rectangular box labeled 'Web servers,' which depicts three vertically stacked, smaller rectangles representing individual web servers.  The arrow from the first MySQL database is labeled '1, 3, 5...', indicating that this database serves odd-numbered requests or data.  Similarly, the arrow from the second MySQL database is labeled '2, 4, 6...', suggesting this database handles even-numbered requests or data, implying a load balancing strategy where requests are distributed across the two databases. The entire diagram is enclosed within a dashed, light-blue border.  A small text at the bottom reads 'Viewer does not support full SVG 1.1,' indicating a limitation of the viewer used to display the diagram.](images/figure-7-2-4ZOIVNTR.svg)

Figure 2

This approach uses the databases’ *auto\_increment* feature. Instead of increasing the next ID by 1, we increase it by *k,* where *k* is the number of database servers in use. As illustrated in Figure 2, next ID to be generated is equal to the previous ID in the same server plus 2. This solves some scalability issues because IDs can scale with the number of database servers. However, this strategy has some major drawbacks:

* Hard to scale with multiple data centers
* IDs do not go up with time across multiple servers.
* It does not scale well when a server is added or removed.

### UUID

A UUID is another easy way to obtain unique IDs. UUID is a 128-bit number used to identify information in computer systems. UUID has a very low probability of getting collusion. Quoted from Wikipedia, “after generating 1 billion UUIDs every second for approximately 100 years would the probability of creating a single duplicate reach 50%” [1].

Here is an example of UUID: *09c93e62-50b4-468d-bf8a-c07e1040bfb2*. UUIDs can be generated independently without coordination between servers. Figure 3 presents the UUIDs design.

![Image represents a system architecture diagram showing four identical units, each enclosed within a dashed, light-blue rectangular border.  Each unit consists of two stacked rectangular boxes. The top box in each unit is labeled 'Web Server,' indicating a web server component.  Below each 'Web Server' box is a smaller box labeled 'ID gen,' suggesting an ID generation component. There are no visible connections or data flows depicted between the units; each unit appears to function independently.  The overall arrangement suggests a horizontally scaled deployment of a system where each unit has a web server and a local ID generator. The 'Viewer does not support full SVG 1.1' message at the bottom indicates a limitation of the viewer used to display the diagram.](images/figure-7-3-Y3ZNPIH3.svg)

Figure 3

In this design, each web server contains an ID generator, and a web server is responsible for generating IDs independently.

Pros:

* Generating UUID is simple. No coordination between servers is needed so there will not be any synchronization issues.
* The system is easy to scale because each web server is responsible for generating IDs they consume. ID generator can easily scale with web servers.

Cons:

* IDs are 128 bits long, but our requirement is 64 bits.
* IDs do not go up with time.
* IDs could be non-numeric.

### Ticket Server

Ticket servers are another interesting way to generate unique IDs. Flicker developed ticket servers to generate distributed primary keys [2]. It is worth mentioning how the system works.

![Image represents a simplified system architecture diagram showing four 'Web Server' components connected to a central 'Ticket Server' component.  Each of the four rectangular boxes labeled 'Web Server' represents a separate web server instance.  Lines connect each 'Web Server' to a single rectangular box labeled 'Ticket Server,' indicating a unidirectional communication flow from each web server to the central ticket server.  This suggests that the web servers might be requesting or sending data (likely ticket-related information) to the central Ticket Server. The overall structure implies a client-server model where multiple web servers act as clients, interacting with a single, central Ticket Server.  The dashed-line border around the entire diagram suggests the scope of the depicted system.  The text 'Viewer does not support full SVG 1.1' at the bottom is a technical note indicating a limitation of the display software, not related to the system architecture itself.](images/figure-7-4-TJJLCKSS.svg)

Figure 4

The idea is to use a centralized *auto\_increment* feature in a single database server (Ticket Server). To learn more about this, refer to flicker’s engineering blog article [2].

Pros:

* Numeric IDs.
* It is easy to implement, and it works for small to medium-scale applications.

Cons:

* Single point of failure. Single ticket server means if the ticket server goes down, all systems that depend on it will face issues. To avoid a single point of failure, we can set up multiple ticket servers. However, this will introduce new challenges such as data synchronization.

### Twitter snowflake approach

Approaches mentioned above give us some ideas about how different ID generation systems work. However, none of them meet our specific requirements; thus, we need another approach. Twitter’s unique ID generation system called “snowflake” [3] is inspiring and can satisfy our requirements.

Divide and conquer is our friend. Instead of generating an ID directly, we divide an ID into different sections. Figure 5 shows the layout of a 64-bit ID.

![Image represents a data structure composed of five distinct fields, each with a specified bit length.  From left to right, the first field is a single bit (1 bit), followed by a 41-bit field.  Next, there's a 5-bit field labeled '0', suggesting it might be a status or version indicator.  This is followed by another 5-bit field labeled 'timestamp...', indicating it stores timestamp information. Finally, a 12-bit field completes the structure.  The fields are arranged horizontally, implying a concatenated structure where the bits of each field are sequentially combined to form a larger data unit. No explicit connections or information flow between the fields are shown; the diagram simply illustrates the composition and size of each component within the overall data structure.](images/figure-7-5-R4B5RGNK.svg)

Figure 5

Each section is explained below.

* Sign bit: 1 bit. It will always be 0. This is reserved for future uses. It can potentially be used to distinguish between signed and unsigned numbers.
* Timestamp: 41 bits. Milliseconds since the epoch or custom epoch. We use Twitter snowflake default epoch 1288834974657, equivalent to Nov 04, 2010, 01:42:54 UTC.
* Datacenter ID: 5 bits, which gives us *2 ^ 5 = 32* datacenters.
* Machine ID: 5 bits, which gives us *2 ^ 5 = 32* machines per datacenter.
* Sequence number: 12 bits. For every ID generated on that machine/process, the sequence number is incremented by 1. The number is reset to 0 every millisecond.

## Step 3 - Design deep dive

In the high-level design, we discussed various options to design a unique ID generator in distributed systems. We settle on an approach that is based on the Twitter snowflake ID generator. Let us dive deep into the design. To refresh our memory, the design diagram is relisted below.

![Image represents a data structure composed of five distinct fields, each with a specified bit length.  From left to right, the fields are: a 1-bit field (likely a flag or boolean value); a 41-bit field (likely representing a large identifier or counter); a 5-bit field labeled '0' (its purpose is unclear without further context); a 5-bit field labeled 'timestamp...' (suggesting a truncated timestamp); and finally, a 12-bit field (likely representing another identifier or data value).  The fields are arranged horizontally, implying a sequential or concatenated structure. No explicit connections are shown between the fields, but the arrangement suggests they are combined to form a single larger data unit.  The 'timestamp...' label indicates that at least part of the data represents a time value, while the other labels and bit lengths provide clues to the potential function of the remaining fields, though their exact meaning remains ambiguous without additional information.](images/figure-7-6-33JFUIC3.svg)

Figure 6

Datacenter IDs and machine IDs are chosen at the startup time, generally fixed once the system is up running. Any changes in datacenter IDs and machine IDs require careful review since an accidental change in those values can lead to ID conflicts. Timestamp and sequence numbers are generated when the ID generator is running.

Timestamp

The most important 41 bits make up the timestamp section. As timestamps grow with time, IDs are sortable by time. Figure 7 shows an example of how binary representation is converted to UTC. You can also convert UTC back to binary representation using a similar method.

![Image represents a flowchart illustrating the conversion of a binary timestamp to a human-readable date and time.  The process begins with a 64-bit binary number, '0-00100010101001011010011011000101101011000-01010-01100-000000000000,' which is first converted to its decimal equivalent, '297616116568.'  This decimal value is then added to the Twitter epoch value, '1288834974657,' resulting in '1586451091225.' This final number, representing milliseconds since the Twitter epoch, is then converted to a UTC date and time, yielding 'Apr 09 2020 16:51UTC.'  The flowchart uses arrows to indicate the flow of data and text labels to describe each transformation step.](images/figure-7-7-PNNDQIF5.svg)

Figure 7

The maximum timestamp that can be represented in 41 bits is

*2 ^ 41 - 1 = 2199023255551* milliseconds (ms), which gives us: ~ 69 years = *2199023255551 ms / 1000 / 365 days / 24 hours/ 3600 seconds*. This means the ID generator will work for 69 years and having a custom epoch time close to today’s date delays the overflow time. After 69 years, we will need a new epoch time or adopt other techniques to migrate IDs.

Sequence number

Sequence number is 12 bits, which give us 2 ^ 12 = 4096 combinations. This field is 0 unless more than one ID is generated in a millisecond on the same server. In theory, a machine can support a maximum of 4096 new IDs per millisecond.

## Step 4 - Wrap up

In this chapter, we discussed different approaches to design a unique ID generator: multi-master replication, UUID, ticket server, and Twitter snowflake-like unique ID generator. We settle on snowflake as it supports all our use cases and is scalable in a distributed environment.

If there is extra time at the end of the interview, here are a few additional talking points:

* Clock synchronization. In our design, we assume ID generation servers have the same clock. This assumption might not be true when a server is running on multiple cores. The same challenge exists in multi-machine scenarios. Solutions to clock synchronization are out of the scope of this course; however, it is important to understand the problem exists. Network Time Protocol is the most popular solution to this problem. For interested readers, refer to the reference material [4].
* Section length tuning. For example, fewer sequence numbers but more timestamp bits are effective for low concurrency and long-term applications.
* High availability. Since an ID generator is a mission-critical system, it must be highly available.

Congratulations on getting this far! Now give yourself a pat on the back. Good job!

## Reference materials

[1] Universally unique identifier:  
<https://en.wikipedia.org/wiki/Universally_unique_identifier>

[2] Ticket Servers: Distributed Unique Primary Keys on the Cheap:  
<https://code.flickr.net/2010/02/08/ticket-servers-distributed-unique-primary-keys-on-the-cheap/>

[3] Announcing Snowflake:  
<https://blog.twitter.com/engineering/en_us/a/2010/announcing-snowflake.html>

[4] Network time protocol:  
<https://en.wikipedia.org/wiki/Network_Time_Protocol>