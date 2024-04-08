library(tidyverse)
library(ggplot2)
# library(dplyr)
# library(forcats)
library(tikzDevice)

source("r/base.r")

options(
    # tikzDocumentDeclaration = "\\documentclass[conference]{IEEEtran}",
    tikzLatexPackages = c(
        getOption("tikzLatexPackages"),
        "\\usepackage{amsmath}" # , "\\usepackage[utf8]{inputenc}"
    )
    # tikzSanitizeCharacters = c("%"),
    # tikzReplacementCharacters = c("\\%")
)
# options(
#     tikzDocumentDeclaration = "\\documentclass[conference]{IEEEtran}",
#     tikzLatexPackages = c(
#         getOption("tikzLatexPackages"),
#         "\\usepackage{amsmath}" # , "\\usepackage[utf8]{inputenc}"
#     ),
#     tikzSanitizeCharacters = c("%"),
#     tikzReplacementCharacters = c("\\%")
# )

do.save.tikz <- function(g, out.name, .width, .height) {
    tikz(str_c("img-tikz/", out.name, ".tex"), width = .width, height = .height)
    print(g)
    dev.off()
}
do.save.pdf <- function(g, out.name, .width, .height) {
    pdf(str_c("img-pdf/", out.name, ".pdf"), width = .width, height = .height)
    print(g)
    dev.off()
}


COLOURS.LIST <- c("black", "#E69F00", "#999999", "#009371",
                  "#beaed4", "#ed665a", "#1f78b4", "#009371")

# theme_paper_base <- function() {
#     return(theme_bw(base_size = BASE.SIZE) +
#         theme(
#             axis.title.x = element_text(size = BASE.SIZE),
#             axis.title.y = element_text(size = BASE.SIZE),
#             legend.title = element_text(size = BASE.SIZE),
#             legend.position = "top",
#             plot.margin = unit(c(0, 0.2, 0, 0), "cm")
#         ))
# }

dat <- read_csv("csvs/algorithm_comparison_n_layers.csv")

dat.sub <- dat %>% filter(!is.na(algorithm))
dat.base <- dat %>% filter(is.na(algorithm)) %>% select(-algorithm) %>% rename(bound=model)

g <- ggplot(dat.sub, aes(x=n_qaoa_layers, y=performance,
                colour=model, shape=model)) +
    scale_colour_manual("Simulation", values=COLOURS.LIST) +
    scale_shape_discrete("Simulation") +
    geom_line(dat=dat.base, inherit.aes=FALSE, 
              aes(x=n_qaoa_layers, y=performance, group=bound, linetype=bound),
              colour=COLOURS.LIST[[3]]) +
    geom_line() + geom_point(size=0.8) + theme_paper_base() +
    facet_grid(cols=vars(algorithm), rows=vars(problem)) +
    xlab("\\# QAOA layers \\(p\\)") + ylab("Relative Performance") +
    scale_linetype_discrete("Bound") + theme(
        legend.position="none",
        legend.box="vertical",
        legend.spacing=unit(c(0), "cm"),
        legend.title=element_text(size=BASE.SIZE)
    )

# g <- ggplot(dat.sub, aes(x=n_qaoa_layers, y=performance,
#                 colour=model, shape=model)) +
#     scale_colour_manual("Simulation", values=COLOURS.LIST) +
#     scale_shape_discrete("Simulation") +
#     geom_line(dat=dat.base, inherit.aes=FALSE, 
#               aes(x=n_qaoa_layers, y=performance, group=bound, linetype=bound),
#               colour=COLOURS.LIST[[3]]) +
#     geom_point(size=0.8) + geom_line() + theme_paper_base() +
#     facet_grid(cols=vars(algorithm), rows=vars(problem)) +
#     xlab("\\# QAOA layers $p$") + ylab("Relative Performance") +
#     scale_linetype_discrete("Bound") +
#     theme(
#         # legend.box="vertical",
#         strip.text = element_text(size=6.8)
#     )


WIDTH <- COLWIDTH
HEIGHT <- WIDTH * 0.55
do.save.pdf(g, "algorithm_comparison_n_layers", WIDTH, HEIGHT)
do.save.tikz(g, "algorithm_comparison_n_layers", WIDTH, HEIGHT)
