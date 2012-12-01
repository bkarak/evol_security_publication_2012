pdf:
	#cd data && make
	pdflatex msr.tex
	bibtex msr
	pdflatex msr.tex
	pdflatex msr.tex

clean:
	-rm -f *.aux
	-rm -f *.bbl *.blg *.log *.out *.dvi *~ *.spl
	-rm -f msr.pdf

bib:
	biblio.py texmode msr.tex > msr.bib

count-words:
	@echo "Counting Words"
	-wc -w *.tex *.bib | tee new-wc.out | diff old-wc.out -
	-mv new-wc.out old-wc.out
