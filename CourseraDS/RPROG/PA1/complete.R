complete <- function(directory, id = 1:332) {
  output <- data.frame(i=id, nobs=rep(0, length(id)))
  
  for (i in id) {
    name <- paste(directory, "/", sprintf("%03d", i), ".csv", sep="")
    
    dat <- read.csv(name, header=TRUE)
    
    nobs <- nrow(na.omit(dat))
    
    output$nobs[output$i == i] <- nobs
  }
  
  output
}