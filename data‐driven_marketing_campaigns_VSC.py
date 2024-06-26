# -*- coding: utf-8 -*-
"""Another copy of Data‐Driven-marketing-campaigns.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rMJNn6o1hQ5_Nvm8oqYe0LpvevbHl9eQ

# 📊 Project Objective:
* ### Analyzed booking **EGYPT** data with Python and Spark to run data‐driven campaigns for two hotels,
* ### Created custom promotions, built cancellation prediction models.

# 🌟 Business Understanding:

| Column Name                        | Description                                                                                      |
|-----------------------------------|--------------------------------------------------------------------------------------------------|
| hotel                             | Type of hotel booked by the customer (e.g., resort hotel or city hotel).                         |
| is_canceled                       | Indicates whether the booking was canceled (1) or not (0).                                        |
| lead_time                         | Number of days between the booking date and the arrival date.                                      |
| arrival_date_year                 | Year of arrival date.                                                                            |
| arrival_date_month                | Month of arrival date.                                                                           |
| arrival_date_week_number          | Week number of arrival date.                                                                     |
| arrival_date_day_of_month         | Day of the month of arrival date.                                                                |
| stays_in_weekend_nights           | Number of weekend nights (Saturday/Sunday) the guest stayed or booked to stay at the hotel.       |
| stays_in_week_nights              | Number of week nights (Monday to Friday) the guest stayed or booked to stay at the hotel.         |
| adults                            | Number of adults.                                                                                |
| children                          | Number of children.                                                                              |
| babies                            | Number of babies.                                                                                |
| meal                              | Type of meal booked (e.g., Undefined/SC – no meal package; BB – Bed & Breakfast; HB – Half board; FB – Full board). |
| country                           | Country of origin of the guest "PRT" Portugal,"ESP"Spain "FRA"  France "DEU"  Germany "GBR" United Kingdom
"USA" the United States of America.                                                                  |
| distribution_channel              | Booking distribution channel (e.g., TA – Travel Agents; TO – Tour Operators).                      |
| is_repeated_guest                 | Indicates if the booking was from a repeated guest (1) or not (0).                                 |
| previous_cancellations            | Number of previous booking cancellations by the customer.                                         |
| previous_bookings_not_canceled    | Number of previous bookings not canceled by the customer.                                          |
| reserved_room_type                | Type of room reserved.                                                                           |
| assigned_room_type                | Type of room assigned to the customer.                                                           |
| booking_changes                   | Number of changes made to the booking.                                                           |
| deposit_type                      | Type of deposit made for the booking (e.g., No Deposit, Non Refund, Refundable).                   |
| agent                             | ID of the travel agency that made the booking.                                                    |
| company                           | ID of the company/entity that made the booking or responsible for payment.                         |
| days_in_waiting_list              | Number of days the booking was in the waiting list before it was confirmed to the customer.       |
| customer_type                     | Type of booking (e.g., Contract, Group, Transient, Transient-Party).                              |
| adr                               | Average daily rate (sum of all lodging transactions divided by the total number of staying nights).|
| required_car_parking_spaces       | Number of car parking spaces required by the customer.                                            |
| total_of_special_requests         | Number of special requests made by the customer (e.g., extra beds, high floor, early check-in).   |

## From the 🌟 Business Understanding:
some key columns that i expect are generally useful for cancellation prediction models:

* Lead Time: This column represents the number of days between the booking date and the arrival date. Bookings made further in advance might have different cancellation patterns compared to last-minute bookings.

* Previous Cancellations: Knowing if the customer has canceled bookings in the past can provide insights into their behavior and the likelihood of them canceling again.

* Booking Changes: The number of changes made to the booking can indicate uncertainty or hesitation from the customer's side, which might correlate with a higher cancellation rate.

* Deposit Type: Understanding the type of deposit made for the booking (e.g., non-refundable vs. refundable) can help anticipate cancellation behavior. Non-refundable bookings, for example, might have a lower cancellation rate.

* Total of Special Requests: The number of special requests made by the customer could reflect their level of engagement and satisfaction with the booking, which might influence their likelihood of canceling.

* ADR (Average Daily Rate): This could indirectly influence cancellation rates, as higher prices might make customers more reluctant to cancel.

* Customer Type: Different types of bookings (e.g., transient vs. group) might have different cancellation patterns.

# 📚 Importing Libraries
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings("ignore")
# %matplotlib inline
sns.set(style="darkgrid",font_scale=1.5)
pd.set_option("display.max.rows",None)
pd.set_option("display.max.columns",None)

"""# ⏳ Loading Dataset"""

