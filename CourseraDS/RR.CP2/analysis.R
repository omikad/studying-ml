library(R.utils)
library(dplyr)
library(data.table)
library(ggplot2)
library(reshape2)

if (!file.exists("repdata-data-StormData.csv")){
  bunzip2("repdata-data-StormData.csv.bz2", remove = FALSE)
}

data <- data.table::fread("repdata-data-StormData.csv", data.table = FALSE)

data <- data %>% 
  select(EVTYPE,FATALITIES,INJURIES,PROPDMG,PROPDMGEXP,CROPDMG,CROPDMGEXP) %>%
  filter(FATALITIES>0 | INJURIES>0 | PROPDMG>0 | CROPDMG>0) 

calc_exp <- function(sym) {
  sym <- ifelse(sym %in% c("H", "h"), 100, sym)
  sym <- ifelse(sym %in% c("K", "k"), 1000, sym)
  sym <- ifelse(sym %in% c("M", "m"), 1000000, sym)
  sym <- ifelse(sym == "B", 1000000000, sym)
  sym <- ifelse(sym %in% c("+", "0", "1", "2", "3"), 1, sym)
  sym <- ifelse(sym %in% c("4", "5", "6", "7", "8"), 1, sym)
  sym <- ifelse(sym %in% c("-", "", "?"), 0, sym)
  sym
}

data <- data %>% mutate(PROPDMGEXP = calc_exp(PROPDMGEXP))
data <- data %>% mutate(CROPDMGEXP = calc_exp(CROPDMGEXP))

data <- data %>% 
  mutate(PROPDMGEXP = as.numeric(PROPDMGEXP)) %>%
  mutate(PROPDMG = PROPDMG * PROPDMGEXP)

data <- data %>% 
  mutate(CROPDMGEXP = as.numeric(CROPDMGEXP)) %>%
  mutate(CROPDMG = CROPDMG * CROPDMGEXP)

harm <- data %>% group_by(EVTYPE) %>% 
  summarize(injuries=sum(INJURIES), fatalities=sum(FATALITIES)) %>%
  arrange(desc(injuries + 10 * fatalities)) %>% top_n(5)

harm$EVTYPE <- factor(harm$EVTYPE, levels=rev(harm$EVTYPE))

harm <- melt(harm, id.vars=c("EVTYPE"))

ggplot(harm, aes(EVTYPE, value, fill=as.factor(harm$variable))) + 
  geom_bar(stat="identity", position="dodge") + 
  geom_text(aes(label=value), position=position_dodge(width=0.9), hjust=-0.25) +
  ylim(c(0, max(harm$value) * 1.1)) +
  xlab("") + ylab("Number of casualties") +
  ggtitle("Most harmful events across USA with respect to population health") +
  guides(fill=guide_legend(title="")) +
  coord_flip() +
  theme(panel.background=element_blank(), axis.text.x=element_blank(),
        axis.ticks.x=element_blank(), axis.ticks.y=element_blank())



economy <- data %>% group_by(EVTYPE) %>% 
  summarize(damage=round(sum(CROPDMG + PROPDMG) / 1e9, digits=2)) %>%
  arrange(desc(damage)) %>% top_n(5)

economy$EVTYPE <- factor(economy$EVTYPE, levels=rev(economy$EVTYPE))

ggplot(economy, aes(EVTYPE, damage)) + 
  geom_bar(stat="identity", position="dodge", fill="palegreen3") + 
  geom_text(aes(label=damage), hjust=-0.25) +
  ylim(c(0, max(economy$damage) * 1.2)) +
  xlab("") + ylab("Damage in billion $") +
  ggtitle("Most harmful events across USA with respect to economic consequences") +
  guides(fill=guide_legend(title="")) +
  coord_flip() +
  theme(panel.background=element_blank(), axis.text.x=element_blank(),
        axis.ticks.x=element_blank(), axis.ticks.y=element_blank())
