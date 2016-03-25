# load data
hyps <- read.csv("hypothesis.csv", sep=";")

hyps$expression <- as.character(hyps$expression)

hyps$prior <- hyps$prior.score / sum(hyps$prior.score)

hyps.set <- list()
for (i in 1:nrow(hyps)) {
  items <- eval(parse(text=hyps$expression[i]))
  hyps.set[[i]] <- items
  hyps$size[i] = length(items)
}

isInHypothesis <- function(x) {
  unlist(lapply(hyps.set, function(s){ x %in% s }))
}

# Prior, likelihood and posterior for D = {16}
d16.likelihood <- 1 / hyps$size * isInHypothesis(16)
d16.posterior <- hyps$prior * d16.likelihood
d16.posterior <- d16.posterior / sum(d16.posterior)

par(mfrow=c(3,1), mar=c(1,4,1,1))

plot(hyps$prior, ylab="Prior", ylim=c(0, 0.2), pch=16)
plot(d16.likelihood, ylab="Likelihood", pch=16)
plot(d16.posterior, pch=16)






