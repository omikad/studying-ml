NEI<-readRDS("summarySCC_PM25.rds")
SCC<-readRDS("Source_Classification_Code.rds")

##then we need to summarize the Emission data (sum) by year.
library(dplyr)
NEI_by_yr<-group_by(NEI,year)
NEI_by_yr_sum<-summarize(NEI_by_yr,Total.Emission.by.year=sum(Emissions,na.rm=T))
##Then, we plot the data
plot(NEI_by_yr_sum,col="red",pch=19,main="Total Emission by year")