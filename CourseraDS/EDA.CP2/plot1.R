NEI <- readRDS("summarySCC_PM25.rds")

# Calc total emission by year in million tons
sum_year <- tapply(NEI$Emissions, NEI$year, sum) / 1e6

years <- names(sum_year)

# Plot without X axis
plot(
  years, 
  sum_year, 
  xaxt="n", 
  ylim=c(0, 1.1*max(sum_year)),
  xlab="Year", 
  ylab="Emissions (million tons)", 
  main="Total US PM2.5 Emissions",
  col="red", 
  type="b",
  pch=8)

# Make X axis labels to show year
axis(1, at=years)

# Create png
dev.copy(png, filename = "plot1.png")
dev.off()

