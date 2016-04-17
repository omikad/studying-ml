rankall <- function(outcome, num="best") {
  data <- read.csv("outcome-of-care-measures.csv", 
                   colClasses = "character", 
                   na.strings="Not Available", 
                   stringsAsFactors=FALSE)
  
  valIndex <- if (outcome == "heart attack") 11 
    else if (outcome == "heart failure") 17
    else if (outcome == "pneumonia") 23
    else -1
  
  if (valIndex == -1) stop("invalid outcome")
  
  data[,valIndex] <- as.numeric(data[,valIndex])
  
  ordCoeff <- if (num == "worst") -1 else 1
  ord <- order(ordCoeff * data[,valIndex], data[,2])
  
  data <- data[ord,c(2,7,valIndex)]
  names(data) <- c("hospital","state","outcome")
  
  splitted <- split(data, data$state)
  
  applied <- lapply(splitted, function(frame) {
    if (is.numeric(num) && num > nrow(frame)) {
      frame <- frame[1,]
      frame$hospital[1] <- NA
      frame$outcome[1] <- NA
      return(frame)
    }
    
    index <- if (num == "best" || num == "worst") 1 else num
    
    frame[index,]
  })
  
  do.call("rbind", applied)[,1:2]
}