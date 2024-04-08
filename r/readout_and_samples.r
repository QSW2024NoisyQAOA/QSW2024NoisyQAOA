library(ggplot2)
library(dplyr)
library(forcats)
library(stringr)
library(tikzDevice)

options(tikzLatexPackages = c(getOption("tikzLatexPackages"),
                              "\\usepackage{amsmath}"))

source("r/base.r")

data <- read.csv("csvs/readout_and_samples.csv", stringsAsFactors = FALSE)

data <- data %>% mutate(algorithm = fct_relevel(algorithm, 
    "QAOA",
    "WSQAOA",
    "WS-Init-QAOA",
    "RQAOA"
))
# facet_titles <- c('QAOA.Depth'="$p$",'Number.of.Qubits'="$n$")
facet_labeller <- function(variable, value) {
    return(paste(facet_titles[variable], value, sep=": "))
}

g <- ggplot(data=data,mapping=aes(x=n_qaoa_layers, y=relative_performance_decrease, color=algorithm)) +
    geom_line() +
    geom_point(aes(shape=algorithm)) +
    # geom_point(aes(shape=Problem), size=1) +
    facet_grid(~ source) +
    # theme(plot.margin=unit(c(5,0,0,0), 'cm')) +
    # theme(legend.margin=unit(-1, 'cm')) +
    scale_color_manual(values=COLOURS.LIST) +
    scale_x_continuous(breaks=c(1,2,3),minor_breaks=NULL) +
    # guides(color=guide_legend(title="Algorithm")) +
    # guides(linetype=guide_legend(title.position="top")) +
    labs(y="Relative\nPerformance Change", x="\\# QAOA Layers") +
    theme(plot.margin=c(10,10,10,10)) +
    theme_paper_base() +
    theme(
        legend.position="right"
    )
    # guides(color=guide_legend(title.position="top")) +

save_name <- "readout_and_samples"

WIDTH <- 1.0 * COLWIDTH
HEIGHT <- 0.4 * COLWIDTH
pdf(str_c(PDF_OUTDIR, save_name, ".pdf"), width = WIDTH, height = HEIGHT)
print(g)
dev.off()
tikz(str_c(TIKZ_OUTDIR, save_name, ".tex"), width = WIDTH, height = HEIGHT)
print(g)
dev.off()