df=pd.read_csv("/content/drive/MyDrive/egphotelbookings.csv")

df.head(8)

"""# 🧠 Basic Understaning of Data"""

list_of_numerics=df.select_dtypes(include=['float','int']).columns
types= df.dtypes
missing= round((df.isnull().sum()/df.shape[0]),3)*100
overview= df.apply(lambda x: [round(x.min()),
                                 round(x.max()),
                                 round(x.mean()),
                                 round(x.quantile(0.5))] if x.name in list_of_numerics else x.unique())

outliers= df.apply(lambda x: sum(
                                 (x<(x.quantile(0.25)-1.5*(x.quantile(0.75)-x.quantile(0.25))))|
                                 (x>(x.quantile(0.75)+1.5*(x.quantile(0.75)-x.quantile(0.25))))
                                 if x.name in list_of_numerics else ''))

explo = pd.DataFrame({'Types': types,
                      'Missing%': missing,
                      'Overview': overview,
                      'Outliers': outliers}).sort_values(by=['Missing%','Types'],ascending=False)
explo.transpose()

"""#### **Company** has 94% null values so we can't fill it, drop it. we don't need babies column so drop this column. **Unnamed**: 0 is just the id drop it. **arrival_date_week_number**: we will not use arrival_date_week_number so drop it."""

"""
print dimensionality of the data, columns, types and missing values
"""
print(f"Data dimension: {df.shape}")

df.columns

"""#🧹 Data Preprocessing Part-1:"""

# drop company,babies and Unnamed column
df.drop(['company', 'babies', 'Unnamed: 0', 'arrival_date_week_number'], axis=1, inplace=True)

import pandas as pd
df.dropna(subset=['country', 'children'], inplace=True)

columns=["adr","lead_time","stays_in_weekend_nights","stays_in_week_nights","adults","is_repeated_guest","previous_cancellations","previous_bookings_not_canceled","booking_changes","days_in_waiting_list","required_car_parking_spaces","total_of_special_requests"]

skewness = df[columns].skew().sort_values()
plt.figure(figsize=(14,6))
sns.barplot(x=skewness.index, y=skewness, palette=sns.color_palette("Reds",19))
for i, v in enumerate(skewness):
  plt.text(i, v, f"{v:.1f}", ha="center", va="bottom",size=15,fontweight="black")

plt.ylabel("Skewness")
plt.xlabel("Columns")
plt.xticks(rotation=90)
plt.title("Skewness of Continous Numerical Columns",fontweight="black",size=20,pad=10)
plt.tight_layout()
plt.show()

# import seaborn as sns

# def remove_outlier(df, list):
#     """Remove outliers from a specified column using the Interquartile Range (IQR) method.

#     Parameters:
#     - df: DataFrame containing the data
#     - col: Column name for which outliers should be removed

#     Returns:
#     - DataFrame with outliers removed
#     """
#     for col in list:
#       q1, q3 = df[col].quantile([0.25, 0.75])
#       iqr = q3 - q1
#       lower = q1 - (1.5 * iqr)
#       upper = q3 + (1.5 * iqr)

#       df = df[((df[col] >= lower) & (df[col] <= upper))]

#     return df
# def boxplot(df, col_name):
#     sns.boxplot( data = df[col_name], orient="h")

def remove_outliers(df, col_name):
    # remove outliers in lead_time
    Q1 = np.percentile(df[col_name], 25, method='midpoint')
    Q3 = np.percentile(df[col_name], 75, method='midpoint')
    IQR = Q3 - Q1
    upper=Q3+1.5*IQR

    #Below Lower bound
    lower=Q1-1.5*IQR
    df = df[((df[col_name]>=lower) & (df[col_name] <= upper))]
    return df
def boxplot(df, col_name):
    sns.boxplot( data = df[col_name], orient="h")

df = remove_outliers(df, 'lead_time')
df = remove_outliers(df, 'adr')

