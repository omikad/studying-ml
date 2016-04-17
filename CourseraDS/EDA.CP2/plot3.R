NEI <- readRDS("summarySCC_PM25.rds")

library(dplyr)
library(ggplot2)

# Filter data only for Baltimore City, Maryland
baltimore <- NEI[NEI$fips == "24510",]

sum_year <- (baltimore
             %>% select(Emissions, year, type) 
             %>% group_by(year, type)
             %>% summarize(total = sum(Emissions)))

years <- unique(sum_year$year)

plot3 <- ggplot(sum_year, aes(x=year, y=total, color=type, group=type)) +
  scale_x_continuous(breaks=years, name="Year") +
  ylab("Emissions (tons)") +
  ggtitle("Baltimore City, Maryland PM2.5 Emissions") +
  geom_point(pch=8, size=3) + 
  geom_line() 

print(plot3)

# Create png
dev.copy(png, filename = "plot3.png")
dev.off()

