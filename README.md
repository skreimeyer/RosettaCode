# RosettaCode

## A humble research project in the expressiveness of programming languages

These programs are a few small utilities that were used to approximate the expressive power of various programming languages. This is done by grouping solutions to problems on rosettacode.org and ordering by the mean lines of code (LOC) count. While LOC is admittedly a very crude metric of complexity, there are identifiable trends within this data set.

![top 10](https://github.com/skreimeyer/RosettaCode/raw/master/top-10.png)

The graphs are a series of box-plots with the distribution of the total LOC used to solve a particular problem. The plots are sorted by the median LOC count for all languages. Different plots highlight specific programming languages which can be referenced in the legend. The lines drawn for these languages are run through a noise-reduction filter to smooth out the very high levels of variation.

Interestingly, there are some consistent relationships between LOC count and various particular languages.

Some insights:

- "Production" languages, like C, C++ and Java tend to have above average verbosity.
- Functional programming languages tend to fall within the inter-quartile range, but there are significant differences between them.
- Python is consistently near the median of LOC. Jack of all trades! 
- Good choices for code golfers: APL and Mathematica
- Modern languages tend to be more terse than older languages
- COBOL is not very good for brevity
