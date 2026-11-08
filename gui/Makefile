ACCOUNT?=$(shell cat ../ACCOUNT)
IMAGE=unum-apps-lightning-gui
VERSION?=dev
SEMVER=?=$(VERSION)
NAME=$(IMAGE)-$(ACCOUNT)

.PHONY: build shell image push semver

build:
	docker build . --build-arg BASE=$(BASE) -t $(ACCOUNT)/$(IMAGE):$(VERSION)

shell:
	-docker run -it --rm $(ACCOUNT)/$(IMAGE):$(VERSION) sh

image: build

push: image
	docker push $(ACCOUNT)/$(IMAGE):$(VERSION)

semver:
	docker pull $(ACCOUNT)/$(IMAGE):$(VERSION)
	docker tag $(ACCOUNT)/$(IMAGE):$(VERSION) $(ACCOUNT)/$(IMAGE):$(SEMVER)
	docker push $(ACCOUNT)/$(IMAGE):$(SEMVER)

TTY=$(shell if tty -s; then echo "-it"; fi)

.PHONY: test

test:
	docker run $(TTY) --rm -v ${PWD}/www/js:/opt/service/www/js -v ${PWD}/www/flow.html:/opt/service/www/flow.html -v ${PWD}/test:/opt/service/test -w /opt/service node:22 sh -c "node --test test/*.test.js"
