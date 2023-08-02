library(knitr)
library(tidyverse)
data <- read.csv("28_07_bez_przecinkow.csv")
govOnTheLeft <- data[data[1] == "L",]
govOnTheRight <- data[data[1] == "R",]
govNo <- data[data[1] == "0",]

x = c(nrow(govOnTheLeft), 100 * nrow(govOnTheLeft)/nrow(data))
y = c(nrow(govOnTheRight), 100* nrow(govOnTheRight)/nrow(data))
z = c(nrow(govNo), 100* nrow(govNo)/nrow(data))

govPosition <- data.frame(Nadrzędnik_z_lewej = x, 
                          Nadrzędnik_z_prawej = y,
                          Brak_nadrzędnika = z)
rownames(govPosition) <- c('Liczba', 'Procent')
kable(govPosition, digits=1)

statystyki_i_Wilcox <- function(data){
  x <- c(median(data[, 20]), median(data[,19]), median(data[, 18]), median(data[, 17]))
  y <- c(median(data[, 29]), median(data[, 28]), median(data[, 27]), median(data[, 26]))
  z <- c(mean(data[, 20]), mean(data[,19]), mean(data[, 18]), mean(data[, 17]))
  w <- c(mean(data[, 29]), mean(data[, 28]), mean(data[, 27]), mean(data[, 26]))
  a <- c(as.double(wilcox.test(data$L.chars, data$R.chars, alternative = "less")[1]), 
         as.double(wilcox.test(data$L.syllables, data$R.syllables, alternative= "less")[1]),
         as.double(wilcox.test(data$L.tokens, data$R.tokens, alternative = "less")[1]),
         as.double(wilcox.test(data$L.words, data$R.words, alternative = "less")[1]))
  
  b <- c(as.double(wilcox.test(data$L.chars, data$R.chars, alternative = "less")[3]), 
         as.double(wilcox.test(data$L.syllables, data$R.syllables, alternative= "less")[3]),
         as.double(wilcox.test(data$L.tokens, data$R.tokens, alternative = "less")[3]),
         as.double(wilcox.test(data$L.words, data$R.words, alternative = "less")[3]))
  
  wyn <- data.frame(median_L = x, median_R = y, mean_L = z, mean_R = w, V = a, p = b)
  rownames(wyn) <- c('znaki', 'sylaby', 'tokeny',  'słowa')
  return (wyn)
}

chi_kwadrat_L_R <- function(data){
  govOnTheLeft <- data[data[1] == "L",]
  govOnTheRight <- data[data[1] == "R",]
  govNo <- data[data[1] == "0",]
  x <- c(nrow(govOnTheLeft[govOnTheLeft[20] < govOnTheLeft[29],])/nrow(govOnTheLeft[govOnTheLeft[20] != govOnTheLeft[29],]),
         nrow(govOnTheLeft[govOnTheLeft[19] < govOnTheLeft[28],])/nrow(govOnTheLeft[govOnTheLeft[19] != govOnTheLeft[28],]),
         nrow(govOnTheLeft[govOnTheLeft[18] < govOnTheLeft[27],])/nrow(govOnTheLeft[govOnTheLeft[18] != govOnTheLeft[27],]),
         nrow(govOnTheLeft[govOnTheLeft[17] < govOnTheLeft[26],])/nrow(govOnTheLeft[govOnTheLeft[17] != govOnTheLeft[26],]))
  y <- c(nrow(govOnTheLeft[govOnTheLeft[20] != govOnTheLeft[29],]), 
         nrow(govOnTheLeft[govOnTheLeft[19] != govOnTheLeft[28],]),
         nrow(govOnTheLeft[govOnTheLeft[18] != govOnTheLeft[27],]),
         nrow(govOnTheLeft[govOnTheLeft[17] != govOnTheLeft[26],]))
  z <- c(nrow(govOnTheRight[govOnTheRight[20] < govOnTheRight[29],])/nrow(govOnTheRight[govOnTheRight[20] != govOnTheRight[29],]),
         nrow(govOnTheRight[govOnTheRight[19] < govOnTheRight[28],])/nrow(govOnTheRight[govOnTheRight[19] != govOnTheRight[28],]),
         nrow(govOnTheRight[govOnTheRight[18] < govOnTheRight[27],])/nrow(govOnTheRight[govOnTheRight[18] != govOnTheRight[27],]),
         nrow(govOnTheRight[govOnTheRight[17] < govOnTheRight[26],])/nrow(govOnTheRight[govOnTheRight[17] != govOnTheRight[26],]))
  w <- c(nrow(govOnTheRight[govOnTheRight[20] != govOnTheRight[29],]),
         nrow(govOnTheRight[govOnTheRight[19] != govOnTheRight[28],]),
         nrow(govOnTheRight[govOnTheRight[18] != govOnTheRight[27],]),
         nrow(govOnTheRight[govOnTheRight[17] != govOnTheRight[26],]))
  
  M1 <- as.table( rbind(c(x[1]*y[1], (1-x[1])*y[1]), c(z[1]*w[1], (1-z[1])*w[1]) ))
  chi_char <- chisq.test(M1)
  
  M2 <- as.table( rbind(c(x[2]*y[2], (1-x[2])*y[2]), c(z[2]*w[2], (1-z[2])*w[2]) ))
  chi_syl <- chisq.test(M2)
  
  M3 <- as.table( rbind(c(x[3]*y[3], (1-x[3])*y[3]), c(z[3]*w[3], (1-z[3])*w[3]) ))
  chi_tokens <- chisq.test(M3)
  
  M4<- as.table( rbind(c(x[4]*y[4], (1-x[4])*y[4]), c(z[4]*w[4], (1-z[4])*w[4]) ))
  chi_words <- chisq.test(M4)

  a <- c(chi_char$statistic, chi_syl$statistic, chi_tokens$statistic, chi_words$statistic)
  b <- c(chi_char$p.value, chi_syl$p.value, chi_tokens$p.value, chi_words$p.value)
  wyn <- data.frame(gov_L_prop = x, gov_L_count  = y, gov_R_prop = z, gov_R_count = w, chi_sqr = a, p = b)
  
  rownames(wyn) <- c('znaki', 'sylaby', 'tokeny', 'słowa')
  return (wyn)
}

