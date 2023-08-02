library(tidyverse)
library(knitr)
library(ggplot2)
library(gridExtra)
library(ggExtra)
data <- read.csv("28_07_bez_przecinkow.csv")

data <- data %>% summarize(position=governor.position, 
                           chars1=L.chars, 
                           syllables1=L.syllables, 
                           words1=L.words, 
                           tokens1=L.tokens, 
                           chars2=R.chars, 
                           syllables2=R.syllables, 
                           words2=R.words, 
                           tokens2=R.tokens,
                           liczba_czlonow = no.conjuncts,
                           id = sent_id,
                           spojnik = conjunction.word)

tmp <- data %>% group_by(liczba_czlonow) %>% count() #liczebności koordynacji ze względu na liczbę członów koordynacji
tmp1 <- data %>% group_by(spojnik) %>% count()

dataLeftGov <- data[data$position == "L",]
dataRightGov <- data[data$position == "R",]
dataNoGov <- data[data$position == "0",]

prepareData <- function(data){
  dataWithDiff <- data %>% summarize(position, 
                                     charsDiff = chars1 - chars2, 
                                     syllablesDiff = syllables1 - syllables2,
                                     wordsDiff = words1 - words2, 
                                     tokensDiff = tokens1 - tokens2)
  
  dataChars <- dataWithDiff %>% filter(charsDiff != 0)
  dataSyllables <- dataWithDiff %>% filter(syllablesDiff != 0)
  dataWords <- dataWithDiff %>% filter(wordsDiff != 0)
  dataTokens <- dataWithDiff %>% filter(tokensDiff != 0)
  
  dataChars <- dataChars %>% 
                             mutate(absCharsDiff = abs(charsDiff)) %>% 
                             group_by(absCharsDiff) %>% 
                             summarize(shorterLeft = ifelse(charsDiff < 0, 1, 0), absCharsDiff,  .groups = 'drop')
  
  dataSyllables <- dataSyllables %>% 
                                mutate(absSyllablesDiff = abs(syllablesDiff)) %>% 
                                group_by(absSyllablesDiff) %>% 
                                summarize(shorterLeft = ifelse(syllablesDiff < 0, 1, 0), absSyllablesDiff,  .groups = 'drop')
  
  dataWords <- dataWords %>% 
                         mutate(absWordsDiff = abs(wordsDiff)) %>%
                         group_by(absWordsDiff) %>% 
                         summarize(shorterLeft = ifelse(wordsDiff < 0, 1, 0), absWordsDiff,  .groups = 'drop')
  
  dataTokens <- dataTokens %>% 
                           mutate(absTokensDiff = abs(tokensDiff)) %>%
                           group_by(absTokensDiff) %>% 
                           summarize(shorterLeft = ifelse(tokensDiff < 0, 1, 0), absTokensDiff,  .groups = 'drop')
  return(list(dataChars, dataSyllables, dataWords, dataTokens))
}

Left <- prepareData(dataLeftGov)
Right <- prepareData(dataRightGov)
No <- prepareData(dataNoGov)

x1 <- do.call(rbind.data.frame, Left[1])
x2 <- do.call(rbind.data.frame, Left[2])
x3 <- do.call(rbind.data.frame, Left[3])
x4 <- do.call(rbind.data.frame, Left[4])
x5 <- do.call(rbind.data.frame, Right[1])
x6 <- do.call(rbind.data.frame, Right[2])
x7 <- do.call(rbind.data.frame, Right[3])
x8 <- do.call(rbind.data.frame, Right[4])
x9 <- do.call(rbind.data.frame, No[1])
x10 <- do.call(rbind.data.frame, No[2])
x11 <- do.call(rbind.data.frame, No[3])
x12 <- do.call(rbind.data.frame, No[4])

