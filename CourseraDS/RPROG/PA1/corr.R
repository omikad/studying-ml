corr <- function(directory, threshold = 0) {
  completeCases <- complete(directory)
  
  completeCases <- completeCases[completeCases$nobs > threshold,]
  
  if (nrow(completeCases) == 0) numeric()
  else {
    output <- c()
    
    for (i in completeCases$i) {
      name <- paste(directory, "/", sprintf("%03d", i), ".csv", sep="")
      
      dat <- read.csv(name, header=TRUE)
      
      realData <- na.omit(dat)
      
      output <- append(output, cor(realData[,2], realData[,3]))
    }
    
    output
  }
}