chi_kwadrat_NoGov_L_R <- function(data){
  govOnTheLeft <- data[data[1] == "L",]
  govOnTheRight <- data[data[1] == "R",]
  govNo <- data[data[1] == "0",]
  m <- c(nrow(govNo[govNo[20] < govNo[29],])/nrow(govNo[govNo[20] != govNo[29],]),
         nrow(govNo[govNo[19] < govNo[28],])/nrow(govNo[govNo[19] != govNo[28],]),
         nrow(govNo[govNo[18] < govNo[27],])/nrow(govNo[govNo[18] != govNo[27],]),
         nrow(govNo[govNo[17] < govNo[26],])/nrow(govNo[govNo[17] != govNo[26],]))
  n <- c(nrow(govNo[govNo[20] != govNo[29],]), 
         nrow(govNo[govNo[19] != govNo[28],]),
         nrow(govNo[govNo[18] != govNo[27],]),
         nrow(govNo[govNo[17] != govNo[26],]))
  x <- c(nrow(govOnTheLeft[govOnTheLeft[20] < govOnTheLeft[29],])/nrow(govOnTheLeft[govOnTheLeft[20] != govOnTheLeft[29],]),
         nrow(govOnTheLeft[govOnTheLeft[19] < govOnTheLeft[28],])/nrow(govOnTheLeft[govOnTheLeft[19] != govOnTheLeft[28],]),
         nrow(govOnTheLeft[govOnTheLeft[18] < govOnTheLeft[27],])/nrow(govOnTheLeft[govOnTheLeft[18] != govOnTheLeft[27],]),
         nrow(govOnTheLeft[govOnTheLeft[17] < govOnTheLeft[26],])/nrow(govOnTheLeft[govOnTheLeft[17] != govOnTheLeft[26],]))
  y <- c(nrow(govOnTheLeft[govOnTheLeft[20] != govOnTheLeft[29],]), 
         nrow(govOnTheLeft[govOnTheLeft[19] != govOnTheLeft[28],]),
         nrow(govOnTheLeft[govOnTheLeft[18] != govOnTheLeft[27],]),
         nrow(govOnTheLeft[govOnTheLeft[17] != govOnTheLeft[26],]))
  z <- c(nrow(govOnTheRight[govOnTheRight[20] < govOnTheRight[29],])/nrow(govOnTheRight[govOnTheRight[20] != govOnTheRight[29],]),
         nrow(govOnTheRight[govOnTheRight[19] < govOnTheRight[28],])/nrow(govOnTheRight[govOnTheRight[19] != govOnTheRight[28],]),
         nrow(govOnTheRight[govOnTheRight[18] < govOnTheRight[27],])/nrow(govOnTheRight[govOnTheRight[18] != govOnTheRight[27],]),
         nrow(govOnTheRight[govOnTheRight[17] < govOnTheRight[26],])/nrow(govOnTheRight[govOnTheRight[17] != govOnTheRight[26],]))
         
  w <- c(nrow(govOnTheRight[govOnTheRight[20] != govOnTheRight[29],]),
         nrow(govOnTheRight[govOnTheRight[19] != govOnTheRight[28],]),
         nrow(govOnTheRight[govOnTheRight[18] != govOnTheRight[27],]),
         nrow(govOnTheRight[govOnTheRight[17] != govOnTheRight[26],]))
  
  M1 <- as.table( rbind(c(m[1]*n[1], (1-m[1])*n[1]), c(x[1]*y[1], (1-x[1])*y[1]) ))
  chi_char_L <- chisq.test(M1)
  M2 <- as.table( rbind(c(m[2]*n[2], (1-m[2])*n[2]), c(x[2]*y[2], (1-x[2])*y[2]) ))
  chi_syl_L <- chisq.test(M2)
  M3 <- as.table( rbind(c(m[3]*n[3], (1-m[3])*n[3]), c(x[3]*y[3], (1-x[3])*y[3]) ))
  chi_tokens_L <- chisq.test(M3)
  M4 <- as.table( rbind(c(m[4]*n[4], (1-m[4])*n[4]), c(x[4]*y[4], (1-x[4])*y[4]) ))
  chi_words_L <- chisq.test(M4)
  
  statL <-c(chi_char_L$statistic, chi_syl_L$statistic, chi_tokens_L$statistic, chi_words_L$statistic)
  pvalL <-c(chi_char_L$p.value, chi_syl_L$p.value, chi_tokens_L$p.value, chi_words_L$p.value)
  
  M5 <- as.table( rbind(c(m[1]*n[1], (1-m[1])*n[1]), c(z[1]*w[1], (1-z[1])*w[1]) ))
  chi_char_R <- chisq.test(M5)
  M6 <- as.table( rbind(c(m[2]*n[2], (1-m[2])*n[2]), c(z[2]*w[2], (1-z[2])*w[2]) ))
  chi_syl_R <- chisq.test(M6)
  M7 <- as.table( rbind(c(m[3]*n[3], (1-m[3])*n[3]), c(z[3]*w[3], (1-z[3])*w[3]) ))
  chi_tokens_R <- chisq.test(M7)
  M8 <- as.table( rbind(c(m[4]*n[4], (1-m[4])*n[4]), c(z[4]*w[4], (1-z[4])*w[4]) ))
  chi_words_R <- chisq.test(M8)
  
  statR <-c(chi_char_R$statistic, chi_syl_R$statistic, chi_tokens_R$statistic, chi_words_R$statistic)
  pvalR <-c(chi_char_R$p.value, chi_syl_R$p.value, chi_tokens_R$p.value, chi_words_R$p.value)
  
  wyn <- data.frame(no_gov_prop = m, no_gov_count = n, chi_sqr_L = statL, p_L = pvalL, chi_sqr_R = statR, p_R=pvalR)
  rownames(wyn) <- c('znaki', 'sylaby', 'tokeny', 'słowa')
  
  return(wyn)
}

# asd <- statystyki_i_Wilcox(govOnTheRight)
# asd <- asd %>% arrange(mean_L)
# asd <- asd %>% group_by()

kable(statystyki_i_Wilcox(data), digits=2, caption = "Wszystkie koordynacje")
kable(statystyki_i_Wilcox(govNo), digits=2, caption = "Brak nadrzędnika")
kable(statystyki_i_Wilcox(govOnTheLeft), digits=2, caption = "Nadrzędnik z lewej")
kable(statystyki_i_Wilcox(govOnTheRight), digits=2, caption = "Nadrzędnik z prawej")

kable(chi_kwadrat_L_R(data), caption= "Procent krótszych członów po lewej w koordynacjach z nadrzędnikiem po lewej i prawej stronie i o członach o różnej długości")

kable(chi_kwadrat_NoGov_L_R(data), caption= "Procent krótszych członów po lewej w koordynacjach bez nadrzędnika i o członach o różnej długości")
