library(ggplot2)
library(dplyr)
library(forcats)
library(stringr)
library(tikzDevice)

options(tikzLatexPackages = c(getOption("tikzLatexPackages"),
                              "\\usepackage{amsmath}"))

source("r/base.r")

data <- read.csv("csvs/circuit_fidelity.csv", stringsAsFactors = FALSE)

data <- data %>% mutate(algorithm = fct_relevel(algorithm, 
    "QAOA",
    "WSQAOA",
    "WS-Init-QAOA"
    # "RQAOA"
))

data$noise_source[data$noise_source == "Thermal Relaxation"] <- "Therm. Relax."
data <- data |> mutate(noise_source = fct_relevel(noise_source,
    "Depolarizing",
    "Therm. Relax.",
    "Both"
))


# facet_titles <- c('QAOA.Depth'="$p$",'Number.of.Qubits'="$n$")
facet_labeller <- function(variable, value) {
    return(paste(facet_titles[variable], value, sep=": "))
}

g <- ggplot(data=data,mapping=aes(x=n_qaoa_layers, y=fidelity, color=algorithm)) +
    geom_line(aes(linetype=noise_source)) +
    geom_point(aes(shape=algorithm), size=0.8) +
    # geom_point(aes(shape=Problem), size=1) +
    facet_grid(~ problem) +
    # theme(plot.margin=unit(c(5,0,0,0), 'cm')) +
    # theme(legend.margin=unit(-1, 'cm')) +
    scale_color_manual(name="Algorithm", values=COLOURS.LIST) +
    scale_shape_discrete(name="Algorithm") +
    scale_linetype_discrete(name="Noise source") +
    scale_x_continuous(breaks=c(1,2,3),minor_breaks=NULL) +
    # guides(color=guide_legend(title="Algorithm")) +
    # guides(linetype=guide_legend(title.position="top")) +
    labs(y="Circuit fidelity", x="\\# QAOA Layers") +
    theme(plot.margin=c(10,10,10,10)) +
    theme_paper_base() +
    theme(
        # legend.position="right",
        legend.box="vertical",
        legend.spacing=unit(c(0), "cm"),
        legend.title=element_text(size=BASE.SIZE)
    )
    # guides(color=guide_legend(title.position="top")) +

save_name <- "circuit_fidelity"

WIDTH <- 1.0 * COLWIDTH
HEIGHT <- 0.6 * COLWIDTH
pdf(str_c(PDF_OUTDIR, save_name, ".pdf"), width = WIDTH, height = HEIGHT)
print(g)
dev.off()
tikz(str_c(TIKZ_OUTDIR, save_name, ".tex"), width = WIDTH, height = HEIGHT)
print(g)
dev.off()