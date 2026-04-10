# Ad Click Prediction on Social Platforms

**08**

# Ad Click Prediction on Social Platforms

## Introduction

Online advertising allows advertisers to bid and place their advertisements (ads) on a platform for measurable responses such as impressions, clicks, and conversions. Displaying relevant ads to users is a fundamental for many online platforms such as Google, Facebook, and Instagram.

![Image represents a smartphone screen displaying two distinct content blocks.  The top block, labeled 'Sponsored' in red text, contains a dashed-line border and shows a video placeholder icon (a black camcorder symbol) within a rectangular area.  A small circle and a rectangular input field are positioned above this sponsored content. An arrow points from the left edge of the screen to the top sponsored ad, indicating its placement within the app's interface. Below this, a second content block displays a stylized mountain icon within a rectangular area, also with a small circle and a rectangular input field above it. Both content blocks are visually similar in structure, suggesting a consistent design pattern for content presentation within the application. The entire layout is contained within the outline of a smartphone screen, implying a mobile application context.](images/ch8-01-1-3UBSMWS6.png)

Figure 8.1: Sponsored ads placed on the user’s timeline

In this chapter, we design an (also known as ) system similar to what popular social media platforms use.

## Clarifying Requirements

Here is a typical interaction between a candidate and an interviewer.

**Candidate**: Can I assume the business objective of building an ad prediction system is to maximize revenue?  
**Interviewer:** Yes, that’s correct.

**Candidate:** There are different types of ads, such as video and image ads. In addition, ads can be displayed in different sizes and formats, like users’ timelines, pop-up ads, etc. For simplicity, can I assume ads are placed on users’ timelines only, and every click generates the same revenue?  
**Interviewer:** That sounds good.

**Candidate:** Can the system show the same ad to the same user more than once?  
**Interviewer:** Yes, we can show an ad more than once. Sometimes, an ad turns into a click after multiple impressions. In reality, companies have a “fatigue period”, that is, they don’t show the same ad to the same user for X days if the user repeatedly ignores it. For simplicity, assume we have no fatigue period.

**Candidate:** Do we support the “hide this ad” feature? How about “block this advertiser”? These kinds of negative feedback help us to detect irrelevant ads.  
**Interviewer:** Good question. Let’s assume users can hide an ad they don’t like. “Block this advertiser” is an interesting feature, but we don’t need to support it for now.

**Candidate:** Would it be okay to assume that the training dataset should be constructed using user and ad data, and the labels should be based on user-ad interactions?  
**Interviewer:** Sure.

**Candidate:** We can construct positive training data points via user clicks, but how do we generate negative data points? Can we assume any impression that is not clicked is a negative data point? What if the user scrolls fast and doesn’t spend time seeing the ad? What if we count an impression as negative, but eventually, the user clicks on it?  
**Interviewer:** These are excellent questions. What are your thoughts?

**Candidate:** If an ad is visible on a user’s screen for a certain duration but not clicked, we can count it as a negative data point. An alternative approach would be to assume impressions are negative until a click is observed. In addition, we can rely on negative feedback such as “hide this ad” to label negative data points.  
**Interviewer:** Makes sense! In practice, we might use other complex techniques to label negative data points . For this interview, let’s proceed with your suggestions.

**Candidate:** In ad click prediction systems, it’s critical for the model to learn from new interactions continuously. Is it fair to assume continual learning is a necessity here?  
**Interviewer:** Great point. Experiments have shown that even a 5-minute delay in updating models can damage performance [1].

Let's summarize the problem statement. We are asked to design an ad click prediction system. The business objective of the system is to maximize revenue. The ads are placed only on users' timelines, and each click generates the same revenue. It is necessary to train the model on new interactions continually. We construct the dataset from the user and ad data, and label them based on interactions. In this chapter, we will not discuss AdTech-specific topics as they are not relevant to ML interviews. To learn more about AdTech, refer to [2].

## Frame the Problem as an ML Task

### Defining the ML objective

The goal of the ad click prediction system is to increase revenue by showing users ads they are more likely to click on. This can be converted into the following ML objective: predicting if an ad will be clicked. This is due to the fact that by correctly predicting click probabilities, the system can display relevant ads to users, which leads to an increase in revenue.

### Specifying the system’s input and output

The ad click prediction system takes a user as input, and outputs a ranked list of ads based on click probabilities.

![Image represents a system for predicting ad clicks.  The system begins with a User, represented by a person icon, who is the input to an 'Ad click prediction system' block. This system receives information from a database cylinder labeled 'Ads,' which contains information about available advertisements.  The 'Ad click prediction system' processes user data and ad information to predict which ads the user is most likely to click. The output of the prediction system is a selection of ads, represented by a dashed-line box labeled 'Ads' containing individual ad boxes labeled 'Ad 1,' 'Ad 2,' '...,' and 'Ad k,' indicating a variable number of ads.  Arrows show the flow of information: from the User to the prediction system, from the 'Ads' database to the prediction system, and from the prediction system to the final selection of ads.  The system essentially takes user data and available ads as input, uses a machine learning model to predict click probability, and outputs a ranked list of ads for display.](images/ch8-02-1-SNQVHGOG.png)

Figure 8.2: Ad click prediction system’s input and output

### Choosing the right ML category

Figure 8.2 illustrates how ad prediction can be framed as a ranking problem. As described in Chapter 7, Event Recommendation System, the pointwise Learning to Rank (LTR) is a great starting point for solving ranking problems. The pointwise LTR employs a binary classification model that takes a ⟨\langle⟨ user, ad ⟩\rangle⟩ pair as input and predicts whether the user will click on the ad. Figure 8.3 shows the model's input and output.

![Image represents a system for predicting the probability of a user clicking on an advertisement.  At the bottom, a simple icon representing a 'User' and a stylized browser window labeled 'Advertisement' (containing a video camera icon) feed information into a central 'Binary classification model' box.  Arrows indicate the flow of data from the user and advertisement into the model. The model then outputs a value 'p' (representing the probability) to a box labeled 'Probability of this user clicking on the ad' at the top of the diagram.  The arrow from the model to the probability box shows the model's prediction of the click-through probability.  The entire diagram illustrates a machine learning pipeline where user and advertisement data are used to predict the likelihood of ad engagement.](images/ch8-03-1-73NOO4FT.png)

Figure 8.3: Binary classification model’s input-output

## Data Preparation

### Data engineering

Here is some raw data available in this system:

* Ads
* Users
* User-ad interactions

#### Ads

Ad data is shown in Table 8.1. In practice, we may have hundreds of attributes associated with each ad. For simplicity, we only list important ones.

| Ad ID | Advertiser ID | Ad group ID | Campaign ID | Category | Subcategory | Images or Videos |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 4 | 7 | travel | hotel | http: //cdn.mysite.com/u1.jpg |
| 2 | 7 | 2 | 9 | insurance | car | http: //cdn.mysite.com/t3.mp4 |
| 3 | 9 | 6 | 28 | travel | airline | http: //cdn.mysite.com/t5.jpg |

Table 8.1: Ad data

#### Users

The schema for user data is shown below.

| ID | Username | Age | Gender | City | Country | Language | Time zone |
| --- | --- | --- | --- | --- | --- | --- | --- |

Table 8.2: Schema for user data

#### User-ad interactions

This table stores user-ad interactions such as impressions, clicks, and conversions.

| User ID | Ad ID | Interaction type | Dwell time | Location (lat, long) | Timestamp |
| --- | --- | --- | --- | --- | --- |
| 11 | 6 | Impression | 5sec | 38.8951  -77.0364 | 165845053 |
| 11 | 7 | Impression | 0.4 sec | 41.9241  -89.0389 | 1658451365 |
| 4 | 20 | Click | - | 22.7531  47.9642 | 1658435948 |
| 11 | 6 | Conversion | - | 22.7531  47.9642 | 1658451849 |

Table 8.3: User-ad interaction data

### Feature engineering

Our aim in this section is to engineer features that will assist us in predicting user clicks.

#### Ad features

Ad features include the following:

* IDs
* Image/video
* Category and subcategory
* Impression and click numbers

Let's examine each in more detail.

##### IDs

These are advertiser ID, campaign ID, ad group ID, ad ID,etc.

**Why is it important?** The IDs represent the advertiser, the campaign, the ad group, and the ad itself. These IDs are used as predictive features to capture the unique characteristics of different advertisers, campaigns, ad groups, and ads.

**How to prepare it?** The embedding layer converts sparse features, such as IDs, into dense feature vectors. Each ID type has its own embedding layer.

##### Image/video

**Why is it important?** A video or image in a post is another signal that can help us predict what the ad is about. For example, an image of an airplane may indicate the ad is related to travel.

**How to prepare it?** The images or videos are first preprocessed. After that, we use a pre-trained model such as SimCLR [3] to convert unstructured data into a feature vector.

##### Ad category and subcategory

As provided by the advertiser, this is the ad's category and subcategory. For example, here is a list of broad types of categories that are targetable: Arts & Entertainment, Autos & Vehicles, Beauty & Fitness, etc.

**Why is it important?** It helps the model to understand which category the ad belongs to.

**How to prepare it?** These are manually provided by the advertiser based on a predefined list of categories and subcategories. To learn more about preparing textual data, read Chapter 4, YouTube Video Search.

##### Impressions and click numbers

* Total impression/clicks on the ad
* Total impressions/clicks on ads supplied by an advertiser
* Total impressions of the campaign

**Why is it important?** These numbers indicate how other users reacted to this ad. For example, users are more likely to click on an ad with a high click-through rate (CTR).

![Image represents a machine learning model architecture diagram illustrating feature concatenation from various sources.  The bottom layer shows three feature groups: 'Textual features' (derived from 'Tokenization' of 'Travel' and 'Flight' categories, processed by a 'Pretrained text model' producing two embedding vectors with numerical values), 'Engagement features' (consisting of numerical values representing 'Ad impressions,' 'Ad clicks,' 'Advertiser total clicks,' and 'Campaign total clicks'), and 'Image/video features' (processed by a 'Pretrained image/video model' resulting in a visual feature vector).  Each feature group feeds into an 'Embedding' layer, generating a vector of numerical values (e.g., [-0.8, 0.6, 0, 0.1, -0.3]). These embeddings, along with the numerical IDs ('Ad ID,' 'Advertiser ID,' 'Campaign ID,' and 'Group ID'), are then concatenated in the top layer, 'Concatenated features,' forming a combined feature vector for subsequent model processing (not shown).  The arrows indicate the data flow, showing how individual features are processed and combined to create the final feature vector.](images/ch8-04-1-QQBOWIK3.png)

Figure 8.4: Summary of ad-related feature preparation

#### User features

Similar to previous chapters, we choose the following features:

* Demographics: age, gender, city, country, etc
* Contextual information: device, time of the day, etc
* Interaction-related features: clicked ads, user's historical engagement statistics, etc

Let's take a closer look at interaction-related features.

##### Clicked ads

Ads previously clicked by the user.

**Why is it important?** Previous clicks indicate a user's interests. For example, when a user clicks on lots of insurance-related ads, it suggests they are likely to click on a similar ad again.

**How to prepare it?** In the same way as described in "Ad features".

##### User’s historical engagement statistics

These are the user’s historical engagement numbers, such as their total ad views and ad click rate.

**Why is it important?** An individual's historical engagement is a good predictor of future engagement. In general, users are more likely to click on ads in the future, if they clicked on ads frequently in the past.

**How to prepare it?** Engagement statistics are represented as numerical values. To prepare them, we scale their values into a similar range.

![Image represents a data processing pipeline for feature engineering in a machine learning system.  The pipeline begins with three distinct feature groups: Demographics (Age, Gender, City, Country, Language), Contextual Information (Time of day, Device), and Interaction-related features (User's ad click rate, User's total ad views, Clicked ad IDs).  Each feature within these groups undergoes preprocessing:  'Bucketize + One-hot' for categorical features like Age and Gender, and 'Embedding' for features like City and Language, resulting in numerical vector representations. These processed features are then individually fed into a 'Concatenated features' block, which combines them into a single feature vector.  Separately, the 'Interaction-related features' undergo an 'Ad-related feature computation' step, likely involving aggregation or transformation.  The output of this computation, along with the output from the 'Scale' block (which processes the User's total ad views), is then aggregated using an 'Aggregate (avg)' function, likely calculating the average of multiple values.  The final output is not explicitly shown but would presumably be the combined feature vector ready for use in a machine learning model.  Numerical values within the boxes represent example feature values or weights.](images/ch8-05-1-EKSODA4Z.png)

Figure 8.5: Feature preparation for user metadata and interactions

Before concluding the data preparation section, let's examine a common challenge in ad click prediction systems. In most cases, these systems deal with lots of high cardinality categorical features. For example, "ad category" takes values from a huge list of all possible categories. Similarly, "advertiser ID" and "user ID" take potentially millions of unique values, depending on how many users or advertisers are active on the platform. Given the huge feature space which often exists, it is common to have thousands or millions of features mostly filled with zeroes. In the model selection section, we will cover techniques to overcome these unique challenges.

## Model Development

### Model selection

As described in the section "Frame the Problem as an ML Task", the binary classification model is chosen to solve the ranking problem. Binary classifications can be modeled in several different ways. The following are common choices in ad click prediction systems:

* Logistic regression
* Feature crossing + logistic regression
* Gradient boosted decision trees
* Gradient boosted decision trees + logistic regression
* Neural networks
* Deep & Cross networks
* Factorization Machines
* Deep Factorization Machines

#### Logistic regression (LR)

LR models the probability of a binary outcome using a linear combination of one or multiple features. LR is fast to train and easy to implement. An LR-based ad click prediction system, however, does have the following drawbacks:

* **Non-linear problems can't be solved with LR.** LR solves the task using a linear combination of input features, which leads to a linear decision boundary. In ad click prediction systems, data is usually not linearly separable, so LR may perform poorly.
* **Inability to capture feature interactions.** LR is not capable of capturing feature interactions. In ad prediction systems, it is very common to have various interactions between features. When features interact with each other, the output probability cannot be expressed as the sum of the feature effects, since the effect of one feature depends on the value of the other feature.

Given these two drawbacks, LR is not the best choice for the ad prediction system. However, because it is fast to implement and easy to train, many companies use it to create a baseline model.

#### Feature crossing + LR

To capture feature interactions better, we use a technique called feature crossing

**What is feature crossing?**

Feature crossing is a technique used in ML to create new features from existing features. It involves combining two or more existing features into one new feature by taking their product, sum, or another combination. It is possible to capture nonlinear interactions between the original features in this way, which can improve the performance of ML models. For example, interactions such as "young and basketball" or "USA and football" may positively impact a model's ability to predict click probability.

**How to create feature crosses?**

In feature crossing, we manually add new features to the existing features based on prior knowledge. As Figure 8.68.68.6 shows, crossing two features, such as "country" and "language" adds six new features to the existing feature space. To learn more about crossing, refer to [4].

![Image represents a Cartesian product operation between two sets.  On the left, we have two feature vectors: `f1: Country` with values `[USA, China, England]` and `f2: Language` with values `[English, Chinese]`.  A horizontal line connects these vectors to a central 'x' symbol representing the Cartesian product.  This 'x' is labeled 'Country' vertically and 'Language' horizontally, indicating the dimensions of the product.  A rightward arrow extends from the 'x' to a list of eight feature vectors (f3-f8) on the right.  These vectors represent all possible combinations resulting from the Cartesian product of the Country and Language sets: f3 (USA and English), f4 (USA and Chinese), f5 (China and English), f6 (China and Chinese), f7 (England and English), and f8 (England and Chinese).  Essentially, the diagram visually demonstrates how combining two sets of features generates a new set containing all possible pairings.](images/ch8-06-1-RQCCRDOJ.png)

Figure 8.6: Crossing two features: country and language

**How to use feature crossing + LR?**

As shown in Figure 8.7, feature crossing + LR works as follows:

1. Use feature crossing on the original set of features to extract new features (crossed features)
2. Use the original and the crossed features as input for the LR model

![Image represents a machine learning model pipeline.  At the bottom, a rectangular box labeled 'Original features' represents the input data, depicted as a series of individual feature columns.  An arrow points upward from this box to a rectangular box labeled 'Feature crossing,' which processes the original features to generate new, combined features.  The output of the feature crossing is a rectangular box labeled 'Crossed features,' also shown as a series of columns, representing the newly created features.  An arrow connects the 'Crossed features' box to a rectangular box labeled 'Logistic regression,' indicating that these features are fed into the logistic regression model.  Another arrow connects the 'Original features' box directly to the 'Logistic regression' box, showing that the original features are also used as input to the logistic regression. Finally, an arrow points upward from the 'Logistic regression' box to a smaller square box labeled 'p,' representing the predicted output (presumably a probability) of the model.  The entire diagram illustrates a system where both original and crossed features are used as input to a logistic regression model to generate a prediction.](images/ch8-07-1-TF5NWYY4.png)

Figure 8.7: Feature crossing performed on original features

This method allows the model to capture certain pairwise (second-order) feature interactions. However, it has three shortcomings:

* **Manual process:** Human involvement is required to choose features to be crossed, which is time-consuming and expensive.
* **Requires domain knowledge:** Feature crossing requires domain expertise. To determine which interactions between features are predictive signals for the model, we need to understand the problem and the feature space in advance.
* **Cannot capture complex interactions:** Crossed features may not be sufficient to capture all the complex interactions from thousands of sparse features.
* **Sparsity:** The original features can be sparse. With feature crossing, the cardinality of the crossed features can become much larger, leading to more sparsity.

Given the drawbacks, this method is not an ideal solution for the ad prediction system.

#### Gradient-boosted decision trees (GBDT)

We examined GBDT in Chapter 7, Event Recommendation System. Here, we will only explore the pros and cons of GBDT when applied to the ad click prediction system.

**Pros**

* GBDT is interpretable and easy to understand

**Cons**

* **Inefficient for continual learning.** In ad click prediction systems, we continuously collect new data such as user, ad, and interaction data. To continually train a model on new data, we generally have two options: 1) training from scratch, or 2) fine-tuning the model on new data. GBDT is not designed to be fine-tuned with new data. So we usually need to train the model from scratch, which is inefficient at a large scale.
* **Cannot train embedding layers.** In ad prediction systems, it's common to have many sparse categorical features, and the embedding layer is an effective way to represent these features. However, GBDT cannot benefit from embedding layers.

#### GBDT + LR

There are two steps in this approach:

1. Train the GBDT model to learn the task.
2. Instead of using the trained model to make predictions, use it to select and extract new predictive features. The newly generated features and the original features are used as input into the LR model for predicting clicks.

**Use GBDT for feature selection**
Feature selection is intended to reduce the number of input features to only those most useful and informative. Using decision trees, we can select a subset of features based on their importance. To better understand how decision trees are used for feature generation, refer to [5].

**Use GBDT for feature extraction**
The purpose of feature extraction is to reduce the number of features by creating new features from existing ones. The newly extracted features are expected to have better predictive power. Figure 8.88.88.8 explains how to extract features using GBDT.

![Image represents a schematic of a Gradient Boosting Decision Tree (GBDT) model extracting features.  At the top, a horizontal rectangle labeled 'Original features' represents the input data, a vector of features.  This vector is fed into three separate decision tree ensembles, each labeled T1, T2, and T3, which are components of the overall GBDT. Each tree is depicted as a series of nodes, with leaf nodes containing numerical values (1, 2, 3, 4).  Dashed boxes enclose the leaf nodes of each tree. Arrows indicate the flow of data through the trees.  The output of each tree is a vector of binary values (0s and 1s) representing extracted features, shown in horizontal rectangles labeled 'Extracted features:' at the bottom.  These extracted features are the result of the data traversing the decision trees, with each leaf node's value contributing to the final feature vector.  The entire GBDT is enclosed in a dashed box.](images/ch8-08-1-SARHSQGK.png)

Figure 8.8: Use GBDT for feature extraction

An overview of GBDT in use followed by LR, is shown in Figure 8.9.

![Image represents a machine learning model ensemble.  At the bottom, a block labeled 'Original features' represents the initial dataset's features, which are fed into a Gradient Boosting Decision Tree (GBDT) model. The GBDT model processes these features and outputs 'Extracted features,' a transformed feature set.  Simultaneously, a separate process selects a subset of the 'Original features,' resulting in 'Selected features.' Both the 'Extracted features' and 'Selected features' are then fed as inputs into a Logistic Regression (LR) model, labeled 'LR.' Finally, the LR model receives a parameter 'p' as input from above, likely representing a hyperparameter or external control variable. The arrows indicate the direction of data flow, showing how the different components interact to produce a final prediction or output from the LR model.](images/ch8-09-1-RMHE3O5R.png)

Figure 8.9: GBDT + LR overview

Let’s explore the pros and cons of this approach.

**Pros:**

* In contrast to the existing features, the newly created ones produced by GBDT are more predictive, making it easier for the LR model to learn the task.

**Cons:**

* **Cannot capture complex interactions.** Similar to LR, this approach cannot learn pairwise feature interactions.
* **Continual learning is slow.** Fine-tuning GBDT models on new data takes time, which slows down continual learning overall.

#### Neural network (NN)

NN is another candidate for building the ad click prediction system. To predict click probabilities using a NN, we have two architectural options:

* Single NN
* Two-tower architecture

**Single NN:** Using the original features as input, a neural network outputs the click probability (Figure 8.10).

![Image represents a simplified machine learning model for predicting the probability of a user clicking an ad.  At the bottom, a rectangular box labeled 'Original features' is depicted as a series of equally sized, smaller, unlabeled boxes representing individual input features about the user. An upward arrow connects this box to a larger rectangular box labeled 'Neural network,' indicating that the original features are fed as input to the neural network.  The neural network processes these features.  An upward arrow then connects the neural network to a smaller square box labeled 'p' at the top, which represents the output of the model: the probability (p) of the user clicking the ad.  Above the 'p' box, the text 'Probability of this user clicking the ad' clarifies the meaning of the output. The overall flow is bottom-up, from input features through the neural network to the final probability prediction.](images/ch8-10-1-YMWPOWQY.png)

Figure 8.10: NN architecture

Two-tower architecture: In this option, we use two encoders: user encoder and ad encoder. The similarity between ad and user embeddings is used to determine the relevance, that is, the click probability. Figure 8.11 shows an overview of this architecture.

![Image represents a two-tower neural network architecture for predicting click-through rates (CTR) in a recommendation system.  The system consists of two independent towers: a 'User encoder' and an 'Ad encoder.'  The User encoder processes 'User-related features' (represented as a horizontal block of cells) to generate a 'User embedding,' a vector of numerical values (e.g., 0.1, 0.7, -0.1, 0.6, 0.5). Similarly, the Ad encoder processes 'Ad-related features' to produce an 'Ad embedding' (e.g., 0, 0.1, -0.9, 0.3, -0.3).  A dashed line connects the User and Ad embeddings, indicating that a similarity measure (represented as P(click) ~ Similarity) is calculated between these two vectors to predict the probability of a user clicking on a given ad.  The entire structure is labeled 'Two-tower NN,' highlighting the two-tower nature of the neural network.  The arrows indicate the flow of information: from features to embeddings, and then the embeddings are used to compute the click-through rate probability.](images/ch8-11-1-3D2KHTZQ.png)

Figure 8.11: Embedding-based NN

Although NNs have many benefits, they may not be the best choice for ad click prediction systems because:

* **Sparsity:** Given that the feature space is usually huge and sparse, most features are filled with zeroes. It may not be possible for NN\mathrm{NN}NN to learn the task effectively because it does not have access to enough data points.
* **Difficult to capture all pairwise feature interactions** due to the large number of features.

Given these limitations, we will not use NNs.

#### Deep & Cross Network (DCN)

In 2017, Google proposed an architecture named DCN [6] to find feature interactions automatically. This addresses the challenges of the manual feature crossing method. The following two parallel networks are used in this method:

* **Deep network:** Learns complex and generalizable features using a Deep Neural Network (DNN) architecture.
* **Cross network:** Automatically captures feature interactions and learns good feature crosses.

The outputs of deep network and cross network are concatenated to make a final prediction.

There are two types of DCN architectures: stacked and parallel. Figure 8.128.128.12 shows the architecture of a parallel DCN. To learn more about stacked architecture, refer to [7]. Note that it's not usually expected to provide details of DCN during ML system design interviews. If you are interested in learning more about DCN networks, refer to [7] [8].

![Image represents a machine learning model architecture.  At the bottom, 'Sparse input features' feed into 'Embedding layers', which generate 'Feature embeddings (Dense features)'. These dense features are input to a 'Deep neural network'.  Separately, 'Dense input features' are processed by a 'Cross network'. The outputs of the 'Deep neural network' and 'Cross network' are then 'Concatenated'. This concatenated output is fed into a 'Sigmoid' layer, producing a final 'Probability' output (P).  The diagram shows data flowing upwards, indicating a feedforward architecture.  The 'Deep neural network' and 'Cross network' represent distinct processing paths for different feature types, with their results combined to make a final prediction.  The shaded rectangles represent the output vectors of each layer, showing the dimensionality of the data at each stage.](images/ch8-12-1-CX5PRL67.png)

Figure 8.12: DCN architecture

DCN architecture is more effective than neural networks because it implicitly learns feature crosses. However, the cross network only models certain feature interactions, which may negatively affect the performance of the cross network model.

#### Factorization Machines (FM)

FM is an embedding-based model which improves logistic regression by automatically modeling all pairwise feature interactions. In ad click prediction systems, FM is widely used because it can efficiently model complex interactions between features.

So, let's understand how FM works. It automatically models all pairwise feature interactions by learning an embedding vector for each feature. The interaction between two features is determined by the dot product of their embeddings. Let's look at its formula to understand it better:

y^(x)=w0+∑iwixi+∑i∑j⟨vi,vj⟩xixj\hat{y}(x)=w\_0+\sum\_i w\_i x\_i+\sum\_i \sum\_j\langle v\_i, v\_j\rangle x\_i x\_jy^​(x)=w0​+i∑​wi​xi​+i∑​j∑​⟨vi​,vj​⟩xi​xj​

Where xix\_ixi​ refers to the iii-th feature, wiw\_iwi​ is the learned
weight, and viv\_ivi​ represents the embedding of the iii-th feature.
⟨\langle⟨ v\_i, v\_j ⟩\rangle⟩ denotes the dot product between two
embeddings.

This formula may look complex, but it's actually easy to understand. The first two terms compute a linear combination of the features, similar to how logistic regression works. The third term models pairwise feature interactions. Figure 8.138.138.13 shows a high-level overview of FM. Refer to [9] to learn the details of FM.

y^(x)=w0+∑iwixi⏟Logistic regression+∑i∑j⟨vi,vj⟩xixj⏟Pairwise interactions\hat{y}(x)=\underbrace{w\_0+\sum\_i w\_i x\_i}\_{\text{Logistic regression}}+\underbrace{\sum\_i \sum\_j\langle v\_i, v\_j\rangle x\_i x\_j}\_{\text{Pairwise interactions}}y^​(x)=Logistic regressionw0​+i∑​wi​xi​​​+Pairwise interactionsi∑​j∑​⟨vi​,vj​⟩xi​xj​​​


![Image represents a Factorization Machine model.  The model takes sparse input features (represented by five empty boxes within a dashed rectangle) as input. These features are fed into embedding layers (a rectangular box), which transform them into dense feature embeddings (multiple columns of empty boxes within a dashed rectangle).  These dense features are then processed to calculate pairwise feature interactions (a rectangular box), which represent the interactions between pairs of features.  Simultaneously, per-feature weights (a rectangular box) are calculated.  Both the pairwise feature interactions and the per-feature weights are then summed (+) and passed through a sigmoid function (a rectangular box) to produce a probability (a rectangular box labeled 'p'). The entire process from sparse input features to the final probability is enclosed within a dashed line labeled 'Factorization Machine'.  Arrows indicate the flow of information between components.](images/ch8-13-1-H33OCDXR.png)

Figure 8.13: Factorization Machine architecture

FM and its variants, such as FFM, effectively capture pairwise interactions between features. FM cannot learn sophisticated higher-order interactions from features, unlike neural networks, which can. In the next method, we combine FM and DNN to overcome this.

#### Deep Factorization Machines (DeepFM)

DeepFM is an ML model that combines the strengths of both NN and FM. A DNN network captures sophisticated higher-order features, and an FM captures low-level pairwise feature interactions. Figure 8.14 shows the high-level architecture of DeepFM. If you are interested to learn more about DeepFM, refer to [10].

![Image represents a machine learning model architecture for predicting a probability (labeled 'P').  The model takes sparse input features (represented by several small squares within a dashed box labeled 'Sparse input features') as input. These features are processed through embedding layers, transforming them into dense feature embeddings (multiple rectangular boxes within a dashed box labeled 'Feature embeddings (Dense features)').  These dense features are then fed into three separate components: 'Per feature weights' (a box representing per-feature weights), 'Pairwise feature interactions' (a box representing pairwise interactions between features), and a 'Deep neural network' (a box representing a deep neural network). The outputs of these three components are summed (+) before being passed through a sigmoid function, resulting in a final probability output (P).  Arrows indicate the flow of information between components, showing how the processed features contribute to the final probability prediction.](images/ch8-14-1-CW7JJ5XS.png)

Figure 8.14: DeepFM overview

One potential improvement is to combine GBDT and DeepFM. A GBDT converts the original features into more predictive features, while DeepFM operates on the new features. This method has won various ad prediction system competitions [11]. However, adding GBDT to DeepFM negatively affects the training and inference speed, and slows down the continual learning process.

In practice, we usually choose the correct model by running experiments. In our case, we start with a simple LR to create a baseline. Next, we experiment with DCN and DeepFM, as both are widely used in the tech industry.

### Model training

#### Constructing the dataset

For every ad impression, we construct a new data point. The input features are computed
from the user and the ad. A label is assigned to the data point, based on the following
strategy:

* **Positive label:** if the user clicks the ad in less than t seconds after the ad is shown, we label the data point as "positive". Note that ttt is a hyperparameter and can be tuned via experimentation.
* **Negative label:** if the user does not click the ad in less than ttt seconds, we label the data point as "negative".

In practice, companies use more complex methods to find the optimal strategy for labeling negative data points. To learn more, refer to [1].

![Image represents a tabular dataset seemingly used for training a machine learning model, likely for ad click prediction.  The table is divided into four columns: a serial number column (#), a column for 'User and interaction features' (represented as a vector of numerical values), a column for 'Ad features' (also a numerical vector), and a 'Label' column indicating whether the data point represents a positive (ad click) or negative (no click) outcome. Each row represents a single data instance.  For instance, row 1 shows a vector of user and interaction features [1, 0, 1, 0.8, 0.1, 1, 0], a vector of ad features [0, 1, 1, 0.4, 0.9, 0], and a positive label. Row 2 similarly presents another data instance with different feature values and a negative label. The numerical values within the feature vectors likely represent different attributes or characteristics of the user, their interaction, and the ad itself.  The table structure suggests a supervised learning scenario where the model learns to associate feature vectors with their corresponding positive or negative labels.](images/ch8-15-1-VBQDNO5G.png)

Figure 8.15: Constructed dataset

To keep the model adaptive to new data, it must continuously be trained. As a result, new training data points should be continuously generated using new interactions. We will discuss continual learning further in the serving section.

#### Choosing the loss function

Since we are training a binary classification model, we choose cross-entropy as a classification loss function.

## Evaluation

### Offline metrics

Two metrics are typically used to evaluate an ad click prediction system:

* Cross-entropy (CE)
* Normalized cross-entropy (NCE)

**CE.** This metric measures how close the model's predicted probabilities are to the ground truth labels. CE is zero if we have an ideal system that predicts a 0 for the negative classes and 1 for the positive classes. The lower the CE, the higher the accuracy of the prediction. The formula is:

H(p,q)=−∑c=1Cpclog⁡qcH(p, q)=-\sum\_{c=1}^C p\_c \log q\_cH(p,q)=−c=1∑C​pc​logqc​

where ppp is the ground truth, qqq is the predicted probability, and CCC is the total number of classes.

For binary classification, the CE formula can be rewritten as:

H(p,q)=−∑ipilog⁡qi=−∑i(yilog⁡y^i+(1−yi)log⁡(1−y^i))H(p, q)=-\sum\_i p\_i \log q\_i=-\sum\_i\left(y\_i \log \hat{y}\_i+\left(1-y\_i\right) \log \left(1-\hat{y}\_i\right)\right)H(p,q)=−i∑​pi​logqi​=−i∑​(yi​logy^​i​+(1−yi​)log(1−y^​i​))

where yiy\_iyi​ is the ground truth label of the iii-th data point and y^i\hat{y}\_iy^​i​ is the predicted probability of iii-th data point.

Let's take a look at a concrete example, as shown in Figure 8.16.

![Image represents a comparison of two machine learning models, Model A and Model B, using cross-entropy (CE) loss to evaluate their performance on a click-through rate prediction task.  Three ad examples are shown, each with a visual representation (video camera or mountain icons) and a true label indicating whether a click occurred (1 for clicked, 0 for not clicked).  For each ad, both Model A and Model B provide a predicted probability of a click, P(click).  These predictions, along with the true labels, are used to calculate the cross-entropy loss for each model. The formula for cross-entropy is shown: CE = -Σᵢ yᵢ log ŷᵢ + (1 - yᵢ) log (1 - ŷᵢ). The calculated CE values for Model A (0.273) and Model B (1.319) are displayed.  A comparison of these CE values shows that CE for Model A is less than CE for Model B, indicating that Model A is a better performing model because it has a lower loss.  Dashed arrows visually connect the predictions and true labels to the CE calculation, and another arrow connects the calculated CE values to the final conclusion that Model A is better than Model B.](images/ch8-16-1-O35DQUM2.png)

Figure 8.16: CE of two ML models

Note that aside from using CE as a metric, it is also commonly used as a standard loss function in classification tasks during model training.

**Normalized cross-entropy (NCE)**. NCE is the ratio between our model's CE\mathrm{CE}CE and the CE of the background CTR (average CTR in the training data). In other words, NCE compares the model with a simple baseline which always predicts the background CTR. A low NCE indicates the model outperforms the simple baseline. NCE≥1N C E \geq 1NCE≥1 indicates that the model is not performing better than the simple baseline.

 Normalized cross entropy =CE( ML model )CE( Simple baseline )\text { Normalized cross entropy }=\frac{C E(\text { ML model })}{C E(\text { Simple baseline })} Normalized cross entropy =CE( Simple baseline )CE( ML model )​

Let's take a look at a concrete example to understand better how NCE is calculated. As shown in Figure 8.17, a simple baseline model always predicts 0.60.60.6 (CTR in the training data). In this case, the NCE value is 0.3240.3240.324 (less than 1), indicating model A outperforms the simple baseline.

![Image represents a calculation of Normalized Cross-Entropy (NCE) for a machine learning model (Model A) predicting click-through rates (CTR) on advertisements.  Three ads are shown, each with a visual representation (Ad 1: video camera; Ad 2: mountains; Ad 3: video camera) and associated true labels (1 for clicked, 0 for not clicked).  Model A provides predicted probabilities of clicks (P(click)) for each ad.  A baseline CTR (background CTR) is also provided, representing a constant probability of a click regardless of the ad.  The cross-entropy (CE) is calculated for both Model A and the baseline using the formula:  -Σᵢ yᵢ log ŷᵢ + (1 - yᵢ) log (1 - ŷᵢ), where yᵢ is the true label and ŷᵢ is the predicted probability.  The calculated CE for Model A is 0.273, and for the baseline is 0.842.  Finally, the NCE for Model A is computed by dividing the Model A CE by the baseline CE (0.273 / 0.842 = 0.324), indicating the relative performance of Model A compared to the baseline.  Dashed arrows visually connect the relevant components, showing the flow of information from the ads and predictions to the CE calculations and finally to the NCE calculation.](images/ch8-17-1-MMNIBRQY.png)

Figure 8.17: NCE calculations for model A

### Online metrics

Let's examine some metrics we may use during online evaluation.

* CTR
* Conversion rate
* Revenue lift
* Hide rate

**CTR**. This metric measures the ratio between clicked ads and the total number of shown ads.

CTR= Number of clicked ads  Number of shown ads C T R=\frac{\text { Number of clicked ads }}{\text { Number of shown ads }}CTR= Number of shown ads  Number of clicked ads ​

CTR is a great online metric for ad click prediction systems, as maximizing user clicks on ads is directly related to an increase in revenue.

**Conversion rate.** This metric measures the ratio between the number of conversions and the total number of ads shown.

 Conversion rate = Number of conversions  Number of impressions \text { Conversion rate }=\frac{\text { Number of conversions }}{\text { Number of impressions }} Conversion rate = Number of impressions  Number of conversions ​

This metric is important to track as it indicates how many times advertisers actually benefited from the system. This matters because advertisers will eventually lose interest and cease spending on ads if their ads do not lead to conversions.

**Revenue lift.** This measures the percentage of revenue increase over time.

**Hide rate.** This metric measures the ratio between the number of ads hidden by users and the number of shown ads.

 Hide rate = Number of ads hidden by users  Number of shown ads \text { Hide rate }=\frac{\text { Number of ads hidden by users }}{\text { Number of shown ads }} Hide rate = Number of shown ads  Number of ads hidden by users ​

This metric is helpful for understanding how many irrelevant ads the system displayed to users, also known as false positives.

## Serving

At serving time, the system is responsible for outputting a list of ads ranked by their click probabilities. The proposed ML system design is shown in Figure 8.18. Let's examine each of the following pipelines:

* Data preparation pipeline
* Continual learning pipeline
* Prediction pipeline

![Image represents a machine learning system for ad ranking.  A stream of new data and interactions feeds into a 'Data preparation pipeline,' which consists of 'Batch feature computation' and 'Online feature computation' processing 'New data' and 'Data lake' respectively.  The outputs are stored in a 'Feature store.'  This pipeline also feeds into 'Dataset generation,' which creates a 'Training dataset' for the 'Continual learning pipeline.' This pipeline includes 'Model training,' 'Model validation and deployment,' and updates a 'Model registry.' The trained 'ML model' is then used by a 'Ranking service,' which receives input from the 'Pool of Ads' and the 'Feature store,' and performs online feature computation. The 'Ranking service' output is further processed by a 'Re-ranking service,' using the 'Online feature computation' and finally, a 'Prediction pipeline' generates 'Ranked ads' for the user.  The entire system is designed for continuous learning and improvement of the ad ranking model.](images/ch8-18-1-TYLNC6R7.png)

Figure 8.18: ML system design

### Data preparation pipeline

The data preparation pipeline performs the following two tasks:

1. Compute online and batch features
2. Continuously generate training data from new ads and interactions

To compute features, the following two options are used: batch feature computation and online feature computation. Let's see how they differ from each other.

**Batch feature computation**
Some of the features we chose are static, which means they change very rarely. For example, an ad's image and category are static features. This component computes static features periodically (e.g., every few days or weeks) with batch jobs and then stores the features in a feature store. This improves the system's performance during serving because the features are precomputed.

**Online feature computation**
Some features are dynamic as they change frequently. For example, the numbers of ad impressions and clicks are examples of dynamic features. These features need to be computed at query time, and this component is used to compute dynamic features.

### Continual learning pipeline

Based on the requirements, continually learning the model is critical. This pipeline is responsible for fine-tuning the model on new training data, evaluating the new model, and deploying the model if it improves the metrics. It ensures the prediction pipeline always uses a model adapted to the most recent data.

### Prediction pipeline

The prediction pipeline takes a query user as input and outputs a list of ads ranked by their click probabilities. Since some of the features which the model relies upon are dynamic, we cannot use batch prediction. Instead, requests are served as they arrive using online prediction.

As we've seen in previous chapters, a two-stage architecture is used in the prediction pipeline. First, we employ a candidate generation service to efficiently narrow down the available pool of ads to a small subset of ads. In this case, we use the ad targeting criteria often provided by advertisers, such as target age, gender, and country.

Next, we employ a ranking model which fetches the candidate ads from the candidate generation service, ranks them based on click probability, and outputs the top ads. This component interacts with the same feature store and online feature computation component. Once the static and dynamic features are obtained, the ranking service uses the model to get a predicted click probability for each candidate ad. These probabilities are used to rank the ads and to output those with the highest click probability.

Finally, a re-ranking service modifies the list of ads by incorporating additional logic and heuristics. For example, we can increase the diversity of ads by removing very similar ads from the list.

## Other Talking Points

If there is time left at the end of the interview, here are some potential talking points you might discuss with the interviewer:

* In ranking and recommendation systems, it's important to avoid data leakage [12][13][12][13][12][13]
* The model needs to be calibrated in ad click prediction systems. Discuss model calibration and techniques for calibrating a model [14].
* A common variant of FM is a field-aware Factorization Machine (FFM). It's good to talk about FFM and how it differs from FM [15].
* A common variant of DeepFM is XDeepFM. Talk about XDeepFM and how it differs from DeepFM [10].
* We've described why continuous learning is necessary for ad click prediction systems. However, continual learning on new data may lead to catastrophic forgetting. Discuss what catastrophic forgetting is and what common solutions are [16].

## References

1. Addressing delayed feedback. <https://arxiv.org/pdf/1907.06558.pdf>.
2. AdTech basics. <https://advertising.amazon.com/library/guides/what-is-adtech>.
3. SimCLR paper. <https://arxiv.org/pdf/2002.05709.pdf>.
4. Feature crossing. <https://developers.google.com/machine-learning/crash-course/feature-crosses/video-lecture>.
5. Feature extraction with GBDT. <https://towardsdatascience.com/gradient-boosted-decision-trees-explained-9259bd8205af/>.
6. DCN paper. <https://arxiv.org/pdf/1708.05123.pdf>.
7. DCN V2 paper. <https://arxiv.org/pdf/2008.13535.pdf>.
8. Microsoft’s deep crossing network paper. <https://www.kdd.org/kdd2016/papers/files/adf0975-shanA.pdf>.
9. Factorization Machines. <https://www.jefkine.com/recsys/2017/03/27/factorization-machines/>.
10. Deep Factorization Machines. <https://d2l.ai/chapter_recommender-systems/deepfm.html>.
11. Kaggle’s winning solution in ad click prediction. <https://www.youtube.com/watch?v=4Go5crRVyuU>.
12. Data leakage in ML systems. <https://machinelearningmastery.com/data-leakage-machine-learning/>.
13. Time-based dataset splitting. <https://www.linkedin.com/pulse/time-based-splitting-determining-train-test-data-come-manraj-chalokia/?trk=public_profile_article_view>.
14. Model calibration. <https://machinelearningmastery.com/calibrated-classification-model-in-scikit-learn/>.
15. Field-aware Factorization Machines. <https://www.csie.ntu.edu.tw/~cjlin/papers/ffm.pdf>.
16. Catastrophic forgetting problem in continual learning. <https://www.cs.uic.edu/~liub/lifelong-learning/continual-learning.pdf>.