skewness = df[columns].skew().sort_values()
plt.figure(figsize=(14,6))
sns.barplot(x=skewness.index, y=skewness, palette=sns.color_palette("Reds",19))
for i, v in enumerate(skewness):
  plt.text(i, v, f"{v:.1f}", ha="center", va="bottom",size=15,fontweight="black")

plt.ylabel("Skewness")
plt.xlabel("Columns")
plt.xticks(rotation=90)
plt.title("Skewness of Continous Numerical Columns",fontweight="black",size=20,pad=10)
plt.tight_layout()
plt.show()

"""# 📊 Exploatory Data Analysis EDA"""

corr = df.corr(numeric_only=True)

# Visualize correlation matrix with heatmap
plt.figure(figsize=(20, 8))
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Matrix Heatmap')
plt.show()

"""### `insight1`
### People who get children with them are `more profitable` to the hotel as there is a correlation between `children` and `adr`

## Check the relation between the lead_time and is_cancelled.
"""

sns.histplot(data=df[(df["is_canceled"]==0)],x="lead_time",bins=20)

"""### We see from the histogram of the `non-cancelled` reservations: `lead_time` is shifted towards left or small number of days, so : people don't tend` to cancel` when they reserved in date `close`r to the check in."""

sns.histplot(data=df[(df["is_canceled"]==1)],x="lead_time",bins=20)

"""### If someone will cancel it's more likely he booked 100 days before the checkin

### Next, We want to see what are the months which are high in booking that are not cancelled.
"""

sns.histplot(df[(df["is_canceled"]==0)],y="arrival_date_month")

"""### insight

### `May, July, August` are the highest months that users book in


"""

sns.histplot(df[(df["is_canceled"]==1)],y="arrival_date_month")

"""# - insight
### `April, May, June ` are the most months that the user book in and cancel.)

## Next see the relation between the `deposit type` and cancelation rate.
"""

sns.histplot(df[(df["is_canceled"]==1 )],y="deposit_type")

sns.histplot(df[(df["is_canceled"]==0 )],y="deposit_type")

"""### So We need to get the ratio between the number of people who choose `No_deposit` and `cancelled bookings`.
### and Also, need to get the `ratio `between the `number of people `who choose `Non Refund and cancelled bookings`.




"""

nodeposit = len(df[(df['deposit_type'] == 'No Deposit')])
nonrefund = len(df[(df['deposit_type'] == 'Non Refund')])
nondepositeAndCancelled = len(df[(df['deposit_type'] == 'No Deposit') & (df['is_canceled']==1)])
nonreufndAndCancelled = len(df[(df['deposit_type'] == 'Non Refund') & (df['is_canceled']==1)])
print('No deposit users', nodeposit)
print('Non Refund users', nonrefund)
print('No deposit users & cancelled', nondepositeAndCancelled)
print('Non Refund users & cancelled', nonreufndAndCancelled)
print('ratio between No deposit users / No deposit users that cancelled = ', nondepositeAndCancelled/nodeposit)
print('ratio between Non Refund users / Non Refund users that cancelled = ', nonreufndAndCancelled/nonrefund)

"""#### There is a strange pattern that users that use deposit type as non refund tends to cancel more than users that `don't add deposit`. The histogram and the ratio strengthen the pattern

### let see relation bettwen previous_cancellations ans cancelled
"""

sns.histplot(df[(df["is_canceled"]== 0 )],y="customer_type")

sns.histplot(df[(df["is_canceled"]== 1 )],y="customer_type")

"""So We need to get the ratio between the number of people who `Transient` and `cancelled bookings`.
and Also, need to get the ratio between the number of people who `Transient and cancelled booking`
"""

