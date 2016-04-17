NEI <- readRDS("summarySCC_PM25.rds")
SCC <- readRDS("Source_Classification_Code.rds")

# Filter classification codes for coal combustion sources
scc_comb_coal <- subset(SCC, grepl('Comb', EI.Sector) & grepl('Coal', EI.Sector))$SCC

# Filter NEI data
comb_coal <- NEI[NEI$SCC %in% scc_comb_coal,]

# Calc total emission by year in thousand tons
sum_year <- tapply(comb_coal$Emissions, comb_coal$year, sum) / 1e3

years <- names(sum_year)

# Plot without X axis
plot(
  years,
  sum_year, 
  xaxt="n", 
  ylim=c(0, 1.1*max(sum_year)),
  xlab="Year", 
  ylab="Emissions (thousand tons)", 
  main="Coal combustion related source PM2.5 Emissions",
  col="red",  
  type="b",
  pch=8)

# Make X axis labels to show year
axis(1, at=years)

# Create png
dev.copy(png, filename = "plot4.png")
dev.off()

