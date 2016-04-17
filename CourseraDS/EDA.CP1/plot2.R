file_name <- "household_power_consumption.txt"

# Read header only
header <- read.csv(
  file_name, 
  nrows = 1, 
  sep =';',
  stringsAsFactors = FALSE)

# Read the data from particular date range
dataset <- read.csv(
  file_name, 
  na.strings = "?", 
  stringsAsFactors = FALSE, 
  sep = ";",
  skip = 66300,
  nrows = 4000,
  comment.char = "")

# Fix column names
colnames(dataset) <- colnames(header)

# Create DateTime column to be posix date and time
dataset <- transform(dataset, DateTime = as.POSIXct(paste(Date, Time), format="%d/%m/%Y %H:%M:%S"))
dataset <- transform(dataset, Date = as.POSIXct(Date, format="%d/%m/%Y"))

# Filter data range
dataset = subset(dataset, Date >= "2007-02-01" & Date <= "2007-02-02")

# Set layout to draw one figure
par(mfrow = c(1,1))

# Create plot
plot(
  dataset$DateTime, 
  dataset$Global_active_power, 
  type = "l",
  xlab = "",
  ylab = "Global Active Power (kilowatts)")

# Create png
dev.copy(png, filename = "plot2.png")
dev.off()


