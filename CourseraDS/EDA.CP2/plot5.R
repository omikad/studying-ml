NEI <- readRDS("summarySCC_PM25.rds")
SCC <- readRDS("Source_Classification_Code.rds")

# Filter data only for emissions in Baltimore
baltimore <- NEI[NEI$fips == "24510",]

# Filter classification codes for motor vehicle (assume motor vehicle means mobile)
scc_mobile_vehicle <- subset(SCC, grepl('Mobile', EI.Sector) & grepl('Vehicle', EI.Sector))$SCC

# Filter NEI data for Baltimore and motor vehicles
mobile_vehicle <- baltimore[baltimore$SCC %in% scc_mobile_vehicle,]

# Calc total emission by year
sum_year <- tapply(mobile_vehicle$Emissions, mobile_vehicle$year, sum)

years <- names(sum_year)

# Plot without X axis
plot(
  years,
  sum_year, 
  xaxt="n", 
  ylim=c(0, 1.1*max(sum_year)),
  xlab="Year", 
  ylab="Emissions (tons)", 
  main="Baltimore Motor Vehicle PM2.5 Emissions",
  col="red",  
  type="b",
  pch=8)

# Make X axis labels to show year
axis(1, at=years)

# Create png
dev.copy(png, filename = "plot5.png")
dev.off()

