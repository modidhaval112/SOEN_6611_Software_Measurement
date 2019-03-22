

library(Hmisc)
library(ggplot2)
library(reshape2)
library(lattice)
library(GGally)
library('caret')
library(e1071)

qt50 <-read.table('qt50.csv',header = T,sep = ",")
qt50<-data.frame(qt50)
data<-qt50
names(qt50)

keep <- c('size',
          'complexity',
          'change_churn',
          'total',
          'minor',
          'major',
          'ownership',
          'review_rate',
          'review_churn_rate',
          'self_reviews',
          'too_quick',
          'little_discussion',
          'post_bugs')


qt50 <- qt50[keep]

correlation <- cor(qt50,method = 'spearman')
print(correlation)
print (describe(correlation))


qt50$binary_post_bugs <- ifelse(qt50$post_bugs>0,1,0)

model <- glm( binary_post_bugs ~ complexity+change_churn+minor+ownership+self_reviews+review_churn_rate+too_quick, 
              family = binomial, 
              data = qt50)
print(summary(model))

model2<- update(model,~.-change_churn)
print(summary(model2))


model2<- update(model,~.-too_quick)
print(summary(model2))

testData <- read.csv2('qt51.csv',header = T,sep = ',')
pred <- predict.glm(model2,newdata = testData,se.fit = FALSE,type = 'response')
pred <- ifelse(pred > 0.05,1,0) 

print(paste('Number of 0 predicted :',length(pred[pred==0])))
print(paste('Number of 1 predicted :',length(pred[pred==1])))
