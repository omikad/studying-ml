rankhospital <- function(state, outcome, num="best") {
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
  data <- data[!is.na(data[,valIndex]),]
  
  ordCoeff <- if (num == "worst") -1 else 1
  
  ord <- order(ordCoeff * data[,valIndex], data[,2])
  
  if (is.numeric(num) && num > nrow(data)) return(NA)
  
  index <- if (num == "best" || num == "worst") 1 else num
  
  data[ord[index],2]
}