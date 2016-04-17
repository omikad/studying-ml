best <- function(state, outcome) {
  data <- read.csv("outcome-of-care-measures.csv", 
                   colClasses = "character", 
                   na.strings="Not Available", 
                   stringsAsFactors=FALSE)
  
  data <- data[data[,7] == state,]
  
  if (nrow(data) == 0) stop("invalid state")
  
  valIndex <- if (outcome == "heart attack") 11 else
              if (outcome == "heart failure") 17 else
              if (outcome == "pneumonia") 23 else -1
  
  if (valIndex == -1) stop("invalid outcome")
  
  data[,valIndex] <- as.numeric(data[,valIndex])
  
  data[order(data[,valIndex], data[,2]),][1,2]
}