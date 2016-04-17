NEI <- readRDS("summarySCC_PM25.rds")
SCC <- readRDS("Source_Classification_Code.rds")

library(dplyr)
library(ggplot2)

# Counties to select
cities_fips <- c("24510", "06037")
cities_names <- c("Baltimore, MD", "Los Angeles, CA")

# Filter data only for emissions in Baltimore
nei_cities <- NEI[NEI$fips %in% cities_fips,]

# Change factors to better understanding
nei_cities$fips <- factor(nei_cities$fips, levels=cities_fips, labels=cities_names)

# Filter classification codes for motor vehicle (assume motor vehicle means mobile)
scc_mobile_vehicle <- subset(SCC, grepl('Mobile', EI.Sector) & grepl('Vehicle', EI.Sector))$SCC

# Filter NEI data and motor vehicles
nei_cities_motor <- nei_cities[nei_cities$SCC %in% scc_mobile_vehicle,]

sum_year <- (nei_cities_motor
             %>% select(Emissions, year, fips) 
             %>% group_by(year, fips)
             %>% summarize(total = sum(Emissions)))

plot6 <- ggplot(sum_year, aes(x=year, y=total, color=fips, group=fips)) +
  ylab("Emissions (tons)") +
  ggtitle("Motor Vehicle PM2.5 Emissions for Baltimore and Los Angeles County") +
  geom_point(pch=8, size=3) + 
  geom_line() 

print(plot6)

# Create png
dev.copy(png, filename = "plot6.png")
dev.off()

