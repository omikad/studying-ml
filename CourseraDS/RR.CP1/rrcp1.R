library(dplyr)
library(ggplot2)

# ~~~~~ Load the data
dataset <- read.csv(unz("activity.zip", "activity.csv"))
dataset$date <- as.Date(dataset$date, "%Y-%m-%d")

# ~~~~~ What is mean total number of steps taken per day?
showMeanMedianByDate <- function (showme) {
  showme.bydate = showme %>% 
    filter(!is.na(steps)) %>%
    group_by(date) %>% 
    summarize(steps = sum(steps))
  
  print(ggplot(showme.bydate, aes(steps)) +
    labs(title="Histogram of the total number of steps taken each day") +
    labs(x="Steps", y="Days") +
    geom_histogram(bins=5, col="white"))
  
  print(paste(
    "Mean and median of the total number of steps taken per day:",
    mean(showme.bydate$steps), 
    "and", 
    median(showme.bydate$steps)))
}

showMeanMedianByDate(dataset)

# ~~~~~ What is the average daily activity pattern?
days.count <- length(unique(dataset$date))

dataset.bytime <- dataset %>%
  filter(!is.na(steps)) %>%
  group_by(interval) %>%
  summarize(steps = mean(steps))

with(dataset.bytime, plot(
  interval, 
  steps, 
  type="l",
  main="Average number of steps taken of 5-minute interval",
  xlab="Interval",
  ylab="Average steps"))

print(paste(
  "5-minute interval, on average across all the days in the dataset,",
  "contains the maximum number of steps:",
  dataset.bytime[which.max(dataset.bytime$steps),]$interval))

# ~~~~~ Imputing missing values
print(paste(
  "Total number of missing values in the dataset:",
  sum(!complete.cases(dataset))
))

# NA values are only in dataset steps column
# Fill all missing values using mean for that 5-minute interval
dataset.fixed <- merge(dataset, dataset.bytime, by="interval") %>%
  rename(steps=steps.x, steps.mean=steps.y) %>%
  mutate(steps=ifelse(is.na(steps),steps.mean,steps)) %>%
  arrange(date, interval)

showMeanMedianByDate(dataset.fixed)

# Are there differences in activity patterns between weekdays and weekends?
dataset.fixed$week <- weekdays(dataset.fixed$date) %in% c("Saturday", "Sunday")
dataset.fixed$week <- factor(dataset.fixed$week, labels=c("weekday","weekend"))

dataset.week <- dataset.fixed %>%
  group_by(interval, week) %>%
  summarize(steps = mean(steps))

print(ggplot(dataset.week, aes(interval, steps)) + 
      geom_line() + 
      xlab("Interval") + ylab("Number of steps") +
      facet_wrap(~week, ncol=1))