# L1 <- ggplot(x1, aes(absCharsDiff, shorterLeft)) +
#   geom_smooth(method="glm", formula = y ~ x, method.args = list(family = binomial))+
#   labs(x = "absolute difference in characters") +
#   labs(y = "proportion of shorter left conjuncts")+
#   coord_cartesian(ylim=c(0.4, 1))
# L2 <- ggplot(x2, aes(absSyllablesDiff, shorterLeft)) +
#   geom_smooth(method="glm", formula = y ~ x, method.args = list(family = binomial))+
#   labs(x = "absolute difference in syllables") +
#   labs(y = "proportion of shorter left conjuncts")+
#   coord_cartesian(ylim=c(0.4, 1))
# L3 <- ggplot(x3, aes(absWordsDiff, shorterLeft)) +
#   geom_smooth(method="glm", formula = y ~ x, method.args = list(family = binomial))+
#   labs(x = "absolute difference in words") +
#   labs(y = "proportion of shorter left conjuncts")+
#   coord_cartesian(ylim=c(0.4, 1))
# L4 <- ggplot(x4, aes(absTokensDiff, shorterLeft)) +
#   geom_smooth(method="glm", formula = y ~ x, method.args = list(family = binomial))+
#   labs(x = "absolute difference in tokens") +
#   labs(y = "proportion of shorter left conjuncts")+
#   coord_cartesian(ylim=c(0.4, 1))
# R1 <- ggplot(x5, aes(absCharsDiff, shorterLeft)) +
#   geom_smooth(method="glm", formula = y ~ x, method.args = list(family = binomial))+
#   labs(x = "absolute difference in characters") +
#   labs(y = "proportion of shorter left conjuncts")+
#   coord_cartesian(ylim=c(0.1, 1))
# R2 <- ggplot(x6, aes(absSyllablesDiff, shorterLeft)) +
#   geom_smooth(method="glm", formula = y ~ x, method.args = list(family = binomial))+
#   labs(x = "absolute difference in syllables") +
#   labs(y = "proportion of shorter left conjuncts")+
#   coord_cartesian(ylim=c(0.1, 1))
# R3 <- ggplot(x7, aes(absWordsDiff, shorterLeft)) +
#   geom_smooth(method="glm", formula = y ~ x, method.args = list(family = binomial))+
#   labs(x = "absolute difference in words") +
#   labs(y = "proportion of shorter left conjuncts")+
#   coord_cartesian(ylim=c(0.1, 1))
# R4 <- ggplot(x8, aes(absTokensDiff, shorterLeft)) +
#   geom_smooth(method="glm", formula = y ~ x, method.args = list(family = binomial))+
#   labs(x = "absolute difference in tokens") +
#   labs(y = "proportion of shorter left conjuncts")+
#   coord_cartesian(ylim=c(0.1, 1))
# N1 <- ggplot(x9, aes(absCharsDiff, shorterLeft)) +
#   geom_smooth(method="glm", formula = y ~ x, method.args = list(family = binomial))+
#   labs(x = "absolute difference in characters") +
#   labs(y = "proportion of shorter left conjuncts")+
#   coord_cartesian(ylim=c(0.4, 1))
# N2 <- ggplot(x10, aes(absSyllablesDiff, shorterLeft)) +
#   geom_smooth(method="glm", formula = y ~ x, method.args = list(family = binomial))+
#   labs(x = "absolute difference in syllables") +
#   labs(y = "proportion of shorter left conjuncts")+
#   coord_cartesian(ylim=c(0.4, 1))
# N3 <- ggplot(x11, aes(absWordsDiff, shorterLeft)) +
#   geom_smooth(method="glm", formula = y ~ x, method.args = list(family = binomial))+
#   labs(x = "absolute difference in words") +
#   labs(y = "proportion of shorter left conjuncts")+
#   coord_cartesian(ylim=c(0.4, 1))
# N4 <- ggplot(x12, aes(absTokensDiff, shorterLeft)) +
#   geom_smooth(method="glm", formula = y ~ x, method.args = list(family = binomial))+
#   labs(x = "absolute difference in tokens") +
#   labs(y = "proportion of shorter left conjuncts")+
#   coord_cartesian(ylim=c(0.4, 1))
# 
# ggpubr::ggarrange(N1, N2, N3, N4, L1, L2, L3, L4, R1, R2, R3, R4, ncol=4, nrow=3)

x1$type = "L"
x2$type = "L"
x3$type = "L"
x4$type = "L"
x5$type = "R"
x6$type = "R"
x7$type = "R"
x8$type = "R"
x9$type = "0"
x10$type = "0"
x11$type = "0"
x12$type = "0"

chars = rbind(x9, x5, x1)
syllables = rbind(x2, x6, x10)
words = rbind(x3, x7, x11)
tokens = rbind(x4, x8, x12)

fitChars <- glm(shorterLeft ~ absCharsDiff * type, data = chars, family = "binomial")
summary(fitChars)

fitSyllables <- glm(shorterLeft ~ absSyllablesDiff * type, data = syllables, family = "binomial")
summary(fitSyllables)

fitWords <- glm(shorterLeft ~ absWordsDiff * type, data = words, family = "binomial")
summary(fitWords)

fitTokens <- glm(shorterLeft ~ absTokensDiff * type, data = tokens, family = "binomial")
summary(fitTokens)

