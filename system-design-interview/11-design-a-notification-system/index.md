# Design A Notification System

**11**

# Design A Notification System

A notification system has already become a very popular feature for many applications in recent years. A notification alerts a user with important information like breaking news, product updates, events, offerings, etc. It has become an indispensable part of our daily life. In this chapter, you are asked to design a notification system.

A notification is more than just mobile push notification. Three types of notification formats are: mobile push notification, SMS message, and Email. Figure 1 shows an example of each of these notifications.

![Image represents a comparison of three different notification methods: push notification, SMS, and email.  The leftmost panel displays a smartphone's notification center showing two push notifications: one from Thinkorswim regarding a stock alert with details like GOOG-GOOGL mark, Impl vol, and a link to 73 more notifications; and another from Amazon confirming a package delivery to Alex, with a link to 3 more notifications. Below these notifications are icons for a flashlight and camera, and the label 'Push notification'. The central panel shows an SMS message alerting about an AT&T phone outage in San Mateo County, providing instructions on contacting emergency services.  The text 'SMS' is labeled below, with a note indicating SVG support limitations. The rightmost panel displays an email from GoDaddy promoting New Year's resolutions, featuring a video preview with the hashtag #Make2020.  The email includes GoDaddy's logo, contact information (including a customer number: 234397112), and the subject line 'Make your screen time count and #Make2020'. The label 'Email' is placed below the email.  Each panel visually represents a distinct communication channel, showcasing different content formats and delivery methods.](images/figure-10-1-4EEWILYD.svg)

Figure 1

## Step 1 - Understand the problem and establish design scope

Building a scalable system that sends out millions of notifications a day is not an easy task. It requires a deep understanding of the notification ecosystem. The interview question is purposely designed to be open-ended and ambiguous, and it is your responsibility to ask questions to clarify the requirements.

**Candidate**: What types of notifications does the system support?  
**Interviewer**: Push notification, SMS message, and email.

**Candidate:** Is it a real-time system?  
**Interviewer:** Let us say it is a soft real-time system. We want a user to receive notifications as soon as possible. However, if the system is under a high workload, a slight delay is acceptable.

**Candidate:** What are the supported devices?  
**Interviewer:** iOS devices, android devices, and laptop/desktop.

**Candidate:** What triggers notifications?  
**Interviewer:** Notifications can be triggered by client applications. They can also be scheduled on the server-side.

**Candidate:** Will users be able to opt-out?  
**Interviewer:** Yes, users who choose to opt-out will no longer receive notifications.

**Candidate:** How many notifications are sent out each day?  
**Interviewer:** 10 million mobile push notifications, 1 million SMS messages, and 5 million emails.

## Step 2 - Propose high-level design and get buy-in

This section shows the high-level design that supports various notification types: iOS push notification, Android push notification, SMS message, and Email. It is structured as follows:

* Different types of notifications
* Contact info gathering flow
* Notification sending/receiving flow

### Different types of notifications

We start by looking at how each notification type works at a high level.

#### iOS push notification

![Image represents a simplified architecture diagram illustrating the communication flow between an iOS device, an APNs (Apple Push Notification service) server, and a service provider.  A circle labeled 'Provider' represents the origin of push notifications. A solid arrow points from the 'Provider' to a cloud-shaped icon labeled 'APNs,' indicating that the provider sends notifications to the APNs server.  Another solid arrow extends from the 'APNs' cloud to a smartphone icon labeled 'iOS,' showing that the APNs server then forwards these notifications to the iOS device.  The diagram visually depicts a unidirectional flow of information: the provider initiates the notification process, which is then relayed through the APNs server to reach the end-user's iOS device.](images/figure-10-2-LRDI5SEA.png)

Figure 2

We primarily need three components to send an iOS push notification:

* Provider. A provider builds and sends notification requests to Apple Push Notification Service (APNS). To construct a push notification, the provider provides the following data:
* Device token: This is a unique identifier used for sending push notifications.
* Payload: This is a JSON dictionary that contains a notification’s payload. Here is an example:

```
{
   "aps":{
      "alert":{
         "title":"Game Request",
         "body":"Bob wants to play chess",
         "action-loc-key":"PLAY"
      },
      "badge":5
   }
}
```

* APNS: This is a remote service provided by Apple to propagate push notifications to iOS devices.
* iOS Device: It is the end client, which receives push notifications.

#### Android push notification

Android adopts a similar notification flow. Instead of using APNs, Firebase Cloud Messaging (FCM) is commonly used to send push notifications to android devices.

![Image represents a simplified architecture diagram illustrating the flow of information for push notifications.  A circular element labeled 'Provider' represents a data source or server sending notification data. A unidirectional arrow connects the 'Provider' to a central component depicted by the Firebase Cloud Messaging (FCM) logo, indicating that the 'Provider' sends data to FCM.  FCM, labeled as such below its logo, acts as a message broker or intermediary service. Another unidirectional arrow extends from FCM to a rectangular element representing an Android device, labeled 'Android,' showing that FCM forwards the notification data to the Android device.  The overall flow depicts the process where a 'Provider' sends push notification data to FCM, which then delivers the notification to the target Android application.](images/figure-10-3-5PEUMLEX.png)

Figure 3

#### SMS message

For SMS messages, third party SMS services like Twilio [1], Nexmo [2], and many others are commonly used. Most of them are commercial services.

![Image represents a simplified architecture for sending an SMS message.  A circular node labeled 'Provider' represents the origin of the SMS message. A directed arrow connects the 'Provider' to a square node representing the 'SMS Service,' depicted with a stylized speech bubble icon and labeled 'SMS Service' below. This arrow indicates the flow of the SMS message data from the provider to the service.  Finally, another directed arrow connects the 'SMS Service' node to a rectangular node representing a smartphone, labeled 'SMS' below. This arrow shows the delivery of the SMS message from the service to the recipient's mobile phone.  The overall diagram illustrates a linear data flow from the message originator (Provider) through an intermediary SMS service to the final recipient (Smartphone).](images/figure-10-4-VBM7JWLQ.png)

Figure 4

#### Email

Although companies can set up their own email servers, many of them opt for commercial email services. Sendgrid [3] and Mailchimp [4] are among the most popular email services, which offer a better delivery rate and data analytics.

![Image represents a simplified email sending process.  A circular node labeled 'Provider' is connected via a unidirectional arrow to a central component representing an 'Email Service.' This service is depicted as an email icon surrounded by four rectangular nodes symbolizing servers, with bidirectional arrows indicating data flow between the servers and the email icon.  The email service then connects to a laptop icon labeled 'Email' via another unidirectional arrow, showing the delivery of the email to the recipient's email client.  The overall flow illustrates data originating from the 'Provider,' being processed by the 'Email Service' servers, and finally delivered to the 'Email' client on a laptop.](images/figure-10-5-XJUEYKYB.png)

Figure 5

Figure 6 shows the design after including all the third-party services.

![Image represents a system architecture diagram illustrating how a system sends notifications to different platforms using various third-party services.  A dashed-line box labeled 'Third Party Services' contains four service icons: a cloud icon labeled 'APNs' (Apple Push Notification service), a triangular icon labeled 'FCM' (Firebase Cloud Messaging), a speech bubble icon within a square labeled 'SMS Service,' and an icon depicting an email surrounded by servers labeled 'Email Service.'  Horizontal arrows extend from each service icon to the right, connecting to corresponding recipient icons: APNs connects to an iOS device icon labeled 'iOS'; FCM connects to an Android device icon labeled 'Android'; SMS Service connects to a smartphone icon labeled 'SMS'; and Email Service connects to a laptop icon labeled 'Email.'  The diagram visually depicts the unidirectional flow of notifications from the various third-party services to their respective target devices or platforms.](images/figure-10-6-OWRSE4LF.png)

Figure 6

### Contact info gathering flow

To send notifications, we need to gather mobile device tokens, phone numbers, or email addresses. As shown in Figure 7, when a user installs our app or signs up for the first time, API servers collect user contact info and store it in the database.

![Image represents a simplified system architecture diagram for user contact information storage.  A light-blue box labeled 'User' contains icons representing a laptop and a mobile phone, indicating user access from multiple devices.  A solid dark-blue arrow originates from the 'User' box, labeled 'on app install or sign up,' connecting to a dark-blue, trapezoidal shape labeled 'Load balancer,' which acts as a traffic distributor.  A solid dark-blue arrow extends from the load balancer to a dashed light-blue box containing three vertically stacked, light-green rectangles representing 'API servers.'  The arrow connecting the load balancer and API servers implies that the load balancer distributes incoming requests across these servers.  A solid dark-blue arrow labeled 'store contact info' connects the API servers to a light-blue box labeled 'DB,' which contains three vertically stacked dark-blue cylinders representing a database where the contact information is stored.  The overall flow depicts a user initiating a request (app install or sign-up), which is balanced across API servers before finally storing the contact information in the database.](images/figure-10-7-W32A7UNW.png)

Figure 7

Figure 8 shows simplified database tables to store contact info. Email addresses and phone numbers are stored in the *user* table, whereas device tokens are stored in the *device* table. A user can have multiple devices, indicating that a push notification can be sent to all the user devices.

![Image represents a database schema diagram showing a one-to-many relationship between two tables: 'user' and 'device'.  The 'user' table has columns for `user_id` (bigint), `email` (varchar), `country_code` (integer), `phone_number` (integer), and `created_at` (timestamp).  The 'device' table contains columns for `id` (bigint), `device_token` (varchar), `user_id` (bigint), and `last_logged_in_at` (timestamp). A blue line connects the `user_id` column in the 'user' table to the `user_id` column in the 'device' table.  The number '1' next to the line on the 'user' table side indicates that one user can have multiple devices. The asterisk '*' on the 'device' table side signifies the many-to-one relationship, meaning multiple device records can reference a single user record through the `user_id` foreign key.  The 'user' table is visually distinguished by a small paint palette icon in its header.](images/figure-10-8-GYVHLNWP.svg)

Figure 8

### Notification sending/receiving flow

We will first present the initial design; then, propose some optimizations.

High-level design

Figure 9 shows the design, and each system component is explained below.

![Image represents a system architecture diagram for a notification system.  Multiple services, labeled 'Service 1,' 'Service 2,' and 'Service N,' feed into a central 'Notification System.' This system then routes notifications to various third-party services based on the recipient's platform.  These third-party services include APNs (Apple Push Notification service) for iOS devices, FCM (Firebase Cloud Messaging) for Android devices, an SMS Service for SMS notifications, and an Email Service for email notifications.  Arrows indicate the flow of notification data from the services to the Notification System and then to the appropriate third-party service, which finally delivers the notification to the end-user's iOS, Android, SMS, or email client.  The third-party services are grouped within a dashed-line box labeled 'Third Party Services.'](images/figure-10-9-62C2GFUU.png)

Figure 9

**Service 1 to N**: A service can be a micro-service, a cron job, or a distributed system that triggers notification sending events. For example, a billing service sends emails to remind customers of their due payment or a shopping website tells customers that their packages will be delivered tomorrow via SMS messages.

**Notification system**: The notification system is the centerpiece of sending/receiving notifications. Starting with something simple, only one notification server is used. It provides APIs for services 1 to N, and builds notification payloads for third party services.

**Third-party services:** Third party services are responsible for delivering notifications to users. While integrating with third-party services, we need to pay extra attention to extensibility. Good extensibility means a flexible system that can easily plugging or unplugging of a third-party service. Another important consideration is that a third-party service might be unavailable in new markets or in the future. For instance, FCM is unavailable in China. Thus, alternative third-party services such as Jpush, PushY, etc are used there.

**iOS, Android, SMS, Email**: Users receive notifications on their devices.

Three problems are identified in this design:

* Single point of failure (SPOF): A single notification server means SPOF.
* Hard to scale: The notification system handles everything related to push notifications in one server. It is challenging to scale databases, caches, and different notification processing components independently.
* Performance bottleneck: Processing and sending notifications can be resource intensive. For example, constructing HTML pages and waiting for responses from third party services could take time. Handling everything in one system can result in the system overload, especially during peak hours.

High-level design (improved)

After enumerating challenges in the initial design, we improve the design as listed below:

* Move the database and cache out of the notification server.
* Add more notification servers and set up automatic horizontal scaling.
* Introduce message queues to decouple the system components.

Figure 10 shows the improved high-level design.

![Image represents a system architecture for sending notifications.  Multiple services (Service 1, Service 2... Service N) send notification requests (labeled 1) to a central 'Notification servers' component. These servers (2) check a cache (CACHE) before querying a database (DB) for necessary information.  The notification servers then route messages to different queues: iOS Push Notification (iOS PN), Android Push Notification (Android PN), SMS queue, and Email queue.  Each queue feeds into a set of 'Workers' (4) which process the messages.  The iOS PN and Android PN messages are sent to Apple Push Notification service (APNs) (5) and Firebase Cloud Messaging (FCM) (5) respectively, before reaching iOS and Android devices (6).  The SMS queue messages are sent to an SMS Service (third-party service), and the Email queue messages are sent to an Email Service (third-party service), both ultimately reaching their respective end-users.  The entire system includes error handling with a 'retry on error' mechanism.](images/figure-10-10-VPOYUWTG.png)

Figure 10

The best way to go through the above diagram is from left to right:

**Service 1 to N**: They represent different services that send notifications via APIs provided by notification servers.

**Notification servers**: They provide the following functionalities:

* Provide APIs for services to send notifications. Those APIs are only accessible internally or by verified clients to prevent spams.
* Carry out basic validations to verify emails, phone numbers, etc.
* Query the database or cache to fetch data needed to render a notification.
* Put notification data to message queues for parallel processing.

Here is an example of the API to send an email:

POST `https://api.example.com/v/sms/send`

Request body

```
{
   "to":[
      {
         "user_id":123456
      }
   ],
   "from":{
      "email":"from_address@example.com"
   },
   "subject":"Hello World!",
   "content":[
      {
         "type":"text/plain",
         "value":"Hello, World!"
      }
   ]
}
```

**Cache**: User info, device info, notification templates are cached.

**DB**: It stores data about user, notification, settings, etc.

**Message queues**: They remove dependencies between components. Message queues serve as buffers when high volumes of notifications are to be sent out. Each notification type is assigned with a distinct message queue so an outage in one third-party service will not affect other notification types.

**Workers**: Workers are a list of servers that pull notification events from message queues and send them to the corresponding third-party services.

**Third-party services**: Already explained in the initial design.

**iOS, Android, SMS, Email**: Already explained in the initial design.

Next, let us examine how every component works together to send a notification:

1. A service calls APIs provided by notification servers to send notifications.

2. Notification servers fetch metadata such as user info, device token, and notification setting from the cache or database.

3. A notification event is sent to the corresponding queue for processing. For instance, an iOS push notification event is sent to the iOS PN queue.

4. Workers pull notification events from message queues.

5. Workers send notifications to third party services.

6. Third-party services send notifications to user devices.

## Step 3 - Design deep dive

In the high-level design, we discussed different types of notifications, contact info gathering flow, and notification sending/receiving flow. We will explore the following in deep dive:

* Reliability.
* Additional component and considerations: notification template, notification settings, rate limiting, retry mechanism, security in push notifications, monitor queued notifications and event tracking.
* Updated design.

### Reliability

We must answer a few important reliability questions when designing a notification system in distributed environments.

How to prevent data loss?

One of the most important requirements in a notification system is that it cannot lose data. Notifications can usually be delayed or re-ordered, but never lost. To satisfy this requirement, the notification system persists notification data in a database and implements a retry mechanism. The notification log database is included for data persistence, as shown in Figure 11.

![Image represents a simplified architecture for an iOS push notification system.  The diagram shows a leftmost component labeled 'iOS PN' depicting three email icons within a rounded rectangle, representing the iOS Push Notification service.  An arrow points right from this component to a dashed-line-bordered box containing three vertically stacked green rectangles labeled 'Worke...', representing a worker server cluster responsible for processing push notifications.  From this worker cluster, another arrow extends to a cloud icon labeled 'APNs,' representing Apple Push Notification service.  Finally, a downward arrow from the worker cluster points to a light-blue-bordered box containing three vertically stacked blue cylinders labeled 'Notification log,' indicating a database storing notification logs.  The text 'Viewer does not support full SVG 1.1' is present below the diagram, indicating a limitation of the viewer used to display the image.  The overall flow shows notifications originating from the iOS PN, being processed by the worker servers, sent to APNs for delivery to iOS devices, and finally logged in the Notification log database.](images/figure-10-11-IAFMAASK.svg)

Figure 11

Will recipients receive a notification exactly once?

The short answer is no. Although notification is delivered exactly once most of the time, the distributed nature could result in duplicate notifications. To reduce the duplication occurrence, we introduce a dedupe mechanism and handle each failure case carefully. Here is a simple dedupe logic:

When a notification event first arrives, we check if it is seen before by checking the event ID. If it is seen before, it is discarded. Otherwise, we will send out the notification. For interested readers to explore why we cannot have exactly once delivery, refer to the reference material [5].

### Additional components and considerations

We have discussed how to collect user contact info, send, and receive a notification. A notification system is a lot more than that. Here we discuss additional components including template reusing, notification settings, event tracking, system monitoring, rate limiting, etc.

#### Notification template

A large notification system sends out millions of notifications per day, and many of these notifications follow a similar format. Notification templates are introduced to avoid building every notification from scratch. A notification template is a preformatted notification to create your unique notification by customizing parameters, styling, tracking links, etc. Here is an example template of push notifications.

```
BODY:
You dreamed of it. We dared it. [ITEM NAME] is back — only until [DATE].

CTA:
Order Now. Or, Save My [ITEM NAME]
```

The benefits of using notification templates include maintaining a consistent format, reducing the margin error, and saving time.

#### Notification setting

Users generally receive way too many notifications daily and they can easily feel overwhelmed. Thus, many websites and apps give users fine-grained control over notification settings. This information is stored in the notification setting table, with the following fields:

user\_id bigInt

channel varchar # push notification, email or SMS

opt\_in boolean # opt-in to receive notification

Before any notification is sent to a user, we first check if a user is opted-in to receive this type of notification.

#### Rate limiting

To avoid overwhelming users with too many notifications, we can limit the number of notifications a user can receive. This is important because receivers could turn off notifications completely if we send too often.

#### Retry mechanism

When a third-party service fails to send a notification, the notification will be added to the message queue for retrying. If the problem persists, an alert will be sent out to developers.

#### Security in push notifications

For iOS or Android apps, appKey and appSecret are used to secure push notification APIs [6]. Only authenticated or verified clients are allowed to send push notifications using our APIs. Interested users should refer to the reference material [6].

#### Monitor queued notifications

A key metric to monitor is the total number of queued notifications. If the number is large, the notification events are not processed fast enough by workers. To avoid delay in the notification delivery, more workers are needed. Figure 12 (credit to [7]) shows an example of queued messages to be processed.

![Image represents a line graph depicting a time series data.  The horizontal axis represents time, specifically from approximately 11:08 to 11:33, with markings at 5-minute intervals. The vertical axis represents a numerical value ranging from 30 to 50, with markings at 2-unit intervals. A red line traces the data points, showing a relatively flat value around 34 until approximately 11:14, where it sharply increases to around 43.  The line then peaks at approximately 46 around 11:16, before declining to around 44 and then to approximately 41 around 11:20.  It remains relatively flat at around 41 until approximately 11:25, where it dips to around 40 before stabilizing again at around 41 until approximately 11:33.  No specific units or labels are provided for the vertical axis, and no additional information, such as URLs or parameters, is present within the image.](images/figure-10-12-WMFNVPQI.svg)

Figure 12

#### Events tracking

Notification metrics, such as open rate, click rate, and engagement are important in understanding customer behaviors. Analytics service implements events tracking. Integration between the notification system and the analytics service is usually required. Figure 13 shows an example of events that might be tracked for analytics purposes.

![Image represents a state diagram illustrating the lifecycle of a message or notification.  The diagram shows a sequence of states connected by arrows indicating transitions.  The states are represented by circles, each labeled with a descriptive name: 'start,' 'pending,' 'sent,' 'deliver,' 'click,' 'unsubscribe,' and 'error.'  The 'error' state is highlighted with a red border. The process begins at 'start,' proceeds to 'pending,' then 'sent,' and finally 'deliver.'  From the 'deliver' state, the process can transition to either 'click' or 'unsubscribe,' representing user interaction.  Both 'pending' and 'sent' states have a transition to the 'error' state, suggesting potential failure points during message processing.  The arrows depict the direction of the flow, showing the progression through the states and the possible branching paths based on events or conditions.](images/figure-10-13-LUL4UIPV.svg)

Figure 13

### Updated design

Putting everything together, Figure 14 shows the updated notification system design.

![Image represents a system architecture diagram for a notification service.  The process begins with 'Service N' sending a request to 'Notification servers', which then performs authentication and rate limiting.  Successful requests proceed to the 'iOS PN' (likely iOS Push Notification) component.  Three 'Workers' process these notifications, sending them via 'APNs' (Apple Push Notification service) to the 'iOS' device.  The entire process is monitored by an 'Analytics service', receiving 'send pending' and 'click tracking' information, and handling retries on errors.  A 'Notification template' component is used by the workers, and a 'Notification log' stores notification history.  The system also includes a cache and a database ('DB') storing 'device setting' and 'user info'.  The flow is unidirectional, except for feedback loops to the 'Analytics service' and error handling from the 'iOS PN' back to the 'Workers'.](images/figure-10-14-XSG2DEDM.png)

Figure 14

In this design, many new components are added in comparison with the previous design.

* The notification servers are equipped with two more critical features: authentication and rate-limiting.
* We also add a retry mechanism to handle notification failures. If the system fails to send notifications, they are put back in the messaging queue and the workers will retry for a predefined number of times.
* Furthermore, notification templates provide a consistent and efficient notification creation process.
* Finally, monitoring and tracking systems are added for system health checks and future improvements.

## Step 4 - Wrap up

Notifications are indispensable because they keep us posted with important information. It could be a push notification about your favorite movie on Netflix, an email about discounts on new products, or a message about your online shopping payment confirmation.

In this chapter, we described the design of a scalable notification system that supports multiple notification formats: push notification, SMS message, and email. We adopted message queues to decouple system components.

Besides the high-level design, we dug deep into more components and optimizations.

* Reliability: We proposed a robust retry mechanism to minimize the failure rate.
* Security: AppKey/appSecret pair is used to ensure only verified clients can send notifications.
* Tracking and monitoring: These are implemented in any stage of a notification flow to capture important stats.
* Respect user settings: Users may opt-out of receiving notifications. Our system checks user settings first before sending notifications.
* Rate limiting: Users will appreciate a frequency capping on the number of notifications they receive.

Congratulations on getting this far! Now give yourself a pat on the back. Good job!

## Reference materials

[1] Twilio SMS: <https://www.twilio.com/sms>

[2] Nexmo SMS: <https://www.nexmo.com/products/sms>

[3] Sendgrid: <https://sendgrid.com/>

[4] Mailchimp: <https://mailchimp.com/>

[5] You Cannot Have Exactly-Once Delivery:  
<https://bravenewgeek.com/you-cannot-have-exactly-once-delivery/>

[6] Security in Push Notifications:  
<https://cloud.ibm.com/docs/event-notifications?topic=event-notifications-en-push-apns>

[7] Key metrics for RabbitMQ monitoring:  
<https://www.datadoghq.com/blog/rabbitmq-monitoring/>