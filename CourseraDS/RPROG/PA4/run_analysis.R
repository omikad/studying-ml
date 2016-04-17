# This script downloads the data, extracts it and performs some cleaning on the data:
# 1. Merges the training and the test sets to create one data set.
# 2. Extracts only the measurements on the mean and standard deviation for each measurement.
# 3. Uses descriptive activity names to name the activities in the data set
# 4. Appropriately labels the data set with descriptive variable names.
# 5. From the data set in step 4, creates a second, independent tidy data set with the average
#    of each variable for each activity and each subject.

library(dplyr)

rowsLimit <- 100000 # Change this variable to 500 to test script

getData = function() {
  "Download data from url and unzip it"
  fileUrl <- "https://d396qusza40orc.cloudfront.net/getdata%2Fprojectfiles%2FUCI%20HAR%20Dataset.zip"
  zipFile <- "UCI HAR Dataset.zip"
  
  if (!file.exists(zipFile)) {
    message("Download data from web")
    download.file(fileUrl, destfile=zipFile, mode="wb")  
  }
  
  if (!dir.exists("UCI HAR Dataset")) {
    message("Extract data from zip")
    unzip(zipFile, exdir=".", overwrite=TRUE)    
  }
}

readPart <- function(dir) {
  "Read all data files to a list of data frames"
  filePaths <- list(
    subject  = paste("UCI HAR Dataset", dir, paste("subject_", dir, ".txt", sep=""), sep="/"),
    features = paste("UCI HAR Dataset", dir, paste("x_", dir, ".txt", sep=""), sep="/"),
    activity = paste("UCI HAR Dataset", dir, paste("y_", dir, ".txt", sep=""), sep="/")
  )
  
  list(
    subject  = read.table(filePaths$subject,  strip.white=TRUE, header=FALSE, nrows=rowsLimit),
    features = read.table(filePaths$features, strip.white=TRUE, header=FALSE, nrows=rowsLimit),
    activity = read.table(filePaths$activity, strip.white=TRUE, header=FALSE, nrows=rowsLimit)   
  )
}

mergeParts <- function(partLeft, partRight) {
  "Merge test and train data sets to a one data set with same structure"
  result <- lapply(seq_along(partLeft), function(i) rbind(partLeft[[i]], partRight[[i]]))
  names(result) <- names(partLeft)
  result
}

getData()

# 1. Merge the training and the test sets to create one data set.
dataSet <- mergeParts(readPart("test"), readPart("train"))

names(dataSet$subject) <- "subject"
names(dataSet$activity) <- "activity"

# 2. Extract only the measurements on the mean and standard deviation for each measurement.
# Read feature names
featuresData <- read.table("UCI HAR Dataset/features.txt", header=FALSE, stringsAsFactors=FALSE)
names(featuresData) <- c("rowindex", "feature")

# Filter feature rows and apply them as column names
featuresData <- filter(featuresData, grepl("mean\\(|std\\(", featuresData$feature))
names(dataSet$features)[featuresData$rowindex] <- make.names(featuresData$feature, unique=TRUE)
dataSet$features <- dataSet$features[,featuresData$rowindex]

# 3. Use descriptive activity names to name the activities in the data set
activityNames <- read.table("UCI HAR Dataset/activity_labels.txt", header=FALSE)
names(activityNames) <- c("code", "name")
dataSet$activity <- activityNames[match(dataSet$activity$activity, activityNames$code), 2]

# 4. Appropriately labels the data set with descriptive variable names.
dataSet<- do.call(cbind, dataSet)

dataSet <- (dataSet 
            %>% setNames(gsub(".mean", ".Mean", names(.)))
            %>% setNames(gsub(".std", ".Std", names(.)))
            %>% setNames(gsub("Acc", "Accelerometer", names(.)))
            %>% setNames(gsub("Gyro", "Gyroscope", names(.)))
            %>% setNames(gsub("gravity", "Gravity", names(.)))
            %>% setNames(gsub("Mag", "Magnitude", names(.)))
            %>% setNames(gsub("angle.t", "tAngle", names(.)))
            %>% setNames(gsub("features\\.|(\\.)+", "", names(.)))
            %>% setNames(gsub("^t", "time", names(.)))
            %>% setNames(gsub("^f", "frequency", names(.)))
)

# 5. From the data set in step 4, creates a second, independent tidy data set with the average
#    of each variable for each activity and each subject.
summaryData <- (dataSet %>% group_by(activity, subject) %>% summarize_each(funs(mean)))

# This instruction creates file to submit
write.table(summaryData, "UCI_HAR_tidy.txt", row.name=FALSE)