g1 <- glm(shorterLeft ~ absCharsDiff * type, family = binomial, data = chars)
emt1 <- emtrends(g1, specs=pairwise~'type', var='absCharsDiff')
sum1 <- summary((emt1),infer=TRUE)
sum1

xd <- unlist(sum4[1])
xd
g2 <- glm(shorterLeft ~ absSyllablesDiff * type, family = binomial, data = syllables)
emt2 <- emtrends(g2, specs=pairwise~'type', var='absSyllablesDiff')
sum2 <- summary((emt2),infer=TRUE)
sum2

g3 <- glm(shorterLeft ~ absTokensDiff * type, family = binomial, data = tokens)
emt3 <- emtrends(g3, specs=pairwise~'type', var='absTokensDiff')
sum3 <- summary((emt3),infer=TRUE)
sum3

g4 <- glm(shorterLeft ~ absWordsDiff * type, family = binomial, data = words)
emt4 <- emtrends(g4, specs=pairwise~'type', var='absWordsDiff')
sum4 <- summary((emt4),infer=TRUE)
sum4

l3 <- ggplot(words, aes(x=absWordsDiff, y=shorterLeft)) + geom_point(alpha = 0.1) +
  geom_smooth(method="glm", formula=y~x, se=TRUE, lwd = 0.4, fill = 'grey70', method.args = list(family = binomial), colour = 'black') + 
  xlab("") + ylab("") + facet_wrap(~ type) +
  ggtitle("Słowa") + theme(plot.title = element_text(hjust = 0.5),
                           panel.background = element_rect('grey95', 'black', 0.2, 'solid', 'black'),
                           panel.grid.major = element_line('white', 0.3, 'solid',
                                                           'square', 'white'),
                           panel.grid.minor = element_line('white', 0.5, 'solid',
                                                           'square', 'white'))

l4 <- ggplot(tokens, aes(x=absTokensDiff, y=shorterLeft)) + geom_point(alpha = 0.1) +
  geom_smooth(method="glm", formula=y~x, se=TRUE, lwd = 0.4, fill = 'grey70', method.args = list(family = binomial), colour = 'black') + 
  xlab("") + ylab("") + facet_wrap(~ type) +
  ggtitle("Tokeny") + theme(plot.title = element_text(hjust = 0.5),
                            panel.background = element_rect('grey95', 'black', 0.2, 'solid', 'black'),
                            panel.grid.major = element_line('white', 0.3, 'solid',
                                                            'square', 'white'),
                            panel.grid.minor = element_line('white', 0.5, 'solid',
                                                            'square', 'white'))

l1 <- ggplot(chars, aes(x=absCharsDiff, y=shorterLeft)) + geom_point(alpha = 0.1) +
  geom_smooth(method="glm", formula=y~x, se=TRUE, lwd = 0.4, fill = 'grey70', method.args = list(family = binomial), colour = 'black') + 
  xlab("") + ylab("") + facet_wrap(~ type) +
  ggtitle("Znaki") + theme(plot.title = element_text(hjust = 0.5), 
                           panel.background = element_rect('grey95', 'black', 0.2, 'solid', 'black'),
                           panel.grid.major = element_line('white', 0.3, 'solid',
                                                           'square', 'white'),
                           panel.grid.minor = element_line('white', 0.5, 'solid',
                                                           'square', 'white'))

l2 <- ggplot(syllables, aes(x=absSyllablesDiff, y=shorterLeft)) + geom_point(alpha = 0.1) +
  geom_smooth(method="glm", formula=y~x, se=TRUE, lwd = 0.4, fill = 'grey70', method.args = list(family = binomial), colour = 'black') + 
  xlab("") + ylab("") + facet_wrap(~ type) +
  ggtitle("Sylaby") + theme(plot.title = element_text(hjust = 0.5), 
                            panel.background = element_rect('grey95', 'black', 0.2, 'solid', 'black'),
                            panel.grid.major = element_line('white', 0.3, 'solid',
                                                            'square', 'white'),
                            panel.grid.minor = element_line('white', 0.5, 'solid',
                                                            'square', 'white'))

plots_words_tokens = list(l3, l4)
grid.arrange(grobs = plots_words_tokens, ncol = 1, nrow = 2, left = "Proporcja krótszego członu z lewej strony", bottom = "Moduł z róźnicy długości członów")

plots_chars_syllables = list(l2, l1)
grid.arrange(grobs = plots_chars_syllables, ncol = 1, nrow = 2, left = "Proporcja krótszego członu z lewej strony", bottom = "Moduł z róźnicy długości członów")