T_Transient = len(df[(df['customer_type'] == 'Transient')])
Transient_prety = len(df[(df['customer_type'] == 'Transient-Party')])
contract = len(df[(df['customer_type'] == 'Contract')])
T_TransientAndCancelled = len(df[(df['customer_type'] == 'Transient') & (df['is_canceled']==1)])
Transient_pretyAndCancelled = len(df[(df['customer_type'] == 'Transient-Party') & (df['is_canceled']==1)])
ContractAndCancelled = len(df[(df['customer_type'] == 'Contract') & (df['is_canceled']==1)])
print('customer_type_Transient', T_Transient)
print('customer_type_Transient_Party',Transient_prety)
print('T_Transient_users & cancelled', T_TransientAndCancelled)
print('Transient_prety users & cancelled', Transient_pretyAndCancelled)
print('ratio between Transient  users & cancelled /Transient users  = ', T_TransientAndCancelled/T_Transient)
print('ratio between Transient_prety users & cancelled / Transient_prety users  = ', Transient_pretyAndCancelled/Transient_prety)
print('ratio between Contract & cancelled / Contract users  = ',ContractAndCancelled/contract)

sns.histplot(df[(df["is_canceled"]== 1 )],y="total_of_special_requests")

sns.histplot(df[(df["is_canceled"]== 0 )],y="total_of_special_requests")

"""## See which customers are more loyal to their hotel, and the next time any customer has this rule will be given a promotion."""

loyal_customers = df[(df['previous_bookings_not_canceled'] > 3) & (df['previous_cancellations'] == 0)]
print('number of loyal customers till now', len(loyal_customers))

"""# 📈 Feature Engineering"""

df['revenue'] = df['adr'] * (df['stays_in_weekend_nights'] + df['stays_in_week_nights'])

"""# ⚙️ Data Preprocessing Part-2
- To transform data for creating more accurate & robust model.
"""

# import seaborn as sns

# def remove_outlier(df, list):
#     """Remove outliers from a specified column using the Interquartile Range (IQR) method.

#     Parameters:
#     - df: DataFrame containing the data
#     - col: Column name for which outliers should be removed

#     Returns:
#     - DataFrame with outliers removed
#     """
#     for col in list:
#       q1, q3 = df[col].quantile([0.25, 0.75])
#       iqr = q3 - q1
#       lower = q1 - (1.5 * iqr)
#       upper = q3 + (1.5 * iqr)

#       df = df[((df[col] >= lower) & (df[col] <= upper))]

#     return df
# def boxplot(df, col_name):
#     sns.boxplot( data = df[col_name], orient="h")

"""# spark"""

! pip install pyspark

from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('Python Spark DataFrames basic example').getOrCreate()

sdf =spark.createDataFrame(df)

sdf.printSchema()

sdf.show(3)

sdf.createOrReplaceTempView("hotels_booking")
sdf.printSchema()

"""### get the most repeated agencies with non cancelled bookings

"""

command="""
select  agent ,count(agent) as numberOfBookings
from hotels_booking
where isnan(agent)=0  and is_canceled = 0
group by agent
order by numberOfBookings DESC
limit 5"""
spark.sql(command).show()

"""##### We have `3 `agencies`(9, 240, 7)` that we can offer their users some promotions, as these agencies bring us huge number of visitors.

### Let's get the users that have large difference between the not canceled bookings and canceled bookings. Any further booking that contains these criteria we will give them promotions. as they are serious customers.
"""

command="""
select * ,(previous_cancellations-previous_bookings_not_canceled)as loyality FROM hotels_booking
where (previous_cancellations-previous_bookings_not_canceled) >1
order by loyality
limit 5"""
spark.sql(command).show()

"""### Get the relation between number of stays in weekend and the adr"""

command="""
select AVG(adr)AS AVG_adr,stays_in_weekend_nights from hotels_booking
group by stays_in_weekend_nights
order by AVG_adr DESC
limit 5
"""
spark.sql(command).show()

"""#### Staying in the weekend `2 or 3` days are the most profitable to the hotel

### Let's discover the average adr according to the room type and what the type of rooms are more profitable
"""

import plotly.express as pltx
pltx.box(data_frame = df[(df['is_canceled'] == 0)], x = 'reserved_room_type', y = 'adr', color = 'hotel')

"""Room of type H,L in Renaissance and G,F in JW Marriott are the highest in ADR.

## Get the room types that are poorly booked
"""

sns.histplot(data=df[(df['is_canceled'] == 0)], x='reserved_room_type', hue='hotel', multiple='stack')

"""## Get the rooms that are least booked

"""

command="""
select reserved_room_type ,count (reserved_room_type) as counter  from hotels_booking
where is_canceled =0
group by reserved_room_type
order by counter
"""
spark.sql(command).show()

