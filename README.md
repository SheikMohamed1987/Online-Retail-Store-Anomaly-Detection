# Online-Retail-Store-UCI-ML-Data---Customer-Churn-Modelling---Anamoly-Detection
Modelling Customer Churn When Churns Are Not Explicitly Observed.

Thanks to Susan for insights - Her article URL in R programming - https://towardsdatascience.com/modelling-customer-churn-when-churns-are-not-explicitly-observed-with-r-a768a1c919d5


Dataset: https://archive.ics.uci.edu/ml/datasets/Online+Retail

Customer churn can be characterized as either contractual or non-contractual. It can also be characterized as voluntary or non-voluntary depending on the cancellation mechanism.
We will only discuss non-contractual and voluntary churn today.
Non-Contractual
Customers are free to buy or not at anytime
Churn event is not explicitly observed
Voluntary
Customers make the choice to leave the service
In general, customer churn is a classification problem. However, at non-contractual business including Amazon (non-prime member), every purchase could be that customer’s last, or one of a long sequence of purchases. Thus, churn modelling in non-contractual business is not a classification problem, it is an anomaly detection problem. In order to determine when customers are churning or likely to churn, we need to know when they are displaying anomalously large between purchase times.
Anomaly Detection
Anomaly detection is a technique used to identify unusual patterns that do not conform to expected behaviour, called outliers. It has many applications in businesses, from credit card fraud detection(based on “amount spent”) to system health monitoring.
And here we are, using anomaly detection to model customer churn for non-contractual business. We want to be able to make claims like “9 times out of 10, Customer X will make his next purchase within Y days”. If Customer X does not make another purchase within Y days, we know that there is only a 1 in 10 chance of this happening, and that this behaviour is anomalous.
To do this, we will need each customer’s between purchase time distribution. This may be difficult to estimate, especially if the distribution is multimodal or irregular. To avoid this difficulty, we will take a non-parametric approach and use the Empirical Cumulative Distribution Function (ECDF) to approximate the quantiles of each customer’s between purchase time distribution. Once we have the ECDF, we can approximate the 90th percentile, and obtain estimates of the nature we have described above. Let’s get started!
