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

# Function to draw plot
make_plot <- function(dataset) {
  # Set layout to draw 4 figures
  par(mfrow = c(2,2))
  
  with(dataset, plot(
    DateTime,
    Global_active_power, 
    type = "l",
    xlab = "",
    ylab = "Global Active Power"))
  
  with(dataset, plot(
    DateTime,
    Voltage, 
    type = "l",
    xlab = "datetime",
    ylab = "Voltage"))
  
  with(dataset, plot(
    DateTime,
    Sub_metering_1, 
    type = "n",
    xlab = "",
    ylab = "Energy sub metering"))
  
  # For the third plot - draw 3 lines for each sub metering
  with(dataset, lines(DateTime, Sub_metering_1, type = "l", col = "black"))
  with(dataset, lines(DateTime, Sub_metering_2, type = "l", col = "red"))
  with(dataset, lines(DateTime, Sub_metering_3, type = "l", col = "blue"))
  
  with(dataset, plot(
    DateTime,
    Global_reactive_power, 
    type = "l",
    xlab = "datetime",
    ylab = "Global_reactive_power")) 
}

# Copying to png from screen works incorrect
# So, I will call function make_plot twice: for screen, for png
make_plot(dataset)

# Create png
png(file = "plot4.png")
make_plot(dataset)
dev.off()