"""### We will do promotions on the room types` (L,H,C,B,G)` as they are the least booked. (promotion #3)

## Get the average room price in each month for each hotel.
"""

df.groupby('arrival_date_month')['adr'].sum().plot(kind='bar')

command="""
select arrival_date_month,avg (adr) as avg_price  from hotels_booking
where is_canceled=0
group by arrival_date_month
order by avg_price DESC
"""
spark.sql(command).show()

"""#### `August, July, June` (summer months) are the highest in room prices. give promotion in these months to increase number of bookings. (promotion#4)

# Visualize the total revenue in each month.
"""

df.groupby('arrival_date_month')['revenue'].sum().plot(kind='bar')

command="""
select arrival_date_month,cast(sum(revenue)as numeric(36,2) )as Total_revenue  from hotels_booking
where is_canceled=0
group by arrival_date_month
order by Total_revenue DESC
"""
spark.sql(command).show()

"""### The most profitable months are `August, July, June`"""

# remove some useless columns to the cancelation to get better results with the predictions (features selection)
sdf_cleaned = sdf.drop('arrival_date_year','arrival_date_day_of_month', 'children', 'meal', 'agent', 'days_in_waiting_list', 'required_car_parking_spaces')

"""# get numerical , categorical columns of the dataframe

"""

# get numerical , categorical columns of the dataframe
numerical_columns = []
categorical_columns = []
for col in sdf_cleaned.dtypes:
    if col[1] == 'string':
        categorical_columns.append(col[0])
    elif col[0] !="is_canceled":
        numerical_columns.append(col[0])

numerical_columns

"""### Do some preprocessing to be able to fit the model to the data."""

from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler
from sklearn.metrics import accuracy_score
from pyspark.ml.feature import StringIndexer, VectorAssembler

# encode the categorical columns to numerical values using StringIndexer
stages = []
for categoricalCol in categorical_columns:
    stringIndexer = StringIndexer(inputCol = categoricalCol, outputCol = categoricalCol + 'Index')
    stages += [stringIndexer]

# apply the stages to the dataframe
featurizationPipeline = Pipeline(stages = stages)
featurizationPipelineModel = featurizationPipeline.fit(sdf)
sdf = featurizationPipelineModel.transform(sdf)

# add the independant variables to the stages except the target variable 'is_canceled'
assemblerInputs = []
for numericalCol in numerical_columns:
    assemblerInputs.append(numericalCol)

for categoricalCol in categorical_columns:
    if categoricalCol != 'is_canceled':
        assemblerInputs.append(categoricalCol + "Index")

# add the numerical columns to the stages
stages_split = []
assembler = VectorAssembler(inputCols=assemblerInputs, outputCol="feature_vector")
stages_split += [assembler]
featurizationPipeline = Pipeline(stages = stages_split)
featurizationPipelineModel = featurizationPipeline.fit(sdf)
sdf = featurizationPipelineModel.transform(sdf)

# # add column named 'label' is the same as 'is_canceled' column as the crossvalidator needs it
sdf = sdf.withColumn("label", sdf["is_canceled"])

sdf.toPandas().head(2)

# split the data to train and test
train, test = sdf.randomSplit([0.8, 0.2], seed = 12345)

"""### [1st Model] will be logistic regression that predicts whether the booking will be canceled or not


"""

from pyspark.ml.classification import LogisticRegression
lr = LogisticRegression(featuresCol = 'feature_vector', labelCol = 'is_canceled', maxIter=25)
lrModel = lr.fit(train)

predictions = lrModel.transform(test)
predictions.select('is_canceled', 'prediction', 'probability').show(10)
# print(lrModel.coefficients) #The coefficients represent the weights assigned to each feature
# # These weights indicate the importance or contribution of each feature towards predicting the target variable
# print(lrModel.intercept)#The intercept term is the constant term added to the linear combination of feature values multiplied by their respective coefficients
# # It represents the baseline prediction when all features are zero.

