NEI <- readRDS("summarySCC_PM25.rds")

# Filter data only for Baltimore City, Maryland
baltimore <- NEI[NEI$fips == "24510",]

# Calc total emission by year in thousand tons
sum_year <- tapply(baltimore$Emissions, baltimore$year, sum) / 1e3

years <- names(sum_year)

# Plot without X axis
plot(
  years,
  sum_year, 
  xaxt="n", 
  ylim=c(0, 1.1*max(sum_year)),
  xlab="Year", 
  ylab="Emissions (thousand tons)", 
  main="Baltimore City, Maryland PM2.5 Emissions",
  col="red",  
  type="b",
  pch=8)

# Make X axis labels to show year
axis(1, at=years)

# Create png
dev.copy(png, filename = "plot2.png")
dev.off()

