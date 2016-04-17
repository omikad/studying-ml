pollutantmean <- function(directory, pollutant, id = 1:332) {
  values <- c()
  
  meanCol <- if (pollutant == "sulfate") 2 else 3
  
  for (i in id) {
    name <- paste(directory, "/", sprintf("%03d", i), ".csv", sep="")
    
    dat <- read.csv(name, header=TRUE)
    
    values <- append(values, dat[,meanCol])
  }
  
  mean(values, na.rm=TRUE)
}