from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# Evaluate model
evaluator = MulticlassClassificationEvaluator(labelCol="is_canceled", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("Accuracy:", accuracy)

"""# evaluate model"""

lrModel.evaluate(test).predictions.show(3)

"""## or"""

# from pyspark.sql.functions import expr

# # Assuming 'predictions' DataFrame contains 'prediction' and 'is_canceled' columns

# # Calculate the number of correct predictions
# correct_predictions = predictions.filter(expr('prediction = label')).count()

# # Calculate the total number of predictions
# total_predictions = predictions.count()

# # Calculate the accuracy score
# accuracy = correct_predictions / total_predictions

# # Print the accuracy score
# print("Accuracy:", accuracy)

"""### Let's tune the hyperparameters of the model using the `crossValidator` which automate the tuning by trying the given parameters and choose the best one based on the evaluator."""

# tune the model using the training data
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from pyspark.ml.evaluation import BinaryClassificationEvaluator
# Create ParamGrid for Cross Validation
paramGrid = (ParamGridBuilder()
                .addGrid(lr.elasticNetParam, [0.0, 0.5, 1.0])
                .addGrid(lr.maxIter, [10, 20, 40])
                .build())

evaluator = BinaryClassificationEvaluator(metricName="areaUnderROC")
cv = CrossValidator(estimator=lr, estimatorParamMaps=paramGrid, evaluator=evaluator, numFolds=5)

cvModel = cv.fit(train)
cvModel.bestModel

predictions = cvModel.transform(test)
predictions.select('is_canceled', 'prediction', 'probability').show(10)

accuracy = accuracy_score(predictions.select('is_canceled').toPandas(), predictions.select('prediction').toPandas())
print('accuracy of the model = ', accuracy*100, '%')

"""78% accuracy score for the logistic regression. focus on  `ROC AREA`

### [2nd Model] will be Decision Tree classifier
"""

from pyspark.ml.classification import DecisionTreeClassifier
dt=DecisionTreeClassifier(featuresCol="feature_vector",labelCol="is_canceled",maxBins=180)
dtModel = dt.fit(train)

predictions = dtModel.transform(test)
predictions.select('is_canceled', 'prediction', 'probability').show(10)

# get the accuracy of the model using accuracy_score on the test data
accuracy = accuracy_score(predictions.select('is_canceled').toPandas(), predictions.select('prediction').toPandas())
print('accuracy of the model = ', accuracy*100, '%')

"""### 77.8 % accuracy for the Decision tree.

# [3rd Model] Try the random forest classifier.
"""

# train random forest model on the data
from pyspark.ml.classification import RandomForestClassifier
rf = RandomForestClassifier(featuresCol = 'feature_vector', labelCol = 'is_canceled', maxBins=180)
rfModel = rf.fit(train)

predictions = rfModel.transform(test)
predictions.select('is_canceled', 'prediction', 'probability').show(10)

# get the accuracy of the model using accuracy_score on the test data
accuracy = accuracy_score(predictions.select('is_canceled').toPandas(), predictions.select('prediction').toPandas())
print('accuracy of the model = ', accuracy*100, '%')

"""## Also 79% accuracy for the Random Forest Model.

## [4th Model] Try to train Support Vector Machines to classify, SVM are the best in binary classifications.
"""

from pyspark.ml.classification import LinearSVC
svm = LinearSVC(featuresCol = 'feature_vector', labelCol = 'is_canceled', maxIter=10)
svmModel = svm.fit(train)

predictions = svmModel.transform(test)
predictions.select('is_canceled', 'prediction').show(10)

# accuracy of the model
accuracy = accuracy_score(predictions.select('is_canceled').toPandas(), predictions.select('prediction').toPandas())
print('accuracy of the model = ', accuracy*100, '%')

"""75% accuracy SVM

# [5th Model] Try Gradient Boost
"""

from pyspark.ml.classification import GBTClassifier
gbt = GBTClassifier(featuresCol = 'feature_vector', labelCol = 'is_canceled', maxIter=10, maxBins=180)
gbtModel = gbt.fit(train)

predictions = gbtModel.transform(test)
predictions.select('is_canceled', 'prediction').show(10)

# accuracy of the model
accuracy = accuracy_score(predictions.select('is_canceled').toPandas(), predictions.select('prediction').toPandas())
print('accuracy of the model = ', accuracy*100, '%')

"""# This is formatted as code


Gradient Boost 82% accuracy
"""

