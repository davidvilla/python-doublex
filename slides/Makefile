
LINKS=css lib plugin js

all: reveal.js $(LINKS)

reveal.js:
	git clone --depth 1 https://github.com/hakimel/reveal.js.git

$(LINKS):
	ln -s reveal.js/$@ $@

clean:
	$(RM) -r reveal.js
	$(RM) $(LINKS)
