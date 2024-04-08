library(ggplot2)
library(stringr)
library(forcats)
library(dplyr)
library(tikzDevice)

options(tikzLatexPackages = c(getOption("tikzLatexPackages"),
                              "\\usepackage{amsmath}"))

source("r/base.r")

COLOURS.LIST <- c("#E69F00", "#999999", "#009371", "black", "#beaed4", "#ed665a", "#1f78b4", "#009371")

data <- read.csv("csvs/rqaoa_samples.csv", stringsAsFactors = FALSE)

data <- data %>% mutate(samples = fct_relevel(samples, 
    "10",
    "100",
    "1000",
    "Exact values"
    # "Random guessing"
))

filtered_data <- data |> filter(samples != "Exact values")


map_qaoa_depth <- function(depth) {
    if (depth == "1") {
        return("1 layer")
    }
    return(str_c(depth, " layers"))
}
map_n_qubits <- function(n) {
    if (n == "1") {
        return("1 qubit")
    }
    return(str_c(n, " qubits"))
}

label_qaoa_depth <- function(depth) {
    return(sapply(depth, map_qaoa_depth))
}
label_n_qubits <- function(n) {
    return(sapply(n, map_n_qubits))
}

g <- ggplot(data=data, aes(x=noise_level, y=performance, color=samples, shape=samples, linetype=samples)) +
    # stat_summary(fun=mean, geom="line") +
    geom_line() +
    geom_point(size=0.8) +
    facet_grid(n_qaoa_layers ~ n_qubits, labeller=labeller(.rows=label_qaoa_depth, .cols=label_n_qubits)) +
    # theme(plot.margin=unit(c(0,0,0,0), 'cm')) +
    # theme(legend.margin=unit(-1, 'cm')) +
    scale_linetype_manual(name="\\# Samples", values=c("solid", "solid", "solid", "11")) +
    scale_color_manual(name="\\# Samples", values=COLOURS.LIST) +
    scale_shape_discrete(name="\\# Samples") +
    # scale_size_manual(name="\\# Samples", values=c(0.8, 0.8, 0.8, 0)) +
    # scale_linetype(name="Algorithm") +
    scale_x_continuous(minor_breaks=NULL) +
    # guides(color=guide_legend(title.position="top", title="Algorithm"), linetype="none") +
    # guides(linetype=guide_legend(title.position="top")) +
    labs(y="Relative performance", x="Noise level") +
    theme_paper_base() +
    theme(
        legend.title=element_text(size=BASE.SIZE)
    )
    # guides(color=guide_legend(title.position="top")) +


save_name <- "rqaoa_samples"
pdf(str_c(PDF_OUTDIR, save_name, ".pdf"), width = COLWIDTH, height = 0.7*COLWIDTH)
print(g)
dev.off()
tikz(str_c(TIKZ_OUTDIR, save_name, ".tex"), width = COLWIDTH, height = 0.7*COLWIDTH)
print(g)
dev.off()