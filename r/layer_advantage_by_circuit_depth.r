library(ggplot2)
library(stringr)
library(forcats)
library(dplyr)
library(tikzDevice)
library(ggnewscale)
library(ggh4x)

options(tikzLatexPackages = c(getOption("tikzLatexPackages"),
                              "\\usepackage{amsmath}"))

source("r/base.r")

light_colors <- c("#333333", "#E9C77A")
data <- read.csv("csvs/layer_advantage_by_circuit_depth_total.csv", stringsAsFactors = FALSE)
average_data <- read.csv("csvs/layer_advantage_by_circuit_depth.csv", stringsAsFactors = FALSE)

# data <- data |> filter(algorithm != "Random")
# data$algorithm[data$algorithm == "Random"] <- "Random guessing"
data <- data %>% mutate(algorithm = fct_relevel(algorithm, 
    "QAOA",
    "WSQAOA",
    "WS-Init-QAOA",
    "RQAOA",
    # "Random guessing"
))

label_noise_level <- function (level) {
    return(str_c("Noise: ", level))
}

strip <- strip_themed(background_x = elem_list_rect(fill =
    c(
        "#dfcef8",
        "#e0e0e0",
        "#e0e0e0",
        "#dfcef8",
        "#e0e0e0",
        "#e0e0e0"
    )
))

g <- ggplot(data=data, aes(x=circuit_depth, y=relative_performance, color=problem)) +
    # stat_summary(fun=mean, geom="line") +
    # geom_line() +
    geom_hline(yintercept=1, linetype="11", linewidth=0.3, color=COLOURS.LIST[3]) +
    geom_point(size=0.1, alpha=0.1) +
    scale_color_manual(values=light_colors) +
    guides(colour=guide_legend(override.aes=list(alpha=1, size=1, shape=4))) +

    new_scale_colour() +
    geom_point(data=average_data, size=0.5, alpha=1, shape=4, aes(color=problem)) +
    scale_color_manual(values=COLOURS.LIST) +
    facet_grid2(
        algorithm ~ noise_level,
        labeller=labeller(noise_level=label_noise_level, algorithm=label_value),
        strip=strip
    ) +
    # theme(plot.margin=unit(c(0,0,0,0), 'cm')) +
    # theme(legend.margin=unit(-1, 'cm')) +
    # scale_linetype_manual(values=c("solid", "11")) +
    # scale_linetype(name="Algorithm") +
    scale_x_continuous(minor_breaks=NULL) +
    scale_y_continuous(breaks=seq(0.8, 1.2, 0.1)) +
    # guides(color=guide_legend(title.position="top", title="Algorithm"), linetype="none") +
    # guides(linetype=guide_legend(title.position="top")) +
    labs(y="Relative advantage of layer 2", x="Circuit depth") +
    theme_paper_base() +
    theme(
        strip.text.y = element_text(size=4),
        strip.text.x = element_text(size=6),
    )

    # guides(color=guide_legend(title.position="top")) +

save_name <- "layer_advantage_by_circuit_depth"
pdf(str_c(PDF_OUTDIR, save_name, ".pdf"), width = COLWIDTH, height = 0.75*COLWIDTH)
print(g)
dev.off()
tikz(str_c(TIKZ_OUTDIR, save_name, ".tex"), width = COLWIDTH, height = 0.7*COLWIDTH)
print(g)
dev.off()